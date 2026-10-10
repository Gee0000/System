import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import math

from PIL import Image, ImageTk, ImageFilter, ImageDraw


# ============================================================
# SETTINGS
# ============================================================

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKGROUND_FILE = os.path.join(
    BASE_DIR,
    "background.jpg"
)

DATABASE_FILE = os.path.join(
    BASE_DIR,
    "smcii_grades.db"
)

DARK = "#10213F"
BLUE = "#2563EB"
GREEN = "#16A34A"
PURPLE = "#9333EA"
RED = "#DC2626"
WHITE = "#FFFFFF"
GRAY = "#64748B"
LIGHT = "#EEF4FA"


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect(DATABASE_FILE)
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

def create_default_user(username, password, role, full_name):

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
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "AUTOMATED SMCII GRADE CALCULATION PERFORMANCE SYSTEM"
)

root.geometry(
    f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
)

root.resizable(False, False)


# ============================================================
# LOAD BACKGROUND
# ============================================================

if not os.path.exists(BACKGROUND_FILE):

    messagebox.showerror(
        "Missing Background",
        "background.jpg was not found.\n\n"
        "Make sure background.jpg is in the same folder as main.py."
    )

    root.destroy()
    raise SystemExit


original_background = Image.open(
    BACKGROUND_FILE
).convert("RGB")


background_image = original_background.resize(
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    Image.Resampling.LANCZOS
)


background_photo = ImageTk.PhotoImage(
    background_image
)


# ============================================================
# BACKGROUND CANVAS
# ============================================================

background_canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    highlightthickness=0,
    bd=0
)

background_canvas.pack(
    fill="both",
    expand=True
)

background_canvas.create_image(
    0,
    0,
    image=background_photo,
    anchor="nw"
)


# ============================================================
# GLASS PANEL
# ============================================================

