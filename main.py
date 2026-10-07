import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

from PIL import Image, ImageTk, ImageFilter


# ============================================================
# AUTOMATED SMCII GRADE CALCULATION PERFORMANCE SYSTEM
# ============================================================

root = tk.Tk()

root.title(
    "AUTOMATED SMCII GRADE CALCULATION PERFORMANCE SYSTEM"
)

root.geometry("1100x700")
root.minsize(900, 600)

root.configure(bg="#eef2f7")


# ============================================================
# BACKGROUND PHOTO SETTINGS
# ============================================================

BACKGROUND_FILE = "background.jpg"

background_label = None
background_photo = None
background_blurred = False


def load_background(blurred=False):

    global background_label
    global background_photo
    global background_blurred

    background_blurred = blurred

    try:

        image = Image.open(BACKGROUND_FILE).convert("RGB")

        width = root.winfo_width()
        height = root.winfo_height()

        if width <= 1:
            width = 1100

        if height <= 1:
            height = 700

        image = image.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )

        if blurred:

            image = image.filter(
                ImageFilter.GaussianBlur(12)
            )

        background_photo = ImageTk.PhotoImage(image)

        if background_label is None:

            background_label = tk.Label(
                root,
                image=background_photo,
                bd=0
            )

            background_label.place(
                x=0,
                y=0,
                relwidth=1,
                relheight=1
            )

        else:

            background_label.configure(
                image=background_photo
            )

        background_label.lower()

    except FileNotFoundError:

        if background_label is not None:

            background_label.destroy()
            background_label = None

        root.configure(bg="#eef2f7")


