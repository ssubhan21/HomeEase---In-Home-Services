from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)
app.secret_key = "homeease_secret"

# Database Connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="homeease",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "admin@gmail.com" and password == "admin":
            session['role'] = 'Admin'
            return redirect(url_for('admin_dashboard'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['role'] = user['role']
            session['user_id'] = user['user_id']
            if user['role'] == 'User':
                return redirect(url_for('user_dashboard'))
            elif user['role'] in ['ServiceProvider', 'VerifiedServiceProvider']:
                return redirect(url_for('provider_dashboard'))
        flash("Invalid Credentials!", "danger")
    return render_template('login.html')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        role = request.form.get('role')

        # Validate form inputs
        if not (full_name and email and phone and address and password and role):
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))

        certification_path = None

        # Handle certification upload if Service Provider
        if role == "ServiceProvider":
            if 'certification' not in request.files:
                flash("Certification file is required for service providers!", "danger")
                return redirect(url_for('register'))

            file = request.files['certification']
            if file.filename == "":
                flash("No file selected for upload!", "danger")
                return redirect(url_for('register'))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                certification_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(certification_path)
            else:
                flash("Invalid file type! Only PDF, PNG, JPG, and JPEG are allowed.", "danger")
                return redirect(url_for('register'))

        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (full_name, email, phone, address, password, role, certification)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (full_name, email, phone, address, password, role, certification_path))
            
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
        except pymysql.MySQLError as e:
            flash(f"Error during registration: {str(e)}", "danger")
            conn.rollback()
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE role IN ('ServiceProvider', 'VerifiedServiceProvider')")
    providers = cursor.fetchall()

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    cursor.execute("SELECT * FROM feedback")
    feedbacks = cursor.fetchall()

    conn.close()
    return render_template('admin_dashboard.html', users=users, providers=providers, bookings=bookings, feedbacks=feedbacks)

