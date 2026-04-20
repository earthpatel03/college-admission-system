import mysql.connector
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# 🔗 DB CONNECTION
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1111",
    database="college_db"
)
cursor = conn.cursor()

# 🔐 ADMIN LOGIN
def admin_login():
    user = input("Username: ")
    pwd = input("Password: ")

    cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (user, pwd))
    if cursor.fetchone():
        print("✅ Login Successful")
        return True
    else:
        print("❌ Invalid Login")
        return False

# ➕ ADD STUDENT
def add_student():
    name = input("Name: ")
    marks = float(input("Marks: "))
    category = input("Category: ")

    cursor.execute("INSERT INTO students (name, marks, category) VALUES (%s,%s,%s)",
                   (name, marks, category))
    conn.commit()

# ➕ ADD COURSE
def add_course():
    cname = input("Course Name: ")
    seats = int(input("Seats: "))
    min_marks = float(input("Min Marks: "))

    cursor.execute("INSERT INTO courses VALUES (NULL,%s,%s,%s,%s)",
                   (cname, seats, seats, min_marks))
    conn.commit()

# 🎯 ADD PREFERENCES
def add_preferences():
    sid = int(input("Student ID: "))
    n = int(input("Number of preferences: "))

    for i in range(1, n+1):
        cid = int(input(f"Course ID {i}: "))
        cursor.execute("INSERT INTO preferences VALUES (NULL,%s,%s,%s)",
                       (sid, cid, i))
    conn.commit()

# 🧠 ALLOCATION (MULTI-ROUND)
def allocate(round_no):
    cursor.execute("SELECT * FROM students ORDER BY marks DESC")
    students = cursor.fetchall()

    for s in students:
        sid, name, marks, cat = s

        # Skip already allocated
        cursor.execute("SELECT * FROM allocations WHERE student_id=%s", (sid,))
        if cursor.fetchone():
            continue

        cursor.execute("""
            SELECT p.course_id, c.available_seats, c.min_marks
            FROM preferences p
            JOIN courses c ON p.course_id=c.id
            WHERE p.student_id=%s
            ORDER BY p.preference_order
        """, (sid,))

        for cid, seats, min_marks in cursor.fetchall():
            if seats > 0 and marks >= min_marks:

                cursor.execute("INSERT INTO allocations VALUES (NULL,%s,%s,%s)",
                               (sid, cid, round_no))

                cursor.execute("UPDATE courses SET available_seats=available_seats-1 WHERE id=%s",
                               (cid,))
                conn.commit()

                print(f"🎯 {name} allocated to course {cid} in round {round_no}")
                break

# 📊 CUTOFF CALCULATION
def cutoff():
    cursor.execute("""
        SELECT c.course_name, MIN(s.marks)
        FROM allocations a
        JOIN students s ON a.student_id=s.id
        JOIN courses c ON a.course_id=c.id
        GROUP BY c.course_name
    """)

    print("\n📊 Cutoff List:")
    for course, cut in cursor.fetchall():
        print(f"{course} → {cut}")

# 🧾 PDF GENERATOR
def generate_pdf():
    sid = int(input("Enter student ID: "))

    cursor.execute("""
        SELECT s.name, c.course_name
        FROM allocations a
        JOIN students s ON a.student_id=s.id
        JOIN courses c ON a.course_id=c.id
        WHERE s.id=%s
    """, (sid,))

    data = cursor.fetchone()

    if not data:
        print("❌ No allocation found")
        return

    name, course = data

    doc = SimpleDocTemplate(f"{name}_admission.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("Admission Confirmed", styles['Title']))
    content.append(Paragraph(f"Name: {name}", styles['Normal']))
    content.append(Paragraph(f"Course: {course}", styles['Normal']))

    doc.build(content)
    print("✅ PDF Generated")

# 📈 EXPORT CSV
def export_csv():
    df = pd.read_sql("""
        SELECT s.name, s.marks, s.category, c.course_name, a.round_no
        FROM allocations a
        JOIN students s ON a.student_id=s.id
        JOIN courses c ON a.course_id=c.id
    """, conn)

    df.to_csv("admissions.csv", index=False)
    print("✅ CSV Exported")

# 📋 SHOW RESULTS
def show_results():
    cursor.execute("""
        SELECT s.name, c.course_name, a.round_no
        FROM allocations a
        JOIN students s ON a.student_id=s.id
        JOIN courses c ON a.course_id=c.id
    """)

    print("\n📋 Results:")
    for r in cursor.fetchall():
        print(f"{r[0]} → {r[1]} (Round {r[2]})")

# 📌 MAIN MENU
def menu():
    if not admin_login():
        return

    while True:
        print("\n===== MENU =====")
        print("1. Add Student")
        print("2. Add Course")
        print("3. Add Preferences")
        print("4. Run Allocation Round")
        print("5. Show Results")
        print("6. Cutoff")
        print("7. Generate PDF")
        print("8. Export CSV")
        print("9. Exit")

        ch = input("Choice: ")

        if ch == "1":
            add_student()
        elif ch == "2":
            add_course()
        elif ch == "3":
            add_preferences()
        elif ch == "4":
            r = int(input("Enter round number: "))
            allocate(r)
        elif ch == "5":
            show_results()
        elif ch == "6":
            cutoff()
        elif ch == "7":
            generate_pdf()
        elif ch == "8":
            export_csv()
        elif ch == "9":
            break
        else:
            print("❌ Invalid choice")

menu()