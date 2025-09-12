***School Voting System
A web-based voting system designed for Kitengela International School JSS Algocracy Elections, enabling students to vote for school and class-specific leadership positions. The system blends student votes with merit-based criteria (e.g., academics, leadership) using a transparent weighted scoring formula. It supports multiple user roles (students, teachers, and admins) and provides features for managing elections, student assignments, and results.
This project is a Python-based application built with Streamlit, SQLite, and bcrypt for secure password hashing, inspired by the simple School Voting System by KelvinMutuku.
Features

Multi-Role Access:
Students: Register, vote for school-wide and class-specific positions, change/reset passwords.
Teachers: Manage student metric scores (academics, discipline, etc.), assign/reassign students to classes, reset student passwords.
Admins: Control voting status, manage positions, candidates, teachers, weights, and system data (backup/import).


Stream-Based Voting: Supports class streams (Blue, Red, Green, Yellow, Pink, Magenta, Purple) for grade-specific roles (e.g., "Grade 7 Blue Prefect").
Weighted Scoring: Combines student votes (30%) with merit criteria (academics, discipline, clubs, community service, teacher score, leadership, public speaking) for fair leader selection.
Security: Passwords are hashed using bcrypt, and admin access requires a PIN.
Data Management: Export/import data in JSON, export votes/results in CSV, and factory reset functionality.
Live Vote Tally: Displays real-time vote counts when voting is closed.
Gender Validation: Ensures only female students can run for "Girl Representative" positions.

Technologies Used

Python: Core programming language.
Streamlit: Web application framework for the user interface.
SQLite: Lightweight database for storing users, votes, and metrics.
bcrypt: Secure password hashing.
Pandas: Data handling for vote tallies and result exports.

Installation
Prerequisites

Python 3.8+
pip (Python package manager)

Steps

Clone the Repository:
git clone https://github.com/KelvinMutuku/School_Voting_System.git
cd School_Voting_System


Install Dependencies:
pip install streamlit sqlite3 bcrypt pandas


Run the Application:
streamlit run app.py


Access the App:

Open your browser and navigate to http://localhost:8501.
The page title should display "KITENGELA INTERNATIONAL SCHOOL JSS ALGOCRACY ELECTIONS".



Usage
Initial Setup

The system initializes an SQLite database (voting_system.db) with default data:
Teachers (e.g., teacher7blue, teacher7red) with password 1234.
Students (e.g., KJS001, KJS002) with password 1234.
Positions (e.g., "School President", "Grade 7 Blue Prefect").
Default admin PIN: 1234.


Streams (Blue, Red, Green, Yellow, Pink, Magenta, Purple) are used for class assignments.

Pages

About: Overview of the system, weighted scoring formula, and election process.
Register: Students can register, change, or reset their passwords.
Vote: Students authenticate and vote for eligible positions (school-wide, grade-specific, or stream-specific).
Results: Displays final election results with weighted scores (after voting closes).
Teacher: Teachers log in to manage student metrics, class rosters, and passwords.
Admin: Admins log in with a PIN to manage voting, positions, candidates, teachers, weights, and data.

Example Workflow

Student Registration:
Register with a student ID (e.g., KJS001), name, password, grade, stream, gender, and security question/answer.
Example: Register as KJS001, Grade 7, Blue stream, Male.


Teacher Actions:
Log in (e.g., teacher7blue, password 1234).
Assign students to Grade 7 Blue or reassign to another stream.
Enter metric scores (0–100) for academics, discipline, etc.


Admin Actions:
Log in with PIN 1234.
Add a position (e.g., "Grade 8 Green Prefect").
Add candidates (e.g., KJS005 for Grade 8 Green).
Toggle voting status or export results.


Voting:
Students log in and vote for positions they’re eligible for (e.g., Grade 7 Blue students vote for "Grade 7 Blue Prefect").
Votes are recorded only once per student.


Results:
After voting closes, view final scores combining votes and metrics.
Export results as CSV for record-keeping.



Database Schema

students: Stores student details (ID, name, password, grade, stream, gender, security question/answer, has_voted).
teachers: Stores teacher details (username, password, grade, stream, security question/answer).
positions: Stores positions (name, grade, stream, candidates JSON).
votes: Stores voter ID and their votes (JSON).
settings: Stores system settings (e.g., admin PIN, voting_open).
weights: Stores criteria weights for scoring.
metrics: Stores student performance metrics.

Security Notes

Passwords are hashed with bcrypt for security.
Admin access requires a PIN (default: 1234), changeable in the Admin panel.
Students cannot vote for themselves.
Gender validation ensures only female students can be candidates for "Girl Representative" positions.

Limitations

No Google Sheets integration (available in the original HTML version but requires external setup).
Streamlit’s UI is functional but less customizable than Tailwind CSS used in votingX12(1).html.
Default data is seeded for Grades 7–9 and Blue/Red streams; expand as needed.

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make changes and commit (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

Please ensure code follows PEP 8 style guidelines and includes relevant tests.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgements

***Original concept by KelvinMutuku.
Built with Streamlit for rapid web app development.
Uses bcrypt for secure password hashing.

***Deployment Links
PHP - MYSQL Version : Access the voting system with  at http://kiscstemclub-schoolvotingsystem.unaux.com/?i=1.


Python - MYSQLite Version (Streamlit-based): Access the voting system with hosted storage at https://kelvinmutuku-school-voting-system-app-lnqane.streamlit.app/.