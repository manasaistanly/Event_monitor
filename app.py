from flask import Flask, render_template, request, redirect, flash
import pymysql
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

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

# Dashboard - Statistics and Overview
@app.route('/dashboard')
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

# Add Event Page
@app.route('/add')
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

# Insert Event
@app.route('/insert', methods=['POST'])
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

# Edit Event Page
@app.route('/edit/<int:event_id>')
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

# Update Event
@app.route('/update/<int:event_id>', methods=['POST'])
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

# Delete Event
@app.route('/delete/<int:event_id>')
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