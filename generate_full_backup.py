import pandas as pd
import json
import secrets
import string
import bcrypt
import glob
import os
import re

# --- CONFIGURATION ---
input_folder = 'kisc-athi-river' 
output_filename = 'full_school_backup.json'
keys_filename = 'access_keys.txt'
STUDENT_DEFAULT_PASSWORD = "123456"

def generate_password(length=6, digits_only=False):
    chars = string.digits if digits_only else string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

students_export = []
teachers_export = []
metrics_export = {}
teacher_passwords_export = {}
processed_classes = set() 

hashed_default_pwd = bcrypt.hashpw(STUDENT_DEFAULT_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

excel_files = glob.glob(os.path.join(input_folder, "*.xlsx"))

if not excel_files:
    print(f"No Excel files found in '{input_folder}'.")
    exit()

for file_path in excel_files:
    file_name = os.path.basename(file_path)
    print(f"Processing: {file_name}...")
    
    try:
        # Load the file
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        
        # Standardize column names based on your file: 'Student Name', 'Reg No', 'Stream'
        df = df.rename(columns={
            'Reg No': 'Adm No.', 
            'ADM': 'Adm No.',
            'Student Name': 'Student Name',
            'NAMES': 'Student Name'
        })

        for _, row in df.iterrows():
            adm = str(row.get('Adm No.', '')).strip()
            name = str(row.get('Student Name', '')).strip()
            stream_val = str(row.get('Stream', '')).upper()
            
            if not adm or adm.lower() == 'nan' or name.lower() == 'nan': 
                continue

            # --- NEW LOGIC: Extract Grade and Stream from the 'Stream' column ---
            # Example: "GRADE 1 BLUE" -> Grade: 1, Stream: Blue
            found_grade = "Unknown"
            found_stream = ""
            
            grade_match = re.search(r'GRADE\s*(\d+)', stream_val)
            if grade_match:
                found_grade = int(grade_match.group(1))
            
            # Check for colors in the stream string
            for color in ["RED", "BLUE", "GREEN", "YELLOW", "PINK", "MAGENTA", "PURPLE", "ORANGE", "WHITE"]:
                if color in stream_val:
                    found_stream = color.capitalize()
                    break

            processed_classes.add((found_grade, found_stream))

            students_export.append({
                "student_id": adm,
                "name": name,
                "password": hashed_default_pwd,
                "grade": found_grade,
                "student_class": found_stream,
                "gender": "Male",
                "security_question": "What is your favorite color?",
                "security_answer": "blue",
                "has_voted": 0
            })
            
            metrics_export[adm] = {
                "academics": 0, "discipline": 0, "neatness": 0, 
                "flexibility": 0, "leadership": 0, "public_speaking": 0, 
                "locked": 0
            }

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# --- TEACHER GENERATION ---
for grade, stream in processed_classes:
    stream_suffix = stream.lower() if stream else "general"
    username = f"teacher{grade}{stream_suffix}"
    raw_pw = generate_password(6)
    hashed_pw = bcrypt.hashpw(raw_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    teachers_export.append({
        "username": username,
        "password": hashed_pw,
        "grade": grade,
        "class": stream,
        "security_question": "What is the school motto?",
        "security_answer": "excellence" 
    })
    teacher_passwords_export[username] = raw_pw

# --- EXPORT ---
admin_pin = generate_password(4, True)
super_admin_pin = generate_password(8, True)

backup_data = {
    "students": students_export,
    "teachers": teachers_export,
    "positions": {}, 
    "votes": {},
    "weights": {},
    "settings": {"pin": admin_pin, "voting_open": "True", "super_admin_pin": super_admin_pin},
    "metrics": metrics_export
}

with open(output_filename, 'w') as f:
    json.dump(backup_data, f, indent=2)

with open(keys_filename, 'w') as f:
    f.write(f"SUPER ADMIN PIN: {super_admin_pin}\nADMIN PIN: {admin_pin}\n\n--- TEACHERS ---\n")
    for user, pwd in teacher_passwords_export.items():
        f.write(f"{user}: {pwd}\n")

print(f"✅ Success! Generated data for {len(students_export)} students.")