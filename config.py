class Config:
    SECRET_KEY = 'your_secret_key'
    
    # MySQL Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '280124'
    MYSQL_DB = 'seminar_hall'
    
    # Email Configuration
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USER = "sugashsugu@gmail.com"
    EMAIL_PASS = "lnzo ipkz ewty lyie"

    # Default User Login Credentials
    USERS = {
        "AD": "password123",
        "AGRI": "password123",
        "CSE": "password123",
        "IT": "password123",
        "ECE": "password123",
        "EEE": "password123",
        "BME": "password123",
        "S&H": "password123",
        "C2C": "password123",
        "CIVIL": "password123",
        "MECH": "password123"
    }

    # Seminar Halls
    SEMINAR_HALLS = ["Hall A", "Hall B", "Hall C", "Hall D"]

    # Admin Credentials
    
    ADMIN_USER = "admin"
    ADMIN_PASS = "admin123"
    

    # Housekeeping Email
    HOUSEKEEPING_EMAIL = "sugashsugu028@gmail.com"







