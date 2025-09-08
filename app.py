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

        # Teacher table - ADDED security fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                grade INTEGER NOT NULL,
                class TEXT NOT NULL,
                security_question TEXT,
                security_answer TEXT
            )
        ''')

        # Position table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                position_name TEXT PRIMARY KEY,
                candidates_json TEXT
            )
        ''')

        # Vote table - Corrected schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                voter_id TEXT,
                position_name TEXT,
                candidate_name TEXT,
                PRIMARY KEY (voter_id, position_name)
            )
        ''')

        # Metrics table - NEW
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                student_id TEXT PRIMARY KEY,
                academics INTEGER,
                discipline INTEGER,
                clubs INTEGER,
                community_service INTEGER,
                teacher_assessment INTEGER,
                leadership INTEGER,
                public_speaking INTEGER
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

        # Seed initial data
        seed_data(conn)

def seed_data(conn):
    """Seeds the database with initial data if tables are empty."""
    cursor = conn.cursor()

    # Seed teachers
    cursor.execute("SELECT COUNT(*) FROM teachers")
    if cursor.fetchone()[0] == 0:
        teachers_data = [
            ('teacher7blue', '1234', 7, 'Blue', 'What is your favorite color?', 'blue'),
            ('teacher7red', '1234', 7, 'Red', 'What is your favorite color?', 'red'),
            ('teacher8blue', '1234', 8, 'Blue', 'What is your favorite color?', 'blue'),
            ('teacher8red', '1234', 8, 'Red', 'What is your favorite color?', 'red'),
            ('teacher9blue', '1234', 9, 'Blue', 'What is your favorite color?', 'blue'),
            ('teacher9red', '1234', 9, 'Red', 'What is your favorite color?', 'red')
        ]
        # Hash passwords before inserting
        hashed_teachers_data = [(u, bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), g, c, sq, sa) for u, p, g, c, sq, sa in teachers_data]
        cursor.executemany("INSERT INTO teachers (username, password, grade, class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)", hashed_teachers_data)
        st.success("Default teachers seeded.")

    # Seed positions and candidates
    cursor.execute("SELECT COUNT(*) FROM positions")
    if cursor.fetchone()[0] == 0:
        positions_data = [
            ('Head Boy', json.dumps([{'student_id': 'KIS-001', 'name': 'John Doe'}, {'student_id': 'KIS-002', 'name': 'Peter Kamau'}])),
            ('Head Girl', json.dumps([{'student_id': 'KIS-003', 'name': 'Mary Jane'}, {'student_id': 'KIS-004', 'name': 'Sarah Wanjiku'}])),
        ]
        cursor.executemany("INSERT INTO positions (position_name, candidates_json) VALUES (?, ?)", positions_data)

    # Seed settings
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (name, value) VALUES (?, ?)", ('pin', '1234'))
        cursor.execute("INSERT INTO settings (name, value) VALUES (?, ?)", ('voting_open', 'True'))

    # Seed weights
    cursor.execute("SELECT COUNT(*) FROM weights")
    if cursor.fetchone()[0] == 0:
        weights_data = [
            ('student_votes', 30), ('academics', 15), ('discipline', 10),
            ('clubs', 10), ('community_service', 5), ('teacher_assessment', 10),
            ('leadership', 10), ('public_speaking', 10)
        ]
        cursor.executemany("INSERT INTO weights (name, value) VALUES (?, ?)", weights_data)
    
    conn.commit()

def fetch_data():
    """Fetches all data from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        students = [dict(row) for row in cursor.execute("SELECT * FROM students").fetchall()]
        teachers = [dict(row) for row in cursor.execute("SELECT * FROM teachers").fetchall()]
        
        positions_raw = cursor.execute("SELECT position_name, candidates_json FROM positions").fetchall()
        positions = {row['position_name']: json.loads(row['candidates_json']) for row in positions_raw}
        
        votes_raw = cursor.execute("SELECT voter_id, position_name, candidate_name FROM votes").fetchall()
        votes = [dict(row) for row in votes_raw]

        settings = {row['name']: row['value'] for row in cursor.execute("SELECT name, value FROM settings").fetchall()}
        weights = {row['name']: row['value'] for row in cursor.execute("SELECT name, value FROM weights").fetchall()}
        metrics = {row['student_id']: dict(row) for row in cursor.execute("SELECT * FROM metrics").fetchall()}

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
    * **Teacher Assessment:** 10%
    * **Leadership:** 10%
    * **Public Speaking:** 10%
    
    ### How it works
    * **Students register with their ID and password, then vote by position.
    * **Teachers record each student's metric scores (0–100).
    * **The system computes Final Score per candidate:
    Final = StudentVotes%×Wsv + Academics%×Wa + Discipline%×Wd + Clubs%×Wc 
    + CommunityService%×Wcs + Teacher%×Wt + Leadership%×Wl + PublicSpeaking%×Wp

Highest Final Score wins each position. Transparent & reproducible.
    """)
    st.image("https://images.unsplash.com/photo-1549419137-9d7a2d480371?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")

def render_registration_page():
    st.header("Student Registration")
    
    tab1, tab2, tab3 = st.tabs(["New Student Registration", "Change Password", "Reset Password"])

    with tab1:
        with st.form("register_form"):
            student_id = st.text_input("Student ID (e.g., KIS-1234)")
            name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            grade = st.selectbox("Grade", [7, 8, 9])
            student_class = st.selectbox("Class", ['Blue', 'Red', 'Green', 'Yellow', 'Pink', 'Magenta', 'Purple'])
            security_question = st.selectbox("Security Question", ["What is your mother's maiden name?", "What is the name of your first pet?", "What city were you born in?"])
            security_answer = st.text_input("Security Answer")
            
            if st.form_submit_button("Register"):
                if not all([student_id, name, password, security_question, security_answer]):
                    st.error("Please fill in all fields.")
                else:
                    try:
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute(
                                "INSERT INTO students (student_id, name, password, grade, student_class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (student_id, name, hashed_password, grade, student_class, security_question, security_answer)
                            )
                        st.success("Student registered successfully!")
                    except sqlite3.IntegrityError:
                        st.error("Student ID already exists.")

    with tab2:
        with st.form("change_password_form"):
            change_id = st.text_input("Student ID")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            if st.form_submit_button("Change Password"):
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
                            st.success("Password changed successfully!")
                        else:
                            st.error("Invalid student ID or current password.")

    with tab3:
        reset_id = st.text_input("Enter Student ID to start password reset", key="reset_id_input")
        if reset_id:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT security_question FROM students WHERE student_id = ?", (reset_id,))
                result = cursor.fetchone()
            if result:
                st.info(f"**Security Question:** {result[0]}")
                with st.form("reset_password_form"):
                    security_answer = st.text_input("Your Security Answer")
                    new_password_reset = st.text_input("New Password (min 6 characters)", type="password", key="new_pass_reset")
                    if st.form_submit_button("Reset Password"):
                        with sqlite3.connect(DB_FILE) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT security_answer FROM students WHERE student_id = ?", (reset_id,))
                            answer_result = cursor.fetchone()
                            if answer_result and answer_result[0].lower() == security_answer.lower():
                                hashed_new_password = bcrypt.hashpw(new_password_reset.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                                cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", (hashed_new_password, reset_id))
                                st.success("Password reset successfully!")
                            else:
                                st.error("Incorrect security answer.")
            else:
                st.warning("Student ID not found.")

def render_teacher_page(teachers, students, metrics):
    st.header("Teacher Panel")
    
    if st.session_state.get('logged_in_teacher'):
        teacher = st.session_state.logged_in_teacher
        st.success(f"Welcome, {teacher['username']}!")

        class_students = [s for s in students if s['grade'] == teacher['grade'] and s['student_class'] == teacher['class']]

        tab1, tab2, tab3 = st.tabs(["Enter Metrics", "Manage Students", "Security"])

        with tab1:
            st.subheader(f"Enter Metrics for Grade {teacher['grade']} {teacher['class']} (0-100)")
            if not class_students:
                st.info("No students found in your class.")
            else:
                metrics_data = []
                for s in class_students:
                    student_metrics = metrics.get(s['student_id'], {})
                    metrics_data.append({
                        'Student ID': s['student_id'],
                        'Name': s['name'],
                        'Academics': student_metrics.get('academics', 0),
                        'Discipline': student_metrics.get('discipline', 0),
                        'Clubs': student_metrics.get('clubs', 0),
                        'Community Service': student_metrics.get('community_service', 0),
                        'Teacher Assessment': student_metrics.get('teacher_assessment', 0),
                        'Leadership': student_metrics.get('leadership', 0),
                        'Public Speaking': student_metrics.get('public_speaking', 0),
                    })
                
                df = pd.DataFrame(metrics_data)
                edited_df = st.data_editor(df, key="metrics_editor", hide_index=True)

                if st.button("Save Metrics"):
                    with sqlite3.connect(DB_FILE) as conn:
                        for _, row in edited_df.iterrows():
                            conn.execute("""
                                INSERT OR REPLACE INTO metrics (student_id, academics, discipline, clubs, community_service, teacher_assessment, leadership, public_speaking)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                row['Student ID'], row['Academics'], row['Discipline'], row['Clubs'],
                                row['Community Service'], row['Teacher Assessment'], row['Leadership'], row['Public Speaking']
                            ))
                    st.success("Metrics saved successfully!")
                    st.rerun()

        with tab2:
            st.subheader("Manage Students in Your Class")
            with st.form("add_student_form"):
                st.write("Add New Student")
                new_student_id = st.text_input("Student ID")
                new_student_name = st.text_input("Student Name")
                if st.form_submit_button("Add Student"):
                    if new_student_id and new_student_name:
                        try:
                            hashed_pw = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode('utf-8')
                            with sqlite3.connect(DB_FILE) as conn:
                                conn.execute(
                                    "INSERT INTO students (student_id, name, password, grade, student_class, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (new_student_id, new_student_name, hashed_pw, teacher['grade'], teacher['class'], "Default Question", "Default Answer")
                                )
                            st.success(f"Student {new_student_name} added.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Student ID already exists.")
                    else:
                        st.error("Please provide both ID and name.")
            st.markdown("---")
            with st.form("remove_student_form"):
                st.write("Remove Student")
                student_ids = [s['student_id'] for s in class_students]
                student_to_remove = st.selectbox("Select Student to Remove", [""] + student_ids)
                if st.form_submit_button("Remove Student", type="primary"):
                    if student_to_remove:
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute("DELETE FROM students WHERE student_id = ?", (student_to_remove,))
                            conn.execute("DELETE FROM metrics WHERE student_id = ?", (student_to_remove,))
                        st.warning(f"Student {student_to_remove} removed.")
                        st.rerun()
                    else:
                        st.error("Please select a student to remove.")

        with tab3:
            st.subheader("Change Password")
            with st.form("teacher_change_password"):
                old_pass = st.text_input("Old Password", type="password")
                new_pass = st.text_input("New Password", type="password")
                if st.form_submit_button("Change Password"):
                    if old_pass and new_pass:
                        if bcrypt.checkpw(old_pass.encode('utf-8'), teacher['password'].encode('utf-8')):
                            hashed_new = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            with sqlite3.connect(DB_FILE) as conn:
                                conn.execute("UPDATE teachers SET password = ? WHERE username = ?", (hashed_new, teacher['username']))
                            st.success("Password updated successfully.")
                            st.session_state.logged_in_teacher['password'] = hashed_new
                        else:
                            st.error("Incorrect old password.")
                    else:
                        st.error("All fields are required.")

            st.subheader("Reset Password")
            with st.form("teacher_reset_password"):
                st.info(f"Your Security Question: **{teacher.get('security_question', 'Not set')}**")
                sec_answer = st.text_input("Security Answer")
                reset_new_pass = st.text_input("New Password", type="password", key="reset_new_pass")
                if st.form_submit_button("Reset Password"):
                    if teacher.get('security_answer') and sec_answer.lower() == teacher['security_answer'].lower():
                        hashed_new = bcrypt.hashpw(reset_new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute("UPDATE teachers SET password = ? WHERE username = ?", (hashed_new, teacher['username']))
                        st.success("Password reset successfully.")
                        st.session_state.logged_in_teacher['password'] = hashed_new
                    else:
                        st.error("Incorrect security answer or no security question set.")

        if st.button("Logout"):
            st.session_state.logged_in_teacher = None
            st.rerun()
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            teacher = next((t for t in teachers if t['username'] == username), None)
            if teacher and bcrypt.checkpw(password.encode('utf-8'), teacher['password'].encode('utf-8')):
                st.session_state.logged_in_teacher = teacher
                st.rerun()
            else:
                st.error("Invalid username or password.")


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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Voting Control", "Positions & Candidates", "Manage Teachers", "Manage Weights", "Security & Data"])

    with tab1:
        st.subheader("Voting Control")
        voting_open_str = settings.get('voting_open', 'True')
        current_voting_status = "Open" if voting_open_str == 'True' else "Closed"
        st.markdown(f"**Current Status:** `{current_voting_status}`")
        if st.button("Toggle Voting Status"):
            new_status = 'False' if voting_open_str == 'True' else 'True'
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("UPDATE settings SET value = ? WHERE name = 'voting_open'", (new_status,))
            st.success("Voting status updated.")
            st.rerun()

    with tab2:
        st.subheader("Positions & Candidates")
        with st.form("add_position_form"):
            new_position_name = st.text_input("New Position Name")
            if st.form_submit_button("Add Position"):
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("INSERT INTO positions (position_name, candidates_json) VALUES (?, ?)", (new_position_name, json.dumps([])))
                st.success(f"Position '{new_position_name}' added.")
                st.rerun()

        st.subheader("Manage Candidates")
        all_positions = list(positions.keys())
        if all_positions:
            selected_position = st.selectbox("Select Position to Manage Candidates", all_positions)
            st.write(f"**Current Candidates for {selected_position}:**")
            current_candidates = positions.get(selected_position, [])
            st.table(pd.DataFrame(current_candidates))
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
                                st.success(f"Added {student_to_add['name']} to {selected_position}.")
                                st.rerun()
                with col2:
                    if st.form_submit_button("Remove Candidate"):
                        updated_candidates = [c for c in current_candidates if c['student_id'] != candidate_id]
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute("UPDATE positions SET candidates_json = ? WHERE position_name = ?", (json.dumps(updated_candidates), selected_position))
                        st.success(f"Removed candidate {candidate_id} from {selected_position}.")
                        st.rerun()

    with tab3:
        st.subheader("Manage Teachers")
        st.table(pd.DataFrame(teachers, columns=['username', 'grade', 'class']))
        with st.form("add_teacher_form"):
            teacher_username = st.text_input("Username")
            teacher_password = st.text_input("Password", type="password")
            teacher_grade = st.selectbox("Grade", [7, 8, 9])
            teacher_class = st.selectbox("Class", ['Blue', 'Red', 'Green', 'Yellow'])
            if st.form_submit_button("Add Teacher"):
                hashed_pw = bcrypt.hashpw(teacher_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("INSERT INTO teachers (username, password, grade, class) VALUES (?, ?, ?, ?)", (teacher_username, hashed_pw, teacher_grade, teacher_class))
                st.success(f"Teacher '{teacher_username}' added.")
                st.rerun()

    with tab4:
        st.subheader("Manage Weights (Must total 100%)")
        with st.form("weights_form"):
            total_weight = 0
            new_weights = {}
            for name, value in weights.items():
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
                    st.success("Weights updated successfully.")
                    st.rerun()

    with tab5:
        st.subheader("Security & Data")
        with st.form("update_pin_form"):
            new_pin = st.text_input("New Admin PIN", type="password")
            if st.form_submit_button("Update PIN"):
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("UPDATE settings SET value = ? WHERE name = 'pin'", (new_pin,))
                st.success("PIN updated successfully!")
    
    if st.button("Logout Admin"):
        st.session_state.logged_in_admin = False
        st.rerun()


def render_voting_page(students, positions, settings):
    st.header("Vote")
    if settings.get('voting_open') != 'True':
        st.warning("Voting is currently closed.")
        return

    if 'current_voter' not in st.session_state:
        st.session_state.current_voter = None

    if not st.session_state.current_voter:
        with st.form("voter_auth_form"):
            voter_id = st.text_input("Enter your Student ID")
            password = st.text_input("Enter your Password", type="password")
            if st.form_submit_button("Authenticate"):
                student = next((s for s in students if s['student_id'] == voter_id), None)
                if student and bcrypt.checkpw(password.encode('utf-8'), student['password'].encode('utf-8')):
                    if student['has_voted']:
                        st.warning("You have already voted.")
                    else:
                        st.session_state.current_voter = student
                        st.rerun()
                else:
                    st.error("Invalid ID or password.")
    else:
        voter = st.session_state.current_voter
        st.success(f"Welcome, {voter['name']}! Cast your votes below.")
        with st.form("cast_vote_form"):
            votes_to_cast = {}
            for position, candidates in positions.items():
                candidate_names = [c['name'] for c in candidates]
                if candidate_names:
                    selected_candidate = st.selectbox(f"Vote for {position}", [""] + candidate_names, key=position)
                    if selected_candidate:
                        votes_to_cast[position] = selected_candidate
            
            if st.form_submit_button("Submit Votes"):
                with sqlite3.connect(DB_FILE) as conn:
                    for position, candidate in votes_to_cast.items():
                        conn.execute("INSERT INTO votes (voter_id, position_name, candidate_name) VALUES (?, ?, ?)", (voter['student_id'], position, candidate))
                    conn.execute("UPDATE students SET has_voted = 1 WHERE student_id = ?", (voter['student_id'],))
                st.success("Your votes have been submitted!")
                st.session_state.current_voter = None
                st.rerun()

def render_results_page(positions, votes, settings, metrics, weights):
    st.header("Election Results")
    st.markdown("---")
    
    if settings.get('voting_open') == 'True':
        st.info("Results will be shown here after voting is closed.")
        return

    st.subheader("Final Tally")
    
    vote_counts = {}
    total_votes_per_position = {}
    for vote in votes:
        pos = vote['position_name']
        cand = vote['candidate_name']
        vote_counts.setdefault(pos, {}).setdefault(cand, 0)
        vote_counts[pos][cand] += 1
        total_votes_per_position[pos] = total_votes_per_position.get(pos, 0) + 1

    results_data = []
    for pos, candidates in positions.items():
        for cand_info in candidates:
            cand_id = cand_info['student_id']
            cand_name = cand_info['name']
            
            total_pos_votes = total_votes_per_position.get(pos, 0)
            cand_votes = vote_counts.get(pos, {}).get(cand_name, 0)
            vote_score = (cand_votes / total_pos_votes * 100) if total_pos_votes > 0 else 0
            
            cand_metrics = metrics.get(cand_id, {})
            
            final_score = (
                (vote_score * weights['student_votes']) +
                (cand_metrics.get('academics', 0) * weights['academics']) +
                (cand_metrics.get('discipline', 0) * weights['discipline']) +
                (cand_metrics.get('clubs', 0) * weights['clubs']) +
                (cand_metrics.get('community_service', 0) * weights['community_service']) +
                (cand_metrics.get('teacher_assessment', 0) * weights['teacher_assessment']) +
                (cand_metrics.get('leadership', 0) * weights['leadership']) +
                (cand_metrics.get('public_speaking', 0) * weights['public_speaking'])
            ) / 100
            
            results_data.append({
                "Position": pos,
                "Candidate": cand_name,
                "Vote %": f"{vote_score:.1f}",
                "Final Score": f"{final_score:.2f}",
                **{k.replace('_', ' ').title(): v for k, v in cand_metrics.items() if k != 'student_id'}
            })

    if results_data:
        df = pd.DataFrame(results_data)
        for pos in df['Position'].unique():
            st.subheader(pos)
            pos_df = df[df['Position'] == pos].sort_values(by='Final Score', ascending=False).reset_index(drop=True)
            st.dataframe(pos_df.drop('Position', axis=1).set_index('Candidate'))

# --- Main Application Logic ---
if __name__ == "__main__":
    st.set_page_config(page_title="KITENGELA INTERNATIONAL SCHOOL JSS Algocracy Elections", layout="wide")
    
    init_db()

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'register'
    if 'logged_in_teacher' not in st.session_state:
        st.session_state.logged_in_teacher = None
    if 'logged_in_admin' not in st.session_state:
        st.session_state.logged_in_admin = False
    if 'current_voter' not in st.session_state:
        st.session_state.current_voter = None

    students, teachers, positions, votes, settings, weights, metrics = fetch_data()

    st.sidebar.image("https://images.unsplash.com/photo-1549419137-9d7a2d480371?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)
    st.sidebar.title("KISC JSS Algocracy Elections")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Register"):
        st.session_state.current_page = 'register'
    if st.sidebar.button("About"):
        st.session_state.current_page = 'about'
    if st.sidebar.button("Vote"):
        st.session_state.current_page = 'vote'
    if st.sidebar.button("Results"):
        st.session_state.current_page = 'results'
    if st.sidebar.button("Teacher"):
        st.session_state.current_page = 'teacher'
    if st.sidebar.button("Admin"):
        st.session_state.current_page = 'admin'

    if st.session_state.current_page == 'register':
        render_registration_page()
    elif st.session_state.current_page == 'about':
        render_about_page()
    elif st.session_state.current_page == 'vote':
        render_voting_page(students, positions, settings)
    elif st.session_state.current_page == 'results':
        render_results_page(positions, votes, settings, metrics, weights)
    elif st.session_state.current_page == 'teacher':
        render_teacher_page(teachers, students, metrics)
    elif st.session_state.current_page == 'admin':
        render_admin_page(settings, students, positions, votes, teachers, weights)