import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import json
import time
import os
import altair as alt

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
        
        # Student table
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
        # Position table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                position_name TEXT PRIMARY KEY,
                grade INTEGER,
                student_class TEXT,
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
        # Metrics table - Added 'locked' column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                student_id TEXT PRIMARY KEY,
                academics INTEGER DEFAULT 0,
                discipline INTEGER DEFAULT 0,
                community_service INTEGER DEFAULT 0,
                leadership INTEGER DEFAULT 0,
                public_speaking INTEGER DEFAULT 0,
                locked INTEGER DEFAULT 0, 
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        # --- MIGRATION: Check if 'locked' column exists (for existing DBs) ---
        cursor.execute("PRAGMA table_info(metrics)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'locked' not in columns:
            cursor.execute("ALTER TABLE metrics ADD COLUMN locked INTEGER DEFAULT 0")
            
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
        
        # Fetch metrics (including locked)
        cursor.execute("SELECT student_id, academics, discipline, community_service, leadership, public_speaking, locked FROM metrics")
        metrics = {row[0]: {'academics': row[1], 'discipline': row[2], 'community_service': row[3], 'leadership': row[4], 'public_speaking': row[5], 'locked': bool(row[6])} for row in cursor.fetchall()}
        
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
        
        # Insert Metrics (Including Locked)
        for student_id, m in data['metrics'].items():
            locked_val = m.get('locked', 1) # Default to 1 (locked) if importing old backup to be safe
            cursor.execute(
                "INSERT INTO metrics (student_id, academics, discipline, community_service, leadership, public_speaking, locked) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (student_id, m['academics'], m['discipline'], m['community_service'], m['leadership'], m['public_speaking'], int(locked_val))
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
    
    # --- Sync Session State with Database ---
    for s in class_students:
        s_id = s['student_id']
        m_data = metrics.get(s_id, {})
        sync_map = {
            f"{s_id}_acad": 'academics',
            f"{s_id}_disc": 'discipline',
            f"{s_id}_comm": 'community_service',
            f"{s_id}_lead": 'leadership',
            f"{s_id}_speak": 'public_speaking'
        }
        for ss_key, db_col in sync_map.items():
            if ss_key in st.session_state:
                st.session_state[ss_key] = m_data.get(db_col, 0)

    if not class_students:
        st.info("There are no students registered in your class yet.")
    else:
        with st.form("metrics_form"):
            metric_inputs = {}
            # Header
            cols = st.columns([2, 1, 1, 1, 1, 1])
            cols[0].write("**Student Name**")
            cols[1].write("Academics")
            cols[2].write("Discipline")
            cols[3].write("Comm. Svc")
            cols[4].write("Leadership")
            cols[5].write("Speaking")
            
            any_unlocked = False

            for s in class_students:
                cols = st.columns([2, 1, 1, 1, 1, 1])
                student_metrics = metrics.get(s['student_id'], {})
                is_locked = student_metrics.get('locked', False)
                
                # Show Name and Status
                status_icon = "🔒" if is_locked else "✏️"
                cols[0].write(f"{status_icon} {s['name']}\n({s['student_id']})")
                
                disabled = is_locked
                if not is_locked:
                    any_unlocked = True

                # Capture inputs
                academics = cols[1].number_input("Acad", 0, 100, student_metrics.get('academics', 0), key=f"{s['student_id']}_acad", label_visibility="collapsed", disabled=disabled)
                discipline = cols[2].number_input("Disc", 0, 100, student_metrics.get('discipline', 0), key=f"{s['student_id']}_disc", label_visibility="collapsed", disabled=disabled)
                comm_svc = cols[3].number_input("Comm", 0, 100, student_metrics.get('community_service', 0), key=f"{s['student_id']}_comm", label_visibility="collapsed", disabled=disabled)
                leadership = cols[4].number_input("Lead", 0, 100, student_metrics.get('leadership', 0), key=f"{s['student_id']}_lead", label_visibility="collapsed", disabled=disabled)
                speaking = cols[5].number_input("Speak", 0, 100, student_metrics.get('public_speaking', 0), key=f"{s['student_id']}_speak", label_visibility="collapsed", disabled=disabled)

                if not is_locked:
                    metric_inputs[s['student_id']] = {
                        'academics': academics,
                        'discipline': discipline,
                        'community_service': comm_svc,
                        'leadership': leadership,
                        'public_speaking': speaking,
                    }
                st.markdown("<hr style='margin: 5px 0'>", unsafe_allow_html=True)
            
            if any_unlocked:
                st.warning("⚠️ Warning: Once you click 'Submit', these scores will be LOCKED.")
                if st.form_submit_button("Submit & Lock Scores"):
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        for student_id, scores in metric_inputs.items():
                            cursor.execute("""
                                INSERT OR REPLACE INTO metrics (student_id, academics, discipline, community_service, leadership, public_speaking, locked)
                                VALUES (?, ?, ?, ?, ?, ?, 1)
                            """, (student_id, scores['academics'], scores['discipline'], scores['community_service'], scores['leadership'], scores['public_speaking']))
                        conn.commit()
                    st.success("Scores submitted and locked successfully!")
                    st.rerun()
            else:
                st.info("All scores for this class have been submitted and locked. Please contact Admin if edits are required.")
                st.form_submit_button("Scores Locked", disabled=True)

    # --- Student Password Management ---
    st.markdown("---")
    st.subheader("Change or Reset Student Passwords")
    # ... (Keep remaining Teacher Page code as is)
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

    st.markdown("---")
    st.subheader("Fix Student Gender")
    st.info("If a student in your class has the wrong gender assigned, correct it here.")

    with st.form("teacher_fix_gender_form"):
        col1, col2 = st.columns([1, 1])
        fix_id = col1.text_input("Enter Student ID (e.g., KJS001)").strip()
        new_gender = col2.selectbox("Select Correct Gender", ["Male", "Female"])

        if st.form_submit_button("Update Gender"):
            if not fix_id:
                st.error("Please enter a Student ID.")
            else:
                student_check = next((s for s in students if s['student_id'] == fix_id), None)
                if not student_check:
                    st.error("Student ID not found.")
                elif student_check['grade'] != teacher['grade'] or student_check['student_class'] != teacher['class']:
                    st.warning(f"Note: This student is in Grade {student_check['grade']} {student_check['student_class']}, not your class. Proceeding with update...")
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE students SET gender = ? WHERE student_id = ?", (new_gender, fix_id))
                        conn.commit()
                    st.success(f"Gender for {fix_id} updated to {new_gender}.")
                else:
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

def render_super_admin_page(settings, students, metrics):
    st.header("Super Admin Panel")
    st.markdown("---")
    
    # --- Login Logic ---
    if not st.session_state.get('logged_in_super_admin'):
        st.subheader("Super Admin Login")
        st.info("Please enter the Master PIN to access sensitive controls.")
        pin = st.text_input("Enter Super Admin PIN", type="password", key="sa_pin")
        if st.button("Login", key="sa_login_btn"):
            # We use the same global PIN from settings
            if pin == settings.get('pin'):
                st.session_state.logged_in_super_admin = True
                st.rerun()
            else:
                st.error("Invalid PIN.")
        return

    st.success("Super Admin access granted.")
    
    # --- Logout Button ---
    if st.button("Logout", key="sa_logout"):
        st.session_state.logged_in_super_admin = False
        st.rerun()
        
    st.markdown("---")
    
    # --- MANAGE TEACHER VOTES (Override) ---
    st.subheader("Manage Teacher Votes (Override)")
    st.info("As Super Admin, you can edit student metric scores even if the teacher has locked them.")
    
    # Filter for finding a student
    col_grade, col_stream = st.columns(2)
    filter_grade = col_grade.selectbox("Filter by Grade", [7, 8, 9], key="sa_metrics_grade")
    filter_stream = col_stream.selectbox("Filter by Stream", STREAMS, key="sa_metrics_stream")
    
    adm_students = [s for s in students if s['grade'] == filter_grade and s['student_class'] == filter_stream]
    
    if adm_students:
        student_opts = {f"{s['name']} ({s['student_id']})": s['student_id'] for s in adm_students}
        selected_s_key = st.selectbox("Select Student to Edit", options=list(student_opts.keys()), key="sa_select_student")
        
        if selected_s_key:
            s_id = student_opts[selected_s_key]
            # Fetch fresh metrics from DB
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("SELECT academics, discipline, community_service, leadership, public_speaking, locked FROM metrics WHERE student_id = ?", (s_id,))
                row = c.fetchone()
                if row:
                    curr_m = {'academics': row[0], 'discipline': row[1], 'community_service': row[2], 'leadership': row[3], 'public_speaking': row[4], 'locked': row[5]}
                else:
                    curr_m = {'academics': 0, 'discipline': 0, 'community_service': 0, 'leadership': 0, 'public_speaking': 0, 'locked': 0}

            st.markdown(f"**Editing Scores for: {selected_s_key}**")
            if curr_m['locked']:
                st.warning("Status: LOCKED by Teacher (You can override)")
            else:
                st.success("Status: Open")

            with st.form("super_admin_edit_metrics"):
                c1, c2, c3, c4, c5 = st.columns(5)
                n_acad = c1.number_input("Academics", 0, 100, curr_m['academics'])
                n_disc = c2.number_input("Discipline", 0, 100, curr_m['discipline'])
                n_comm = c3.number_input("Comm. Svc", 0, 100, curr_m['community_service'])
                n_lead = c4.number_input("Leadership", 0, 100, curr_m['leadership'])
                n_speak = c5.number_input("Speaking", 0, 100, curr_m['public_speaking'])
                
                # Option to unlock
                unlock_student = st.checkbox("Unlock this student (Allow teacher to edit again)?")

                if st.form_submit_button("Update Scores"):
                    new_lock_status = 0 if unlock_student else 1 
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO metrics (student_id, academics, discipline, community_service, leadership, public_speaking, locked)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (s_id, n_acad, n_disc, n_comm, n_lead, n_speak, new_lock_status))
                        conn.commit()
                    st.success("Scores updated successfully.")
                    st.rerun()
    else:
        st.info("No students found in this class.")

    st.markdown("---")
    
    # --- CHANGE ADMIN PIN (New Feature) ---
    st.subheader("Security Settings")
    with st.expander("Change Admin PIN"):
        with st.form("change_pin_form"):
            current_pin = st.text_input("Current PIN", type="password")
            new_pin = st.text_input("New PIN", type="password")
            confirm_pin = st.text_input("Confirm New PIN", type="password")
            
            if st.form_submit_button("Update PIN"):
                if not all([current_pin, new_pin, confirm_pin]):
                    st.error("Please fill in all fields.")
                elif current_pin != settings.get('pin'):
                    st.error("Incorrect current PIN.")
                elif new_pin != confirm_pin:
                    st.error("New PINs do not match.")
                elif len(new_pin) < 4:
                    st.error("PIN must be at least 4 characters.")
                else:
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE settings SET value = ? WHERE name = 'pin'", (new_pin,))
                        conn.commit()
                    st.success("Admin PIN updated successfully. Please re-login.")
                    st.session_state.logged_in_super_admin = False
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
        for position_name in list(positions.keys()):
            col1, col2 = st.columns([4, 1])
            col1.write(position_name)
            if col2.button("Remove", key=f"remove_pos_{position_name}"):
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("DELETE FROM positions WHERE position_name = ?", (position_name,))
                    conn.commit()
                st.success(f"Position '{position_name}' removed.")
                st.rerun()
    
    with st.form("add_position_form"):
        new_position_name = st.text_input("New Position Name")
        grade_options = {0: "All Grades", 7: "Grade 7", 8: "Grade 8", 9: "Grade 9"}
        selected_grade = st.selectbox("Assign to Grade", options=list(grade_options.keys()), format_func=lambda x: grade_options[x])
        selected_stream = st.selectbox("Assign to Stream (optional)", options=[None] + STREAMS, format_func=lambda x: "None (Grade/School-wide)" if x is None else x)
        
        if st.form_submit_button("Add Position"):
            if new_position_name:
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("INSERT INTO positions (position_name, grade, student_class, candidates_json) VALUES (?, ?, ?, ?)",
                                (new_position_name, selected_grade, selected_stream, json.dumps([])))
                        conn.commit()
                    st.success(f"Position '{new_position_name}' added.")
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
        
        st.write(f"**Current Candidates for {selected_position_name}:**")
        current_candidates = position_details.get('candidates', [])
        
        if current_candidates:
            st.table(pd.DataFrame(current_candidates))
        else:
            st.info("No candidates yet.")

        # --- SINGLE FORM FOR CANDIDATES ---
        with st.form("manage_candidates_form"):
            is_joint_ticket = "President & Deputy" in selected_position_name
            
            # 1. Inputs
            if is_joint_ticket:
                st.info("Joint Ticket: Enter IDs for both President and Deputy.")
                c1, c2 = st.columns(2)
                id_pres = c1.text_input("President ID", key="pres_input").strip()
                id_dep = c2.text_input("Deputy ID", key="dep_input").strip()
                candidate_id = f"{id_pres}+{id_dep}"
            else:
                candidate_id = st.text_input("Student ID to Add/Remove", key="single_input").strip()

            # 2. Buttons
            col1, col2 = st.columns(2)
            
            # ADD BUTTON
            if col1.form_submit_button("Add Candidate"):
                if is_joint_ticket:
                    # Joint Ticket Logic
                    s1 = next((s for s in students if s['student_id'] == id_pres), None)
                    s2 = next((s for s in students if s['student_id'] == id_dep), None)
                    
                    if not s1 or not s2:
                        st.error("One or both Student IDs not found.")
                    elif id_pres == id_dep:
                        st.error("IDs must be different.")
                    else:
                        name = f"{s1['name']} & {s2['name']}"
                        new_cand = {'student_id': candidate_id, 'name': name}
                        if new_cand not in current_candidates:
                            current_candidates.append(new_cand)
                            with sqlite3.connect(DB_FILE) as conn:
                                conn.execute("UPDATE positions SET candidates_json=? WHERE position_name=?", (json.dumps(current_candidates), selected_position_name))
                                conn.commit()
                            st.success(f"Added: {name}")
                            st.rerun()
                        else:
                            st.warning("Already added.")
                else:
                    # Single Candidate Logic
                    s = next((s for s in students if s['student_id'] == candidate_id), None)
                    if s:
                        # Validations
                        if 'Girl Representative' in selected_position_name and s['gender'] != 'Female':
                            st.error("Must be Female.")
                        elif student_class and (s['student_class'] != student_class or s['grade'] != grade):
                            st.error(f"Must be Grade {grade} {student_class}.")
                        elif grade != 0 and s['grade'] != grade:
                            st.error(f"Must be Grade {grade}.")
                        else:
                            new_cand = {'student_id': s['student_id'], 'name': s['name']}
                            if new_cand not in current_candidates:
                                current_candidates.append(new_cand)
                                with sqlite3.connect(DB_FILE) as conn:
                                    conn.execute("UPDATE positions SET candidates_json=? WHERE position_name=?", (json.dumps(current_candidates), selected_position_name))
                                    conn.commit()
                                st.success(f"Added: {s['name']}")
                                st.rerun()
                            else:
                                st.warning("Already added.")
                    else:
                        st.error("ID Not Found.")

            # REMOVE BUTTON
            if col2.form_submit_button("Remove Candidate"):
                # Filter out the ID
                new_list = [c for c in current_candidates if c['student_id'] != candidate_id]
                if len(new_list) < len(current_candidates):
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE positions SET candidates_json=? WHERE position_name=?", (json.dumps(new_list), selected_position_name))
                        conn.commit()
                    st.success("Removed.")
                    st.rerun()
                else:
                    st.error("ID not found in list.")

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
        tu = st.text_input("Username")
        tp = st.text_input("Password", type="password")
        tg = st.selectbox("Grade", GRADES, key="new_teach_grade")
        tc = st.selectbox("Stream", STREAMS, key="new_teach_stream")
        sq = st.text_input("Security Question")
        sa = st.text_input("Security Answer")
        
        if st.form_submit_button("Add Teacher"):
            if len(tp) < 6:
                st.error("Password too short.")
            else:
                try:
                    hp = bcrypt.hashpw(tp.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("INSERT INTO teachers VALUES (?,?,?,?,?,?)", (tu, hp, tg, tc, sq, sa))
                        conn.commit()
                    st.success("Teacher Added.")
                    st.rerun()
                except:
                    st.error("Error adding teacher.")

    st.markdown("---")
    
    # --- Manage Weights ---
    st.subheader("Manage Weights (Must total 100%)")
    with st.form("weights_form"):
        allowed = ['student_votes', 'academics', 'discipline', 'community_service', 'leadership', 'public_speaking']
        current_w = {k: weights.get(k, 0) for k in allowed}
        new_w = {}
        total = 0
        cols = st.columns(2)
        
        for i, k in enumerate(allowed):
            with cols[i % 2]:
                new_w[k] = st.number_input(k.replace('_',' ').title(), 0, 100, current_w[k])
                total += new_w[k]
        
        st.info(f"Total: {total}%")
        
        if st.form_submit_button("Save Weights"):
            if total == 100:
                with sqlite3.connect(DB_FILE) as conn:
                    for k, v in new_w.items():
                        conn.execute("INSERT OR REPLACE INTO weights (name, value) VALUES (?, ?)", (k, v))
                    conn.execute("DELETE FROM weights WHERE name IN ('clubs', 'teacher')")
                    conn.commit()
                st.success("Weights Saved.")
                st.rerun()
            else:
                st.error("Total must be 100.")

    st.markdown("---")
    
    # --- Data Management ---
    st.subheader("Data Management")
    # Export Votes
    v_df = pd.DataFrame.from_dict(votes, orient='index')
    st.download_button("Export Votes CSV", v_df.to_csv(), "votes.csv", "text/csv")
    
    # Export Backup
    st.download_button("Download JSON Backup", export_backup(), "backup.json", "application/json")
    
    # Import Backup
    up_file = st.file_uploader("Import JSON", type="json")
    if up_file:
        try:
            import_backup(json.load(up_file))
            st.success("Imported.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    # Reset
    st.markdown("---")
    st.subheader("Danger Zone")
    if st.button("Factory Reset (Deletes ALL Data)"):
        if st.checkbox("Confirm Delete All Data"):
            with sqlite3.connect(DB_FILE) as conn:
                for t in ["students", "votes", "positions", "teachers", "settings", "weights", "metrics"]:
                    conn.execute(f"DROP TABLE IF EXISTS {t}")
                init_db()
            st.success("Reset Complete.")
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

    # --- HELPER: Get Metrics (Handles Single OR Joint Tickets) ---
    def get_candidate_metrics(student_id):
        """
        Fetches metrics for a candidate. 
        If student_id contains '+', it splits the IDs, fetches both, and returns the average.
        """
        # Default zero-scores to avoid errors
        default_m = {'academics': 0, 'discipline': 0, 'community_service': 0, 'leadership': 0, 'public_speaking': 0}
        
        if '+' in student_id:
            # Joint Ticket (e.g., "KJS001+KJS002")
            try:
                id1, id2 = student_id.split('+')
                m1 = metrics.get(id1.strip(), default_m)
                m2 = metrics.get(id2.strip(), default_m)
                
                # Average the scores
                avg_metrics = {}
                for key in default_m.keys():
                    avg_metrics[key] = (m1.get(key, 0) + m2.get(key, 0)) / 2.0
                return avg_metrics
            except:
                return default_m
        else:
            # Single Candidate
            return metrics.get(student_id, default_m)

    # --- HELPER: Calculate Score ---
    def calculate_final_score(c_metrics, vote_percentage):
        score = (
            (vote_percentage * weights.get('student_votes', 0)) +
            (c_metrics.get('academics', 0) * weights.get('academics', 0)) +
            (c_metrics.get('discipline', 0) * weights.get('discipline', 0)) +
            (c_metrics.get('community_service', 0) * weights.get('community_service', 0)) +
            (c_metrics.get('leadership', 0) * weights.get('leadership', 0)) +
            (c_metrics.get('public_speaking', 0) * weights.get('public_speaking', 0))
        ) / 100.0
        return score

    # --- LOGIC: Render Tables ---
    if voting_is_open:
        st.subheader("Live Computed Results (Student Votes + Criteria)")
    else:
        st.subheader("Final Computed Results")

    # Prepare CSV Header with exact About Page names
    csv_lines = ["Position,Candidate,Student Votes,Academics,Discipline,Community Service,Leadership,Public Speaking,Final Score"]

    for position_name, position_data in positions.items():
        st.markdown(f"### {position_name}")
        candidates = position_data['candidates']
        
        if not candidates:
            st.info("No candidates for this position.")
            continue
        
        # 1. Tally Votes
        vote_counts = {c['student_id']: 0 for c in candidates}
        total_votes = 0
        for voter_id, cast_votes in votes.items():
            voted_candidate_name = cast_votes.get(position_name)
            if voted_candidate_name:
                # Find the candidate object that matches the voted name
                candidate_obj = next((c for c in candidates if c['name'] == voted_candidate_name), None)
                if candidate_obj:
                    vote_counts[candidate_obj['student_id']] += 1
                    total_votes += 1
        
        # 2. Build Table Data
        tally_data = []
        for candidate in candidates:
            c_id = candidate['student_id']
            c_name = candidate['name']
            
            # Calculate Vote %
            votes_received = vote_counts.get(c_id, 0)
            vote_percentage = (votes_received / total_votes * 100) if total_votes > 0 else 0
            
            # Get Metrics
            m = get_candidate_metrics(c_id)
            
            # Calculate Final Score
            final_score = calculate_final_score(m, vote_percentage)
            
            # Append data with keys exactly matching About Page
            tally_data.append({
                'Candidate': c_name,
                'Student Votes': f"{vote_percentage:.2f}",   # Renamed from 'Vote %'
                'Academics': f"{m.get('academics', 0):.1f}",
                'Discipline': f"{m.get('discipline', 0):.1f}",
                'Community Service': f"{m.get('community_service', 0):.1f}", # Renamed from 'Comm. Service'
                'Leadership': f"{m.get('leadership', 0):.1f}",
                'Public Speaking': f"{m.get('public_speaking', 0):.1f}",
                'Final Score': final_score
            })
            
            # Add to CSV string if needed
            if not voting_is_open:
                 csv_lines.append(f"{position_name},{c_name},{vote_percentage:.2f},{m.get('academics')},{m.get('discipline')},{m.get('community_service')},{m.get('leadership')},{m.get('public_speaking')},{final_score:.2f}")

        # 3. Render Dataframe
        if tally_data:
            # Sort by Final Score (Descending)
            tally_df = pd.DataFrame(tally_data).sort_values(by='Final Score', ascending=False).reset_index(drop=True)
            
            # Identify the leader/winner
            leader_name = tally_df.iloc[0]['Candidate']
            leader_score = tally_df.iloc[0]['Final Score']
            
            # Format the float score for display
            tally_df['Final Score'] = tally_df['Final Score'].map(lambda x: f"{x:.2f}")

            if voting_is_open:
                st.success(f"**Leading: {leader_name}** with a score of **{leader_score:.2f}**")
            else:
                st.success(f"**Winner: {leader_name}** with a score of **{leader_score:.2f}**")
            
            st.dataframe(tally_df)

            # --- NEW CHART SECTION (PIE CHART) ---
            # Create a dedicated dataframe for plotting with numeric types
            chart_rows = []
            for candidate in candidates:
                c_id = candidate['student_id']
                votes_rx = vote_counts.get(c_id, 0)
                pct = (votes_rx / total_votes * 100) if total_votes > 0 else 0
                chart_rows.append({
                    "Candidate": candidate['name'],
                    "Total Votes": votes_rx,
                    "Percentage": pct
                })
            
            chart_df = pd.DataFrame(chart_rows)
            
            # Create Base Chart
            base = alt.Chart(chart_df).encode(
                theta=alt.Theta("Total Votes", stack=True)
            )
            
            # Pie Chart (Arcs)
            pie = base.mark_arc(outerRadius=120).encode(
                color=alt.Color("Candidate"),
                order=alt.Order("Total Votes", sort="descending"),
                tooltip=["Candidate", "Total Votes", alt.Tooltip("Percentage", format=".1f")]
            )
            
            # Text Labels over arcs
            text = base.mark_text(radius=140).encode(
                text=alt.Text("Percentage", format=".1f"),
                order=alt.Order("Total Votes", sort="descending"),
                color=alt.value("black")
            )
            
            st.markdown("**Vote Breakdown Chart**")
            st.altair_chart(pie + text, use_container_width=True)
            
        else:
            st.info("No candidates found.")

    # 4. CSV Download Button (Only if voting is closed)
    if not voting_is_open:
        st.download_button("Export Results (CSV)", "\n".join(csv_lines), "election_results.csv", "text/csv")

# --- Main Application Logic ---
if __name__ == "__main__":
    init_db()
    
    # Session State Initialization
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'about'
    if 'logged_in_teacher' not in st.session_state:
        st.session_state.logged_in_teacher = None
    if 'logged_in_admin' not in st.session_state:
        st.session_state.logged_in_admin = False
    if 'logged_in_super_admin' not in st.session_state:  # NEW
        st.session_state.logged_in_super_admin = False
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
    
    # Updated Page Map with Super Admin
    page_map = {
        "About": "about",
        "Register": "register",
        "Vote": "vote",
        "Results": "results",
        "Teacher": "teacher",
        "Admin": "admin",
        "Super Admin": "super_admin" # NEW TAB
    }
    
    for page_name, page_key in page_map.items():
        if st.sidebar.button(page_name):
            st.session_state.current_page = page_key
            st.session_state.last_refresh_time = time.time()
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
    elif page_to_render == 'super_admin':  # NEW RENDER CALL
        render_super_admin_page(settings, students, metrics)