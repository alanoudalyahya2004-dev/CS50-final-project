# Volunteer Hub
CS50 Final Project

## Video Demo
https://youtu.be/v4DBJbmbirU

## Description
Volunteer Hub is a web-based application developed to help student clubs and organizations manage volunteers, track volunteering hours, and recognize contributions in an organized and efficient way.

The platform supports two main user roles: volunteers and administrators. Volunteers can register, view upcoming events, and submit their volunteering hours, while administrators can manage events, review submitted hours, and generate reports.

## Features
- User authentication with separate roles for volunteers and administrators
- Event creation, editing, and deletion by administrators
- Volunteer registration for events with capacity control
- Submission and review of volunteering hours
- Approval and rejection workflow for submitted hours
- Exporting volunteer reports to CSV files
- Support for Arabic and English interfaces
- Dark mode option for improved accessibility

## Technologies Used
- Python (Flask)
- SQLite
- HTML
- CSS
- JavaScript
- Bootstrap

## Project Structure
- app.py: Main Flask application and route handling
- templates/: HTML templates using Jinja2
- static/: CSS, JavaScript, and static assets
- instance/app.db: SQLite database

## Design Decisions
Flask and SQLite were chosen for simplicity and lightweight deployment. Jinja2 templates were used to support multilingual content, while Bootstrap ensures a responsive and clean user interface. Database constraints are implemented to maintain data integrity and prevent duplicate registrations.

## Future Improvements
- Email notifications for event reminders and approvals
- Analytical dashboards for administrators
- API support for mobile applications
- Exporting reports directly to Excel format

## How to Run
1. Clone the repository and navigate to the project directory  
2. Install dependencies using `pip install flask`  
3. Initialize the database using `flask --app app.py init-db`  
4. Run the application using `flask --app app.py run`
