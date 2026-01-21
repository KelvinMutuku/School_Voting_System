import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import json
import time
import os

# --- Path Setup ---
# Get the folder where this script (app.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the path to the image
IMG_PATH = os.path.join(BASE_DIR, 'img-1.jfif')
# --- Constants ---
STREAMS = ["Blue", "Red", "Green", "Yellow", "Pink", "Magenta", "Purple"]
GRADES = [7, 8, 9]
DB_FILE = 'voting_system.db'
REFRESH_INTERVAL = 10  # Seconds to refresh results page

# --- Set Page Configuration ---
st.set_page_config(page_title="KITENGELA INTERNATIONAL SCHOOL JSS ALGOCRACY ELECTIONS")

# --- 1. Database Management ---
def init_db():
    """Initializes the SQLite database with all necessary tables."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Student table (includes gender)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                grade INTEGER NOT NULL,
                student_class TEXT NOT NULL,
                gender TEXT NOT NULL,
                security_question TEXT NOT NULL,
                security_answer TEXT NOT NULL,
                has_voted INTEGER DEFAULT 0
            )
        ''')
        # Teacher table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                grade INTEGER NOT NULL,
                class TEXT NOT NULL,
                security_question TEXT NOT NULL,
                security_answer TEXT NOT NULL
            )
        ''')
        # Position table (added student_class for stream-specific positions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                position_name TEXT PRIMARY KEY,
                grade INTEGER, -- Can be 0 for school-wide
                student_class TEXT, -- Can be NULL for non-class-specific
                candidates_json TEXT
            )
        ''')
        # Vote table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                voter_id TEXT PRIMARY KEY,
                votes_json TEXT
            )
        ''')
        # Setting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                name TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # Weights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weights (
                name TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )
        ''')
        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                student_id TEXT PRIMARY KEY,
                academics INTEGER DEFAULT 0,
                discipline INTEGER DEFAULT 0,
                community_service INTEGER DEFAULT 0,
                leadership INTEGER DEFAULT 0,
                public_speaking INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        # Seed initial data
        seed_data(conn)

def seed_data(conn):
    """Seeds the database with initial data if tables are empty."""
    cursor = conn.cursor()
    # Seed teachers
    cursor.execute("SELECT COUNT(*) FROM teachers")
    if cursor.fetchone()[0] == 0:
        hashed_password = bcrypt.hashpw('1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        teachers_data = []
        for grade in GRADES:
            for stream in STREAMS[:2]: # Limit to Blue, Red for default teachers
                teachers_data.append((
                    f'teacher{grade}{stream.lower()}', hashed_password, grade, stream,
                    'What is your favorite color?', stream.lower()
                ))
        cursor.executemany("INSERT INTO teachers (username, password, grade, class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)", teachers_data)
        st.success("Default teachers seeded with hashed passwords.")
    # Seed positions and candidates (updated for streams)
    cursor.execute("SELECT COUNT(*) FROM positions")
    if cursor.fetchone()[0] == 0:
        positions_data = [
            ('School President', 0, None, json.dumps([
                {'student_id': 'KJS001', 'name': 'John Doe'},
                {'student_id': 'KJS002', 'name': 'Peter Kamau'}
            ])),
            ('School Senator', 0, None, json.dumps([
                {'student_id': 'KJS003', 'name': 'Mary Jane'},
                {'student_id': 'KJS004', 'name': 'Sarah Wanjiku'}
            ]))
        ]
        # Add grade- and stream-specific positions
        for grade in GRADES:
            for stream in STREAMS[:2]: # Blue, Red for defaults
                positions_data.extend([
                    (f'Grade {grade} {stream} Prefect', grade, stream, json.dumps([
                        {'student_id': f'KJS{grade:02d}{stream[:1]}1', 'name': f'{stream} Student {grade}1'}
                    ])),
                    (f'Grade {grade} {stream} Girl Representative', grade, stream, json.dumps([
                        {'student_id': f'KJS{grade:02d}{stream[:1]}2', 'name': f'{stream} Girl {grade}1'}
                    ]))
                ])
        cursor.executemany("INSERT INTO positions (position_name, grade, student_class, candidates_json) VALUES (?, ?, ?, ?)", positions_data)
        st.success("Default positions and candidates seeded.")
    # Seed students
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students_data = []
        student_id = 1
        for grade in GRADES:
            for stream in STREAMS[:2]: # Blue, Red for defaults
                for i in range(1, 3): # Two students per stream
                    student_id_str = f'KJS{student_id:03d}'
                    name = f'Student {grade}{stream[:1]}{i}'
                    hashed_password = bcrypt.hashpw('1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    gender = 'Female' if i == 2 and 'Girl Representative' in name else 'Male'
                    students_data.append((
                        student_id_str, name, hashed_password, grade, stream, gender,
                        'What is your favorite color?', stream.lower()
                    ))
                    student_id += 1
        cursor.executemany("INSERT INTO students (student_id, name, password, grade, student_class, gender, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", students_data)
        st.success("Default students seeded.")
    # Seed settings
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (name, value) VALUES (?, ?)", ('pin', '1234'))
        cursor.execute("INSERT INTO settings (name, value) VALUES (?, ?)", ('voting_open', 'True'))
        st.success("Default settings seeded.")
    # Seed weights
    cursor.execute("SELECT COUNT(*) FROM weights")
    if cursor.fetchone()[0] == 0:
        weights_data = [
            ('student_votes', 30), ('academics', 15), ('discipline', 10),
             ('community_service', 5),
            ('leadership', 10), ('public_speaking', 30)
        ]
        cursor.executemany("INSERT INTO weights (name, value) VALUES (?, ?)", weights_data)
        st.success("Default weights seeded.")
    
    conn.commit()

def fetch_data():
    """Fetches all data from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Fetch students
        cursor.execute("SELECT student_id, name, password, grade, student_class, gender, security_question, security_answer, has_voted FROM students")
        students = [{'student_id': row[0], 'name': row[1], 'password': row[2], 'grade': row[3], 'student_class': row[4], 'gender': row[5], 'security_question': row[6], 'security_answer': row[7], 'has_voted': bool(row[8])} for row in cursor.fetchall()]
        # Fetch teachers
        cursor.execute("SELECT username, password, grade, class, security_question, security_answer FROM teachers")
        teachers = [{'username': row[0], 'password': row[1], 'grade': row[2], 'class': row[3], 'security_question': row[4], 'security_answer': row[5]} for row in cursor.fetchall()]
        # Fetch positions
        cursor.execute("SELECT position_name, grade, student_class, candidates_json FROM positions")
        positions = {row[0]: {'grade': row[1], 'student_class': row[2], 'candidates': json.loads(row[3])} for row in cursor.fetchall()}
        # Fetch votes
        cursor.execute("SELECT voter_id, votes_json FROM votes")
        votes = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
        # Fetch settings
        cursor.execute("SELECT name, value FROM settings")
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        # Fetch weights
        cursor.execute("SELECT name, value FROM weights")
        weights = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Fetch metrics
        cursor.execute("SELECT student_id, academics, discipline, clubs, community_service, teacher, leadership, public_speaking FROM metrics")
        metrics = {row[0]: {'academics': row[1], 'discipline': row[2], 'clubs': row[3], 'community_service': row[4], 'teacher': row[5], 'leadership': row[6], 'public_speaking': row[7]} for row in cursor.fetchall()}
    return students, teachers, positions, votes, settings, weights, metrics

