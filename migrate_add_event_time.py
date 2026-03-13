import pymysql

# Migration script to add missing 'event_time' column to events table

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
        
        # Check if event_time column exists
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='events' AND COLUMN_NAME='event_time'
        """)
        
        if cursor.fetchone():
            print("✓ Column 'event_time' already exists")
        else:
            print("Adding 'event_time' column to events table...")
            
            # Add the event_time column
            cursor.execute("""
                ALTER TABLE events 
                ADD COLUMN event_time TIME DEFAULT '09:00:00' AFTER event_date
            """)
            
            db.commit()
            print("✓ Column 'event_time' added successfully!")
        
        cursor.close()
        db.close()
        print("\n✓ Migration completed successfully!")
        
    except pymysql.Error as e:
        print(f"✗ Error during migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate()
