# JobTrack - Job & Internship Application Tracker

A web-based application that helps job seekers and freshers track, organize, and manage their job and internship applications in one place.

## 📌 Project Overview

When applying for multiple jobs and internships, it can be difficult to remember company names, job positions, application dates, deadlines, and application status.

JobTrack provides a centralized platform where users can record and manage their applications throughout the recruitment process.

## ✨ Features

- User Registration and Login
- Secure Password Hashing
- User Session Management
- Add Job Applications
- Add Internship Applications
- View All Applications
- Edit Applications
- Delete Applications
- Search Applications
- Filter by Application Status
- Filter by Job / Internship
- Track Application Dates
- Track Application Deadlines
- Store Job URLs
- Store Salary / Stipend Information
- Add Application Notes
- Dashboard Statistics
- Recent Applications
- Responsive User Interface

## 📊 Dashboard

The dashboard provides an overview of application progress:

- Total Applications
- Interviews
- Selected Applications
- Rejected Applications
- Recent Applications

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Database
- SQLite

### Security
- Werkzeug Password Hashing
- Flask Sessions

## 📁 Project Structure

```text
Job Internship Tracker/
│
├── app.py
├── README.md
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_application.html
│   ├── applications.html
│   └── edit_application.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── script.js
│
└── database.db


🔐 User Authentication

Users can create an account and securely log in.

Passwords are stored using Werkzeug password hashing instead of storing plain-text passwords.

🎯 Project Objective

The main objective of JobTrack is to provide a simple and organized way for freshers and job seekers to manage multiple job and internship applications without relying on manual notes or spreadsheets.

🔮 Future Improvements
Email notifications for deadlines
Interview calendar
Application analytics and charts
CSV export
Resume management
Automated job search integration
Interview reminders