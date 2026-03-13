import pymysql
from datetime import datetime, timedelta

def seed_database():
    try:
        # Connect to MySQL
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="college_event_radar"
        )
        
        cursor = db.cursor()
        
        # Sample events data
        sample_events = [
            {
                'name': 'Annual Tech Summit 2026',
                'date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
                'time': '09:30:00',
                'location': 'Main Auditorium',
                'description': 'A comprehensive summit featuring keynote speakers from leading tech companies discussing recent innovations in AI and cloud computing.',
                'category': 'Technology',
                'organizer': 'Tech Department',
                'max_attendees': 500
            },
            {
                'name': 'Literature and Arts Festival',
                'date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                'time': '14:00:00',
                'location': 'Arts Building',
                'description': 'Celebrate creativity through poetry readings, art exhibitions, and performances by student artists.',
                'category': 'Arts',
                'organizer': 'Arts Club',
                'max_attendees': 300
            },
            {
                'name': 'Annual Sports Day',
                'date': (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d'),
                'time': '08:00:00',
                'location': 'Sports Ground',
                'description': 'Compete in various sports including cricket, badminton, volleyball, and athletics.',
                'category': 'Sports',
                'organizer': 'Sports Committee',
                'max_attendees': 1000
            },
            {
                'name': 'Entrepreneurship Bootcamp',
                'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'time': '10:00:00',
                'location': 'Innovation Hub',
                'description': 'Learn to start your own business with mentorship from successful entrepreneurs and investors.',
                'category': 'Workshop',
                'organizer': 'Entrepreneurship Club',
                'max_attendees': 100
            },
            {
                'name': 'Environmental Awareness Walk',
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '07:00:00',
                'location': 'Campus & Surroundings',
                'description': 'Join us for a community walk to raise awareness about environmental conservation and sustainability.',
                'category': 'Environment',
                'organizer': 'Green Club',
                'max_attendees': 200
            },
            {
                'name': 'Career Fair 2026',
                'date': (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d'),
                'time': '11:00:00',
                'location': 'Convention Center',
                'description': 'Meet recruiters from Fortune 500 companies and explore career opportunities.',
                'category': 'Career',
                'organizer': 'Placement Cell',
                'max_attendees': 800
            }
        ]
        
        # Check if events already exist
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✓ Database already contains {count} event(s). Skipping seeding.")
        else:
            print("Adding sample events to database...")
            
            for event in sample_events:
                query = """
                    INSERT INTO events 
                    (event_name, event_date, event_time, event_location, event_description, category, organizer, max_attendees) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    event['name'],
                    event['date'],
                    event['time'],
                    event['location'],
                    event['description'],
                    event['category'],
                    event['organizer'],
                    event['max_attendees']
                )
                cursor.execute(query, values)
            
            db.commit()
            print(f"✓ Successfully added {len(sample_events)} sample events!")
            print("\nSample events added:")
            for i, event in enumerate(sample_events, 1):
                print(f"  {i}. {event['name']} - {event['date']}")
        
        cursor.close()
        db.close()
        print("\n✓ Database seeding completed!")
        
    except pymysql.Error as e:
        print(f"✗ Error seeding database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    seed_database()
