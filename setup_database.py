import pymysql

def setup_database():
    try:
        # First, connect to MySQL without specifying a database
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="root"
        )
        
        cursor = db.cursor()
        
        # Read and execute the SQL script
        with open('database.sql', 'r') as sql_file:
            sql_commands = sql_file.read()
            
        # Split by semicolon and execute each command
        for command in sql_commands.split(';'):
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                except pymysql.Error as e:
                    # Skip if database already exists
                    if "already exists" in str(e):
                        continue
                    raise
        
        db.commit()
        cursor.close()
        db.close()
        
        print("✓ Database setup completed successfully!")
        print("✓ Users table created")
        print("✓ Events table created")
        print("✓ Default admin account created")
        print("\nLogin credentials:")
        print("  Email: admin@gmail.com")
        print("  Password: admin123")
        
    except pymysql.Error as e:
        print(f"✗ Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()
