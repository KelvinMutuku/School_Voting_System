import pandas as pd
import json
import bcrypt
import secrets
import string

# --- CONFIGURATION ---
input_file = 'jss.xlsx'

# --- HELPER: Generate Random Password ---
def generate_password(length=8, digits_only=False):
    if digits_only:
        chars = string.digits
    else:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# 1. Load the Data
try:
    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)
    df.columns = df.columns.str.strip()
    
    required_columns = ['Adm No.', 'Student Name', 'Class']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"File is missing one of these columns: {required_columns}")

    # --- 2. Setup Security & Passwords ---
    print("Generating unique credentials...")
    
    # A. Admin & Super Admin Keys (Randomly Generated)
    admin_pin = generate_password(length=6, digits_only=True)
    super_admin_pin = generate_password(length=8, digits_only=False)
    
    # Store plain text keys for export
    keys_export = {
        "ADMIN_ACCESS": {
            "Admin PIN": admin_pin,
            "Super Admin PIN": super_admin_pin
        },
        "TEACHER_PASSWORDS": {},
        "STUDENT_STREAM_PASSWORDS": {}
    }

    students_list = []
    grade_stream_pairs = set()
    grades_found = set()
    
    # Pre-scan for streams to generate passwords
    print("Analyzing streams...")
    stream_passwords = {} # Map (grade, stream) -> (plaintext, hash)
    
    for index, row in df.iterrows():
        raw_class = str(row['Class']).strip()
        parts = raw_class.split()
        if len(parts) >= 3 and parts[0].lower() == 'grade':
            try:
                g = int(parts[1])
                s = " ".join(parts[2:]).title()
                if (g, s) not in stream_passwords:
                    # --- PASSWORD SET TO 123456 ---
                    pw = "123456"
                    pw_hash = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    stream_passwords[(g, s)] = (pw, pw_hash)
                    
                    # Add to export list
                    keys_export["STUDENT_STREAM_PASSWORDS"][f"Grade {g} {s}"] = pw
            except ValueError:
                pass

    # 3. Process Students
    print("Processing students...")
    for index, row in df.iterrows():
        raw_class = str(row['Class']).strip()
        student_id = str(row['Adm No.']).strip()
        name = str(row['Student Name']).strip()
        
        grade = 0
        stream = "Unknown"
        password_hash = "" # Default if class not found
        
        parts = raw_class.split()
        
        if len(parts) >= 3 and parts[0].lower() == 'grade':
            try:
                grade = int(parts[1])
                stream = " ".join(parts[2:]).title() 
                grade_stream_pairs.add((grade, stream))
                grades_found.add(grade)
                
                # Get the specific hash for this stream
                if (grade, stream) in stream_passwords:
                    password_hash = stream_passwords[(grade, stream)][1]
                else:
                    # Fallback
                    fallback_pw = "123456"
                    password_hash = bcrypt.hashpw(fallback_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            except ValueError:
                pass

        students_list.append({
            "student_id": student_id,
            "name": name,
            "password": password_hash,
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
    # UPDATE: Merged President & Deputy
    school_wide_positions = [
        "School President & Deputy President", 
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

    # --- B) Grade-Specific Positions ---
    for grade in sorted(list(grades_found)):
        positions[f"Grade {grade} Governor"] = {"grade": grade, "student_class": None, "candidates": []}
        positions[f"Grade {grade} Senator"] = {"grade": grade, "student_class": None, "candidates": []}
        positions[f"Grade {grade} Girl Representative"] = {"grade": grade, "student_class": None, "candidates": []}

    # --- C) Stream-Specific Positions & Teachers ---
    teachers_list = []
    for grade, stream in sorted(list(grade_stream_pairs)):
        # Prefect
        positions[f"Grade {grade} {stream} Prefect"] = {
            "grade": grade, "student_class": stream, "candidates": []
        }

        # Teacher Account (Unique Random Password)
        clean_stream = stream.lower().replace(" ", "")
        username = f"teacher{grade}{clean_stream}"
        
        # Generate unique password for teacher
        t_pass = generate_password(length=8)
        t_hash = bcrypt.hashpw(t_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Save to export
        keys_export["TEACHER_PASSWORDS"][f"{username} (Grade {grade} {stream})"] = t_pass
        
        teachers_list.append({
            "username": username,
            "password": t_hash,
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
        "settings": {
            "pin": admin_pin, 
            "super_admin_pin": super_admin_pin,
            "voting_open": "True"
        },
        "weights": {
            "student_votes": 30, "academics": 15, "discipline": 10,
            "community_service": 5,
            "leadership": 10, "public_speaking": 30
        },
        "metrics": {}
    }

    output_filename = 'full_school_backup.json'
    keys_filename = 'access_keys.txt'
    
    # Write JSON Backup
    with open(output_filename, 'w') as f:
        json.dump(backup_data, f, indent=2)

    # Write Keys File
    with open(keys_filename, 'w') as f:
        f.write("=== ALGOCRACY SYSTEM ACCESS KEYS ===\n")
        f.write("DO NOT SHARE THIS FILE WITH UNAUTHORIZED USERS\n\n")
        
        f.write("--- 1. ADMIN ACCESS ---\n")
        for k, v in keys_export["ADMIN_ACCESS"].items():
            f.write(f"{k}: {v}\n")
        
        f.write("\n--- 2. STUDENT PASSWORDS ---\n")
        f.write("(Same password for all students: 123456)\n")
        for k, v in sorted(keys_export["STUDENT_STREAM_PASSWORDS"].items()):
            f.write(f"{k}: {v}\n")
            
        f.write("\n--- 3. TEACHER PASSWORDS ---\n")
        for k, v in sorted(keys_export["TEACHER_PASSWORDS"].items()):
            f.write(f"{k}: {v}\n")
            
    print(f"Success! Created '{output_filename}' (Database)")
    print(f"Success! Created '{keys_filename}' (READ ME - Contains Passwords)")
    print(f" - Students: {len(students_list)}")
    print(f" - Teachers: {len(teachers_list)}")

except Exception as e:
    print(f"An error occurred: {e}")