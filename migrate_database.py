import pymysql

# Migration script to add missing 'category' column to events table

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
        
        # Check if category column exists
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='events' AND COLUMN_NAME='category'
        """)
        
        if cursor.fetchone():
            print("✓ Column 'category' already exists")
        else:
            print("Adding 'category' column to events table...")
            
            # Add the category column with a default value
            cursor.execute("""
                ALTER TABLE events 
                ADD COLUMN category VARCHAR(50) DEFAULT 'General'
            """)
            
            db.commit()
            print("✓ Column 'category' added successfully!")
        
        cursor.close()
        db.close()
        print("\n✓ Migration completed successfully!")
        
    except pymysql.Error as e:
        print(f"✗ Error during migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    migrate()
