from flask_mysqldb import MySQL
from flask import Flask
from config import Config

mysql = MySQL()

def init_db(app):
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = Config.MYSQL_DB

    mysql.init_app(app)
    
    with app.app_context():
        cursor = mysql.connection.cursor()
        
        # Create events table with time slots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                dept_name VARCHAR(20) NOT NULL,
                seminar_hall VARCHAR(20) NOT NULL,
                event_name VARCHAR(100) NOT NULL,
                event_date DATE NOT NULL,
                start_time VARCHAR(10) NOT NULL,
                student_count INT NOT NULL,
                description TEXT NOT NULL,
                status ENUM('Pending', 'Housekeeping Approved', 'Approved', 'Rejected') DEFAULT 'Pending',
                display_status BOOLEAN DEFAULT TRUE  -- Add display_status column
            )
        """)

        mysql.connection.commit()
        cursor.close()