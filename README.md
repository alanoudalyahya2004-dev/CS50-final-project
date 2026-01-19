## CS50 Final Project
# Volunteer Hub

#### Video Demo: https://youtu.be/v4DBJbmbirU?si=4Pn2yXgo-bpDCKFs
#### Description:
Volunteer Hub is a **web-based application** built with **Flask (Python), SQLite, HTML, CSS, and Bootstrap**.
It is designed to help student clubs and organizations manage volunteers, track their hours, and recognize their contributions.

The platform makes volunteering easier for both **volunteers** and **administrators**:
- Volunteers can register, log in, view upcoming events, and submit their volunteering hours.
- Administrators can create, edit, and delete events, approve or reject submitted hours, and export reports to Excel/CSV.

---

## Features

1. **User Authentication**
   - Volunteers and administrators can register and log in with different roles.
   - Sessions are handled securely using Flask sessions.

2. **Event Management**
   - Admins can create events with a title, description, location, start and end times, and capacity.
   - Events automatically calculate their base duration (hours).

3. **Volunteer Registration**
   - Volunteers can register for events (if capacity is not full).
   - They can cancel their registration if needed.

4. **Hour Submission**
   - Volunteers can submit additional details about their work (e.g., preparing giveaways, printing materials).
   - Submitted hours go into a **pending state** until reviewed.

5. **Admin Review**
   - Admins can approve or reject hours.
   - Approved hours are added to the volunteerâs total.
   - Rejected submissions are marked with status **âCancelledâ** and set to 0 hours.

6. **Export to Excel/CSV**
   - Admins can download a CSV file containing:
     - Volunteer name and email
     - Event details
     - Submitted hours and descriptions
     - Approval status and date
   - This feature makes it easier to send reports to external organizations.

7. **Language & Theme Options**
   - Supports both **Arabic** and **English** interface.
   - Includes a **dark mode toggle** for accessibility.

---

## File Overview

- **app.py**
  Main Flask application file. Handles routes for events, user authentication, hour submission, and admin dashboard.

- **templates/**
  Contains HTML files written with Jinja2 templating.
  - `base.html` â Main layout file (header, navbar, footer).
  - `home.html` â Homepage showing upcoming events.
  - `events.html` â List of all events with registration buttons.
  - `event_detail.html` â Detailed view of a single event, including hour submission.
  - `login.html` / `register.html` â Authentication pages.
  - `dashboard_admin.html` â Admin dashboard for stats, event management, and approvals.
  - `dashboard_volunteer.html` â Volunteer dashboard showing personal hours and registrations.
  - `404.html` â Custom error page.

- **static/**
  Contains static assets:
  - `style.css` â Custom CSS styling.
  - `js/main.js` â Handles language switching and dark mode.
  - `favicon.ico` â Website icon.

- **instance/app.db**
  SQLite database storing users, events, registrations, and submitted hours.

---

## Design Choices

- **Flask + SQLite** were chosen for simplicity and lightweight deployment. SQLite works well for a small to medium project like this.
- **Jinja2 templates** allowed easy integration of translation keys (`{{ _('...') }}`) for Arabic and English support.
- **Bootstrap 5** was used for styling, ensuring responsive design and a clean modern interface.
- A **custom filter** (`datetimeformat`) was added in `app.py` to display dates and times clearly in both English and Arabic, including AM/PM.
- Data integrity is enforced in the database to prevent duplicate registrations.

---

## Future Improvements

- Add email notifications for event reminders and hour approvals.
- Implement charts in the admin dashboard (e.g., total hours per volunteer).
- Add API endpoints for mobile app integration.
- Support exporting reports directly to Excel (`.xlsx`) instead of CSV.

---

## How to Run

# 1. Clone the repository
git clone <your-repo-link>
cd project

# 2. Install dependencies
pip install flask

# 3. Initialize the database
flask --app app.py init-db

# 4. Run the server
flask --app app.py run