def resize_background(event=None):

    if background_label is not None:

        load_background(background_blurred)


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect("smcii_grades.db")

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT NOT NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_username TEXT NOT NULL,
    subject TEXT NOT NULL,
    quizzes REAL NOT NULL,
    activities REAL NOT NULL,
    midterm REAL NOT NULL,
    final_exam REAL NOT NULL,
    final_grade REAL NOT NULL
)
""")


conn.commit()


# ============================================================
# DEFAULT USERS
# ============================================================

def create_default_user(
    username,
    password,
    role,
    full_name
):

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    if cursor.fetchone() is None:

        cursor.execute("""
            INSERT INTO users
            (username, password, role, full_name)
            VALUES (?, ?, ?, ?)
        """, (
            username,
            password,
            role,
            full_name
        ))

        conn.commit()


create_default_user(
    "admin",
    "admin123",
    "Admin",
    "System Administrator"
)


create_default_user(
    "teacher",
    "teacher123",
    "Teacher",
    "SMCII Teacher"
)


create_default_user(
    "student",
    "student123",
    "Student",
    "Sample Student"
)


# ============================================================
# GENERAL FUNCTIONS
# ============================================================

def clear_window():

    for widget in root.winfo_children():

        if widget != background_label:

            widget.destroy()


def logout():

    show_login_selection()


def close_system():

    conn.close()
    root.destroy()


# ============================================================
# LOGIN SELECTION
# CLEAR BACKGROUND PHOTO
# ============================================================

def show_login_selection():

    clear_window()

    load_background(False)

    # --------------------------------------------------------
    # MAIN CONTENT
    # --------------------------------------------------------

    main_frame = tk.Frame(
        root,
        bg="#eef2f7"
    )

    main_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    tk.Label(
        main_frame,
        text="SMCII PORTAL",
        font=("Arial", 30, "bold"),
        bg="#eef2f7",
        fg="#172033"
    ).pack(
        pady=(0, 20)
    )


    # --------------------------------------------------------
    # LOGIN TYPE
    # --------------------------------------------------------

    tk.Label(
        main_frame,
        text="Select your Login Type",
        font=("Arial", 19, "bold"),
        bg="#eef2f7",
        fg="#2563eb"
    ).pack(
        pady=(0, 15)
    )


    # --------------------------------------------------------
    # LOGIN BOX
    # --------------------------------------------------------

    selection_frame = tk.Frame(
        main_frame,
        bg="white",
        bd=1,
        relief="solid",
        width=430,
        height=350
    )

    selection_frame.pack()

    selection_frame.pack_propagate(False)


    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    tk.Button(
        selection_frame,
        text="ADMIN LOGIN",
        command=lambda: show_role_login("Admin"),
        font=("Arial", 12, "bold"),
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        width=28,
        height=2,
        cursor="hand2",
        bd=0
    ).pack(
        pady=(45, 10)
    )


    # --------------------------------------------------------
    # TEACHER
    # --------------------------------------------------------

    tk.Button(
        selection_frame,
        text="TEACHER LOGIN",
        command=lambda: show_role_login("Teacher"),
        font=("Arial", 12, "bold"),
        bg="#16a34a",
        fg="white",
        activebackground="#15803d",
        activeforeground="white",
        width=28,
        height=2,
        cursor="hand2",
        bd=0
    ).pack(
        pady=10
    )


    # --------------------------------------------------------
    # STUDENT
    # --------------------------------------------------------

    tk.Button(
        selection_frame,
        text="STUDENT LOGIN",
        command=lambda: show_role_login("Student"),
        font=("Arial", 12, "bold"),
        bg="#9333ea",
        fg="white",
        activebackground="#7e22ce",
        activeforeground="white",
        width=28,
        height=2,
        cursor="hand2",
        bd=0
    ).pack(
        pady=10
    )


    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    tk.Label(
        main_frame,
        text="@GogonsAndFriends SMCII Portal Management System",
        font=("Arial", 10),
        bg="#eef2f7",
        fg="#64748b"
    ).pack(
        pady=20
    )


# ============================================================
# ROLE LOGIN
# BLURRED BACKGROUND PHOTO
# ============================================================

def show_role_login(role):

    clear_window()

    load_background(True)

    # --------------------------------------------------------
    # LOGIN CONTENT
    # --------------------------------------------------------

    main_frame = tk.Frame(
        root,
        bg="#eef2f7",
        bd=0
    )

    main_frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    tk.Label(
        main_frame,
        text="AUTOMATED SMCII\nGRADE CALCULATION PERFORMANCE SYSTEM",
        font=("Arial", 21, "bold"),
        bg="#eef2f7",
        fg="#172033",
        justify="center"
    ).pack(
        pady=(0, 15)
    )


    # --------------------------------------------------------
    # ROLE
    # --------------------------------------------------------

    tk.Label(
        main_frame,
        text=role.upper() + " LOGIN",
        font=("Arial", 19, "bold"),
        bg="#eef2f7",
        fg="#2563eb"
    ).pack(
        pady=10
    )


    # --------------------------------------------------------
    # LOGIN BOX
    # --------------------------------------------------------

    login_frame = tk.Frame(
        main_frame,
        bg="white",
        bd=1,
        relief="solid"
    )

    login_frame.pack(
        ipadx=50,
        ipady=30
    )


    # ========================================================
    # USERNAME
    # ========================================================

    tk.Label(
        login_frame,
        text="Username:",
        font=("Arial", 11),
        bg="white"
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=12,
        sticky="w"
    )


    username_entry = tk.Entry(
        login_frame,
        width=30,
        font=("Arial", 11)
    )

    username_entry.grid(
        row=0,
        column=1,
        columnspan=2,
        padx=10,
        pady=12
    )


    # ========================================================
    # PASSWORD
    # ========================================================

    tk.Label(
        login_frame,
        text="Password:",
        font=("Arial", 11),
        bg="white"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=12,
        sticky="w"
    )


    password_entry = tk.Entry(
        login_frame,
        width=25,
        font=("Arial", 11),
        show="*"
    )

    password_entry.grid(
        row=1,
        column=1,
        padx=(10, 0),
        pady=12
    )


    # ========================================================
    # PASSWORD SHOW / HIDE
    # ========================================================

    def toggle_password():

        if password_entry.cget("show") == "*":

            password_entry.config(
                show=""
            )

            eye_button.config(
                text="◉"
            )

        else:

            password_entry.config(
                show="*"
            )

            eye_button.config(
                text="●"
            )


    eye_button = tk.Button(
        login_frame,
        text="●",
        command=toggle_password,
        font=("Arial", 10, "bold"),
        bg="white",
        fg="#2563eb",
        bd=0,
        cursor="hand2",
        width=3
    )

    eye_button.grid(
        row=1,
        column=2,
        padx=5,
        pady=12
    )


    # ========================================================
    # LOGIN FUNCTION
    # ========================================================

    def login():

        username = username_entry.get().strip()
        password = password_entry.get().strip()


        if username == "" or password == "":

            messagebox.showerror(
                "Login Error",
                "Please enter your username and password."
            )

            return


        cursor.execute("""
            SELECT username, password, role, full_name
            FROM users
            WHERE username = ?
            AND password = ?
            AND role = ?
        """, (
            username,
            password,
            role
        ))


        user = cursor.fetchone()


        if user is None:

            messagebox.showerror(
                "Login Error",
                "Invalid username, password, or login type."
            )

            return


        user_username = user[0]
        user_role = user[2]
        full_name = user[3]


        if user_role == "Admin":

            show_admin_dashboard(
                user_username,
                full_name
            )


        elif user_role == "Teacher":

            show_teacher_dashboard(
                user_username,
                full_name
            )


        elif user_role == "Student":

            show_student_dashboard(
                user_username,
                full_name
            )


    # ========================================================
    # LOGIN BUTTON
    # ========================================================

    tk.Button(
        login_frame,
        text="LOGIN",
        command=login,
        font=("Arial", 11, "bold"),
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        width=20,
        cursor="hand2",
        bd=0
    ).grid(
        row=2,
        column=0,
        columnspan=3,
        pady=15
    )


    # ========================================================
    # BACK BUTTON
    # ========================================================

    tk.Button(
        login_frame,
        text="BACK",
        command=show_login_selection,
        font=("Arial", 10),
        bg="#64748b",
        fg="white",
        activebackground="#475569",
        activeforeground="white",
        width=20,
        cursor="hand2",
        bd=0
    ).grid(
        row=3,
        column=0,
        columnspan=3,
        pady=5
    )


    username_entry.focus()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def show_admin_dashboard(username, full_name):

    clear_window()

    load_background(True)


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        root,
        bg="#172033",
        height=75
    )

    header.pack(
        fill="x"
    )


    tk.Label(
        header,
        text="ADMIN DASHBOARD",
        font=("Arial", 20, "bold"),
        bg="#172033",
        fg="white"
    ).pack(
        side="left",
        padx=25,
        pady=20
    )


    tk.Button(
        header,
        text="LOGOUT",
        command=logout,
        bg="#dc2626",
        fg="white",
        width=10,
        cursor="hand2"
    ).pack(
        side="right",
        padx=20
    )


    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    content = tk.Frame(
        root,
        bg="#eef2f7"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=20
    )


    tk.Label(
        content,
        text="Welcome, " + full_name,
        font=("Arial", 18, "bold"),
        bg="#eef2f7",
        fg="#172033"
    ).pack(
        anchor="w",
        pady=10
    )


    # ========================================================
    # ADD USER
    # ========================================================

    user_frame = tk.LabelFrame(
        content,
        text="ADD USER",
        font=("Arial", 12, "bold"),
        bg="white",
        padx=15,
        pady=15
    )

    user_frame.pack(
        fill="x",
        pady=10
    )


    tk.Label(
        user_frame,
        text="Username:",
        bg="white"
    ).grid(
        row=0,
        column=0,
        padx=5,
        pady=7
    )


    username_entry = tk.Entry(
        user_frame,
        width=20
    )

    username_entry.grid(
        row=0,
        column=1,
        padx=5,
        pady=7
    )


    tk.Label(
        user_frame,
        text="Password:",
        bg="white"
    ).grid(
        row=0,
        column=2,
        padx=5,
        pady=7
    )


    password_entry = tk.Entry(
        user_frame,
        width=20
    )

    password_entry.grid(
        row=0,
        column=3,
        padx=5,
        pady=7
    )


    tk.Label(
        user_frame,
        text="Full Name:",
        bg="white"
    ).grid(
        row=1,
        column=0,
        padx=5,
        pady=7
    )


    fullname_entry = tk.Entry(
        user_frame,
        width=20
    )

    fullname_entry.grid(
        row=1,
        column=1,
        padx=5,
        pady=7
    )


    tk.Label(
        user_frame,
        text="Role:",
        bg="white"
    ).grid(
        row=1,
        column=2,
        padx=5,
        pady=7
    )


    role_combo = ttk.Combobox(
        user_frame,
        values=[
            "Admin",
            "Teacher",
            "Student"
        ],
        state="readonly",
        width=18
    )

    role_combo.grid(
        row=1,
        column=3,
        padx=5,
        pady=7
    )

    role_combo.set("Student")


    # ========================================================
    # ADD USER FUNCTION
    # ========================================================

    def add_user():

        new_username = username_entry.get().strip()
        new_password = password_entry.get().strip()
        new_fullname = fullname_entry.get().strip()
        new_role = role_combo.get()


        if (
            new_username == ""
            or new_password == ""
            or new_fullname == ""
        ):

            messagebox.showerror(
                "Error",
                "Please complete all fields."
            )

            return


        try:

            cursor.execute("""
                INSERT INTO users
                (username, password, role, full_name)
                VALUES (?, ?, ?, ?)
            """, (
                new_username,
                new_password,
                new_role,
                new_fullname
            ))

            conn.commit()


            messagebox.showinfo(
                "Success",
                "User successfully added."
            )


            username_entry.delete(
                0,
                tk.END
            )

            password_entry.delete(
                0,
                tk.END
            )

            fullname_entry.delete(
                0,
                tk.END
            )


            load_users()


        except sqlite3.IntegrityError:

            messagebox.showerror(
                "Error",
                "Username already exists."
            )


    tk.Button(
        user_frame,
        text="ADD USER",
        command=add_user,
        bg="#2563eb",
        fg="white",
        width=18,
        cursor="hand2"
    ).grid(
        row=2,
        column=0,
        columnspan=4,
        pady=12
    )


    # ========================================================
    # USER TABLE
    # ========================================================

    list_frame = tk.LabelFrame(
        content,
        text="REGISTERED USERS",
        font=("Arial", 12, "bold"),
        bg="white",
        padx=10,
        pady=10
    )

    list_frame.pack(
        fill="both",
        expand=True,
        pady=10
    )


    columns = (
        "ID",
        "Username",
        "Full Name",
        "Role"
    )


    user_table = ttk.Treeview(
        list_frame,
        columns=columns,
        show="headings"
    )


    for column in columns:

        user_table.heading(
            column,
            text=column
        )

        user_table.column(
            column,
            width=180
        )


    user_table.pack(
        fill="both",
        expand=True
    )


    def load_users():

        for item in user_table.get_children():

            user_table.delete(item)


        cursor.execute("""
            SELECT id, username, full_name, role
            FROM users
            ORDER BY id
        """)


        users = cursor.fetchall()


        for user in users:

            user_table.insert(
                "",
                tk.END,
                values=user
            )


    load_users()


# ============================================================
# TEACHER DASHBOARD
# ============================================================

def show_teacher_dashboard(username, full_name):

    clear_window()

    load_background(True)


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        root,
        bg="#172033",
        height=75
    )

    header.pack(
        fill="x"
    )


    tk.Label(
        header,
        text="TEACHER DASHBOARD",
        font=("Arial", 20, "bold"),
        bg="#172033",
        fg="white"
    ).pack(
        side="left",
        padx=25,
        pady=20
    )


    tk.Button(
        header,
        text="LOGOUT",
        command=logout,
        bg="#dc2626",
        fg="white",
        width=10,
        cursor="hand2"
    ).pack(
        side="right",
        padx=20
    )


    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    content = tk.Frame(
        root,
        bg="#eef2f7"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=15
    )


    tk.Label(
        content,
        text="Welcome, " + full_name,
        font=("Arial", 18, "bold"),
        bg="#eef2f7",
        fg="#172033"
    ).pack(
        anchor="w",
        pady=8
    )


    # ========================================================
    # GRADE ENTRY
    # ========================================================

    grade_frame = tk.LabelFrame(
        content,
        text="ENTER STUDENT GRADE",
        font=("Arial", 12, "bold"),
        bg="white",
        padx=20,
        pady=15
    )

    grade_frame.pack(
        fill="x",
        pady=8
    )


    labels = [
        "Student Username",
        "Subject",
        "Quizzes",
        "Activities",
        "Midterm",
        "Final Exam"
    ]


    entries = {}


    for i, label in enumerate(labels):

        row = i // 2
        column = (i % 2) * 2


        tk.Label(
            grade_frame,
            text=label + ":",
            bg="white",
            font=("Arial", 10)
        ).grid(
            row=row,
            column=column,
            padx=10,
            pady=7,
            sticky="w"
        )


        entry = tk.Entry(
            grade_frame,
            width=25
        )


        entry.grid(
            row=row,
            column=column + 1,
            padx=10,
            pady=7
        )


        entries[label] = entry


    # ========================================================
    # SAVE GRADE
    # ========================================================

    def save_grade():

        student = entries[
            "Student Username"
        ].get().strip()


        subject = entries[
            "Subject"
        ].get().strip()


        try:

            quizzes = float(
                entries["Quizzes"].get()
            )

            activities = float(
                entries["Activities"].get()
            )

            midterm = float(
                entries["Midterm"].get()
            )

            final_exam = float(
                entries["Final Exam"].get()
            )


        except ValueError:

            messagebox.showerror(
                "Error",
                "Please enter valid numbers for all grades."
            )

            return


        if student == "" or subject == "":

            messagebox.showerror(
                "Error",
                "Please enter the student username and subject."
            )

            return


        grade_values = [
            quizzes,
            activities,
            midterm,
            final_exam
        ]


        for grade in grade_values:

            if grade < 0 or grade > 100:

                messagebox.showerror(
                    "Error",
                    "Grades must be between 0 and 100."
                )

                return


        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = ?
            AND role = 'Student'
        """, (
            student,
        ))


        if cursor.fetchone() is None:

            messagebox.showerror(
                "Error",
                "Student username does not exist."
            )

            return


        # ----------------------------------------------------
        # FINAL GRADE FORMULA
        # ----------------------------------------------------

        final_grade = (
            quizzes * 0.20
            + activities * 0.20
            + midterm * 0.25
            + final_exam * 0.35
        )


        cursor.execute("""
            INSERT INTO grades
            (
                student_username,
                subject,
                quizzes,
                activities,
                midterm,
                final_exam,
                final_grade
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student,
            subject,
            quizzes,
            activities,
            midterm,
            final_exam,
            final_grade
        ))


        conn.commit()


        messagebox.showinfo(
            "Grade Saved",
            "Grade successfully saved!\n\n"
            + f"Final Grade: {final_grade:.2f}"
        )


        for entry in entries.values():

            entry.delete(
                0,
                tk.END
            )


        load_grades()


    # ========================================================
    # CALCULATE AND SAVE
    # ========================================================

    tk.Button(
        grade_frame,
        text="CALCULATE AND SAVE",
        command=save_grade,
        bg="#2563eb",
        fg="white",
        font=("Arial", 10, "bold"),
        width=25,
        cursor="hand2"
    ).grid(
        row=3,
        column=0,
        columnspan=4,
        pady=12
    )


    # ========================================================
    # SUBMITTED GRADES
    # ========================================================

    table_frame = tk.LabelFrame(
        content,
        text="SUBMITTED GRADES",
        font=("Arial", 12, "bold"),
        bg="white",
        padx=10,
        pady=10
    )

    table_frame.pack(
        fill="both",
        expand=True,
        pady=8
    )


    columns = (
        "Student",
        "Subject",
        "Quizzes",
        "Activities",
        "Midterm",
        "Final Exam",
        "Final Grade"
    )


    grade_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )


    for column in columns:

        grade_table.heading(
            column,
            text=column
        )

        grade_table.column(
            column,
            width=120
        )


    grade_table.pack(
        fill="both",
        expand=True
    )


    def load_grades():

        for item in grade_table.get_children():

            grade_table.delete(item)


        cursor.execute("""
            SELECT
                student_username,
                subject,
                quizzes,
                activities,
                midterm,
                final_exam,
                final_grade
            FROM grades
            ORDER BY id DESC
        """)


        rows = cursor.fetchall()


        for row in rows:

            grade_table.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    f"{row[2]:.2f}",
                    f"{row[3]:.2f}",
                    f"{row[4]:.2f}",
                    f"{row[5]:.2f}",
                    f"{row[6]:.2f}"
                )
            )


    load_grades()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def show_student_dashboard(username, full_name):

    clear_window()

    load_background(True)


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        root,
        bg="#172033",
        height=75
    )

    header.pack(
        fill="x"
    )


    tk.Label(
        header,
        text="STUDENT DASHBOARD",
        font=("Arial", 20, "bold"),
        bg="#172033",
        fg="white"
    ).pack(
        side="left",
        padx=25,
        pady=20
    )


    tk.Button(
        header,
        text="LOGOUT",
        command=logout,
        bg="#dc2626",
        fg="white",
        width=10,
        cursor="hand2"
    ).pack(
        side="right",
        padx=20
    )


    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    content = tk.Frame(
        root,
        bg="#eef2f7"
    )

    content.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=25
    )


    tk.Label(
        content,
        text="Student: " + full_name,
        font=("Arial", 19, "bold"),
        bg="#eef2f7",
        fg="#172033"
    ).pack(
        anchor="w",
        pady=8
    )


    tk.Label(
        content,
        text="YOUR ACADEMIC PERFORMANCE",
        font=("Arial", 13, "bold"),
        bg="#eef2f7",
        fg="#2563eb"
    ).pack(
        anchor="w",
        pady=(0, 15)
    )


    # ========================================================
    # TABLE
    # ========================================================

    table_frame = tk.Frame(
        content,
        bg="white"
    )

    table_frame.pack(
        fill="both",
        expand=True
    )


    columns = (
        "Subject",
        "Quizzes",
        "Activities",
        "Midterm",
        "Final Exam",
        "Final Grade",
        "Status"
    )


    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )


    for column in columns:

        table.heading(
            column,
            text=column
        )

        table.column(
            column,
            width=130
        )


    table.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )


    cursor.execute("""
        SELECT
            subject,
            quizzes,
            activities,
            midterm,
            final_exam,
            final_grade
        FROM grades
        WHERE student_username = ?
        ORDER BY id DESC
    """, (
        username,
    ))


    rows = cursor.fetchall()


    for row in rows:

        final_grade = row[5]


        if final_grade >= 75:

            status = "PASSED"

        else:

            status = "FAILED"


        table.insert(
            "",
            tk.END,
            values=(
                row[0],
                f"{row[1]:.2f}",
                f"{row[2]:.2f}",
                f"{row[3]:.2f}",
                f"{row[4]:.2f}",
                f"{row[5]:.2f}",
                status
            )
        )


    # ========================================================
    # FORMULA
    # ========================================================

    formula_frame = tk.Frame(
        content,
        bg="white"
    )

    formula_frame.pack(
        fill="x",
        pady=15
    )


    tk.Label(
        formula_frame,
        text=(
            "GRADE FORMULA\n"
            "Quizzes 20% + Activities 20% + "
            "Midterm 25% + Final Exam 35%"
        ),
        font=("Arial", 10),
        bg="white",
        fg="#64748b",
        justify="center"
    ).pack(
        pady=15
    )


# ============================================================
# WINDOW RESIZE
# ============================================================

root.bind(
    "<Configure>",
    resize_background
)


# ============================================================
# CLOSE EVENT
# ============================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_system
)


# ============================================================
# START SYSTEM
# ============================================================

show_login_selection()

root.mainloop()