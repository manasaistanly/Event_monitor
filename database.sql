CREATE DATABASE college_event_radar;

USE college_event_radar;

CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME DEFAULT '09:00:00',
    event_location VARCHAR(100) NOT NULL,
    event_description TEXT,
    category VARCHAR(50) DEFAULT 'General',
    organizer VARCHAR(100),
    max_attendees INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;