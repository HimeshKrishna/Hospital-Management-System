import os
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "hospital-assignment-secret")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Parikshit@1356"),
    "database": os.environ.get("DB_NAME", "Hospital_MS"),
}


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db_connection():
    """Return a new MySQL connection using the global config."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create all required tables if they do not already exist and seed
    starter data where appropriate."""
    db = get_db_connection()
    cursor = db.cursor()

    # Admin table (for authentication)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL
        )
        """
    )

    # Login audit log
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_logins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            username VARCHAR(100) NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Patient table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Patient (
            patient_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100),
            age INT,
            gender VARCHAR(10),
            phone VARCHAR(20),
            address VARCHAR(255)
        )
        """
    )

    # Doctor table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Doctor (
            doctor_id VARCHAR(20) PRIMARY KEY,
            doctor_name VARCHAR(100),
            specialization VARCHAR(100),
            doctor_phone VARCHAR(20),
            availability VARCHAR(50)
        )
        """
    )

    # Appointment table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Appointment (
            appointment_id VARCHAR(20) PRIMARY KEY,
            patient_id VARCHAR(20),
            doctor_id VARCHAR(20),
            appointment_date DATE,
            status VARCHAR(30)
        )
        """
    )

    # Billing table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Billing (
            bill_id VARCHAR(20) PRIMARY KEY,
            patient_id VARCHAR(20),
            amount DECIMAL(10, 2),
            payment_status VARCHAR(30),
            bill_date DATE
        )
        """
    )

    # Room table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Room (
            room_no INT PRIMARY KEY,
            room_type VARCHAR(50),
            availability VARCHAR(30)
        )
        """
    )

    # Seed a few rooms if the table is empty
    cursor.execute("SELECT COUNT(*) FROM Room")
    room_count = cursor.fetchone()[0]
    if room_count == 0:
        starter_rooms = [
            (101, "General", "Available"),
            (102, "General", "Occupied"),
            (201, "ICU", "Available"),
            (202, "ICU", "Occupied"),
            (301, "Private", "Available"),
        ]
        cursor.executemany(
            "INSERT INTO Room (room_no, room_type, availability) VALUES (%s, %s, %s)",
            starter_rooms,
        )

    db.commit()
    cursor.close()
    db.close()


# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------

def login_required(route_function):
    """Redirect unauthenticated users to the home / login page."""
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("home"))
        return route_function(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Reusable data-fetching utilities
# ---------------------------------------------------------------------------

def fetch_table_data(table_candidates, limit=100):
    """Look for the first existing table from *table_candidates* and return
    (table_name, column_list, row_list)."""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    existing_table = None
    for candidate in table_candidates:
        cursor.execute(
            """
            SELECT table_name AS tbl
            FROM information_schema.tables
            WHERE table_schema = %s AND LOWER(table_name) = LOWER(%s)
            LIMIT 1
            """,
            (DB_CONFIG["database"], candidate),
        )
        found = cursor.fetchone()
        if found:
            existing_table = found["tbl"]
            break

    rows = []
    columns = []
    if existing_table:
        cursor.execute(f"SELECT * FROM `{existing_table}` LIMIT %s", (limit,))
        rows = cursor.fetchall()
        if rows:
            columns = list(rows[0].keys())

    cursor.close()
    db.close()
    return existing_table, columns, rows


def execute_insert(query, values):
    """Run a single INSERT and commit."""
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    db.close()


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Landing page (index.html) — shows the login form."""
    return render_template("index.html")


@app.route("/login-page")
def login_page():
    """Standalone login page."""
    return render_template("login.html")


@app.route("/register-page")
def register_page():
    """Registration page."""
    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard — shows stats, tables, and inline add-forms."""
    doctor_table, doctor_columns, doctors = fetch_table_data(["Doctor", "Doctors"])
    patient_table, patient_columns, patients = fetch_table_data(["Patient", "Patients"])
    room_table, room_columns, rooms = fetch_table_data(["Room", "Rooms"])
    appointment_table, appointment_columns, appointments = fetch_table_data(["Appointment", "Appointments"])
    billing_table, billing_columns, billings = fetch_table_data(["Billing", "Billings"])

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        doctor_table=doctor_table,
        doctor_columns=doctor_columns,
        doctors=doctors,
        patient_table=patient_table,
        patient_columns=patient_columns,
        patients=patients,
        room_table=room_table,
        room_columns=room_columns,
        rooms=rooms,
        appointment_table=appointment_table,
        appointment_columns=appointment_columns,
        appointments=appointments,
        billing_table=billing_table,
        billing_columns=billing_columns,
        billings=billings,
    )


@app.route("/patients")
@login_required
def patients_page():
    """Dedicated patient management page."""
    _, patient_columns, patients = fetch_table_data(["Patient", "Patients"])
    return render_template(
        "patient.html",
        patient_columns=patient_columns,
        patients=patients,
    )


@app.route("/doctors")
@login_required
def doctors_page():
    """Dedicated doctor management page."""
    _, doctor_columns, doctors = fetch_table_data(["Doctor", "Doctors"])
    return render_template(
        "doctor.html",
        doctor_columns=doctor_columns,
        doctors=doctors,
    )