@app.route('/verify_provider/<int:provider_id>')
def verify_provider(provider_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role='VerifiedServiceProvider' WHERE user_id=%s", (provider_id,))
    conn.commit()
    conn.close()
    flash("Service Provider Verified Successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# ----------------------- USER MODULE -----------------------

@app.route('/user_dashboard')
def user_dashboard():
    if session.get('role') != 'User':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()

    cursor.execute("SELECT * FROM bookings WHERE user_id=%s", (session['user_id'],))
    bookings = cursor.fetchall()

    conn.close()
    return render_template('user_dashboard.html', services=services, bookings=bookings)

@app.route('/book_service/<int:service_id>', methods=['POST'])
def book_service(service_id):
    if session.get('role') != 'User':
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve provider_id from the selected service
    cursor.execute("SELECT provider_id FROM services WHERE service_id=%s", (service_id,))
    service = cursor.fetchone()

    if not service:
        flash("Service not found!", "danger")
        return redirect(url_for('user_dashboard'))

    provider_id = service['provider_id']
    user_id = session['user_id']

    # Insert booking into the database
    try:
        cursor.execute("""
            INSERT INTO bookings (user_id, provider_id, service_id, status)
            VALUES (%s, %s, %s, 'Pending')
        """, (user_id, provider_id, service_id))

        conn.commit()
        flash("Service booked successfully!", "success")
    except pymysql.MySQLError as e:
        flash(f"Booking failed: {str(e)}", "danger")

    conn.close()
    return redirect(url_for('user_dashboard'))

from datetime import datetime

@app.route('/process_payment/<int:booking_id>', methods=['GET', 'POST'])
def process_payment(booking_id):
    if session.get('role') != 'User':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve booking details
    cursor.execute("""
        SELECT bookings.booking_id, bookings.provider_id, bookings.user_id, services.price 
        FROM bookings
        JOIN services ON bookings.service_id = services.service_id
        WHERE bookings.booking_id = %s AND bookings.status = 'Accepted'
    """, (booking_id,))
    
    booking = cursor.fetchone()

    if not booking:
        flash("Invalid booking or payment already completed.", "danger")
        conn.close()
        return redirect(url_for('user_dashboard'))

    amount = booking['price']

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        return render_template('payment_gateway.html', booking_id=booking_id, amount=amount, payment_method=payment_method)

    conn.close()
    return render_template('payment_selection.html', booking_id=booking_id, amount=amount)


@app.route('/complete_payment/<int:booking_id>/<string:payment_method>', methods=['POST'])
def complete_payment(booking_id, payment_method):
    if session.get('role') != 'User':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Debugging: Log booking ID and payment method
        print(f"Processing payment for Booking ID: {booking_id}, Method: {payment_method}")

        # Explicitly specify table names to avoid ambiguity
        cursor.execute("""
            SELECT b.provider_id, b.user_id, s.price 
            FROM bookings AS b
            JOIN services AS s ON b.service_id = s.service_id
            WHERE b.booking_id = %s
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            flash("Error: Booking not found!", "danger")
            print("Error: Booking not found!")
            conn.close()
            return redirect(url_for('user_dashboard'))

        provider_id = booking['provider_id']
        user_id = booking['user_id']
        amount = booking['price']

        # Debugging: Check if payment already exists
        cursor.execute("SELECT * FROM payments WHERE booking_id = %s", (booking_id,))
        existing_payment = cursor.fetchone()

        if existing_payment:
            flash("Payment already processed for this booking!", "info")
            print("Payment already exists in database.")
            conn.close()
            return redirect(url_for('user_dashboard'))

        # Insert payment record
        cursor.execute("""
            INSERT INTO payments (booking_id, provider_id, user_id, amount, payment_status, payment_date, payment_method)
            VALUES (%s, %s, %s, %s, 'Completed', %s, %s)
        """, (booking_id, provider_id, user_id, amount, payment_date, payment_method))

        # Debugging: Ensure payment was inserted
        cursor.execute("SELECT * FROM payments WHERE booking_id = %s", (booking_id,))
        check_payment = cursor.fetchone()
        if not check_payment:
            flash("Error: Payment was not recorded!", "danger")
            print("Error: Payment was not inserted into database.")
            conn.rollback()
            conn.close()
            return redirect(url_for('user_dashboard'))

        # Update booking status to 'Paid'
        cursor.execute("UPDATE bookings SET status='Paid' WHERE booking_id=%s", (booking_id,))
        conn.commit()

        # Debugging: Ensure booking status was updated
        cursor.execute("SELECT status FROM bookings WHERE booking_id = %s", (booking_id,))
        updated_booking = cursor.fetchone()
        if updated_booking['status'] != 'Paid':
            flash("Error: Booking status not updated!", "danger")
            print("Error: Booking status update failed.")
            conn.rollback()
            conn.close()
            return redirect(url_for('user_dashboard'))

        flash("Payment successful! Your booking is now confirmed.", "success")
        print("Payment successful and booking status updated.")

    except pymysql.MySQLError as e:
        conn.rollback()
        flash(f"Payment failed: {str(e)}", "danger")
        print(f"MySQL Error: {str(e)}")
    finally:
        conn.close()

    return redirect(url_for('user_dashboard'))

from datetime import datetime

@app.route('/submit_feedback/<int:provider_id>', methods=['POST'])
def submit_feedback(provider_id):
    if session.get('role') != 'User':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    rating = request.form.get('rating')
    comments = request.form.get('comments')

    # Validate rating input
    if not rating or int(rating) not in range(1, 6):
        flash("Invalid rating. Please select a rating between 1 and 5.", "danger")
        return redirect(url_for('user_dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure user has a completed booking with the provider
    cursor.execute("""
        SELECT booking_id FROM bookings 
        WHERE user_id=%s AND provider_id=%s AND status='Paid' 
        ORDER BY booking_time DESC LIMIT 1
    """, (session['user_id'], provider_id))
    
    booking = cursor.fetchone()

    if not booking:
        flash("You can only submit feedback for completed bookings.", "warning")
        conn.close()
        return redirect(url_for('user_dashboard'))

    booking_id = booking['booking_id']
    feedback_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if feedback for this booking already exists
    cursor.execute("""
        SELECT feedback_id FROM feedback WHERE booking_id=%s
    """, (booking_id,))
    
    existing_feedback = cursor.fetchone()

    if existing_feedback:
        flash("You have already submitted feedback for this booking.", "info")
        conn.close()
        return redirect(url_for('user_dashboard'))

    # Insert feedback into database
    try:
        cursor.execute("""
            INSERT INTO feedback (booking_id, user_id, provider_id, rating, comments, feedback_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (booking_id, session['user_id'], provider_id, rating, comments, feedback_date))
        
        conn.commit()
        flash("Feedback submitted successfully!", "success")
    except pymysql.MySQLError as e:
        conn.rollback()
        flash(f"Error submitting feedback: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for('user_dashboard'))


@app.route('/services')
def services():
    return render_template('services.html')
# @app.route('/services')
# def services():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT service_id, provider_id, service_name, description
#         FROM services
#     """)
#     services = cursor.fetchall()

#     conn.close()
#     return render_template('services.html', services=services)


# ----------------------- SERVICE PROVIDER MODULE -----------------------

@app.route('/provider_dashboard')
def provider_dashboard():
    if session.get('role') not in ['ServiceProvider', 'VerifiedServiceProvider']:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM services WHERE provider_id=%s", (session['user_id'],))
    services = cursor.fetchall()

    cursor.execute("SELECT * FROM bookings WHERE provider_id=%s", (session['user_id'],))
    bookings = cursor.fetchall()

    cursor.execute("SELECT * FROM payments WHERE provider_id=%s", (session['user_id'],))
    payments = cursor.fetchall()

    conn.close()
    return render_template('provider_dashboard.html', services=services, bookings=bookings, payments=payments)

@app.route('/add_service', methods=['POST'])
def add_service():
    if session.get('role') not in ['ServiceProvider', 'VerifiedServiceProvider']:
        return redirect(url_for('login'))

    service_name = request.form.get('service_name')
    description = request.form.get('description')
    price = request.form.get('price')
    provider_id = session['user_id']

    if not service_name or not description or not price:
        flash("Please fill in all required fields.", "danger")
        return redirect(url_for('provider_dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO services (provider_id, service_name, description, price, availability) 
            VALUES (%s, %s, %s, %s, 'Available')
        """, (provider_id, service_name, description, price))
        
        conn.commit()
        flash("Service added successfully!", "success")
    except pymysql.MySQLError as e:
        flash(f"Error adding service: {str(e)}", "danger")
    
    conn.close()
    return redirect(url_for('provider_dashboard'))



@app.route('/update_availability/<int:service_id>', methods=['POST'])
def update_availability(service_id):
    if session.get('role') not in ['ServiceProvider', 'VerifiedServiceProvider']:
        return redirect(url_for('login'))

    availability = request.form['availability']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE services SET availability=%s WHERE service_id=%s", (availability, service_id))
    conn.commit()
    conn.close()
    flash("Availability updated!", "success")
    return redirect(url_for('provider_dashboard'))

@app.route('/update_booking_status/<int:booking_id>/<string:status>')
def update_booking_status(booking_id, status):
    if session.get('role') not in ['ServiceProvider', 'VerifiedServiceProvider']:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status=%s WHERE booking_id=%s", (status, booking_id))
    conn.commit()
    conn.close()
    flash(f"Booking {status} successfully!", "success")
    return redirect(url_for('provider_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
