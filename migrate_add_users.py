import pymysql
import hashlib

# Migration script to add users table

def migrate():
    try:
        # Connect to MySQL
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="college_event_radar"
        )
        
        cursor = db.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME='users' AND TABLE_SCHEMA='college_event_radar'
        """)
        
        if cursor.fetchone():
            print("✓ Table 'users' already exists")
        else:
            print("Creating 'users' table...")
            
            # Create the users table
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'student') DEFAULT 'student',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            db.commit()
            print("✓ Table 'users' created successfully!")
            
            # Add a default admin account
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (name, email, password, role) 
                VALUES (%s, %s, %s, %s)
            """, ("Admin", "admin@college.com", admin_password, "admin"))
            
            db.commit()
            print("✓ Default admin account created!")
            print("  Email: admin@college.com")
            print("  Password: admin123")
        
        cursor.close()
        db.close()
        print("\n✓ Migration completed successfully!")
        
    except pymysql.Error as e:
        print(f"✗ Error during migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate()
