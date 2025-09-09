import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import json

# --- 1. Database Management ---
DB_FILE = 'voting_system.db'

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
                security_question TEXT NOT NULL DEFAULT 'What is your favorite subject to teach?',
                security_answer TEXT NOT NULL DEFAULT 'math'
            )
        ''')

        # Position table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                position_name TEXT PRIMARY KEY,
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
        
        # Metrics table to store teacher-inputted scores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                student_id TEXT PRIMARY KEY,
                academics INTEGER DEFAULT 0,
                discipline INTEGER DEFAULT 0,
                clubs INTEGER DEFAULT 0,
                community_service INTEGER DEFAULT 0,
                teacher INTEGER DEFAULT 0,
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
        # Hash the default password '1234'
        hashed_password = bcrypt.hashpw('1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        teachers_data = [
            ('teacher7blue', hashed_password, 7, 'Blue', 'What is your favorite color?', 'blue'),
            ('teacher7red', hashed_password, 7, 'Red', 'What is your favorite color?', 'red'),
            ('teacher8blue', hashed_password, 8, 'Blue', 'What is your favorite color?', 'blue'),
            ('teacher8red', hashed_password, 8, 'Red', 'What is your favorite color?', 'red'),
            ('teacher9blue', hashed_password, 9, 'Blue', 'What is your favorite color?', 'blue'),
            ('teacher9red', hashed_password, 9, 'Red', 'What is your favorite color?', 'red')
        ]
        cursor.executemany("INSERT INTO teachers (username, password, grade, class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)", teachers_data)
        st.success("Default teachers seeded with hashed passwords.")

    # Seed positions and candidates
    cursor.execute("SELECT COUNT(*) FROM positions")
    if cursor.fetchone()[0] == 0:
        positions_data = [
            ('Head Boy', json.dumps([{'student_id': 'KIS-001', 'name': 'John Doe'}, {'student_id': 'KIS-002', 'name': 'Peter Kamau'}])),
            ('Head Girl', json.dumps([{'student_id': 'KIS-003', 'name': 'Mary Jane'}, {'student_id': 'KIS-004', 'name': 'Sarah Wanjiku'}])),
            ('Academics Prefect', json.dumps([{'student_id': 'KIS-005', 'name': 'Alex Omondi'}, {'student_id': 'KIS-006', 'name': 'Brian Kibet'}])),
            ('Discipline Prefect', json.dumps([{'student_id': 'KIS-007', 'name': 'Cynthia Wangui'}, {'student_id': 'KIS-008', 'name': 'Diana Anyango'}]))
        ]
        cursor.executemany("INSERT INTO positions (position_name, candidates_json) VALUES (?, ?)", positions_data)
        st.success("Default positions and candidates seeded.")

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
            ('clubs', 10), ('community_service', 5), ('teacher', 10),
            ('leadership', 10), ('public_speaking', 10)
        ]
        cursor.executemany("INSERT INTO weights (name, value) VALUES (?, ?)", weights_data)
        st.success("Default weights seeded.")
    
    conn.commit()

def fetch_data():
    """Fetches all data from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Fetch students
        cursor.execute("SELECT student_id, name, password, grade, student_class, security_question, security_answer, has_voted FROM students")
        students = [{'student_id': row[0], 'name': row[1], 'password': row[2], 'grade': row[3], 'student_class': row[4], 'security_question': row[5], 'security_answer': row[6], 'has_voted': bool(row[7])} for row in cursor.fetchall()]

        # Fetch teachers
        cursor.execute("SELECT username, password, grade, class, security_question, security_answer FROM teachers")
        teachers = [{'username': row[0], 'password': row[1], 'grade': row[2], 'class': row[3], 'security_question': row[4], 'security_answer': row[5]} for row in cursor.fetchall()]

        # Fetch positions
        cursor.execute("SELECT position_name, candidates_json FROM positions")
        positions = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

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

# --- 2. UI and Logic Functions ---
def render_about_page():
    st.header("Student Leaders – Algocracy System")
    st.markdown("""
    This platform blends student choice with merit using a clear, public formula. Student votes are combined with leadership and performance criteria to select the most suitable leaders.

    ### Criteria & Weights (Total 100%)
    These weights can be adjusted by Admin (with a PIN). Default model:

    * **Student Votes:** 30%
    * **Academics:** 15%
    * **Discipline:** 10%
    * **Clubs:** 10%
    * **Community Service:** 5%
    * **Teacher:** 10%
    * **Leadership:** 10%
    * **Public Speaking:** 10%

    ### How it works
    * Students register with their ID and password, then vote by position.
    * Teachers record each student's metric scores (0–100).
    * The system computes Final Score per candidate:
        `Final = StudentVotes%×Wsv + Academics%×Wa + Discipline%×Wd + Clubs%×Wc + CommunityService%×Wcs + Teacher%×Wt + Leadership%×Wl + PublicSpeaking%×Wp`
    * The candidate with the highest Final Score wins each position. The system is transparent and reproducible.
    """)
    st.image("https://images.unsplash.com/photo-1549419137-9d7a2d480371?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")

def render_registration_page():
    st.header("Student Registration")
    
    st.subheader("New Student Registration")
    with st.form("register_form"):
        student_id = st.text_input("Student ID (e.g., KIS-1234)")
        name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        grade = st.selectbox("Grade", [7, 8, 9])
        student_class = st.selectbox("Class", ['Blue', 'Red', 'Green', 'Yellow', 'Pink', 'Magenta', 'Purple'])
        security_question = st.selectbox("Security Question", ["What is your mother's maiden name?", "What is the name of your first pet?", "What city were you born in?"])
        security_answer = st.text_input("Security Answer")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not all([student_id, name, password, security_question, security_answer]):
                st.error("Please fill in all fields.")
            else:
                try:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO students (student_id, name, password, grade, student_class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (student_id, name, hashed_password, grade, student_class, security_question, security_answer)
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
        new_password = st.text_input("New Password", type="password")
        
        change_submitted = st.form_submit_button("Change Password")

        if change_submitted:
            if not all([change_id, current_password, new_password]):
                st.error("Please fill in all fields.")
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
    
    reset_id = st.text_input("Enter Student ID to start password reset", key="reset_id_input")

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
                    st.warning("Student ID not found. Please check the ID and try again.")
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
                            st.session_state.teacher_reset_username = None # Clear state
                        else:
                            st.error("Incorrect security answer.")

        return

    # --- TEACHER IS LOGGED IN ---
    teacher = st.session_state.logged_in_teacher
    st.success(f"Welcome, {teacher['username']}!")
    
    st.subheader(f"Enter Metric Scores for Grade {teacher['grade']} {teacher['class']} (0-100)")
    class_students = [s for s in students if s['grade'] == teacher['grade'] and s['student_class'] == teacher['class']]
    
    if not class_students:
        st.info("There are no students registered in your class yet.")
    else:
        # (Metrics form logic remains unchanged)
        with st.form("metrics_form"):
            metric_inputs = {}
            for s in class_students:
                st.markdown(f"**{s['name']} ({s['student_id']})**")
                cols = st.columns(4)
                student_metrics = metrics.get(s['student_id'], {})
                metric_inputs[s['student_id']] = {
                    'academics': cols[0].number_input("Academics", 0, 100, student_metrics.get('academics', 0), key=f"{s['student_id']}_acad"),
                    'discipline': cols[1].number_input("Discipline", 0, 100, student_metrics.get('discipline', 0), key=f"{s['student_id']}_disc"),
                    'clubs': cols[2].number_input("Clubs", 0, 100, student_metrics.get('clubs', 0), key=f"{s['student_id']}_clubs"),
                    'community_service': cols[3].number_input("Community", 0, 100, student_metrics.get('community_service', 0), key=f"{s['student_id']}_comm"),
                    'teacher': cols[0].number_input("Teacher Score", 0, 100, student_metrics.get('teacher', 0), key=f"{s['student_id']}_teach"),
                    'leadership': cols[1].number_input("Leadership", 0, 100, student_metrics.get('leadership', 0), key=f"{s['student_id']}_lead"),
                    'public_speaking': cols[2].number_input("Public Speaking", 0, 100, student_metrics.get('public_speaking', 0), key=f"{s['student_id']}_speak"),
                }
                st.markdown("---")

            if st.form_submit_button("Save All Metric Scores"):
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    for student_id, scores in metric_inputs.items():
                        cursor.execute("""
                            INSERT OR REPLACE INTO metrics (student_id, academics, discipline, clubs, community_service, teacher, leadership, public_speaking)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (student_id, scores['academics'], scores['discipline'], scores['clubs'], scores['community_service'], scores['teacher'], scores['leadership'], scores['public_speaking']))
                    conn.commit()
                st.success("All metric scores have been saved successfully!")
                st.rerun()

    # --- Student Password Management Section ---
    st.markdown("---")
    st.subheader("Change or Reset Student Passwords")
    if not class_students:
        st.info("No students in your class to manage.")
    else:
        st.info("You can set a new password for a student in your class if they forget theirs.")
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
    
    # --- Class Roster Management Section ---
    st.markdown("---")
    st.subheader("Manage Class Roster")
    with st.form("add_student_to_class_form"):
        st.markdown(f"**Assign an Existing Student to Your Class (Grade {teacher['grade']} {teacher['class']})**")
        student_id_to_add = st.text_input("Enter Student ID to find and assign")
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
                        st.success(f"Successfully assigned {student_to_add['name']} ({student_id_to_add}) to your class.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred while assigning the student: {e}")

    if class_students:
        with st.form("remove_student_from_class_form"):
            st.markdown("**Re-assign a Student From Your Current Class**")
            student_options = {f"{s['name']} ({s['student_id']})": s['student_id'] for s in class_students}
            selected_student_display = st.selectbox("Select student to re-assign", options=list(student_options.keys()))
            all_grades = [7, 8, 9]
            all_classes = ['Blue', 'Red', 'Green', 'Yellow', 'Pink', 'Magenta', 'Purple', 'Unassigned']
            new_grade = st.selectbox("Select New Grade", options=all_grades, index=all_grades.index(teacher['grade']))
            new_class = st.selectbox("Select New Class", options=all_classes)
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
                    st.session_state.logged_in_teacher['password'] = hashed_new_password # Update session state
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
    with st.form("add_position_form"):
        new_position_name = st.text_input("New Position Name")
        add_position_submitted = st.form_submit_button("Add Position")
        if add_position_submitted and new_position_name:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("INSERT INTO positions (position_name, candidates_json) VALUES (?, ?)", (new_position_name, json.dumps([])))
                conn.commit()
            st.success(f"Position '{new_position_name}' added.")
            st.rerun()

    st.markdown("---")

    # --- Manage Candidates ---
    st.subheader("Manage Candidates")
    all_positions = list(positions.keys())
    if not all_positions:
        st.warning("No positions created yet. Add a position above.")
    else:
        selected_position = st.selectbox("Select Position to Manage Candidates", all_positions)
        st.write(f"**Current Candidates for {selected_position}:**")
        current_candidates = positions.get(selected_position, [])
        if current_candidates:
            st.table(pd.DataFrame(current_candidates))
        else:
            st.info("No candidates for this position yet.")
        with st.form("manage_candidates_form"):
            candidate_id = st.text_input("Student ID to Add/Remove")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Candidate"):
                    student_to_add = next((s for s in students if s['student_id'] == candidate_id), None)
                    if student_to_add:
                        candidate_info = {'student_id': student_to_add['student_id'], 'name': student_to_add['name']}
                        if candidate_info not in current_candidates:
                            current_candidates.append(candidate_info)
                            with sqlite3.connect(DB_FILE) as conn:
                                conn.execute("UPDATE positions SET candidates_json = ? WHERE position_name = ?", (json.dumps(current_candidates), selected_position))
                                conn.commit()
                            st.success(f"Added {student_to_add['name']} to {selected_position}.")
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
                            conn.execute("UPDATE positions SET candidates_json = ? WHERE position_name = ?", (json.dumps(updated_candidates), selected_position))
                            conn.commit()
                        st.success(f"Removed candidate {candidate_id} from {selected_position}.")
                        st.rerun()
                    else:
                        st.error("Candidate not found in this position.")

    st.markdown("---")

    # --- Manage Teachers ---
    st.subheader("Manage Teachers")
    st.write("**Current Teachers:**")
    st.table(pd.DataFrame(teachers, columns=['username', 'grade', 'class']))
    with st.form("add_teacher_form"):
        st.write("**Add New Teacher**")
        teacher_username = st.text_input("Username")
        teacher_password = st.text_input("Password", type="password")
        teacher_grade = st.selectbox("Grade", [7, 8, 9])
        teacher_class = st.selectbox("Class", ['Blue', 'Red', 'Green', 'Yellow', 'Pink', 'Magenta', 'Purple'])
        security_question = st.text_input("Security Question (e.g., What is your favorite subject?)")
        security_answer = st.text_input("Security Answer")
        if st.form_submit_button("Add Teacher"):
            if not all([teacher_username, teacher_password, security_question, security_answer]):
                st.error("Please fill all fields for the new teacher.")
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
    st.subheader("Manage Weights (Must total 100%)")
    with st.form("weights_form"):
        total_weight = 0
        new_weights = {}
        cols = st.columns(2)
        weight_names = list(weights.keys())
        for i, (name, value) in enumerate(weights.items()):
            with cols[i % 2]:
                new_weights[name] = st.number_input(name.replace('_', ' ').title(), min_value=0, max_value=100, value=value)
                total_weight += new_weights[name]
        st.info(f"**Total Weight:** {total_weight}%")
        if st.form_submit_button("Save Weights"):
            if total_weight != 100:
                st.error("Weights must sum to exactly 100.")
            else:
                with sqlite3.connect(DB_FILE) as conn:
                    for name, value in new_weights.items():
                        conn.execute("UPDATE weights SET value = ? WHERE name = ?", (value, name))
                    conn.commit()
                st.success("Weights updated successfully.")
                st.rerun()

    st.markdown("---")

    # --- Security & Data ---
    st.subheader("Security & Data")
    with st.form("update_pin_form"):
        new_pin = st.text_input("New Admin PIN", type="password")
        if st.form_submit_button("Update PIN"):
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("UPDATE settings SET value = ? WHERE name = 'pin'", (new_pin,))
                conn.commit()
            st.success("PIN updated successfully!")

    votes_df = pd.DataFrame.from_dict(votes, orient='index')
    csv_file = votes_df.to_csv(index=True, header=True)
    st.download_button(label="Export Votes (CSV)", data=csv_file, file_name="algocracy_votes.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("Danger Zone")
    if st.button("Factory Reset (Deletes ALL Data)"):
        if st.checkbox("I am sure I want to delete all students, votes, and positions and reset the system."):
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS students")
                cursor.execute("DROP TABLE IF EXISTS votes")
                cursor.execute("DROP TABLE IF EXISTS positions")
                cursor.execute("DROP TABLE IF EXISTS teachers")
                cursor.execute("DROP TABLE IF EXISTS settings")
                cursor.execute("DROP TABLE IF EXISTS weights")
                cursor.execute("DROP TABLE IF EXISTS metrics")
                init_db() # Re-initialize and seed
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
        with st.form("cast_vote_form"):
            st.subheader("Cast Your Votes")
            selected_votes = {}
            for position, candidates in positions.items():
                candidate_names = [c['name'] for c in candidates]
                if not candidate_names:
                    st.info(f"No candidates for {position} yet.")
                else:
                    selected_candidate = st.selectbox(f"Vote for {position}", [""] + candidate_names, key=position)
                    if selected_candidate:
                        selected_votes[position] = selected_candidate

            if st.form_submit_button("Submit Vote"):
                try:
                    votes_json = json.dumps(selected_votes)
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO votes (voter_id, votes_json) VALUES (?, ?)", (st.session_state.current_voter['student_id'], votes_json))
                        cursor.execute("UPDATE students SET has_voted = 1 WHERE student_id = ?", (st.session_state.current_voter['student_id'],))
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
    
    if settings.get('voting_open') == 'True':
        st.info("Results will be shown here after voting is closed.")
        return

    st.subheader("Final Computed Results")

    for position_name, candidates_list in positions.items():
        st.markdown(f"### Results for {position_name}")
        
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
            candidate_metrics = metrics.get(student_id, {'academics': 0, 'discipline': 0, 'clubs': 0, 'community_service': 0, 'teacher': 0, 'leadership': 0, 'public_speaking': 0})
            final_score = (
                (vote_score * weights.get('student_votes', 0)) +
                (candidate_metrics['academics'] * weights.get('academics', 0)) +
                (candidate_metrics['discipline'] * weights.get('discipline', 0)) +
                (candidate_metrics['clubs'] * weights.get('clubs', 0)) +
                (candidate_metrics['community_service'] * weights.get('community_service', 0)) +
                (candidate_metrics['teacher'] * weights.get('teacher', 0)) +
                (candidate_metrics['leadership'] * weights.get('leadership', 0)) +
                (candidate_metrics['public_speaking'] * weights.get('public_speaking', 0))
            ) / 100.0
            results_data.append({'Candidate': name, 'Vote %': f"{vote_score:.2f}", 'Academics': candidate_metrics['academics'], 'Discipline': candidate_metrics['discipline'], 'Clubs': candidate_metrics['clubs'], 'Comm. Service': candidate_metrics['community_service'], 'Teacher': candidate_metrics['teacher'], 'Public Speaking': candidate_metrics['public_speaking'], 'Leadership': candidate_metrics['leadership'], 'Final Score': final_score})
            
        if not results_data:
            st.info("No votes have been cast for this position yet.")
            continue

        results_df = pd.DataFrame(results_data).sort_values(by='Final Score', ascending=False).reset_index(drop=True)
        display_columns = ['Candidate', 'Final Score', 'Vote %', 'Academics', 'Discipline', 'Leadership', 'Public Speaking', 'Clubs', 'Comm. Service', 'Teacher']
        existing_columns = [col for col in display_columns if col in results_df.columns]
        results_df = results_df[existing_columns]

        if not results_df.empty:
            st.success(f"**Winner: {results_df.iloc[0]['Candidate']}** with a final score of **{results_df.iloc[0]['Final Score']:.2f}**")
            st.dataframe(results_df)


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

    students, teachers, positions, votes, settings, weights, metrics = fetch_data()

    st.sidebar.image("https://images.unsplash.com/photo-1549419137-9d7a2d480371?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)
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