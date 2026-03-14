import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
from dbe import execute_query, get_next_id

class PlacementTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Placement Tracker System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f2f5')

        self.current_role = None
        self.current_user = None

        # Entry point
        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

   
    def create_header(self, title_text):
        header = tk.Frame(self.root, bg='white', height=60)
        header.pack(fill='x')
        tk.Label(header, text=title_text, font=('Helvetica', 18, 'bold'), bg='white').pack(side='left', padx=20)
        tk.Button(header, text="Home", command=self.show_login_screen, bg='#6b7280', fg='white').pack(side='right', padx=10, pady=10)
        tk.Button(header, text="Quit", command=self.root.quit, bg='#ef4444', fg='white').pack(side='right', padx=10, pady=10)

    
    def create_stat_card(self, parent, title, value, color, col_index):
        card = tk.Frame(parent, bg='white', relief='ridge', bd=1)
        card.grid(row=0, column=col_index, padx=10, pady=10, sticky='nsew')
        tk.Label(card, text=title, font=('Helvetica', 10, 'bold'), bg='white', fg='#6b7280').pack(padx=10, pady=(10,4))
        tk.Label(card, text=value, font=('Helvetica', 16, 'bold'), bg='white', fg=color).pack(padx=10, pady=(0,10))
        return card

    
    # Login Screen
    def show_login_screen(self):
        self.clear_window()

        # Main container
        container = tk.Frame(self.root, bg='#f0f2f5')
        container.pack(expand=True, fill='both')

        # Login card
        login_frame = tk.Frame(container, bg='white', relief='raised', bd=2)
        login_frame.place(relx=0.5, rely=0.5, anchor='center', width=420, height=520)

        # Title
        title = tk.Label(login_frame, text="🎓 Placement Tracker",
                         font=('Helvetica', 24, 'bold'), bg='white', fg='#1e40af')
        title.pack(pady=30)

        subtitle = tk.Label(login_frame, text="Select your role to continue",
                            font=('Helvetica', 12), bg='white', fg='#6b7280')
        subtitle.pack(pady=10)

        # Role buttons
        btn_style = {'font': ('Helvetica', 12, 'bold'), 'width': 25, 'height': 2,
                     'relief': 'flat', 'cursor': 'hand2'}

        student_btn = tk.Button(login_frame, text="👨‍🎓 Student Portal",
                                bg='#3b82f6', fg='white',
                                command=lambda: self.role_selected('student'),
                                **btn_style)
        student_btn.pack(pady=15)

        admin_btn = tk.Button(login_frame, text="👔 TPO/Admin Portal",
                              bg='#10b981', fg='white',
                              command=lambda: self.role_selected('admin'),
                              **btn_style)
        admin_btn.pack(pady=15)

        company_btn = tk.Button(login_frame, text="🏢 Company Portal",
                                bg='#8b5cf6', fg='white',
                                command=lambda: self.role_selected('company'),
                                **btn_style)
        company_btn.pack(pady=15)

    def role_selected(self, role):
        self.current_role = role
        if role == 'student':
            self.show_student_login()
        elif role == 'admin':
            self.show_admin_dashboard()
        elif role == 'company':
            self.show_company_dashboard()

   
    # Student Login
    def show_student_login(self):
        self.clear_window()

        container = tk.Frame(self.root, bg='#f0f2f5')
        container.pack(expand=True, fill='both')

        login_frame = tk.Frame(container, bg='white', relief='raised', bd=2)
        login_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=300)

        tk.Label(login_frame, text="Student Login",
                 font=('Helvetica', 20, 'bold'), bg='white').pack(pady=20)

        tk.Label(login_frame, text="Enter Student ID:",
                 font=('Helvetica', 12), bg='white').pack(pady=10)

        student_id_entry = tk.Entry(login_frame, font=('Helvetica', 14), width=20)
        student_id_entry.pack(pady=10)

        def login():
            try:
                sid = int(student_id_entry.get())
                # Verify student exists
                q = "SELECT Student_ID FROM STUDENTS WHERE Student_ID = %s"
                result = execute_query(q, (sid,), fetch=True)
                if result:
                    self.current_user = sid
                    self.show_student_dashboard()
                else:
                    messagebox.showerror("Error", "Student ID not found")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid Student ID")

        login_btn = tk.Button(login_frame, text="Login",
                              bg='#3b82f6', fg='white',
                              font=('Helvetica', 12, 'bold'),
                              command=login, width=15, height=2)
        login_btn.pack(pady=20)

        back_btn = tk.Button(login_frame, text="← Back",
                             command=self.show_login_screen,
                             bg='#6b7280', fg='white', font=('Helvetica', 10))
        back_btn.pack()

    # -------------------------
    # Student Dashboard
    # -------------------------
    def show_student_dashboard(self):
        self.clear_window()
        self.create_header("Student Portal")

        # Main container with scrollbar
        main_container = tk.Frame(self.root, bg='#f0f2f5')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        canvas = tk.Canvas(main_container, bg='#f0f2f5')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f2f5')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Get student data
        q = """
        SELECT s.Student_ID, s.Name, s.Email, s.CGPA, s.Backlog_Count,
               CASE WHEN s.is_Placed THEN 'Placed' ELSE 'Not Placed' END AS Status,
               d.Dept_Name
        FROM STUDENTS s JOIN DEPARTMENTS d ON s.Dept_ID = d.Dept_ID
        WHERE s.Student_ID = %s
        """
        student_data = execute_query(q, (self.current_user,), fetch=True)

        if not student_data:
            messagebox.showerror("Error", "Student data not found")
            return

        sid, name, email, cgpa, backlogs, status, dept = student_data[0]

        # Stats cards
        stats_frame = tk.Frame(scrollable_frame, bg='#f0f2f5')
        stats_frame.pack(fill='x', pady=10)
        stats_frame.columnconfigure((0,1,2,3), weight=1)

        self.create_stat_card(stats_frame, "CGPA", str(cgpa), "#3b82f6", 0)

        # Get application count
        app_count_q = "SELECT COUNT(*) FROM APPLICATIONS WHERE Student_ID = %s"
        app_count_res = execute_query(app_count_q, (self.current_user,), fetch=True)
        app_count = app_count_res[0][0] if app_count_res else 0
        self.create_stat_card(stats_frame, "Applications", str(app_count), "#10b981", 1)
        self.create_stat_card(stats_frame, "Status", status, "#8b5cf6", 2)

        avg_ctc_result = execute_query("SELECT ROUND(AVG(CTC_Final), 2) FROM PLACEMENTS", fetch=True)
        avg_ctc = avg_ctc_result[0][0] if avg_ctc_result and avg_ctc_result[0][0] else 0
        self.create_stat_card(stats_frame, "Avg CTC (LPA)", f"{avg_ctc}", "#f59e0b", 3)

        # Profile section
        profile_frame = tk.LabelFrame(scrollable_frame, text="Profile Information",
                                     font=('Helvetica', 14, 'bold'), bg='white', padx=20, pady=20)
        profile_frame.pack(fill='x', pady=10)

        info_labels = [
            ("Name:", name),
            ("Email:", email),
            ("Department:", dept),
            ("Backlogs:", str(backlogs))
        ]

        for i, (label, value) in enumerate(info_labels):
            tk.Label(profile_frame, text=label, font=('Helvetica', 11, 'bold'),
                    bg='white', anchor='w').grid(row=i, column=0, sticky='w', pady=5, padx=10)
            tk.Label(profile_frame, text=value, font=('Helvetica', 11),
                    bg='white', anchor='w').grid(row=i, column=1, sticky='w', pady=5, padx=10)

        # Applications section
        apps_frame = tk.LabelFrame(scrollable_frame, text="My Applications",
                                  font=('Helvetica', 14, 'bold'), bg='white', padx=20, pady=20)
        apps_frame.pack(fill='both', expand=True, pady=10)

        q = """
        SELECT c.Name AS Company, j.Role, a.Status, a.Date_Applied
        FROM APPLICATIONS a JOIN JOB_POSTINGS j ON a.Job_ID = j.Job_ID
        JOIN COMPANIES c ON j.Company_ID = c.Company_ID
        WHERE a.Student_ID = %s ORDER BY a.Date_Applied DESC
        """
        apps = execute_query(q, (self.current_user,), fetch=True)

        if apps:
            tree = ttk.Treeview(apps_frame, columns=('Company', 'Role', 'Status', 'Date'),
                                show='headings', height=8)
            tree.heading('Company', text='Company')
            tree.heading('Role', text='Role')
            tree.heading('Status', text='Status')
            tree.heading('Date', text='Date Applied')

            for app in apps:
                tree.insert('', 'end', values=app)

            tree.pack(fill='both', expand=True)
        else:
            tk.Label(apps_frame, text="No applications yet",
                     font=('Helvetica', 12), bg='white').pack(pady=20)

        # Available jobs section
        jobs_frame = tk.LabelFrame(scrollable_frame, text="Available Jobs",
                                  font=('Helvetica', 14, 'bold'), bg='white', padx=20, pady=20)
        jobs_frame.pack(fill='both', expand=True, pady=10)

        q = """
        SELECT j.Job_ID, c.Name AS Company, j.Role, j.CTC_Min, j.Min_GPA_Req
        FROM JOB_POSTINGS j JOIN COMPANIES c ON j.Company_ID = c.Company_ID
        WHERE j.Min_GPA_Req <= %s
        AND j.Job_ID NOT IN (SELECT Job_ID FROM APPLICATIONS WHERE Student_ID = %s)
        ORDER BY j.Posting_Date DESC
        LIMIT 10
        """
        jobs = execute_query(q, (cgpa, self.current_user), fetch=True)

        if jobs:
            for job in jobs:
                job_id, company, role, ctc, min_gpa = job
                job_card = tk.Frame(jobs_frame, bg='#f9fafb', relief='solid', bd=1)
                job_card.pack(fill='x', pady=5)

                tk.Label(job_card, text=role, font=('Helvetica', 12, 'bold'),
                        bg='#f9fafb').pack(anchor='w', padx=10, pady=(10, 0))
                tk.Label(job_card, text=company, font=('Helvetica', 10),
                        bg='#f9fafb', fg='#6b7280').pack(anchor='w', padx=10)
                tk.Label(job_card, text=f"CTC: ₹{ctc} LPA | Min GPA: {min_gpa}",
                        font=('Helvetica', 9), bg='#f9fafb', fg='#6b7280').pack(anchor='w', padx=10, pady=(0, 10))

                apply_btn = tk.Button(job_card, text="Apply", bg='#3b82f6', fg='white',
                                     command=lambda jid=job_id: self.apply_job(jid))
                apply_btn.pack(anchor='e', padx=10, pady=5)
        else:
            tk.Label(jobs_frame, text="No available jobs matching your profile",
                     font=('Helvetica', 12), bg='white').pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def apply_job(self, job_id):
        app_id = get_next_id("APPLICATIONS", "Application_ID", start=4001)
        if app_id is None:
            messagebox.showerror("Error", "Could not generate application ID")
            return

        q = """INSERT INTO APPLICATIONS 
               (Application_ID, Student_ID, Job_ID, Status, Date_Applied) 
               VALUES (%s, %s, %s, 'Applied', %s)"""

        if execute_query(q, (app_id, self.current_user, job_id,
                             datetime.today().strftime("%Y-%m-%d"))):
            messagebox.showinfo("Success", "Application submitted successfully!")
            self.show_student_dashboard()

    # -------------------------
    # Admin Dashboard
    # -------------------------
    def show_admin_dashboard(self):
        self.clear_window()
        self.create_header("TPO/Admin Portal")

        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # Analytics Tab
        analytics_frame = tk.Frame(notebook, bg='#f0f2f5')
        notebook.add(analytics_frame, text='📊 Analytics')

        # Students Tab
        students_frame = tk.Frame(notebook, bg='#f0f2f5')
        notebook.add(students_frame, text='👥 Students')

        # Jobs Tab
        jobs_frame = tk.Frame(notebook, bg='#f0f2f5')
        notebook.add(jobs_frame, text='💼 Jobs')

        # Build Analytics Tab
        self.build_analytics_tab(analytics_frame)

        # Build Students Tab
        self.build_students_tab(students_frame)

        # Build Jobs Tab
        self.build_jobs_tab(jobs_frame)

    def build_analytics_tab(self, parent):
        # Stats cards
        stats_frame = tk.Frame(parent, bg='#f0f2f5')
        stats_frame.pack(fill='x', pady=10, padx=10)
        stats_frame.columnconfigure((0,1,2,3), weight=1)

        total_students_res = execute_query("SELECT COUNT(*) FROM STUDENTS", fetch=True)
        total_students = total_students_res[0][0] if total_students_res else 0

        placed_students_res = execute_query("SELECT COUNT(*) FROM STUDENTS WHERE is_Placed=TRUE", fetch=True)
        placed_students = placed_students_res[0][0] if placed_students_res else 0

        placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0

        avg_ctc_result = execute_query("SELECT ROUND(AVG(CTC_Final), 2) FROM PLACEMENTS", fetch=True)
        avg_ctc = avg_ctc_result[0][0] if avg_ctc_result and avg_ctc_result[0][0] else 0

        self.create_stat_card(stats_frame, "Total Students", str(total_students), "#3b82f6", 0)
        self.create_stat_card(stats_frame, "Placed", str(placed_students), "#10b981", 1)
        self.create_stat_card(stats_frame, "Placement Rate", f"{placement_rate:.1f}%", "#f59e0b", 2)
        self.create_stat_card(stats_frame, "Avg CTC (LPA)", f"{avg_ctc}", "#8b5cf6", 3)

        # Charts container
        charts_frame = tk.Frame(parent, bg='#f0f2f5')
        charts_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Department-wise placement chart
        dept_frame = tk.LabelFrame(charts_frame, text="Department-wise Placement",
                                   font=('Helvetica', 12, 'bold'), bg='white')
        dept_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        q = """
        SELECT d.Dept_Name,
               SUM(s.is_Placed) AS Placed_Count,
               (COUNT(s.Student_ID) - SUM(s.is_Placed)) AS Not_Placed
        FROM STUDENTS s JOIN DEPARTMENTS d ON s.Dept_ID = d.Dept_ID
        GROUP BY d.Dept_Name
        ORDER BY Placed_Count DESC
        LIMIT 5
        """
        dept_data = execute_query(q, fetch=True) or []

        if dept_data:
            fig = Figure(figsize=(6, 4), facecolor='white')
            ax = fig.add_subplot(111)

            depts = [row[0][:15] for row in dept_data]
            placed = [row[1] for row in dept_data]
            not_placed = [row[2] for row in dept_data]

            x = np.arange(len(depts))
            width = 0.35

            ax.bar(x - width/2, placed, width, label='Placed', color='#10b981')
            ax.bar(x + width/2, not_placed, width, label='Not Placed', color='#ef4444')

            ax.set_xlabel('Department')
            ax.set_ylabel('Number of Students')
            ax.set_xticks(x)
            ax.set_xticklabels(depts, rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, dept_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        # Application status pie chart
        status_frame = tk.LabelFrame(charts_frame, text="Application Status Distribution",
                                     font=('Helvetica', 12, 'bold'), bg='white')
        status_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        status_q = "SELECT Status, COUNT(*) FROM APPLICATIONS GROUP BY Status"
        status_data = execute_query(status_q, fetch=True) or []

        if status_data:
            fig = Figure(figsize=(6, 4), facecolor='white')
            ax = fig.add_subplot(111)

            statuses = [row[0] for row in status_data]
            counts = [row[1] for row in status_data]

            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
            ax.pie(counts, labels=statuses, autopct='%1.1f%%', colors=colors[:len(statuses)])

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, status_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        # Placement success rate by department
        success_frame = tk.LabelFrame(charts_frame, text="Placement Success Rate",
                                      font=('Helvetica', 12, 'bold'), bg='white')
        success_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        success_q = """
        SELECT d.Dept_Name,
               ROUND((SUM(s.is_Placed)/COUNT(s.Student_ID))*100, 1) AS Success_Rate
        FROM STUDENTS s JOIN DEPARTMENTS d ON s.Dept_ID = d.Dept_ID
        GROUP BY d.Dept_Name
        ORDER BY Success_Rate DESC
        LIMIT 8
        """
        success_data = execute_query(success_q, fetch=True) or []

        if success_data:
            fig = Figure(figsize=(12, 3), facecolor='white')
            ax = fig.add_subplot(111)

            depts = [row[0][:20] for row in success_data]
            rates = [row[1] for row in success_data]

            bars = ax.barh(depts, rates, color='#3b82f6')
            ax.set_xlabel('Success Rate (%)')
            ax.set_xlim(0, 100)
            ax.grid(axis='x', alpha=0.3)

            for bar in bars:
                width = bar.get_width()
                ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                        f'{width:.1f}%', ha='left', va='center')

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, success_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)

    def build_students_tab(self, parent):
        # Top controls
        control_frame = tk.Frame(parent, bg='#f0f2f5')
        control_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(control_frame, text="➕ Add Student", bg='#10b981', fg='white',
                  font=('Helvetica', 11, 'bold'), command=self.add_student_dialog).pack(side='left', padx=5)

        # Students table
        table_frame = tk.LabelFrame(parent, text="All Students",
                                   font=('Helvetica', 12, 'bold'), bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side='right', fill='y')

        columns = ('ID', 'Name', 'Email', 'Department', 'CGPA', 'Backlogs', 'Status')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                            yscrollcommand=tree_scroll.set, height=20)
        tree_scroll.config(command=tree.yview)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        q = """
        SELECT s.Student_ID, s.Name, s.Email, d.Dept_Name, s.CGPA, s.Backlog_Count,
               CASE WHEN s.is_Placed THEN 'Placed' ELSE 'Active' END AS Status
        FROM STUDENTS s JOIN DEPARTMENTS d ON s.Dept_ID = d.Dept_ID
        ORDER BY s.Student_ID
        """
        students = execute_query(q, fetch=True) or []

        if students:
            for student in students:
                tree.insert('', 'end', values=student)

        tree.pack(fill='both', expand=True, padx=10, pady=10)

    def build_jobs_tab(self, parent):
        table_frame = tk.LabelFrame(parent, text="Job Postings",
                                   font=('Helvetica', 12, 'bold'), bg='white')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side='right', fill='y')

        columns = ('Job ID', 'Company', 'Role', 'CTC (LPA)', 'Min GPA', 'Date')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                            yscrollcommand=tree_scroll.set, height=25)
        tree_scroll.config(command=tree.yview)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        q = """
        SELECT j.Job_ID, c.Name, j.Role, j.CTC_Min, j.Min_GPA_Req, j.Posting_Date
        FROM JOB_POSTINGS j JOIN COMPANIES c ON j.Company_ID = c.Company_ID
        ORDER BY j.Posting_Date DESC
        """
        jobs = execute_query(q, fetch=True) or []

        if jobs:
            for job in jobs:
                tree.insert('', 'end', values=job)

        tree.pack(fill='both', expand=True, padx=10, pady=10)

    def add_student_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("420x420")
        dialog.configure(bg='white')

        fields = [
            ("Student ID:", "id"),
            ("Name:", "name"),
            ("Email:", "email"),
            ("Department ID:", "dept"),
            ("CGPA:", "cgpa"),
            ("Backlogs:", "backlogs")
        ]

        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label, bg='white', font=('Helvetica', 11)).grid(
                row=i, column=0, padx=20, pady=8, sticky='w')
            entry = tk.Entry(dialog, font=('Helvetica', 11), width=25)
            entry.grid(row=i, column=1, padx=20, pady=8)
            entries[key] = entry

        def save_student():
            try:
                sid = int(entries['id'].get())
                name = entries['name'].get()
                email = entries['email'].get()
                dept = int(entries['dept'].get())
                cgpa = float(entries['cgpa'].get())
                backlogs = int(entries['backlogs'].get())

                q = """INSERT INTO STUDENTS 
                       (Student_ID, Name, Email, Dept_ID, CGPA, Backlog_Count, is_Placed) 
                       VALUES (%s, %s, %s, %s, %s, %s, FALSE)"""

                if execute_query(q, (sid, name, email, dept, cgpa, backlogs)):
                    messagebox.showinfo("Success", "Student added successfully!")
                    dialog.destroy()
                    self.show_admin_dashboard()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid data")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(dialog, text="Save", bg='#10b981', fg='white',
                 font=('Helvetica', 12, 'bold'), command=save_student,
                 width=15).grid(row=len(fields), column=0, columnspan=2, pady=20)

    # -------------------------
    # Company Dashboard (completed)
    # -------------------------
    
    def show_company_dashboard(self):
        self.clear_window()
        self.create_header("Company Portal")

        container = tk.Frame(self.root, bg='#f0f2f5')
        # Container
        container.pack(expand=True, fill='both', padx=20, pady=20)

        companies = execute_query("SELECT Company_ID, Name FROM COMPANIES ORDER BY Name LIMIT 20", fetch=True) or []

        if not companies:
            tk.Label(container, text="No companies registered", font=('Helvetica', 14), bg='#f0f2f5').pack()
            return

        # Split left-right
        left = tk.Frame(container, bg='#f0f2f5', width=280)
        left.pack(side='left', fill='y', padx=10, pady=10)

        right = tk.Frame(container, bg='#f0f2f5')
        right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Left side: Company list
        tk.Label(left, text="Companies (select):", font=('Helvetica', 12, 'bold'), bg='#f0f2f5').pack(anchor='nw', pady=(0,8))
        company_listbox = tk.Listbox(left, width=35, height=20)
        company_listbox.pack(fill='y', expand=False)

        comp_map = []
        for cid, cname in companies:
            company_listbox.insert('end', cname)
            comp_map.append((cid, cname))

        # Right side: Company Actions + Info
        action_frame = tk.LabelFrame(right, text="Actions", font=('Helvetica', 12, 'bold'), bg='white')
        action_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(action_frame, text="Post New Job", command=lambda: post_job_dialog(comp_map, company_listbox)).pack(side='left', padx=8, pady=8)
        ttk.Button(action_frame, text="View My Jobs", command=lambda: view_company_jobs(comp_map, company_listbox, info_frame)).pack(side='left', padx=8, pady=8)
        ttk.Button(action_frame, text="View Applicants", command=lambda: view_applicants_dialog(comp_map, company_listbox)).pack(side='left', padx=8, pady=8)
        ttk.Button(action_frame, text="Show Analytics", command=lambda: show_company_analytics(comp_map, company_listbox)).pack(side='left', padx=8, pady=8)

        info_frame = tk.LabelFrame(right, text="Company Info / Jobs", font=('Helvetica', 12, 'bold'), bg='white')
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)

        info_label = tk.Label(info_frame, text="Select a company and choose an action.", bg='white', anchor='nw', justify='left')
        info_label.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Helper functions ---
        def get_selected_company(comp_map_ref, lb):
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Select", "Please select a company from the list.")
                return None
            idx = sel[0]
            return comp_map_ref[idx][0]  # company_id

        def post_job_dialog(comp_map_ref, lb):
            cid = get_selected_company(comp_map_ref, lb)
            if cid is None: return

            dialog = tk.Toplevel(self.root)
            dialog.title("Post New Job")
            dialog.geometry("420x340")
            dialog.configure(bg='white')

            labels = ["Role:", "Min CTC (LPA):", "Min GPA:"]
            entries = []
            for i, lbl in enumerate(labels):
                tk.Label(dialog, text=lbl, bg='white').grid(row=i, column=0, padx=10, pady=8, sticky='w')
                e = tk.Entry(dialog, width=30)
                e.grid(row=i, column=1, padx=10, pady=8)
                entries.append(e)

            def save_job():
                try:
                    role, ctc, mgpa = entries[0].get().strip(), float(entries[1].get().strip()), float(entries[2].get().strip())
                except ValueError:
                    messagebox.showerror("Input", "Enter valid numeric values for CTC and GPA")
                    return

                jid = get_next_id("JOB_POSTINGS", "Job_ID", start=3001)
                if jid is None:
                    messagebox.showerror("Error", "Could not generate job ID")
                    return

                if execute_query("""
                    INSERT INTO JOB_POSTINGS (Job_ID, Company_ID, Role, CTC_Min, Min_GPA_Req, Posting_Date)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (jid, cid, role, ctc, mgpa, datetime.today().strftime("%Y-%m-%d"))):
                    messagebox.showinfo("Success", f"Job posted successfully (ID: {jid})")
                    dialog.destroy()

            tk.Button(dialog, text="Post Job", bg='#2563eb', fg='white', command=save_job).grid(row=3, column=0, columnspan=2, pady=20)

        def view_company_jobs(comp_map_ref, lb, parent_frame):
            cid = get_selected_company(comp_map_ref, lb)
            if cid is None: return

            jobs = execute_query("""
                SELECT Job_ID, Role, CTC_Min, Min_GPA_Req, Posting_Date 
                FROM JOB_POSTINGS WHERE Company_ID=%s ORDER BY Posting_Date DESC
            """, (cid,), fetch=True) or []

            for widget in parent_frame.winfo_children():
                widget.destroy()

            lf = tk.LabelFrame(parent_frame, text=f"Jobs by Company ID {cid}", font=('Helvetica', 12, 'bold'), bg='white')
            lf.pack(fill='both', expand=True, padx=10, pady=10)

            tree_scroll = ttk.Scrollbar(lf)
            tree_scroll.pack(side='right', fill='y')
            cols = ('Job ID', 'Role', 'CTC (LPA)', 'Min GPA', 'Posted On')
            tree = ttk.Treeview(lf, columns=cols, show='headings', yscrollcommand=tree_scroll.set)
            tree_scroll.config(command=tree.yview)
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=140)
            for j in jobs:
                tree.insert('', 'end', values=j)
            tree.pack(fill='both', expand=True, padx=6, pady=6)

        def view_applicants_dialog(comp_map_ref, lb):
            cid = get_selected_company(comp_map_ref, lb)
            if cid is None: return
            jid = simpledialog.askinteger("Job ID", "Enter Job ID to view applicants:", parent=self.root)
            if not jid: return

            rows = execute_query("""
                SELECT s.Student_ID, s.Name, s.Email, s.CGPA, a.Status, a.Date_Applied
                FROM APPLICATIONS a
                JOIN STUDENTS s ON a.Student_ID = s.Student_ID
                JOIN JOB_POSTINGS j ON a.Job_ID = j.Job_ID
                WHERE j.Company_ID = %s AND a.Job_ID = %s
                ORDER BY a.Date_Applied DESC
            """, (cid, jid), fetch=True) or []

            dialog = tk.Toplevel(self.root)
            dialog.title(f"Applicants for Job {jid}")
            dialog.geometry("800x400")
            tree_scroll = ttk.Scrollbar(dialog)
            tree_scroll.pack(side='right', fill='y')
            cols = ('Student ID','Name','Email','CGPA','Status','Applied On')
            tree = ttk.Treeview(dialog, columns=cols, show='headings', yscrollcommand=tree_scroll.set)
            tree_scroll.config(command=tree.yview)
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=120)
            for r in rows:
                tree.insert('', 'end', values=r)
            tree.pack(fill='both', expand=True, padx=6, pady=6)

        def show_company_analytics(comp_map_ref, lb):
            cid = get_selected_company(comp_map_ref, lb)
            if cid is None: return

            # Data for graphs
            jobs = execute_query("SELECT Role, Posting_Date FROM JOB_POSTINGS WHERE Company_ID=%s", (cid,), fetch=True) or []
            applicants = execute_query("""
                SELECT j.Role, COUNT(a.Application_ID) FROM APPLICATIONS a
                JOIN JOB_POSTINGS j ON a.Job_ID = j.Job_ID
                WHERE j.Company_ID=%s GROUP BY j.Role
            """, (cid,), fetch=True) or []

            dialog = tk.Toplevel(self.root)
            dialog.title("Company Analytics")
            dialog.geometry("900x500")

            fig, axs = plt.subplots(1, 2, figsize=(9, 4))
            fig.tight_layout(pad=4)

            # Plot 1: Job Posting Trend
            if jobs:
                roles = [r[0] for r in jobs]
                axs[0].barh(roles, range(1, len(roles)+1))
                axs[0].set_title("Job Postings Trend")
                axs[0].set_xlabel("Posting Order")
            else:
                axs[0].text(0.5, 0.5, "No job postings yet", ha='center')

            # Plot 2: Applicants Distribution
            if applicants:
                labels = [a[0] for a in applicants]
                sizes = [a[1] for a in applicants]
                axs[1].pie(sizes, labels=labels, autopct='%1.1f%%')
                axs[1].set_title("Applicants by Job Role")
            else:
                axs[1].text(0.5, 0.5, "No applicants data", ha='center')

            canvas = FigureCanvasTkAgg(fig, master=dialog)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