def create_glass_panel(
    canvas,
    x,
    y,
    width,
    height,
    radius=32,
    blur_radius=14,
    transparency=105
):

    # Crop background behind the panel
    crop = background_image.crop(
        (
            x,
            y,
            x + width,
            y + height
        )
    )

    # Blur the background
    blurred = crop.filter(
        ImageFilter.GaussianBlur(
            blur_radius
        )
    )

    # Transparent white glass layer
    glass_overlay = Image.new(
        "RGBA",
        (width, height),
        (255, 255, 255, transparency)
    )

    blurred = blurred.convert("RGBA")

    glass_panel = Image.alpha_composite(
        blurred,
        glass_overlay
    )

    # Rounded corners
    mask = Image.new(
        "L",
        (width, height),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.rounded_rectangle(
        (
            0,
            0,
            width - 1,
            height - 1
        ),
        radius=radius,
        fill=255
    )

    glass_panel.putalpha(mask)

    panel_photo = ImageTk.PhotoImage(
        glass_panel
    )

    canvas.create_image(
        x,
        y,
        image=panel_photo,
        anchor="nw"
    )

    # Keep image reference
    canvas.glass_image = panel_photo

    # NO WHITE BORDER HERE

    return panel_photo


# ============================================================
# DARKER BUTTON COLOR
# ============================================================

def darken_color(color):

    colors = {

        "#2563EB": "#1D4ED8",

        "#16A34A": "#15803D",

        "#9333EA": "#7E22CE",

        "#DC2626": "#B91C1C"

    }

    return colors.get(
        color,
        color
    )


# ============================================================
# ROUNDED BUTTON
# ============================================================

def rounded_button(
    canvas,
    x,
    y,
    width,
    height,
    text,
    color,
    command,
    font=("Arial", 12, "bold")
):

    radius = 18

    points = []

    # Top
    points.append(
        (x + radius, y)
    )

    points.append(
        (x + width - radius, y)
    )

    # Top-right curve
    for i in range(11):

        angle = -90 + (90 * i / 10)

        px = (
            x
            + width
            - radius
            + radius * math.cos(math.radians(angle))
        )

        py = (
            y
            + radius
            + radius * math.sin(math.radians(angle))
        )

        points.append(
            (px, py)
        )

    # Right
    points.append(
        (x + width, y + radius)
    )

    points.append(
        (x + width, y + height - radius)
    )

    # Bottom-right curve
    for i in range(11):

        angle = 0 + (90 * i / 10)

        px = (
            x
            + width
            - radius
            + radius * math.cos(math.radians(angle))
        )

        py = (
            y
            + height
            - radius
            + radius * math.sin(math.radians(angle))
        )

        points.append(
            (px, py)
        )

    # Bottom
    points.append(
        (x + width - radius, y + height)
    )

    points.append(
        (x + radius, y + height)
    )

    # Bottom-left curve
    for i in range(11):

        angle = 90 + (90 * i / 10)

        px = (
            x
            + radius
            + radius * math.cos(math.radians(angle))
        )

        py = (
            y
            + height
            - radius
            + radius * math.sin(math.radians(angle))
        )

        points.append(
            (px, py)
        )

    # Left
    points.append(
        (x, y + height - radius)
    )

    points.append(
        (x, y + radius)
    )

    # Top-left curve
    for i in range(11):

        angle = 180 + (90 * i / 10)

        px = (
            x
            + radius
            + radius * math.cos(math.radians(angle))
        )

        py = (
            y
            + radius
            + radius * math.sin(math.radians(angle))
        )

        points.append(
            (px, py)
        )

    polygon_points = []

    for point in points:
        polygon_points.extend(point)

    button_id = canvas.create_polygon(
        polygon_points,
        fill=color,
        outline="",
        smooth=True
    )

    text_id = canvas.create_text(
        x + width / 2,
        y + height / 2,
        text=text,
        fill="white",
        font=font
    )

    # Hover
    def enter(event):

        canvas.itemconfig(
            button_id,
            fill=darken_color(color)
        )

    def leave(event):

        canvas.itemconfig(
            button_id,
            fill=color
        )

    def click(event):

        command()

    canvas.tag_bind(
        button_id,
        "<Enter>",
        enter
    )

    canvas.tag_bind(
        text_id,
        "<Enter>",
        enter
    )

    canvas.tag_bind(
        button_id,
        "<Leave>",
        leave
    )

    canvas.tag_bind(
        text_id,
        "<Leave>",
        leave
    )

    canvas.tag_bind(
        button_id,
        "<Button-1>",
        click
    )

    canvas.tag_bind(
        text_id,
        "<Button-1>",
        click
    )

    return button_id, text_id


# ============================================================
# CLEAR SCREEN
# ============================================================

def clear_window():

    for widget in root.winfo_children():

        if widget != background_canvas:
            widget.destroy()

    background_canvas.delete(
        "all"
    )

    background_canvas.create_image(
        0,
        0,
        image=background_photo,
        anchor="nw"
    )


# ============================================================
# LOGOUT
# ============================================================

def logout():

    show_login_selection()


# ============================================================
# LOGIN SELECTION
# ============================================================

def show_login_selection():

    clear_window()

    # Glass panel
    panel_x = 280
    panel_y = 75
    panel_width = 540
    panel_height = 570

    create_glass_panel(
        background_canvas,
        panel_x,
        panel_y,
        panel_width,
        panel_height,
        radius=32,
        blur_radius=14,
        transparency=105
    )

    # Title
    background_canvas.create_text(
        550,
        125,
        text="SMCII",
        font=("Arial", 42, "bold"),
        fill=DARK
    )

    background_canvas.create_text(
        550,
        175,
        text="PORTAL",
        font=("Arial", 42, "bold"),
        fill=BLUE
    )

    # Subtitle
    background_canvas.create_text(
        550,
        235,
        text="Automated Grade Calculation\nPerformance System",
        font=("Arial", 13),
        fill=GRAY,
        justify="center"
    )

    # Line
    background_canvas.create_line(
        350,
        290,
        750,
        290,
        fill=BLUE,
        width=3
    )

    # Login title
    background_canvas.create_text(
        550,
        335,
        text="SELECT YOUR LOGIN TYPE",
        font=("Arial", 19, "bold"),
        fill=DARK
    )

    # Admin
    rounded_button(
        background_canvas,
        395,
        370,
        310,
        55,
        "ADMIN LOGIN",
        BLUE,
        lambda: show_role_login("Admin")
    )

    # Teacher
    rounded_button(
        background_canvas,
        395,
        440,
        310,
        55,
        "TEACHER LOGIN",
        GREEN,
        lambda: show_role_login("Teacher")
    )

    # Student
    rounded_button(
        background_canvas,
        395,
        510,
        310,
        55,
        "STUDENT LOGIN",
        PURPLE,
        lambda: show_role_login("Student")
    )

    # Footer
    background_canvas.create_text(
        550,
        625,
        text="@GogonsAndFriends  SMCII Portal Management System",
        font=("Arial", 9),
        fill=GRAY
    )


# ============================================================
# ROLE LOGIN
# ============================================================

def show_role_login(role):

    clear_window()

    # Glass login panel
    panel_x = 300
    panel_y = 90
    panel_width = 500
    panel_height = 520

    create_glass_panel(
        background_canvas,
        panel_x,
        panel_y,
        panel_width,
        panel_height,
        radius=32,
        blur_radius=15,
        transparency=120
    )

    # Role title
    background_canvas.create_text(
        550,
        150,
        text=role.upper() + " LOGIN",
        font=("Arial", 28, "bold"),
        fill=DARK
    )

    background_canvas.create_text(
        550,
        195,
        text="Enter your account details",
        font=("Arial", 12),
        fill=GRAY
    )

    # Username label
    background_canvas.create_text(
        390,
        250,
        text="Username",
        font=("Arial", 11, "bold"),
        fill=DARK,
        anchor="w"
    )

    username_entry = tk.Entry(
        root,
        font=("Arial", 13),
        width=30,
        bg="#FFFFFF",
        fg=DARK,
        relief="flat",
        bd=0,
        highlightthickness=2,
        highlightbackground="#D5DEEA",
        highlightcolor=BLUE
    )

    username_entry.place(
        x=390,
        y=270,
        width=320,
        height=40
    )

    # Password label
    background_canvas.create_text(
        390,
        335,
        text="Password",
        font=("Arial", 11, "bold"),
        fill=DARK,
        anchor="w"
    )

    password_entry = tk.Entry(
        root,
        font=("Arial", 13),
        width=30,
        show="*",
        bg="#FFFFFF",
        fg=DARK,
        relief="flat",
        bd=0,
        highlightthickness=2,
        highlightbackground="#D5DEEA",
        highlightcolor=BLUE
    )

    password_entry.place(
        x=390,
        y=355,
        width=270,
        height=40
    )

    # Show / Hide password
    def toggle_password():

        if password_entry.cget("show") == "*":

            password_entry.config(
                show=""
            )

            eye_button.config(
                text="HIDE"
            )

        else:

            password_entry.config(
                show="*"
            )

            eye_button.config(
                text="SHOW"
            )

    eye_button = tk.Button(
        root,
        text="SHOW",
        command=toggle_password,
        font=("Arial", 9, "bold"),
        bg="#E8EEF7",
        fg=BLUE,
        activebackground="#DCE6F5",
        relief="flat",
        bd=0,
        cursor="hand2"
    )

    eye_button.place(
        x=665,
        y=355,
        width=45,
        height=40
    )

    # Login
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

    # Login button
    rounded_button(
        background_canvas,
        390,
        425,
        320,
        55,
        "LOGIN",
        BLUE,
        login
    )

    # Back button
    rounded_button(
        background_canvas,
        390,
        495,
        320,
        45,
        "BACK",
        GRAY,
        show_login_selection,
        font=("Arial", 10, "bold")
    )

    background_canvas.create_text(
        550,
        570,
        text="SMCII Secure Login",
        font=("Arial", 10),
        fill=GRAY
    )

    username_entry.focus()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def show_admin_dashboard(username, full_name):

    clear_window()

    header = tk.Frame(
        root,
        bg=DARK,
        height=70
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text="ADMIN DASHBOARD",
        font=("Arial", 20, "bold"),
        bg=DARK,
        fg=WHITE
    ).pack(
        side="left",
        padx=25,
        pady=18
    )

    tk.Button(
        header,
        text="LOGOUT",
        command=logout,
        bg=RED,
        fg=WHITE,
        relief="flat",
        width=10,
        cursor="hand2"
    ).pack(
        side="right",
        padx=20
    )

    content = tk.Frame(
        root,
        bg=LIGHT
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
        bg=LIGHT,
        fg=DARK
    ).pack(
        anchor="w",
        pady=10
    )

    # Add User
    user_frame = tk.LabelFrame(
        content,
        text="ADD USER",
        font=("Arial", 12, "bold"),
        bg=WHITE,
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
        bg=WHITE
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
        bg=WHITE
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
        bg=WHITE
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
        bg=WHITE
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

    role_combo.set(
        "Student"
    )

    # User table
    list_frame = tk.LabelFrame(
        content,
        text="REGISTERED USERS",
        font=("Arial", 12, "bold"),
        bg=WHITE,
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
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        width=18,
        cursor="hand2"
    ).grid(
        row=2,
        column=0,
        columnspan=4,
        pady=12
    )

    load_users()


# ============================================================
# TEACHER DASHBOARD
# ============================================================

def show_teacher_dashboard(username, full_name):

    clear_window()

    header = tk.Frame(
        root,
        bg=DARK,
        height=70
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text="TEACHER DASHBOARD",
        font=("Arial", 20, "bold"),
        bg=DARK,
        fg=WHITE
    ).pack(
        side="left",
        padx=25,
        pady=18
    )

    tk.Button(
        header,
        text="LOGOUT",
        command=logout,
        bg=RED,
        fg=WHITE,
        relief="flat",
        width=10,
        cursor="hand2"
    ).pack(
        side="right",
        padx=20
    )

    content = tk.Frame(
        root,
        bg=LIGHT
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
        bg=LIGHT,
        fg=DARK
    ).pack(
        anchor="w",
        pady=8
    )

    # Grade input
    grade_frame = tk.LabelFrame(
        content,
        text="ENTER STUDENT GRADE",
        font=("Arial", 12, "bold"),
        bg=WHITE,
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
            bg=WHITE
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

    # Grade table
    table_frame = tk.LabelFrame(
        content,
        text="SUBMITTED GRADES",
        font=("Arial", 12, "bold"),
        bg=WHITE,
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

    # Load grades
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

    # Save grade
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
                "Please enter valid numbers."
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
            f"Final Grade: {final_grade:.2f}"
        )

        for entry in entries.values():

            entry.delete(
                0,
                tk.END
            )

        load_grades()

    tk.Button(
        grade_frame,
        text="CALCULATE AND SAVE",
        command=save_grade,
        bg=BLUE,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        width=25,
        cursor="hand2"
    ).grid(
        row=3,
        column=0,
        columnspan=4,
        pady=12
    )

    load_grades()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def show_student_dashboard(username, full_name):

    clear_window()

    header = tk.Frame(
        root,
        bg=DARK,
        height=70
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text="STUDENT DASHBOARD",
        font=("Arial", 20, "bold"),
        bg=DARK,
        fg=WHITE
    ).pack(
        side="left",
        padx=25,
        pady=18
    )

    tk.Button(
        header,
        text="LOGOUT",
        command=logout,
        bg=RED,
        fg=WHITE,
        relief="flat",
        width=10,
        cursor="hand2"
    ).pack(
        side="right",
        padx=20
    )

    content = tk.Frame(
        root,
        bg=LIGHT
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
        bg=LIGHT,
        fg=DARK
    ).pack(
        anchor="w",
        pady=8
    )

    tk.Label(
        content,
        text="YOUR ACADEMIC PERFORMANCE",
        font=("Arial", 13, "bold"),
        bg=LIGHT,
        fg=BLUE
    ).pack(
        anchor="w",
        pady=(0, 15)
    )

    table_frame = tk.Frame(
        content,
        bg=WHITE
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

    formula_frame = tk.Frame(
        content,
        bg=WHITE
    )

    formula_frame.pack(
        fill="x",
        pady=15
    )

    tk.Label(
        formula_frame,
        text=(
            "GRADE FORMULA\n\n"
            "Quizzes 20% + Activities 20% + "
            "Midterm 25% + Final Exam 35%"
        ),
        font=("Arial", 10),
        bg=WHITE,
        fg=GRAY,
        justify="center"
    ).pack(
        pady=15
    )


# ============================================================
# START SYSTEM
# ============================================================

show_login_selection()


# ============================================================
# CLOSE DATABASE SAFELY
# ============================================================

def close_application():

    try:
        conn.close()
    except:
        pass

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# RUN
# ============================================================

root.mainloop()
