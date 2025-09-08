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
                class TEXT NOT NULL
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

        # Seed initial data
        seed_data(conn)

def seed_data(conn):
    """Seeds the database with initial data if tables are empty."""
    cursor = conn.cursor()

    # Seed teachers
    cursor.execute("SELECT COUNT(*) FROM teachers")
    if cursor.fetchone()[0] == 0:
        teachers_data = [
            ('teacher7blue', '1234', 7, 'Blue'), ('teacher7red', '1234', 7, 'Red'),
            ('teacher8blue', '1234', 8, 'Blue'), ('teacher8red', '1234', 8, 'Red'),
            ('teacher9blue', '1234', 9, 'Blue'), ('teacher9red', '1234', 9, 'Red')
        ]
        cursor.executemany("INSERT INTO teachers (username, password, grade, class) VALUES (?, ?, ?, ?)", teachers_data)
        st.success("Default teachers seeded.")

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
    
    conn.commit()

def fetch_data():
    """Fetches all data from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Fetch students
        cursor.execute("SELECT student_id, name, password, grade, student_class, security_question, security_answer, has_voted FROM students")
        students = [{'student_id': row[0], 'name': row[1], 'password': row[2], 'grade': row[3], 'student_class': row[4], 'security_question': row[5], 'security_answer': row[6], 'has_voted': bool(row[7])} for row in cursor.fetchall()]

        # Fetch teachers
        cursor.execute("SELECT username, password, grade, class FROM teachers")
        teachers = [{'username': row[0], 'password': row[1], 'grade': row[2], 'class': row[3]} for row in cursor.fetchall()]

        # Fetch positions
        cursor.execute("SELECT position_name, candidates_json FROM positions")
        positions = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

        # Fetch votes
        cursor.execute("SELECT voter_id, votes_json FROM votes")
        votes = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

        # Fetch settings
        cursor.execute("SELECT name, value FROM settings")
        settings = {row[0]: row[1] for row in cursor.fetchall()}

    return students, teachers, positions, votes, settings

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
                    hashed_password = bcrypt.hash(password, 10).decode('utf-8')
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
                        hashed_new_password = bcrypt.hash(new_password, 10).decode('utf-8')
                        cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", (hashed_new_password, change_id))
                        conn.commit()
                        st.success("Password changed successfully!")
                    else:
                        st.error("Invalid student ID or current password.")

    st.markdown("---")
    st.subheader("Reset Password")
    with st.form("reset_password_form"):
        reset_id = st.text_input("Student ID", key="reset_id_input")
        
        if reset_id:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT security_question FROM students WHERE student_id = ?", (reset_id,))
                result = cursor.fetchone()
                
                if result:
                    st.info(f"Your security question is: **{result[0]}**")
                    security_answer = st.text_input("Your Answer", key="reset_answer_input")
                    new_password = st.text_input("New Password", type="password", key="reset_new_password_input")
                    
                    reset_submitted = st.form_submit_button("Reset Password")

                    if reset_submitted:
                        cursor.execute("SELECT security_answer FROM students WHERE student_id = ?", (reset_id,))
                        answer_result = cursor.fetchone()
                        
                        if answer_result and answer_result[0].lower() == security_answer.lower():
                            hashed_new_password = bcrypt.hash(new_password, 10).decode('utf-8')
                            cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", (hashed_new_password, reset_id))
                            conn.commit()
                            st.success("Password reset successfully!")
                        else:
                            st.error("Incorrect security answer.")
                else:
                    st.error("Student ID not found.")


def render_teacher_page(teachers, students):
    st.header("Teacher Login")
    
    if st.session_state.get('logged_in_teacher'):
        teacher = st.session_state.logged_in_teacher
        st.success(f"Welcome, {teacher['username']}!")
        
        st.subheader(f"Students in Grade {teacher['grade']} {teacher['class']}")
        class_students = [s for s in students if s['grade'] == teacher['grade'] and s['student_class'] == teacher['class']]
        
        df = pd.DataFrame(class_students, columns=['student_id', 'name', 'has_voted'])
        st.table(df)

        if st.button("Logout"):
            st.session_state.logged_in_teacher = None
            st.rerun()
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            teacher = next((t for t in teachers if t['username'] == username and t['password'] == password), None)
            if teacher:
                st.session_state.logged_in_teacher = teacher
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

def render_admin_page(settings, students, votes):
    st.header("Admin Panel")
    
    if st.session_state.get('logged_in_admin'):
        st.success("Admin access granted.")
        
        # Use .get() to safely access the key with a default value
        voting_open_str = settings.get('voting_open', 'True')
        current_voting_status = "Open" if voting_open_str == 'True' else "Closed"
        
        st.subheader("Manage Voting")
        st.markdown(f"**Current Status:** `{current_voting_status}`")
        if st.button("Toggle Voting Status"):
            new_status = 'False' if voting_open_str == 'True' else 'True'
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("UPDATE settings SET value = ? WHERE name = 'voting_open'", (new_status,))
                conn.commit()
            st.success("Voting status updated.")
            st.rerun()

        st.subheader("Update Admin PIN")
        with st.form("update_pin_form"):
            new_pin = st.text_input("New PIN", type="password")
            submitted = st.form_submit_button("Update PIN")
            if submitted:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("UPDATE settings SET value = ? WHERE name = 'pin'", (new_pin,))
                    conn.commit()
                st.success("PIN updated successfully!")
                st.rerun()
                
        st.subheader("System Management")
        
        votes_df = pd.DataFrame.from_dict(votes, orient='index')
        csv_file = votes_df.to_csv(index=True, header=True)
        st.download_button(
            label="Export Votes (CSV)",
            data=csv_file,
            file_name="algocracy_votes.csv",
            mime="text/csv",
        )

        if st.button("Reset System (DANGER ZONE)", help="This will delete all student data and votes."):
            if st.checkbox("Confirm Reset"):
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM students")
                    cursor.execute("DELETE FROM votes")
                    conn.commit()
                st.success("System reset successfully.")
                st.rerun()

        if st.button("Logout"):
            st.session_state.logged_in_admin = False
            st.rerun()

    else:
        pin = st.text_input("Enter Admin PIN", type="password")
        if st.button("Login"):
            if pin == settings.get('pin'):
                st.session_state.logged_in_admin = True
                st.rerun()
            else:
                st.error("Invalid PIN.")

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

def render_results_page(positions, votes, settings):
    st.header("Election Results")
    st.markdown("---")
    
    if settings.get('voting_open') == 'True':
        st.info("Results will be shown here after voting is closed.")
    else:
        st.subheader("Final Tally")
        
        # Calculate votes for each candidate
        vote_counts = {pos: {c['name']: 0 for c in candidates} for pos, candidates in positions.items()}
        
        for voter, voter_votes in votes.items():
            for position, candidate in voter_votes.items():
                if position in vote_counts and candidate in vote_counts[position]:
                    vote_counts[position][candidate] += 1
        
        # Display results
        for position, candidates in vote_counts.items():
            st.subheader(f"Results for {position}")
            if not candidates:
                st.info("No votes cast for this position.")
            else:
                df = pd.DataFrame(candidates.items(), columns=['Candidate', 'Votes'])
                df = df.sort_values(by='Votes', ascending=False)
                st.dataframe(df.set_index('Candidate'))

# --- Main Application Logic ---
if __name__ == "__main__":
    init_db()
    
    # Initialize session state for navigation and login
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'register'
    if 'logged_in_teacher' not in st.session_state:
        st.session_state.logged_in_teacher = None
    if 'logged_in_admin' not in st.session_state:
        st.session_state.logged_in_admin = False
    if 'current_voter' not in st.session_state:
        st.session_state.current_voter = None

    students, teachers, positions, votes, settings = fetch_data()

    # Sidebar for navigation
    st.sidebar.image("https://images.unsplash.com/photo-1549419137-9d7a2d480371?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_column_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    
    pages = {
        "Register": 'register',
        "About": 'about',
        "Vote": 'vote',
        "Results": 'results',
        "Teacher": 'teacher',
        "Admin": 'admin'
    }

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

    # Display the current page based on session state
    if st.session_state.current_page == 'register':
        render_registration_page()
    elif st.session_state.current_page == 'about':
        render_about_page()
    elif st.session_state.current_page == 'vote':
        render_voting_page(students, positions, settings)
    elif st.session_state.current_page == 'results':
        render_results_page(positions, votes, settings)
    elif st.session_state.current_page == 'teacher':
        render_teacher_page(teachers, students)
    elif st.session_state.current_page == 'admin':
        render_admin_page(settings, students, votes)