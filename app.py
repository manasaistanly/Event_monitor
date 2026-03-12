from flask import Flask, render_template, request, redirect, flash, session
import pymysql
from datetime import datetime
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_please_change_it'

# MySQL Connection Function
def get_db_connection():
    try:
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="college_event_radar"
        )
        return db
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'error')
            return redirect('/login')
        
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page!', 'error')
            return redirect('/')
        
        return f(*args, **kwargs)
    return decorated_function

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Please enter email and password!', 'error')
            return render_template('login.html')
        
        try:
            db = get_db_connection()
            if db is None:
                flash('Database connection failed!', 'error')
                return render_template('login.html')
            
            cursor = db.cursor()
            cursor.execute("SELECT id, name, email, role FROM users WHERE email = %s AND password = %s", 
                         (email, hash_password(password)))
            user = cursor.fetchone()
            cursor.close()
            db.close()
            
            if user:
                session['user_id'] = user[0]
                session['name'] = user[1]
                session['email'] = user[2]
                session['role'] = user[3]
                
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect('/')
            else:
                flash('Invalid email or password!', 'error')
                return render_template('login.html')
        
        except pymysql.Error as e:
            flash(f'Error logging in: {e}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'student').strip()
        
        if not all([name, email, password, confirm_password]):
            flash('Please fill in all fields!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('register.html')
        
        if role not in ['admin', 'student']:
            role = 'student'
        
        try:
            db = get_db_connection()
            if db is None:
                flash('Database connection failed!', 'error')
                return render_template('register.html')
            
            cursor = db.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'error')
                cursor.close()
                db.close()
                return render_template('register.html')
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hash_password(password), role)
            )
            db.commit()
            cursor.close()
            db.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect('/login')
        
        except pymysql.Error as e:
            flash(f'Error registering: {e}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'success')
    return redirect('/')

# Dashboard - Statistics and Overview (Admin only)
@app.route('/dashboard')
@admin_required
def dashboard():
    try:
        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return render_template("dashboard.html", stats={})
        
        cursor = db.cursor()
        
        # Get total events
        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]
        
        # Get upcoming events
        cursor.execute("SELECT COUNT(*) FROM events WHERE event_date >= DATE(NOW())")
        upcoming_events = cursor.fetchone()[0]
        
        # Get past events
        cursor.execute("SELECT COUNT(*) FROM events WHERE event_date < DATE(NOW())")
        past_events = cursor.fetchone()[0]
        
        # Get events by category
        cursor.execute("SELECT category, COUNT(*) as count FROM events GROUP BY category")
        categories = cursor.fetchall()
        
        # Get recent events
        cursor.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT 5")
        recent_events = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        stats = {
            'total': total_events,
            'upcoming': upcoming_events,
            'past': past_events,
            'categories': categories,
            'recent': recent_events
        }
        
        return render_template("dashboard.html", stats=stats)
    except pymysql.Error as e:
        flash(f'Error loading dashboard: {e}', 'error')
        return render_template("dashboard.html", stats={})

# Home Page - List All Events
@app.route('/')
def index():
    try:
        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return render_template("index.html", events=[])
        
        cursor = db.cursor()
        
        # Get search and filter parameters
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        sort = request.args.get('sort', 'date_asc')
        
        # Build query
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if search:
            query += " AND (event_name LIKE %s OR event_description LIKE %s OR event_location LIKE %s)"
            search_param = f"%{search}%"
            params = [search_param, search_param, search_param]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        # Add sorting
        if sort == 'date_desc':
            query += " ORDER BY event_date DESC"
        elif sort == 'name':
            query += " ORDER BY event_name ASC"
        else:  # date_asc
            query += " ORDER BY event_date ASC"
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        
        # Get all categories for filter
        cursor.execute("SELECT DISTINCT category FROM events")
        categories = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        db.close()
        
        if not events and search:
            flash(f'No events found for "{search}"', 'info')
        elif not events:
            flash('No events found. Create your first event!', 'info')
        
        return render_template("index.html", events=events, categories=categories, search=search, category=category, sort=sort)
    except pymysql.Error as e:
        flash(f'Error retrieving events: {e}', 'error')
        return render_template("index.html", events=[])

# Add Event Page (Admin only)
@app.route('/add')
@admin_required
def add():
    try:
        db = get_db_connection()
        if db is None:
            return render_template("add_event.html", categories=[])
        
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT category FROM events")
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        db.close()
        
        return render_template("add_event.html", categories=categories)
    except:
        return render_template("add_event.html", categories=[])

# Insert Event (Admin only)
@app.route('/insert', methods=['POST'])
@admin_required
def insert():
    try:
        name = request.form.get('name', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '09:00').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General').strip()
        organizer = request.form.get('organizer', '').strip()
        max_attendees = request.form.get('max_attendees', '0').strip()

        if not all([name, date, location]):
            flash('Please fill in all required fields!', 'error')
            return redirect('/add')

        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return redirect('/add')

        cursor = db.cursor()
        query = "INSERT INTO events (event_name, event_date, event_time, event_location, event_description, category, organizer, max_attendees) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, date, time, location, description, category, organizer, max_attendees or 0)

        cursor.execute(query, values)
        db.commit()
        cursor.close()
        db.close()

        flash('Event added successfully!', 'success')
        return redirect('/')
    except pymysql.Error as e:
        flash(f'Error adding event: {e}', 'error')
        return redirect('/add')

# Edit Event Page (Admin only)
@app.route('/edit/<int:event_id>')
@admin_required
def edit(event_id):
    try:
        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return redirect('/')
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        
        cursor.execute("SELECT DISTINCT category FROM events")
        categories = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        db.close()
        
        if not event:
            flash('Event not found!', 'error')
            return redirect('/')
        
        return render_template("edit_event.html", event=event, categories=categories)
    except pymysql.Error as e:
        flash(f'Error loading event: {e}', 'error')
        return redirect('/')

# Update Event (Admin only)
@app.route('/update/<int:event_id>', methods=['POST'])
@admin_required
def update(event_id):
    try:
        name = request.form.get('name', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '09:00').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General').strip()
        organizer = request.form.get('organizer', '').strip()
        max_attendees = request.form.get('max_attendees', '0').strip()

        if not all([name, date, location]):
            flash('Please fill in all required fields!', 'error')
            return redirect(f'/edit/{event_id}')

        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return redirect(f'/edit/{event_id}')

        cursor = db.cursor()
        query = "UPDATE events SET event_name=%s, event_date=%s, event_time=%s, event_location=%s, event_description=%s, category=%s, organizer=%s, max_attendees=%s WHERE id=%s"
        values = (name, date, time, location, description, category, organizer, max_attendees or 0, event_id)

        cursor.execute(query, values)
        db.commit()
        cursor.close()
        db.close()

        flash('Event updated successfully!', 'success')
        return redirect('/')
    except pymysql.Error as e:
        flash(f'Error updating event: {e}', 'error')
        return redirect(f'/edit/{event_id}')

# Delete Event (Admin only)
@app.route('/delete/<int:event_id>')
@admin_required
def delete(event_id):
    try:
        db = get_db_connection()
        if db is None:
            flash('Database connection failed!', 'error')
            return redirect('/')

        cursor = db.cursor()
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        db.commit()
        cursor.close()
        db.close()

        flash('Event deleted successfully!', 'success')
    except pymysql.Error as e:
        flash(f'Error deleting event: {e}', 'error')
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)