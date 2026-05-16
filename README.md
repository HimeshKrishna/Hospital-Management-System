# 🏥 MediCare HMS – Hospital Management System

A modern full-stack Hospital Management System developed using **Flask, MySQL, HTML, CSS, and JavaScript**.
The project provides an interactive admin dashboard for managing hospital operations including patients, doctors, appointments, rooms, and billing.

---

# 🚀 Features

## 🔐 Authentication System

* User Registration
* Admin Login
* Credential Verification using MySQL
* Secure Dashboard Access

## 📊 Admin Dashboard

* Modern dark-themed dashboard
* Responsive sidebar navigation
* Search bars for records
* Dynamic statistics cards
* Professional hospital management UI

## 👨‍⚕️ Patient Management

* Add patient details
* Store patient data in MySQL database
* Gender selection and validation

## 🩺 Doctor Management

* Add doctor records
* Store specialization and availability
* Unique phone number validation

## 📅 Appointment Management

* Schedule appointments
* Track appointment status
* Manage doctor-patient mapping

## 🛏️ Room Management

* Add and manage room details
* Track room availability

## 💳 Billing Management

* Generate patient bills
* Store billing information
* Track payment status

---

# 🛠️ Technologies Used

| Technology   | Purpose            |
| ------------ | ------------------ |
| Python       | Backend Logic      |
| Flask        | Web Framework      |
| MySQL        | Database           |
| HTML         | Frontend Structure |
| CSS          | Styling            |
| JavaScript   | UI Interactions    |
| Git & GitHub | Version Control    |

---

# 🧠 Database Concepts Implemented

* Relational Database Design
* Primary Keys
* Foreign Keys
* Constraints
* Data Integrity
* CRUD Operations
* Database Connectivity

---

# 📂 Project Structure

```text
Hospital-Management-System/
│
├── app.py
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── patient.html
│   ├── doctor.html
│   ├── appointment.html
│   ├── room.html
│   └── billing.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/HimeshKrishna/Hospital-Management-System.git
```

---

## 2️⃣ Open Project Folder

```bash
cd Hospital-Management-System
```

---

## 3️⃣ Install Required Packages

```bash
pip install -r requirements.txt
```

If `requirements.txt` is unavailable:

```bash
pip install flask mysql-connector-python
```

---

## 4️⃣ Configure MySQL Database

Create database:

```sql
CREATE DATABASE Hospital_MS;
```

Update MySQL credentials inside:

```python
app.py
```

Example:

```python
host="localhost"
user="root"
password="your_password"
database="Hospital_MS"
```

---

## 5️⃣ Run Flask Application

```bash
python app.py
```

---

# 🌐 Open in Browser

```text
http://127.0.0.1:5000
```

---

# 🎯 Project Objectives

The objective of this project is to design and implement a database-driven Hospital Management System capable of managing hospital operations efficiently through a modern web-based interface.

The project demonstrates:

* Frontend & Backend Integration
* Real-time Database Connectivity
* Relational Database Implementation
* Authentication System
* CRUD Operations
* Dashboard UI Design

---

# 🔥 Key Highlights

✅ Full-stack Hospital Management System

✅ Modern Admin Dashboard

✅ Flask + MySQL Integration

✅ Responsive User Interface

✅ Real-time Database Operations

✅ Professional Project Structure

---

# ⭐ Conclusion

The MediCare HMS project successfully demonstrates the implementation of a modern Hospital Management System using Flask and MySQL. The system integrates frontend design, backend processing, authentication, and relational database concepts into a fully functional web application.