# --- JSON Backup/Import Functions ---
def export_backup():
    students, teachers, positions, votes, settings, weights, metrics = fetch_data()
    backup_data = {
        'students': students,
        'teachers': teachers,
        'positions': positions,
        'votes': votes,
        'settings': settings,
        'weights': weights,
        'metrics': metrics
    }
    return json.dumps(backup_data, indent=2)

def import_backup(data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM teachers")
        cursor.execute("DELETE FROM positions")
        cursor.execute("DELETE FROM votes")
        cursor.execute("DELETE FROM settings")
        cursor.execute("DELETE FROM weights")
        cursor.execute("DELETE FROM metrics")
        
        # Insert students
        for s in data['students']:
            cursor.execute(
                "INSERT INTO students (student_id, name, password, grade, student_class, gender, security_question, security_answer, has_voted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (s['student_id'], s['name'], s['password'], s['grade'], s['student_class'], s['gender'], s['security_question'], s['security_answer'], int(s['has_voted']))
            )
        
        # Insert teachers
        for t in data['teachers']:
            cursor.execute(
                "INSERT INTO teachers (username, password, grade, class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)",
                (t['username'], t['password'], t['grade'], t['class'], t['security_question'], t['security_answer'])
            )
        
        # Insert positions
        for pos_name, pos in data['positions'].items():
            cursor.execute(
                "INSERT INTO positions (position_name, grade, student_class, candidates_json) VALUES (?, ?, ?, ?)",
                (pos_name, pos['grade'], pos.get('student_class'), json.dumps(pos['candidates']))
            )
        
        # Insert votes
        for voter_id, v in data['votes'].items():
            cursor.execute(
                "INSERT INTO votes (voter_id, votes_json) VALUES (?, ?)",
                (voter_id, json.dumps(v))
            )
        
        # Insert settings
        for name, value in data['settings'].items():
            cursor.execute("INSERT INTO settings (name, value) VALUES (?, ?)", (name, value))
        
        # Insert weights
        for name, value in data['weights'].items():
            cursor.execute("INSERT INTO weights (name, value) VALUES (?, ?)", (name, value))
        
        # Insert metrics
        for student_id, m in data['metrics'].items():
            cursor.execute(
                "INSERT INTO metrics (student_id, academics, discipline, community_service, leadership, public_speaking) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (student_id, m['academics'], m['discipline'], m['community_service'], m['leadership'], m['public_speaking'])
            )
        
        conn.commit()

# --- 2. UI and Logic Functions ---
def render_about_page():
    st.header("KITENGELA INTERNATIONAL SCHOOL JSS ALGOCRACY ELECTIONS")
    st.markdown("""
    This platform blends student choice with merit using a transparent formula. Student votes are combined with leadership and performance criteria to select the most suitable leaders.
    ### Criteria & Weights (Total 100%)
    These weights can be adjusted by Admin (with a PIN). Default model:
    * **Student Votes:** 30%
    * **Academics:** 15%
    * **Discipline:** 10%
    * **Community Service:** 5%
    * **Leadership:** 10%
    * **Public Speaking:** 30%
    ### How it works
    * Students register with their ID and password, then vote by position. Some positions are school-wide, while others (like Class Prefect) are restricted to voters of a specific grade and stream.
    * Teachers record each student's metric scores (0–100).
    * The system computes Final Score per candidate:
        `Final = StudentVotes%×Wsv + Academics%×Wa + Discipline%×Wd +  CommunityService%×Wcs + Leadership%×Wl + PublicSpeaking%×Wp`
    * The candidate with the highest Final Score wins each position. The system is transparent and reproducible.
    """)
    st.image(IMG_PATH)

def render_registration_page():
    st.header("Student Registration")
    
    st.subheader("New Student Registration")
    with st.form("register_form"):
        student_id = st.text_input("Student ID (e.g., KJS001)")
        name = st.text_input("Full Name")
        password = st.text_input("Password (min 6 characters)", type="password")
        grade = st.selectbox("Grade", GRADES)
        student_class = st.selectbox("Stream", STREAMS)
        gender = st.selectbox("Gender", ['Male', 'Female', 'Other'])
        security_question = st.selectbox("Security Question", [
            "What is your mother's maiden name?",
            "What is the name of your first pet?",
            "What city were you born in?"
        ])
        security_answer = st.text_input("Security Answer")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not all([student_id, name, password, security_question, security_answer, gender]):
                st.error("Please fill in all fields.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif not student_id.startswith('KJS') or not student_id[3:].isdigit():
                st.error("Student ID must be in format KJS### (e.g., KJS001).")
            else:
                try:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO students (student_id, name, password, grade, student_class, gender, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (student_id, name, hashed_password, grade, student_class, gender, security_question, security_answer)
                        )
                        conn.commit()
                        st.success("Student registered successfully!")
                except sqlite3.IntegrityError:
                    st.error("Student ID already exists.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    st.markdown("---")
    st.subheader("Change Password")
    with st.form("change_password_form"):
        change_id = st.text_input("Student ID")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password (min 6 characters)", type="password")
        
        change_submitted = st.form_submit_button("Change Password")
        if change_submitted:
            if not all([change_id, current_password, new_password]):
                st.error("Please fill in all fields.")
            elif len(new_password) < 6:
                st.error("New password must be at least 6 characters long.")
            else:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT password FROM students WHERE student_id = ?", (change_id,))
                    result = cursor.fetchone()
                    
                    if result and bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
                        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", (hashed_new_password, change_id))
                        conn.commit()
                        st.success("Password changed successfully!")
                    else:
                        st.error("Invalid student ID or current password.")
    st.markdown("---")
    st.subheader("Reset Password")
    
    reset_id = st.text_input("Enter Student ID to start password reset")
    if reset_id:
        question = None
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT security_question FROM students WHERE student_id = ?", (reset_id,))
                result = cursor.fetchone()
                if result:
                    question = result[0]
                else:
                    st.warning("Student ID not found.")
        except Exception as e:
            st.error(f"Database error: {e}")
        if question:
            st.info(f"**Security Question:** {question}")
            with st.form("reset_password_form"):
                security_answer = st.text_input("Your Security Answer")
                new_password = st.text_input("New Password (min 6 characters)", type="password")
                
                reset_submitted = st.form_submit_button("Reset Password")
                if reset_submitted:
                    if len(new_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif not security_answer:
                        st.error("Please enter your security answer.")
                    else:
                        try:
                            with sqlite3.connect(DB_FILE) as conn:
                                cursor = conn.cursor()
                                cursor.execute("SELECT security_answer FROM students WHERE student_id = ?", (reset_id,))
                                answer_result = cursor.fetchone()
                                
                                if answer_result and answer_result[0].lower() == security_answer.lower():
                                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                    cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", (hashed_new_password, reset_id))
                                    conn.commit()
                                    st.success("Password reset successfully!")
                                else:
                                    st.error("Incorrect security answer.")
                        except Exception as e:
                            st.error(f"An error occurred during password reset: {e}")

def render_teacher_page(teachers, students, metrics):
    st.header("Teacher Dashboard")
    if 'teacher_reset_username' not in st.session_state:
        st.session_state.teacher_reset_username = None
    
    if not st.session_state.get('logged_in_teacher'):
        st.subheader("Teacher Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            teacher = next((t for t in teachers if t['username'] == username), None)
            if teacher and bcrypt.checkpw(password.encode('utf-8'), teacher['password'].encode('utf-8')):
                st.session_state.logged_in_teacher = teacher
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        
        st.markdown("---")
        with st.expander("Forgot Your Password?"):
            if not st.session_state.teacher_reset_username:
                with st.form("teacher_find_user_form"):
                    reset_username = st.text_input("Enter your username to begin")
                    if st.form_submit_button("Find My Account"):
                        teacher_to_reset = next((t for t in teachers if t['username'] == reset_username), None)
                        if teacher_to_reset:
                            st.session_state.teacher_reset_username = teacher_to_reset
                            st.rerun()
                        else:
                            st.error("Username not found.")
            
            if st.session_state.teacher_reset_username:
                teacher = st.session_state.teacher_reset_username
                st.info(f"**Security Question:** {teacher['security_question']}")
                with st.form("teacher_reset_form"):
                    security_answer = st.text_input("Your Security Answer")
                    new_password = st.text_input("New Password (min 6 characters)", type="password")
                    if st.form_submit_button("Reset Password"):
                        if len(new_password) < 6:
                            st.error("Password must be at least 6 characters long.")
                        elif not security_answer:
                            st.error("Please provide your security answer.")
                        elif security_answer.lower() == teacher['security_answer'].lower():
                            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            with sqlite3.connect(DB_FILE) as conn:
                                conn.execute("UPDATE teachers SET password = ? WHERE username = ?", (hashed_new_password, teacher['username']))
                                conn.commit()
                            st.success("Password reset successfully! You can now log in.")
                            st.session_state.teacher_reset_username = None
                        else:
                            st.error("Incorrect security answer.")
        return
    # --- TEACHER IS LOGGED IN ---
    teacher = st.session_state.logged_in_teacher
    st.success(f"Welcome, {teacher['username']} (Grade {teacher['grade']} {teacher['class']})!")
    
    st.subheader(f"Enter Metric Scores for Grade {teacher['grade']} {teacher['class']} (0-100)")
    class_students = [s for s in students if s['grade'] == teacher['grade'] and s['student_class'] == teacher['class']]
    
    if not class_students:
        st.info("There are no students registered in your class yet.")
    else:
        with st.form("metrics_form"):
            metric_inputs = {}
            for s in class_students:
                st.markdown(f"**{s['name']} ({s['student_id']})**")
                cols = st.columns(4)
                student_metrics = metrics.get(s['student_id'], {})
                metric_inputs[s['student_id']] = {
                    'academics': cols[0].number_input("Academics", 0, 100, student_metrics.get('academics', 0), key=f"{s['student_id']}_acad"),
                    'discipline': cols[1].number_input("Discipline", 0, 100, student_metrics.get('discipline', 0), key=f"{s['student_id']}_disc"),
                    'community_service': cols[3].number_input("Community", 0, 100, student_metrics.get('community_service', 0), key=f"{s['student_id']}_comm"),
                    'leadership': cols[1].number_input("Leadership", 0, 100, student_metrics.get('leadership', 0), key=f"{s['student_id']}_lead"),
                    'public_speaking': cols[2].number_input("Public Speaking", 0, 100, student_metrics.get('public_speaking', 0), key=f"{s['student_id']}_speak"),
                }
                st.markdown("---")
            if st.form_submit_button("Save All Metric Scores"):
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    for student_id, scores in metric_inputs.items():
                        cursor.execute("""
                            INSERT OR REPLACE INTO metrics (student_id, academics, discipline, community_service, leadership, public_speaking)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (student_id, scores['academics'], scores['discipline'], scores['community_service'], scores['leadership'], scores['public_speaking']))
                    conn.commit()
                st.success("All metric scores have been saved successfully!")
                st.rerun()
    # --- Student Password Management ---
    st.markdown("---")
    st.subheader("Change or Reset Student Passwords")
    if not class_students:
        st.info("No students in your class to manage.")
    else:
        st.info("You can set a new password for a student in your class.")
        for student in class_students:
            with st.expander(f"Manage Password for: {student['name']} ({student['student_id']})"):
                with st.form(key=f"reset_form_{student['student_id']}"):
                    new_password = st.text_input("Enter New Password", type="password", key=f"password_{student['student_id']}")
                    submitted = st.form_submit_button("Set New Password")
                    if submitted:
                        if len(new_password) < 6:
                            st.error("Password must be at least 6 characters long.")
                        else:
                            try:
                                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                with sqlite3.connect(DB_FILE) as conn:
                                    conn.execute("UPDATE students SET password = ? WHERE student_id = ?", (hashed_password, student['student_id']))
                                    conn.commit()
                                st.success(f"Password for {student['name']} has been set successfully!")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
    
    # --- Class Roster Management ---
    st.markdown("---")
    st.subheader("Manage Class Roster")
    # [PASTE THIS INSIDE render_teacher_page, AFTER "Manage Class Roster"]

    st.markdown("---")
    st.subheader("Fix Student Gender")
    st.info("If a student in your class has the wrong gender assigned, correct it here.")

    with st.form("teacher_fix_gender_form"):
        col1, col2 = st.columns([1, 1])
        # .strip() prevents errors if they copy-paste with spaces
        fix_id = col1.text_input("Enter Student ID (e.g., KJS001)").strip()
        new_gender = col2.selectbox("Select Correct Gender", ["Male", "Female"])

        if st.form_submit_button("Update Gender"):
            if not fix_id:
                st.error("Please enter a Student ID.")
            else:
                # Optional: Check if student belongs to this teacher's class
                # (Remove this check if you want teachers to fix ANY student)
                student_check = next((s for s in students if s['student_id'] == fix_id), None)
                
                if not student_check:
                    st.error("Student ID not found.")
                elif student_check['grade'] != teacher['grade'] or student_check['student_class'] != teacher['class']:
                    st.warning(f"Note: This student is in Grade {student_check['grade']} {student_check['student_class']}, not your class. Proceeding with update...")
                    # We allow the update anyway, but gave a warning.
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE students SET gender = ? WHERE student_id = ?", (new_gender, fix_id))
                        conn.commit()
                    st.success(f"Gender for {fix_id} updated to {new_gender}.")
                else:
                    # Student is in their class, update immediately
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE students SET gender = ? WHERE student_id = ?", (new_gender, fix_id))
                        conn.commit()
                    st.success(f"Gender for {student_check['name']} ({fix_id}) updated to {new_gender}.")
                    st.rerun()
    with st.form("add_student_to_class_form"):
        st.markdown(f"**Assign an Existing Student to Your Class (Grade {teacher['grade']} {teacher['class']})**")
        student_id_to_add = st.text_input("Enter Student ID to assign")
        add_student_submitted = st.form_submit_button("Assign to My Class")
        if add_student_submitted:
            if not student_id_to_add:
                st.error("Please enter a Student ID.")
            else:
                student_to_add = next((s for s in students if s['student_id'] == student_id_to_add), None)
                if not student_to_add:
                    st.error(f"Student with ID '{student_id_to_add}' not found.")
                elif student_to_add['grade'] == teacher['grade'] and student_to_add['student_class'] == teacher['class']:
                    st.warning(f"{student_to_add['name']} is already in your class.")
                else:
                    try:
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute("UPDATE students SET grade = ?, student_class = ? WHERE student_id = ?", (teacher['grade'], teacher['class'], student_id_to_add))
                            conn.commit()
                        st.success(f"Successfully assigned {student_to_add['name']} ({student_id_to_add}) to Grade {teacher['grade']} {teacher['class']}.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred while assigning the student: {e}")
    if class_students:
        with st.form("remove_student_from_class_form"):
            st.markdown("**Re-assign a Student From Your Current Class**")
            student_options = {f"{s['name']} ({s['student_id']})": s['student_id'] for s in class_students}
            selected_student_display = st.selectbox("Select student to re-assign", options=list(student_options.keys()))
            new_grade = st.selectbox("Select New Grade", options=GRADES, index=GRADES.index(teacher['grade']))
            new_class = st.selectbox("Select New Stream", options=STREAMS + ['Unassigned'])
            remove_student_submitted = st.form_submit_button("Re-assign Student")
            if remove_student_submitted and selected_student_display:
                student_id_to_remove = student_options[selected_student_display]
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE students SET grade = ?, student_class = ? WHERE student_id = ?", (new_grade, new_class, student_id_to_remove))
                        conn.commit()
                    st.success(f"Successfully re-assigned {selected_student_display} to Grade {new_grade} {new_class}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred while re-assigning the student: {e}")
    # --- Clear All Students ---
    st.markdown("---")
    st.subheader("Danger Zone")
    if st.button("Clear All Students"):
        if st.checkbox("I am sure I want to delete all students"):
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("DELETE FROM students")
                conn.execute("DELETE FROM metrics")
                conn.execute("DELETE FROM votes")
                conn.commit()
            st.success("All students have been cleared.")
            st.rerun()
    # --- Teacher Account Management ---
    st.markdown("---")
    st.subheader("My Account")
    with st.form("teacher_change_password_form"):
        st.markdown("**Change Your Password**")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password (min 6 characters)", type="password")
        change_submitted = st.form_submit_button("Change My Password")
        if change_submitted:
            if not all([current_password, new_password]):
                st.error("Please fill in all fields.")
            elif len(new_password) < 6:
                st.error("New password must be at least 6 characters long.")
            else:
                if bcrypt.checkpw(current_password.encode('utf-8'), teacher['password'].encode('utf-8')):
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE teachers SET password = ? WHERE username = ?", (hashed_new_password, teacher['username']))
                        conn.commit()
                    st.success("Your password has been changed successfully!")
                    st.session_state.logged_in_teacher['password'] = hashed_new_password
                else:
                    st.error("Incorrect current password.")
    if st.button("Logout"):
        st.session_state.logged_in_teacher = None
        st.session_state.teacher_reset_username = None
        st.rerun()

def render_admin_page(settings, students, positions, votes, teachers, weights):
    st.header("Admin Panel")
    
    if not st.session_state.get('logged_in_admin'):
        pin = st.text_input("Enter Admin PIN", type="password")
        if st.button("Login"):
            if pin == settings.get('pin'):
                st.session_state.logged_in_admin = True
                st.rerun()
            else:
                st.error("Invalid PIN.")
        return
    st.success("Admin access granted.")
    # --- Voting Control ---
    st.subheader("Voting Control")
    voting_open_str = settings.get('voting_open', 'True')
    current_voting_status = "Open" if voting_open_str == 'True' else "Closed"
    st.markdown(f"**Current Status:** `{current_voting_status}`")
    if st.button("Toggle Voting Status"):
        new_status = 'False' if voting_open_str == 'True' else 'True'
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("UPDATE settings SET value = ? WHERE name = 'voting_open'", (new_status,))
            conn.commit()
        st.success("Voting status updated.")
        st.rerun()
    st.markdown("---")
    # --- Positions & Candidates ---
    st.subheader("Positions & Candidates")
    st.write("**Current Positions:**")
    if not positions:
        st.info("No positions defined.")
    else:
        # Create a container for the list to keep it organized
        for position_name in list(positions.keys()):
            col1, col2 = st.columns([4, 1])
            col1.write(position_name)
            # Unique key for each button is essential
            if col2.button("Remove", key=f"remove_pos_{position_name}"):
                with sqlite3.connect(DB_FILE) as conn:
                    # Delete the position from the database
                    conn.execute("DELETE FROM positions WHERE position_name = ?", (position_name,))
                    conn.commit()
                st.success(f"Position '{position_name}' removed.")
                st.rerun()
    with st.form("add_position_form"):
        new_position_name = st.text_input("New Position Name")
        grade_options = {0: "All Grades", 7: "Grade 7", 8: "Grade 8", 9: "Grade 9"}
        selected_grade = st.selectbox("Assign to Grade", options=list(grade_options.keys()), format_func=lambda x: grade_options[x])
        selected_stream = st.selectbox("Assign to Stream (optional)", options=[None] + STREAMS, format_func=lambda x: "None (Grade/School-wide)" if x is None else x)
        
        add_position_submitted = st.form_submit_button("Add Position")
        if add_position_submitted and new_position_name:
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("INSERT INTO positions (position_name, grade, student_class, candidates_json) VALUES (?, ?, ?, ?)",
                                 (new_position_name, selected_grade, selected_stream, json.dumps([])))
                    conn.commit()
                st.success(f"Position '{new_position_name}' added for '{grade_options[selected_grade]}'{' ' + selected_stream if selected_stream else ''}.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Position name already exists.")
    st.markdown("---")
    # --- Manage Candidates ---
    st.subheader("Manage Candidates")
    all_position_names = sorted(list(positions.keys()))
    if not all_position_names:
        st.warning("No positions created yet. Add a position above.")
    else:
        selected_position_name = st.selectbox("Select Position to Manage Candidates", all_position_names)
        
        position_details = positions.get(selected_position_name, {})
        grade = position_details.get('grade')
        student_class = position_details.get('student_class')
        grade_display = grade_options.get(grade, "N/A")
        stream_display = student_class if student_class else "None (Grade/School-wide)"
        st.write(f"**Position:** {selected_position_name} | **For:** {grade_display}{' ' + stream_display if student_class else ''}")
        st.write(f"**Current Candidates:**")
        current_candidates = position_details.get('candidates', [])
        if current_candidates:
            st.table(pd.DataFrame(current_candidates))
        else:
            st.info("No candidates for this position yet.")
        with st.form("manage_candidates_form"):
            candidate_id = st.text_input("Student ID to Add/Remove").strip()
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Candidate"):
                    student_to_add = next((s for s in students if s['student_id'] == candidate_id), None)
                    if student_to_add:
                        # Gender validation for Girl Representative
                        if 'Girl Representative' in selected_position_name and student_to_add['gender'] != 'Female':
                            st.error("Only female students can be candidates for Girl Representative positions.")
                        # Grade and stream validation
                        elif student_class and (student_to_add['student_class'] != student_class or student_to_add['grade'] != grade):
                            st.error(f"Candidate must be in Grade {grade} {student_class}.")
                        elif grade != 0 and student_to_add['grade'] != grade:
                            st.error(f"Candidate must be in Grade {grade}.")
                        else:
                            candidate_info = {'student_id': student_to_add['student_id'], 'name': student_to_add['name']}
                            if candidate_info not in current_candidates:
                                current_candidates.append(candidate_info)
                                with sqlite3.connect(DB_FILE) as conn:
                                    conn.execute("UPDATE positions SET candidates_json = ? WHERE position_name = ?", (json.dumps(current_candidates), selected_position_name))
                                    conn.commit()
                                st.success(f"Added {student_to_add['name']} to {selected_position_name}.")
                                st.rerun()
                            else:
                                st.warning("Candidate already in this position.")
                    else:
                        st.error("Student ID not found.")
            with col2:
                if st.form_submit_button("Remove Candidate"):
                    if any(c['student_id'] == candidate_id for c in current_candidates):
                        updated_candidates = [c for c in current_candidates if c['student_id'] != candidate_id]
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute("UPDATE positions SET candidates_json = ? WHERE position_name = ?", (json.dumps(updated_candidates), selected_position_name))
                            conn.commit()
                        st.success(f"Removed candidate {candidate_id} from {selected_position_name}.")
                        st.rerun()
                    else:
                        st.error("Candidate not found in this position.")
    st.markdown("---")
    # --- Manage Teachers ---
    st.subheader("Manage Teachers")
    st.write("**Current Teachers:**")
    for teacher in teachers:
        col1, col2 = st.columns([4, 1])
        col1.write(f"{teacher['username']} (Grade {teacher['grade']} {teacher['class']})")
        if col2.button("Remove", key=f"remove_{teacher['username']}"):
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("DELETE FROM teachers WHERE username = ?", (teacher['username'],))
                conn.commit()
            st.success(f"Teacher {teacher['username']} removed.")
            st.rerun()
    with st.form("add_teacher_form"):
        st.write("**Add New Teacher**")
        teacher_username = st.text_input("Username")
        teacher_password = st.text_input("Password (min 6 characters)", type="password")
        teacher_grade = st.selectbox("Grade", GRADES)
        teacher_class = st.selectbox("Stream", STREAMS)
        security_question = st.text_input("Security Question")
        security_answer = st.text_input("Security Answer")
        if st.form_submit_button("Add Teacher"):
            if not all([teacher_username, teacher_password, security_question, security_answer]):
                st.error("Please fill all fields for the new teacher.")
            elif len(teacher_password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                try:
                    hashed_password = bcrypt.hashpw(teacher_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("INSERT INTO teachers (username, password, grade, class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)",
                                     (teacher_username, hashed_password, teacher_grade, teacher_class, security_question, security_answer))
                        conn.commit()
                    st.success(f"Teacher '{teacher_username}' added.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Teacher username already exists.")
    st.markdown("---")
    # --- Manage Weights ---
# --- Manage Weights ---
    st.subheader("Manage Weights (Must total 100%)")
    with st.form("weights_form"):
        # 1. Define exactly what we want to keep
        allowed_keys = ['student_votes', 'academics', 'discipline', 'community_service', 'leadership', 'public_speaking']
        
        # 2. Filter the current weights to show only these
        # If a key is missing from DB, default it to 0
        current_visible_weights = {k: weights.get(k, 0) for k in allowed_keys}
        
        total_weight = 0
        new_weights = {}
        cols = st.columns(2)
        
        # 3. Create inputs only for the allowed keys
        for i, name in enumerate(allowed_keys):
            with cols[i % 2]:
                # Use the value from DB, or 0 if not found
                val = current_visible_weights[name]
                label = name.replace('_', ' ').title()
                new_weights[name] = st.number_input(label, min_value=0, max_value=100, value=val)
                total_weight += new_weights[name]
        
        st.info(f"**Total Weight:** {total_weight}%")
        
        if st.form_submit_button("Save Weights"):
            if total_weight != 100:
                st.error(f"Weights must sum to exactly 100. Current total: {total_weight}")
            else:
                with sqlite3.connect(DB_FILE) as conn:
                    # A. Update the allowed weights
                    for name, value in new_weights.items():
                        # Insert or Update (upsert) to ensure they exist
                        conn.execute("INSERT OR REPLACE INTO weights (name, value) VALUES (?, ?)", (name, value))
                    
                    # B. NUKE the unwanted weights from the DB so they are gone forever
                    conn.execute("DELETE FROM weights WHERE name IN ('clubs', 'teacher')")
                    conn.commit()
                    
                st.success("Weights updated successfully! (Clubs and Teacher removed from DB)")
                st.rerun()
    # --- Security & Data ---
    st.subheader("Security & Data")
    with st.form("update_pin_form"):
        new_pin = st.text_input("New Admin PIN (min 4 characters)", type="password")
        if st.form_submit_button("Update PIN"):
            if len(new_pin) < 4:
                st.error("PIN must be at least 4 characters long.")
            else:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("UPDATE settings SET value = ? WHERE name = 'pin'", (new_pin,))
                    conn.commit()
                st.success("PIN updated successfully!")
    votes_df = pd.DataFrame.from_dict(votes, orient='index')
    csv_file = votes_df.to_csv(index=True, header=True)
    st.download_button(label="Export Votes (CSV)", data=csv_file, file_name="algocracy_votes.csv", mime="text/csv")
    json_backup = export_backup()
    st.download_button("Download Backup (JSON)", data=json_backup, file_name="backup.json", mime="application/json")
    uploaded_file = st.file_uploader("Import Backup (JSON)", type="json")
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            import_backup(data)
            st.success("Backup imported successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error importing backup: {e}")
    st.markdown("---")
    st.subheader("Danger Zone")
    if st.button("Factory Reset (Deletes ALL Data)"):
        if st.checkbox("I am sure I want to delete all data and reset the system."):
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS students")
                cursor.execute("DROP TABLE IF EXISTS votes")
                cursor.execute("DROP TABLE IF EXISTS positions")
                cursor.execute("DROP TABLE IF EXISTS teachers")
                cursor.execute("DROP TABLE IF EXISTS settings")
                cursor.execute("DROP TABLE IF EXISTS weights")
                cursor.execute("DROP TABLE IF EXISTS metrics")
                init_db()
            st.success("System has been reset to factory settings.")
            st.rerun()
    if st.button("Logout"):
        st.session_state.logged_in_admin = False
        st.rerun()

def render_voting_page(students, positions, settings):
    st.header("Vote")
    st.markdown("---")
    voting_is_open = settings.get('voting_open') == 'True'
    if not voting_is_open:
        st.warning("Voting is currently closed.")
        st.subheader("Live Vote Tally")
        for position_name, position_data in positions.items():
            st.markdown(f"#### {position_name}")
            candidates = position_data['candidates']
            vote_counts = {c['student_id']: 0 for c in candidates}
            total_votes = 0
            for voter_id, cast_votes in votes.items():
                voted_candidate_name = cast_votes.get(position_name)
                if voted_candidate_name:
                    candidate_obj = next((c for c in candidates if c['name'] == voted_candidate_name), None)
                    if candidate_obj:
                        vote_counts[candidate_obj['student_id']] += 1
                        total_votes += 1
            tally_data = []
            for candidate in candidates:
                votes_received = vote_counts.get(candidate['student_id'], 0)
                percentage = (votes_received / total_votes * 100) if total_votes > 0 else 0
                tally_data.append({'Candidate': candidate['name'], 'Votes': votes_received, 'Percentage': f"{percentage:.2f}%"})
            if tally_data:
                st.dataframe(pd.DataFrame(tally_data))
            else:
                st.info("No votes yet.")
        return
    with st.form("vote_form"):
        st.subheader("Voter Authentication")
        voter_id = st.text_input("Enter your Student ID")
        password = st.text_input("Enter your Password", type="password")
        auth_button = st.form_submit_button("Authenticate")
        if auth_button:
            student = next((s for s in students if s['student_id'] == voter_id), None)
            if student and bcrypt.checkpw(password.encode('utf-8'), student['password'].encode('utf-8')):
                if student['has_voted']:
                    st.warning("You have already voted.")
                else:
                    st.session_state.current_voter = student
                    st.success(f"Welcome, {student['name']}! You can now vote.")
            else:
                st.error("Invalid ID or password.")
                st.session_state.current_voter = None
                
    if st.session_state.get('current_voter') and not st.session_state.current_voter['has_voted']:
        voter = st.session_state.current_voter
        voter_grade = voter['grade']
        voter_stream = voter['student_class']
        with st.form("cast_vote_form"):
            st.subheader("Cast Your Votes")
            st.info(f"You are in Grade {voter_grade} {voter_stream}. You can vote for school-wide positions, grade-specific positions, and positions specific to your stream.")
            
            selected_votes = {}
            
            for position_name, position_data in positions.items():
                position_grade = position_data['grade']
                position_stream = position_data['student_class']
                
                # Filter positions: school-wide (grade=0), grade-specific (same grade), or stream-specific (same grade and stream)
                if (position_grade == 0 and position_stream is None) or \
                   (position_grade == voter_grade and position_stream is None) or \
                   (position_grade == voter_grade and position_stream == voter_stream):
                    candidates = position_data['candidates']
                    candidate_names = [c['name'] for c in candidates if c['student_id'] != voter['student_id']] # Exclude voter
                    if not candidate_names:
                        st.info(f"No eligible candidates for {position_name}.")
                    else:
                        selected_candidate = st.selectbox(f"Vote for {position_name}", [""] + candidate_names, key=position_name)
                        if selected_candidate:
                            selected_votes[position_name] = selected_candidate
            if st.form_submit_button("Submit Vote"):
                try:
                    votes_json = json.dumps(selected_votes)
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO votes (voter_id, votes_json) VALUES (?, ?)", (voter['student_id'], votes_json))
                        cursor.execute("UPDATE students SET has_voted = 1 WHERE student_id = ?", (voter['student_id'],))
                        conn.commit()
                    st.success("Your vote has been submitted successfully!")
                    st.session_state.current_voter['has_voted'] = True
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("You have already voted.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

def render_results_page(positions, votes, settings, weights, metrics):
    st.header("Election Results")
    st.markdown("---")
    
    # Display voting status
    voting_is_open = settings.get('voting_open') == 'True'
    st.markdown(f"**Voting Status:** {'Open' if voting_is_open else 'Closed'}")
    st.info(f"Results page auto-refreshes every {REFRESH_INTERVAL} seconds to show live updates.")

    if voting_is_open:
        st.subheader("Live Computed Results (Student Votes + Criteria)")
        for position_name, position_data in positions.items():
            st.markdown(f"### {position_name}")
            candidates = position_data['candidates']
            
            if not candidates:
                st.info("No candidates for this position.")
                continue
            
            vote_counts = {c['student_id']: 0 for c in candidates}
            total_votes = 0
            for voter_id, cast_votes in votes.items():
                voted_candidate_name = cast_votes.get(position_name)
                if voted_candidate_name:
                    candidate_obj = next((c for c in candidates if c['name'] == voted_candidate_name), None)
                    if candidate_obj:
                        vote_counts[candidate_obj['student_id']] += 1
                        total_votes += 1
            
            tally_data = []
            for candidate in candidates:
                student_id = candidate['student_id']
                name = candidate['name']
                votes_received = vote_counts.get(student_id, 0)
                vote_percentage = (votes_received / total_votes * 100) if total_votes > 0 else 0
                candidate_metrics = metrics.get(student_id, {
                    'academics': 0, 'discipline': 0, 
                    'community_service': 0, 'leadership': 0,
                    'public_speaking': 0
                })
                final_score = (
                    (vote_percentage * weights.get('student_votes', 0)) +
                    (candidate_metrics['academics'] * weights.get('academics', 0)) +
                    (candidate_metrics['discipline'] * weights.get('discipline', 0)) +
                    #
                    (candidate_metrics['community_service'] * weights.get('community_service', 0)) +
                    #
                    (candidate_metrics['leadership'] * weights.get('leadership', 0)) +
                    (candidate_metrics['public_speaking'] * weights.get('public_speaking', 0))
                ) / 100.0
                tally_data.append({
                    'Candidate': name,
                    'Vote %': f"{vote_percentage:.2f}",
                    'Academics': candidate_metrics['academics'],
                    'Discipline': candidate_metrics['discipline'],
                    #'Clubs': candidate_metrics['clubs'],
                    'Comm. Service': candidate_metrics['community_service'],
                    #'Teacher': candidate_metrics['teacher'],
                    'Leadership': candidate_metrics['leadership'],
                    'Public Speaking': candidate_metrics['public_speaking'],
                    'Final Score': final_score
                })
            
            if tally_data:
                tally_df = pd.DataFrame(tally_data).sort_values(by='Final Score', ascending=False).reset_index(drop=True)
                display_columns = ['Candidate', 'Final Score', 'Vote %', 'Academics', 'Discipline', 'Leadership', 'Public Speaking', 'Clubs', 'Comm. Service', 'Teacher']
                existing_columns = [col for col in display_columns if col in tally_df.columns]
                tally_df = tally_df[existing_columns]
                if not tally_df.empty:
                    st.success(f"**Leading: {tally_df.iloc[0]['Candidate']}** with a final score of **{tally_df.iloc[0]['Final Score']:.2f}**")
                    st.dataframe(tally_df)
            else:
                st.info("No votes yet for this position.")
    else:
        st.subheader("Final Computed Results")
        csv_lines = ["Position,Candidate,Student Votes,Academics,Discipline,Community Service,Leadership,Public Speaking,Final Score"]
        for position_name, position_data in positions.items():
            st.markdown(f"### Results for {position_name}")
            
            candidates_list = position_data['candidates']
            
            if not candidates_list:
                st.info("No candidates for this position.")
                continue
            vote_counts = {c['student_id']: 0 for c in candidates_list}
            total_position_votes = 0
            for voter_id, cast_votes in votes.items():
                voted_candidate_name = cast_votes.get(position_name)
                if voted_candidate_name:
                    candidate_obj = next((c for c in candidates_list if c['name'] == voted_candidate_name), None)
                    if candidate_obj:
                        vote_counts[candidate_obj['student_id']] += 1
                        total_position_votes += 1
            results_data = []
            for candidate in candidates_list:
                student_id = candidate['student_id']
                name = candidate['name']
                candidate_votes = vote_counts.get(student_id, 0)
                vote_score = (candidate_votes / total_position_votes * 100) if total_position_votes > 0 else 0
                candidate_metrics = metrics.get(student_id, {
                    'academics': 0, 'discipline': 0, 
                    'community_service': 0,  'leadership': 0,
                    'public_speaking': 0
                })
                final_score = (
                    (vote_score * weights.get('student_votes', 0)) +
                    (candidate_metrics['academics'] * weights.get('academics', 0)) +
                    (candidate_metrics['discipline'] * weights.get('discipline', 0)) +
                    #(candidate_metrics['clubs'] * weights.get('clubs', 0)) +
                    (candidate_metrics['community_service'] * weights.get('community_service', 0)) +
                    #(candidate_metrics['teacher'] * weights.get('teacher', 0)) +
                    (candidate_metrics['leadership'] * weights.get('leadership', 0)) +
                    (candidate_metrics['public_speaking'] * weights.get('public_speaking', 0))
                ) / 100.0
                results_data.append({
                    'Candidate': name, 'Vote %': f"{vote_score:.2f}",
                    'Academics': candidate_metrics['academics'],
                    'Discipline': candidate_metrics['discipline'],
                    #'Clubs': candidate_metrics['clubs'],
                    'Comm. Service': candidate_metrics['community_service'],
                    #'Teacher': candidate_metrics['teacher'],
                    'Public Speaking': candidate_metrics['public_speaking'],
                    'Leadership': candidate_metrics['leadership'],
                    'Final Score': final_score
                })
                
                csv_lines.append(f"{position_name},{name},{vote_score:.2f}%,{candidate_metrics['academics']},{candidate_metrics['discipline']},{candidate_metrics['community_service']},{candidate_metrics['leadership']},{candidate_metrics['public_speaking']},{final_score:.2f}")
            if not results_data:
                st.info("No votes have been cast for this position yet.")
                continue
            results_df = pd.DataFrame(results_data).sort_values(by='Final Score', ascending=False).reset_index(drop=True)
            display_columns = ['Candidate', 'Final Score', 'Vote %', 'Academics', 'Discipline', 'Leadership', 'Public Speaking', 'Comm. Service']
            existing_columns = [col for col in display_columns if col in results_df.columns]
            results_df = results_df[existing_columns]
            if not results_df.empty:
                st.success(f"**Winner: {results_df.iloc[0]['Candidate']}** with a final score of **{results_df.iloc[0]['Final Score']:.2f}**")
                st.dataframe(results_df)
        csv_data = "\n".join(csv_lines)
        st.download_button("Export Results (CSV)", data=csv_data, file_name="election_results.csv", mime="text/csv")

# --- Main Application Logic ---
if __name__ == "__main__":
    init_db()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'about'
    if 'logged_in_teacher' not in st.session_state:
        st.session_state.logged_in_teacher = None
    if 'logged_in_admin' not in st.session_state:
        st.session_state.logged_in_admin = False
    if 'current_voter' not in st.session_state:
        st.session_state.current_voter = None
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = time.time()
    
    students, teachers, positions, votes, settings, weights, metrics = fetch_data()
    
    # Auto-refresh for results page
    if st.session_state.current_page == 'results':
        current_time = time.time()
        if current_time - st.session_state.last_refresh_time >= REFRESH_INTERVAL:
            st.session_state.last_refresh_time = current_time
            st.rerun()
    
    st.sidebar.image(IMG_PATH, use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    page_map = {
        "About": "about",
        "Register": "register",
        "Vote": "vote",
        "Results": "results",
        "Teacher": "teacher",
        "Admin": "admin"
    }
    for page_name, page_key in page_map.items():
        if st.sidebar.button(page_name):
            st.session_state.current_page = page_key
            st.session_state.last_refresh_time = time.time()  # Reset refresh timer on page change
            st.rerun()
    
    page_to_render = st.session_state.get('current_page', 'about')
    if page_to_render == 'register':
        render_registration_page()
    elif page_to_render == 'about':
        render_about_page()
    elif page_to_render == 'vote':
        render_voting_page(students, positions, settings)
    elif page_to_render == 'results':
        render_results_page(positions, votes, settings, weights, metrics)
    elif page_to_render == 'teacher':
        render_teacher_page(teachers, students, metrics)
    elif page_to_render == 'admin':
        render_admin_page(settings, students, positions, votes, teachers, weights)