@app.route("/appointments")
@login_required
def appointments_page():
    """Dedicated appointment management page."""
    _, appointment_columns, appointments = fetch_table_data(["Appointment", "Appointments"])
    return render_template(
        "appointment.html",
        appointment_columns=appointment_columns,
        appointments=appointments,
    )


@app.route("/billing-page")
@login_required
def billing_page():
    """Dedicated billing management page."""
    _, billing_columns, billings = fetch_table_data(["Billing", "Billings"])
    return render_template(
        "billing.html",
        billing_columns=billing_columns,
        billings=billings,
    )


@app.route("/rooms")
@login_required
def rooms_page():
    """Dedicated room management page."""
    _, room_columns, rooms = fetch_table_data(["Room", "Rooms"])
    return render_template(
        "room.html",
        room_columns=room_columns,
        rooms=rooms,
    )


# ---------------------------------------------------------------------------
# Routes — authentication
# ---------------------------------------------------------------------------

@app.route("/login", methods=["POST"])
def login():
    """Authenticate an existing user from the admin table."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("home"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT admin_id, username, password FROM admin WHERE username = %s",
        (username,),
    )
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        db.close()
        flash("Account not found. Please register first.", "error")
        return redirect(url_for("home"))

    if user["password"] != password:
        cursor.close()
        db.close()
        flash("Invalid password. Please try again.", "error")
        return redirect(url_for("home"))

    # Audit log
    cursor.execute(
        "INSERT INTO user_logins (user_id, username) VALUES (%s, %s)",
        (user["admin_id"], user["username"]),
    )
    db.commit()
    cursor.close()
    db.close()

    session["user_id"] = user["admin_id"]
    session["username"] = user["username"]
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["POST"])
def register():
    """Register a new user in the admin table."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("home"))

    if password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("home"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check if username already exists
    cursor.execute("SELECT admin_id FROM admin WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        db.close()
        flash("Username already exists. Please choose a different one.", "error")
        return redirect(url_for("home"))

    # Create the account
    cursor.execute(
        "INSERT INTO admin (username, password) VALUES (%s, %s)",
        (username, password),
    )
    db.commit()
    cursor.close()
    db.close()

    flash("Account created successfully! You can now sign in.", "success")
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    """Clear the session and redirect to the landing page."""
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Routes — data insertion (POST only)
# ---------------------------------------------------------------------------

@app.route("/add_patient", methods=["POST"])
@login_required
def add_patient():
    data = request.form
    try:
        query = "INSERT INTO Patient VALUES (%s, %s, %s, %s, %s, %s)"
        values = (
            data["patient_id"],
            data["name"],
            data["age"],
            data["gender"],
            data["phone"],
            data["address"],
        )
        execute_insert(query, values)
        flash("Patient added successfully.")
    except mysql.connector.Error as err:
        flash(f"Error adding patient: {err}")
    return redirect(url_for("dashboard"))


@app.route("/add_doctor", methods=["POST"])
@login_required
def add_doctor():
    data = request.form
    try:
        query = "INSERT INTO Doctor VALUES (%s, %s, %s, %s, %s)"
        values = (
            data["doctor_id"],
            data["doctor_name"],
            data["specialization"],
            data["doctor_phone"],
            data["availability"],
        )
        execute_insert(query, values)
        flash("Doctor added successfully.")
    except mysql.connector.Error as err:
        flash(f"Error adding doctor: {err}")
    return redirect(url_for("dashboard"))


@app.route("/add_appointment", methods=["POST"])
@login_required
def add_appointment():
    data = request.form
    try:
        query = "INSERT INTO Appointment VALUES (%s, %s, %s, %s, %s)"
        values = (
            data["appointment_id"],
            data["patient_id"],
            data["doctor_id"],
            data["appointment_date"],
            data["status"],
        )
        execute_insert(query, values)
        flash("Appointment booked successfully.")
    except mysql.connector.Error as err:
        flash(f"Error booking appointment: {err}")
    return redirect(url_for("dashboard"))


@app.route("/add_billing", methods=["POST"])
@login_required
def add_billing():
    data = request.form
    try:
        query = "INSERT INTO Billing VALUES (%s, %s, %s, %s, %s)"
        values = (
            data["bill_id"],
            data["patient_id"],
            data["amount"],
            data["payment_status"],
            data["bill_date"],
        )
        execute_insert(query, values)
        flash("Billing record added successfully.")
    except mysql.connector.Error as err:
        flash(f"Error adding billing record: {err}")
    return redirect(url_for("dashboard"))


@app.route("/add_room", methods=["POST"])
@login_required
def add_room():
    data = request.form
    try:
        query = "INSERT INTO Room (room_no, room_type, availability) VALUES (%s, %s, %s)"
        values = (
            data["room_no"],
            data["room_type"],
            data["availability"],
        )
        execute_insert(query, values)
        flash("Room added successfully.")
    except mysql.connector.Error as err:
        flash(f"Error adding room: {err}")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    # Supports running through `flask run` as well.
    init_db()
