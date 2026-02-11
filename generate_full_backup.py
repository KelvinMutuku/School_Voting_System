import pandas as pd
import json
import secrets
import string
import bcrypt

# --- CONFIGURATION ---
input_filename = 'GRADE 10 SENIOR BOYS_converted.xlsx' # Ensure this matches your file
output_filename = 'full_school_backup.json'
keys_filename = 'access_keys.txt'
DEFAULT_STREAM = 'Red'  # Fallback if class isn't detected
DEFAULT_GRADE = 10      # The grade these teachers/students belong to
STUDENT_DEFAULT_PASSWORD = "123456" # <--- NEW DEFAULT PASSWORD

# --- HELPER: Generate Random Password ---
def generate_password(length=6, digits_only=False):
    if digits_only:
        chars = string.digits
    else:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- 1. LOAD AND CLEAN STUDENT DATA ---
print(f"Reading {input_filename}...")
try:
    # Read first row to detect class name (e.g. "GRADE 10 RED...")
    header_text = pd.read_excel(input_filename, header=None, nrows=1).iloc[0].astype(str).str.cat().upper()
    
    # Find header row for data
    df_raw = pd.read_excel(input_filename, header=None)
    header_row_index = -1
    for i, row in df_raw.head(10).iterrows():
        if row.astype(str).str.contains('ADM', case=False).any():
            header_row_index = i
            break
            
    if header_row_index != -1:
        df = pd.read_excel(input_filename, header=header_row_index)
    else:
        df = pd.read_excel(input_filename)

except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit()

# --- 2. FIX COLUMNS & EXTRACT CLASS ---
df.columns = df.columns.str.strip()
rename_map = {'ADM': 'Adm No.', 'NAMES': 'Student Name'}
df = df.rename(columns=rename_map)

# Detect Class from Header
if 'Class' not in df.columns:
    found_stream = DEFAULT_STREAM
    for color in ["RED", "BLUE", "GREEN", "YELLOW", "PINK", "MAGENTA", "PURPLE"]:
        if color in header_text:
            found_stream = color.capitalize()
            break
    df['Class'] = found_stream

df = df.dropna(subset=['Adm No.'])

# --- 3. GENERATE CREDENTIALS ---
print("Generating credentials...")
admin_pin = generate_password(length=4, digits_only=True)
super_admin_pin = generate_password(length=8, digits_only=True)

# Data Containers
students_export = []
teachers_export = []
metrics_export = {}
teacher_passwords_export = {} # For Teachers only

# A. PROCESS STUDENTS (Default Password: 123456)
# Pre-hash the default password once to save processing time
hashed_default_pwd = bcrypt.hashpw(STUDENT_DEFAULT_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

for index, row in df.iterrows():
    try:
        adm = str(row['Adm No.']).strip()
        name = str(row['Student Name']).strip()
        stream = str(row['Class']).strip()
        
        if not adm or adm.lower() == 'nan': continue

        # Use the pre-hashed default password
        students_export.append({
            "student_id": adm,
            "name": name,
            "password": hashed_default_pwd, # All students get 123456
            "grade": DEFAULT_GRADE,
            "student_class": stream,
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

    except Exception:
        continue

# B. PROCESS TEACHERS (Red, Green, Blue)
target_streams = ['Red', 'Green', 'Blue']

for stream in target_streams:
    # Username format: teacher10red, teacher10green, etc.
    username = f"teacher{DEFAULT_GRADE}{stream.lower()}"
    raw_pw = generate_password(6) # Random password for teachers (safer)
    hashed_pw = bcrypt.hashpw(raw_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    teachers_export.append({
        "username": username,
        "password": hashed_pw,
        "grade": DEFAULT_GRADE,
        "class": stream,
        "security_question": "What is the school motto?",
        "security_answer": "excellence" 
    })
    
    teacher_passwords_export[username] = raw_pw

# --- 4. EXPORT JSON & KEYS ---
backup_data = {
    "students": students_export,
    "teachers": teachers_export,
    "positions": {},
    "votes": {},
    "settings": {
        "pin": admin_pin,
        "voting_open": "True",
        "super_admin_pin": super_admin_pin
    },
    "weights": {
        "student_votes": 30, "academics": 15, "discipline": 10,
        "neatness": 5, "flexibility": 10, "leadership": 10, "public_speaking": 20
    },
    "metrics": metrics_export
}

# Write JSON
with open(output_filename, 'w') as f:
    json.dump(backup_data, f, indent=2)
print(f"✅ JSON Backup saved to: {output_filename}")

# Write Access Keys
with open(keys_filename, 'w') as f:
    f.write("=== ALGOCRACY SYSTEM ACCESS KEYS ===\n")
    f.write(f"SUPER ADMIN PIN: {super_admin_pin}\n")
    f.write(f"ADMIN PIN:       {admin_pin}\n\n")
    
    f.write("--- TEACHER ACCOUNTS ---\n")
    for user, pwd in teacher_passwords_export.items():
        f.write(f"Username: {user:<15} | Password: {pwd}\n")
    
    f.write("\n--- STUDENT PASSWORDS ---\n")
    f.write(f"ALL STUDENTS DEFAULT PASSWORD: {STUDENT_DEFAULT_PASSWORD}\n")
    f.write("(Individual student passwords are no longer listed since they are identical)")

print(f"✅ Access Keys saved to: {keys_filename}")