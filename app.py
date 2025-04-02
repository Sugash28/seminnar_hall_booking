from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from db import mysql, init_db
from config import Config
import MySQLdb.cursors
import smtplib
from email.mime.text import MIMEText
from datetime import datetime


app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
init_db(app)

# Route: Login
# filepath: /g:/seminaar-hall/app.py
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check Admin Login
        if username == Config.ADMIN_USER and password == Config.ADMIN_PASS:
            session['admin'] = True  # Set admin session
            session['loggedin'] = True
            return redirect(url_for('admin_dashboard'))

        # Check Housekeeping Login
        

        # Check Department Login
        if username in Config.USERS and Config.USERS[username] == password:
            session['loggedin'] = True
            session['dept_name'] = username  # Store department name
            return redirect(url_for('dashboard'))

        flash("Invalid credentials", "danger")

    return render_template('login.html')

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route: Dashboard
# filepath: /g:/seminaar-hall/app.py
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT * FROM events
            ORDER BY event_date DESC
        """)
        events = cursor.fetchall()
        return render_template('dashboard.html', events=events, halls=Config.SEMINAR_HALLS)
    return redirect(url_for('login'))

# Route: Fetch Available Slots for a Given Day & Hall (AJAX)
@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    if 'loggedin' in session:
        event_date = request.form.get('event_date')
        seminar_hall = request.form.get('seminar_hall')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT start_time FROM events WHERE event_date=%s AND seminar_hall=%s AND status='Approved'
        """, (event_date, seminar_hall))
        booked_slots = [event['start_time'] for event in cursor.fetchall()]

        all_slots = generate_half_hour_slots()  
        available_slots = [slot for slot in all_slots if slot not in booked_slots]

        return jsonify(available_slots)
    return jsonify([])


from datetime import datetime


@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    """Handles event creation and sends email notifications."""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            event_name = request.form.get('event_name')
            event_date = request.form.get('event_date')
            seminar_hall = request.form.get('seminar_hall')
            selected_slots = request.form.getlist('time_slots')
            student_count = request.form.get('student_count')
            description = request.form.get('description')
            dept_name = session.get('dept_name')or request.form.get('dept_name')

            # ✅ Validate event_date
            if not event_date or event_date.strip() == "":
                flash("Please select a valid date!", "danger")
                return redirect(url_for('create_event'))

            try:
                event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format! Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('create_event'))

            if not (event_name and seminar_hall and selected_slots and student_count and description):
                flash("All fields are required!", "danger")
                return redirect(url_for('create_event'))

            # ✅ Check if selected slots are already booked
            for start_time in selected_slots:
                cursor.execute("""
                    SELECT id FROM events 
                    WHERE event_date=%s AND seminar_hall=%s AND start_time=%s
                    AND status IN ('Pending', 'Housekeeping Approved', 'Approved')
                """, (event_date, seminar_hall, start_time))
                existing_booking = cursor.fetchone()
                if existing_booking:
                    flash(f"Slot {start_time} is already booked. Please select another slot.", "danger")
                    return redirect(url_for('create_event'))

            # ✅ Insert event into database
            for start_time in selected_slots:
                cursor.execute("""
                    INSERT INTO events 
                    (dept_name, seminar_hall, event_name, event_date, start_time, student_count, description, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
                """, (dept_name, seminar_hall, event_name, event_date, start_time, student_count, description))

            mysql.connection.commit()

            # ✅ Fetch user email
            # user_email = Config.USER_EMAILS.get(dept_name, "defaultuser@example.com")

            # ✅ Prepare email details
            subject = f"Event Created: {event_name}"
            body = f"""
Hello {dept_name},

Your event request has been successfully created.

📅 Event Name: {event_name}
📆 Date: {event_date}
🏛️ Seminar Hall: {seminar_hall}
⏰ Time Slot(s): {', '.join(selected_slots)}
👥 Student Count: {student_count}
📝 Description: {description}

Thank you,
Seminar Hall Booking System
            """

            # ✅ Send email to both User & Housekeeping
            send_email( Config.HOUSEKEEPING_EMAIL, subject, body)

            flash("Event request created. Confirmation email sent.", "success")
            return redirect(url_for('dashboard'))
            # GET method: set up available slots
        event_date = request.args.get('event_date', '')
        seminar_hall = request.args.get('seminar_hall', '')
        if event_date:
            try:
                event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format! Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('create_event'))
        else:
            event_date = None
        cursor.execute("""
            SELECT start_time FROM events 
            WHERE event_date=%s AND seminar_hall=%s 
            AND status='Approved'
        """, (event_date, seminar_hall))
        booked_slots = [event['start_time'] for event in cursor.fetchall()]

        all_slots = generate_half_hour_slots()
        available_slots = {slot: "Available" if slot not in booked_slots else "Booked" for slot in all_slots}

        return render_template('create_event.html', halls=Config.SEMINAR_HALLS,
                               available_slots=available_slots, event_date=event_date, seminar_hall=seminar_hall)
    else:
        return redirect(url_for('login'))


# Route: Housekeeping Approval Panel


# Route: Approve Event (Housekeeping Step)
# filepath: /g:/seminaar-hall/app.py


# Route: Admin Approval Panel
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch events with "Pending" status for admin review
        cursor.execute("SELECT * FROM events WHERE status='Pending'")
        events = cursor.fetchall()
        return render_template('admin_dashboard.html', events=events)
    return redirect(url_for('login'))

# Route: Approve Event (Final Step by Admin)
@app.route('/approve_event/<int:event_id>')
def approve_event(event_id):
    if 'admin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor here
        cursor.execute(
            "UPDATE events SET status='Approved', display_status=TRUE WHERE id=%s",
            (event_id,)
        )
        mysql.connection.commit()
        
        # Fetch event details for email notification
        cursor.execute("SELECT * FROM events WHERE id=%s", (event_id,))
        event = cursor.fetchone()  # Fetch the event as a dictionary
        if event:
            subject = f"Event Approved: {event['event_name']}"
            body = f"""
Hello Housekeeping,

The following event has been approved by Admin:

Department: {event['dept_name']}
Seminar Hall: {event['seminar_hall']}
Event Name: {event['event_name']}
Date: {event['event_date']}
Time Slot: {event['start_time']}
Student Count: {event['student_count']}
Description: {event['description']}

Please take the necessary actions.
            """
            send_email(Config.HOUSEKEEPING_EMAIL, subject, body)
        
        flash("Event approved successfully and notification sent!", "success")
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

# Route: Reject Event
# filepath: /g:/seminaar-hall/app.py
@app.route('/reject_event/<int:event_id>')
def reject_event(event_id):
    if 'admin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE events SET status='Rejected', display_status=FALSE WHERE id=%s", [event_id])
        mysql.connection.commit()
        flash("Event rejected.", "success")
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))



# Function: Generate 30-Minute Slots
def generate_half_hour_slots():
    slots = []
    for hour in range(9, 17):  
        slots.append(f"{hour}:00")
        slots.append(f"{hour}:30")
    return slots

# Function: Send Email
def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = Config.EMAIL_USER
        msg["To"] = to

        server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
        server.starttls()
        server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
        server.sendmail(Config.EMAIL_USER, to, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email failed: {e}")

if __name__ == '__main__':
    app.run(debug=True)
