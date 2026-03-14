import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'abhijeet',
    'database': 'TRACKER'
}

def connect_to_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Connection failed: {e}")
    return None

def execute_query(query, params=None, fetch=False):
    conn = connect_to_db()
    if not conn:
        return None
    cur = conn.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        if fetch:
            rows = cur.fetchall()
            return rows
        conn.commit()
        return True
    except Error as e:
        messagebox.showerror("Query Error", str(e))
        return None
    finally:
        cur.close()
        conn.close()

def get_next_id(table, col, start=1000):
    q = f"SELECT COALESCE(MAX({col}), {start-1}) + 1 FROM {table}"
    res = execute_query(q, fetch=True)
    if res is None:
        return None
    return int(res[0][0])

def setup_database():
    conn = connect_to_db()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS DEPARTMENTS (
            Dept_ID INT PRIMARY KEY,
            Dept_Name VARCHAR(100) NOT NULL UNIQUE,
            Head_of_Dept VARCHAR(100)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS COMPANIES (
            Company_ID INT PRIMARY KEY,
            Name VARCHAR(150) NOT NULL UNIQUE,
            Industry VARCHAR(100),
            Location VARCHAR(100),
            Contact_Email VARCHAR(100)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS STUDENTS (
            Student_ID INT PRIMARY KEY,
            Name VARCHAR(150) NOT NULL,
            Email VARCHAR(150) NOT NULL UNIQUE,
            Dept_ID INT NOT NULL,
            CGPA DECIMAL(3,2),
            Backlog_Count INT DEFAULT 0,
            is_Placed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (Dept_ID) REFERENCES DEPARTMENTS(Dept_ID)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS JOB_POSTINGS (
            Job_ID INT PRIMARY KEY,
            Company_ID INT NOT NULL,
            Role VARCHAR(100) NOT NULL,
            CTC_Min DECIMAL(10,2),
            Min_GPA_Req DECIMAL(3,2),
            Posting_Date DATE,
            FOREIGN KEY (Company_ID) REFERENCES COMPANIES(Company_ID)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS APPLICATIONS (
            Application_ID INT PRIMARY KEY,
            Student_ID INT NOT NULL,
            Job_ID INT NOT NULL,
            Status ENUM('Wishlist', 'Applied', 'Assessment', 'Interview', 'Offered', 'Rejected') NOT NULL,
            Date_Applied DATE,
            FOREIGN KEY (Student_ID) REFERENCES STUDENTS(Student_ID),
            FOREIGN KEY (Job_ID) REFERENCES JOB_POSTINGS(Job_ID)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS PLACEMENTS (
            Placement_ID INT PRIMARY KEY,
            Application_ID INT NOT NULL UNIQUE,
            CTC_Final DECIMAL(10,2),
            Offer_Date DATE,
            Joining_Date DATE,
            Document_Path VARCHAR(255),
            FOREIGN KEY (Application_ID) REFERENCES APPLICATIONS(Application_ID)
        )""")
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM DEPARTMENTS")
        if cur.fetchone()[0] == 0:
            cur.execute("""
            INSERT INTO DEPARTMENTS (Dept_ID, Dept_Name, Head_of_Dept) VALUES
            (101, 'Computer Science Engineering', 'Dr. Sharma'),
            (102, 'Electronics & Communication', 'Prof. Rao'),
            (103, 'Mechanical Engineering', 'Dr. Singh'),
            (104, 'Civil Engineering', 'Dr. Kumar'),
            (105, 'Electrical Engineering', 'Prof. Reddy'),
            (106, 'Information Technology', 'Dr. Verma'),
            (107, 'Chemical Engineering', 'Prof. Gupta'),
            (108, 'Aerospace Engineering', 'Dr. Patel'),
            (109, 'Data Science', 'Prof. Iyer'),
            (110, 'Artificial Intelligence', 'Dr. Khan')
            """)
            conn.commit()

        
        cur.execute("SELECT COUNT(*) FROM COMPANIES")
        if cur.fetchone()[0] == 0:
            cur.execute("""
            INSERT INTO COMPANIES (Company_ID, Name, Industry, Location, Contact_Email) VALUES
            (501, 'TechWave Solutions', 'Software', 'Bangalore', 'hr@techwave.com'),
            (502, 'AutoMech Motors', 'Automotive', 'Pune', 'hiring@automech.in')
            """)
            conn.commit()

        
        cur.execute("SELECT COUNT(*) FROM STUDENTS")
        if cur.fetchone()[0] == 0:
            cur.execute("""
            INSERT INTO STUDENTS (Student_ID, Name, Email, Dept_ID, CGPA, Backlog_Count, is_Placed) VALUES
            (2001, 'Aisha Khan', 'aisha.k@email.com', 101, 8.55, 0, FALSE),
            (2002, 'Ravi Verma', 'ravi.v@email.com', 101, 7.10, 1, FALSE)
            """)
            conn.commit()
    except Error as e:
        messagebox.showerror("DB Setup Error", str(e))
    finally:
        cur.close()
        conn.close()


