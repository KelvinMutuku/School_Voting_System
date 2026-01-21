import pandas as pd
import json
import bcrypt

# --- CONFIGURATION ---
input_file = 'jss.xlsx'
student_default_pass = "123456"
teacher_default_pass = "teacher123"

# 1. Load the Data
try:
    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)
    df.columns = df.columns.str.strip()
    
    required_columns = ['Adm No.', 'Student Name', 'Class']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"File is missing one of these columns: {required_columns}")

    # 2. Setup Security
    print("Generating password hashes...")
    student_hash = bcrypt.hashpw(student_default_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    teacher_hash = bcrypt.hashpw(teacher_default_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    students_list = []
    grade_stream_pairs = set()
    grades_found = set()

    # 3. Process Students
    print("Processing students...")
    for index, row in df.iterrows():
        raw_class = str(row['Class']).strip()
        student_id = str(row['Adm No.']).strip()
        name = str(row['Student Name']).strip()
        
        grade = 0
        stream = "Unknown"
        parts = raw_class.split()
        
        if len(parts) >= 3 and parts[0].lower() == 'grade':
            try:
                grade = int(parts[1])
                stream = " ".join(parts[2:]).title() 
                grade_stream_pairs.add((grade, stream))
                grades_found.add(grade)
            except ValueError:
                pass

        students_list.append({
            "student_id": student_id,
            "name": name,
            "password": student_hash,
            "grade": grade,
            "student_class": stream,
            "gender": "Unknown", 
            "security_question": "What is your favorite color?",
            "security_answer": "blue",
            "has_voted": False
        })

    # 4. Generate Positions
    print("Generating positions...")
    positions = {}
    
    # --- A) School-Wide Positions (Grade 0) ---
    school_wide_positions = [
        "School President", 
        "Deputy President",
        "C.S Dormitory (Boys)",
        "C.S Dormitory (Girls)",
        "C.S Games and Sports (Boys)",
        "C.S Games and Sports (Girls)",
        "C.S Clubs and Societies (Boys)",
        "C.S Clubs and Societies (Girls)",
        "C.S Dining Hall (Boys)",
        "C.S Dining Hall (Girls)",
        "C.S Entertainment (Boys)",
        "C.S Entertainment (Girls)",
        "C.S Sanitation (Boys)",
        "C.S Sanitation (Girls)",
        "C.S ENVIRONMENTAL SAFETY AND GOVERNANCE (ESG)",
        "C.S  SPIRITUAL WELFARE (Boys)",
        "C.S  SPIRITUAL WELFARE (Girls)",
        "Timekeeper (Block B)", 
        "Timekeeper (Block C)"
    ]

    for pos in school_wide_positions:
        positions[pos] = {"grade": 0, "student_class": None, "candidates": []}

    # --- B) Grade-Specific Positions (Governor, Senator, Girl Rep) ---
    # These are voted on by everyone in that specific Grade (regardless of stream)
    for grade in sorted(list(grades_found)):
        # Governor
        positions[f"Grade {grade} Governor"] = {
            "grade": grade, "student_class": None, "candidates": []
        }
        # Senator
        positions[f"Grade {grade} Senator"] = {
            "grade": grade, "student_class": None, "candidates": []
        }
        # Girl Representative (Moved here so it is per Grade, not Stream)
        positions[f"Grade {grade} Girl Representative"] = {
            "grade": grade, "student_class": None, "candidates": []
        }

    # --- C) Stream-Specific Positions (Prefect Only) ---
    teachers_list = []
    for grade, stream in sorted(list(grade_stream_pairs)):
        # Prefect (Still per stream)
        positions[f"Grade {grade} {stream} Prefect"] = {
            "grade": grade, "student_class": stream, "candidates": []
        }

        # Teacher Account
        clean_stream = stream.lower().replace(" ", "")
        username = f"teacher{grade}{clean_stream}"
        teachers_list.append({
            "username": username,
            "password": teacher_hash,
            "grade": grade,
            "class": stream,
            "security_question": "What is your favorite color?",
            "security_answer": "blue"
        })

    # 5. Output
    backup_data = {
        "students": students_list,
        "teachers": teachers_list, 
        "positions": positions,
        "votes": {},
        "settings": {"pin": "1234", "voting_open": "True"},
        "weights": {
            "student_votes": 30, "academics": 15, "discipline": 10,
            "clubs": 10, "community_service": 5, "teacher": 10,
            "leadership": 10, "public_speaking": 10
        },
        "metrics": {}
    }

    output_filename = 'full_school_backup.json'
    with open(output_filename, 'w') as f:
        json.dump(backup_data, f, indent=2)
        
    print(f"Success! Created '{output_filename}'")
    print(f" - Students: {len(students_list)}")
    print(f" - Teachers: {len(teachers_list)}")
    print(f" - Positions: {len(positions)}")

except Exception as e:
    print(f"An error occurred: {e}")