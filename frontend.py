"""Frontend for the SMCII Grade Calculation Performance System."""

import os
import math
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk, ImageFilter, ImageDraw

from backend import (
    data_store,
    save_data,
    authenticate_user,
    add_user,
    add_grade,
    grades_for_student,
    grades_for_teacher,
    TERM_NAMES,
    ASSESSMENT_NAMES,
    ASSESSMENT_LABELS,
)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_FILE = os.path.join(BASE_DIR, "background.jpg")

DARK = "#10213F"
BLUE = "#2563EB"
GREEN = "#16A34A"
PURPLE = "#9333EA"
RED = "#DC2626"
WHITE = "#FFFFFF"
GRAY = "#64748B"
LIGHT = "#EEF4FA"
BORDER = "#D5DEEA"

root = tk.Tk()
root.title("AUTOMATED SMCII GRADE CALCULATION PERFORMANCE SYSTEM")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.configure(bg=LIGHT)


# --------------------------------------------------
# BACKGROUND
# --------------------------------------------------

background_image = Image.new(
    "RGB",
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    "#DCE8F7"
)

if os.path.exists(BACKGROUND_FILE):
    try:
        original_background = Image.open(
            BACKGROUND_FILE
        ).convert("RGB")

        background_image = original_background.resize(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            Image.Resampling.LANCZOS
        )

    except (OSError, ValueError):
        pass

background_photo = ImageTk.PhotoImage(background_image)

background_canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    highlightthickness=0,
    bd=0
)

background_canvas.place(
    x=0,
    y=0,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT
)

background_canvas.glass_images = []


def draw_background():
    background_canvas.delete("all")

    background_canvas.create_image(
        0,
        0,
        image=background_photo,
        anchor="nw",
        tags="background"
    )

    background_canvas.glass_images = []


def clear_screen():
    for widget in root.winfo_children():
        if widget is not background_canvas:
            widget.destroy()

    draw_background()


# --------------------------------------------------
# GLASS PANEL
# --------------------------------------------------

def create_glass_panel(
    canvas,
    x,
    y,
    width,
    height,
    radius=32,
    blur_radius=15,
    transparency=120
):
    crop = background_image.crop(
        (x, y, x + width, y + height)
    )

    blurred = crop.filter(
        ImageFilter.GaussianBlur(blur_radius)
    ).convert("RGBA")

    overlay = Image.new(
        "RGBA",
        (width, height),
        (255, 255, 255, transparency)
    )

    glass_panel = Image.alpha_composite(
        blurred,
        overlay
    )

    mask = Image.new(
        "L",
        (width, height),
        0
    )

    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        fill=255
    )

    glass_panel.putalpha(mask)

    panel_photo = ImageTk.PhotoImage(glass_panel)

    canvas.create_image(
        x,
        y,
        image=panel_photo,
        anchor="nw"
    )

    canvas.glass_images.append(panel_photo)

    return panel_photo


# --------------------------------------------------
# MODERN ROUNDED BUTTONS
# --------------------------------------------------

def darken_color(color):
    colors = {
        BLUE: "#1D4ED8",
        GREEN: "#15803D",
        PURPLE: "#7E22CE",
        RED: "#B91C1C",
        GRAY: "#475569",
    }

    return colors.get(color, color)


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
    radius = min(18, height // 2)

    def make_points():
        points = []

        corners = [
            (
                x + width - radius,
                y + radius,
                -90,
                0
            ),
            (
                x + width - radius,
                y + height - radius,
                0,
                90
            ),
            (
                x + radius,
                y + height - radius,
                90,
                180
            ),
            (
                x + radius,
                y + radius,
                180,
                270
            ),
        ]

        for cx, cy, start_angle, end_angle in corners:
            for i in range(13):
                angle = math.radians(
                    start_angle
                    + (end_angle - start_angle) * i / 12
                )

                points.append((
                    cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle)
                ))

        return [
            value
            for point in points
            for value in point
        ]

    canvas.create_polygon(
        [
            value + (4 if index % 2 == 1 else 0)
            for index, value in enumerate(make_points())
        ],
        fill="#AAB7C8",
        outline="",
        smooth=True
    )

    button_id = canvas.create_polygon(
        make_points(),
        fill=color,
        outline="",
        smooth=True
    )

    text_id = canvas.create_text(
        x + width / 2,
        y + height / 2,
        text=text,
        fill=WHITE,
        font=font
    )

    def enter(event):
        canvas.itemconfig(
            button_id,
            fill=darken_color(color)
        )
        canvas.configure(cursor="hand2")

    def leave(event):
        canvas.itemconfig(
            button_id,
            fill=color
        )
        canvas.configure(cursor="")

    def click(event):
        command()

    for item in (button_id, text_id):
        canvas.tag_bind(item, "<Enter>", enter)
        canvas.tag_bind(item, "<Leave>", leave)
        canvas.tag_bind(item, "<Button-1>", click)

    return button_id, text_id


# --------------------------------------------------
# COMMON WIDGETS
# --------------------------------------------------

def make_button(parent, text, command, color=BLUE, **kwargs):
    font = kwargs.pop("font", ("Arial", 10, "bold"))

    return tk.Button(
        parent,
        text=text,
        command=command,
        font=font,
        bg=color,
        fg=WHITE,
        activebackground=darken_color(color),
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        padx=10,
        pady=6,
        **kwargs
    )


def make_entry(parent, width=24, show=None):
    options = {
        "font": ("Arial", 10),
        "relief": "solid",
        "bd": 1,
        "highlightthickness": 1,
        "highlightbackground": BORDER,
        "highlightcolor": BLUE,
    }

    if show is not None:
        options["show"] = show

    return tk.Entry(parent, width=width, **options)


def build_header(title, full_name):
    header = tk.Frame(root, bg=DARK, height=70)
    header.place(
        x=0,
        y=0,
        width=WINDOW_WIDTH,
        height=70
    )

    tk.Label(
        header,
        text=title,
        font=("Arial", 18, "bold"),
        bg=DARK,
        fg=WHITE
    ).pack(side="left", padx=24, pady=18)

    tk.Label(
        header,
        text=full_name,
        font=("Arial", 10),
        bg=DARK,
        fg=WHITE
    ).pack(side="left", padx=12)

    make_button(
        header,
        "LOGOUT",
        logout,
        RED
    ).pack(side="right", padx=20, pady=14)


# --------------------------------------------------
# LOGIN TYPE SELECTION
# --------------------------------------------------

def logout():
    show_login_selection()


def show_login_selection():
    clear_screen()

    create_glass_panel(
        background_canvas,
        280,
        75,
        540,
        575,
        radius=32,
        blur_radius=16,
        transparency=110
    )

    background_canvas.create_text(
        550,
        135,
        text="SMCII",
        font=("Arial", 42, "bold"),
        fill=DARK
    )

    background_canvas.create_text(
        550,
        180,
        text="PORTAL",
        font=("Arial", 42, "bold"),
        fill=BLUE
    )

    background_canvas.create_text(
        550,
        226,
        text="Automated Grade Calculation\nPerformance System",
        font=("Arial", 13),
        fill=GRAY,
        justify="center"
    )

    background_canvas.create_line(
        350,
        275,
        750,
        275,
        fill=BLUE,
        width=3
    )

    background_canvas.create_text(
        550,
        315,
        text="SELECT YOUR LOGIN TYPE",
        font=("Arial", 19, "bold"),
        fill=DARK
    )

    rounded_button(
        background_canvas,
        390,
        350,
        320,
        55,
        "ADMIN LOGIN",
        BLUE,
        lambda: show_login("Admin")
    )

    rounded_button(
        background_canvas,
        390,
        420,
        320,
        55,
        "TEACHER LOGIN",
        GREEN,
        lambda: show_login("Teacher")
    )

    rounded_button(
        background_canvas,
        390,
        490,
        320,
        55,
        "STUDENT LOGIN",
        PURPLE,
        lambda: show_login("Student")
    )

    background_canvas.create_text(
        550,
        615,
        text="SMCII  |  PORTAL MANAGEMENT SYSTEM",
        font=("Arial", 9),
        fill=GRAY
    )


# --------------------------------------------------
# LOGIN FORM
# --------------------------------------------------

def show_login(role):
    clear_screen()

    create_glass_panel(
        background_canvas,
        300,
        90,
        500,
        520,
        radius=32,
        blur_radius=15,
        transparency=120
    )

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

    background_canvas.create_line(
        390,
        220,
        710,
        220,
        fill=BLUE,
        width=2
    )

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
        bg=WHITE,
        fg=DARK,
        relief="flat",
        bd=0,
        highlightthickness=2,
        highlightbackground=BORDER,
        highlightcolor=BLUE
    )

    username_entry.place(
        x=390,
        y=270,
        width=320,
        height=40
    )

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
        show="*",
        bg=WHITE,
        fg=DARK,
        relief="flat",
        bd=0,
        highlightthickness=2,
        highlightbackground=BORDER,
        highlightcolor=BLUE
    )

    password_entry.place(
        x=390,
        y=355,
        width=270,
        height=40
    )

    def toggle_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
            eye_button.config(text="HIDE")
        else:
            password_entry.config(show="*")
            eye_button.config(text="SHOW")

    eye_button = tk.Button(
        root,
        text="SHOW",
        command=toggle_password,
        font=("Arial", 8, "bold"),
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

    def login():
        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password.strip():
            messagebox.showerror(
                "Login Error",
                "Please enter your username and password.",
                parent=root
            )
            return

        user = authenticate_user(
            username,
            password,
            role
        )

        if user is None:
            messagebox.showerror(
                "Login Failed",
                "Invalid username, password, or login type.",
                parent=root
            )

            password_entry.delete(0, tk.END)
            password_entry.focus_set()
            return

        account_username = user.get("username", username)
        full_name = user.get("full_name", username)

        if role == "Admin":
            show_admin_dashboard(
                full_name,
                account_username
            )
        elif role == "Teacher":
            show_teacher_dashboard(
                full_name,
                account_username
            )
        else:
            show_student_dashboard(
                account_username,
                full_name
            )

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
        text="SMCII SECURE LOGIN",
        font=("Arial", 10),
        fill=GRAY
    )

    username_entry.bind(
        "<Return>",
        lambda event: password_entry.focus_set()
    )

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )

    username_entry.focus_set()


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

def show_admin_dashboard(full_name, admin_username):
    clear_screen()
    build_header("ADMIN DASHBOARD", full_name)

    content = tk.Frame(root, bg=LIGHT)
    content.place(
        x=0,
        y=70,
        width=WINDOW_WIDTH,
        height=630
    )

    title_row = tk.Frame(content, bg=LIGHT)
    title_row.pack(
        fill="x",
        padx=25,
        pady=(12, 8)
    )

    tk.Label(
        title_row,
        text="User Management",
        font=("Arial", 20, "bold"),
        bg=LIGHT,
        fg=DARK
    ).pack(side="left")

    make_button(
        title_row,
        "ACCOUNTS",
        lambda: show_accounts(
            full_name,
            admin_username,
            "Teacher"
        ),
        GREEN
    ).pack(side="left", padx=18)

    form = tk.LabelFrame(
        content,
        text="Create Account",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        padx=12,
        pady=8
    )

    form.pack(
        fill="x",
        padx=25,
        pady=4
    )

    entries = {}

    field_layout = [
        ("Username", 0, 0),
        ("Password", 0, 2),
        ("Full Name", 1, 0),
    ]

    for name, row, col in field_layout:
        tk.Label(
            form,
            text=name + ":",
            bg=WHITE
        ).grid(
            row=row,
            column=col,
            padx=8,
            pady=6,
            sticky="w"
        )

        entry = make_entry(form, width=23)

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=6,
            sticky="w"
        )

        entries[name] = entry

    tk.Label(
        form,
        text="Role:",
        bg=WHITE
    ).grid(
        row=1,
        column=2,
        padx=8,
        pady=6,
        sticky="w"
    )

    role_box = ttk.Combobox(
        form,
        values=["Admin", "Teacher", "Student"],
        state="readonly",
        width=21
    )

    role_box.grid(
        row=1,
        column=3,
        padx=8,
        pady=6,
        sticky="w"
    )

    role_box.set("Student")

    table_frame = tk.LabelFrame(
        content,
        text="Registered Accounts",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        padx=8,
        pady=8
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(8, 12)
    )

    columns = ("ID", "Username", "Full Name", "Role")

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    for column, width in zip(
        columns,
        (65, 200, 420, 150)
    ):
        table.heading(column, text=column)
        table.column(column, width=width, anchor="w")

    table.pack(fill="both", expand=True)

    def refresh_users():
        table.delete(*table.get_children())

        for user in sorted(
            data_store["users"],
            key=lambda item: item.get("id", 0)
        ):
            table.insert(
                "",
                "end",
                values=(
                    user.get("id", ""),
                    user.get("username", ""),
                    user.get("full_name", ""),
                    user.get("role", "")
                )
            )

    def create_account():
        success, message = add_user(
            entries["Username"].get(),
            entries["Password"].get(),
            entries["Full Name"].get(),
            role_box.get()
        )

        if success:
            messagebox.showinfo(
                "Success",
                message,
                parent=root
            )

            for entry in entries.values():
                entry.delete(0, tk.END)

            refresh_users()

        else:
            messagebox.showerror(
                "Account Error",
                message,
                parent=root
            )

    make_button(
        form,
        "ADD ACCOUNT",
        create_account,
        BLUE
    ).grid(
        row=2,
        column=0,
        columnspan=4,
        pady=8
    )

    refresh_users()


# --------------------------------------------------
# ADMIN ACCOUNTS
# --------------------------------------------------

def show_accounts(
    admin_full_name,
    admin_username,
    account_type="Teacher"
):
    clear_screen()
    build_header("ADMIN ACCOUNTS", admin_full_name)

    content = tk.Frame(root, bg=LIGHT)
    content.place(
        x=0,
        y=70,
        width=WINDOW_WIDTH,
        height=630
    )

    top = tk.Frame(content, bg=LIGHT)
    top.pack(
        fill="x",
        padx=20,
        pady=(10, 8)
    )

    tk.Label(
        top,
        text="Accounts",
        font=("Arial", 20, "bold"),
        bg=LIGHT,
        fg=DARK
    ).pack(side="left", padx=(0, 12))

    make_button(
        top,
        "TEACHERS",
        lambda: show_accounts(
            admin_full_name,
            admin_username,
            "Teacher"
        ),
        BLUE if account_type == "Teacher" else GRAY
    ).pack(side="left", padx=4)

    make_button(
        top,
        "STUDENTS",
        lambda: show_accounts(
            admin_full_name,
            admin_username,
            "Student"
        ),
        BLUE if account_type == "Student" else GRAY
    ).pack(side="left", padx=4)

    make_button(
        top,
        "BACK TO USER MANAGEMENT",
        lambda: show_admin_dashboard(
            admin_full_name,
            admin_username
        ),
        GRAY
    ).pack(side="right")

    body = tk.Frame(content, bg=LIGHT)
    body.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 14)
    )

    left = tk.LabelFrame(
        body,
        text=f"{account_type} Accounts",
        bg=WHITE,
        font=("Arial", 10, "bold"),
        padx=6,
        pady=6
    )

    left.place(
        x=0,
        y=0,
        width=415,
        height=520
    )

    account_table = ttk.Treeview(
        left,
        columns=("Username", "Full Name"),
        show="headings"
    )

    account_table.heading("Username", text="Username")
    account_table.heading("Full Name", text="Full Name")
    account_table.column("Username", width=125, anchor="w")
    account_table.column("Full Name", width=225, anchor="w")

    account_table.pack(fill="both", expand=True)

    right = tk.LabelFrame(
        body,
        text="Account Details",
        bg=WHITE,
        font=("Arial", 10, "bold"),
        padx=10,
        pady=8
    )

    right.place(
        x=430,
        y=0,
        width=630,
        height=520
    )

    def clear_details():
        for widget in right.winfo_children():
            widget.destroy()

    def detail_line(parent, label, value, row):
        tk.Label(
            parent,
            text=label + ":",
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 9, "bold")
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=6,
            pady=3
        )

        tk.Label(
            parent,
            text=str(value if value not in (None, "") else "—"),
            bg=WHITE,
            fg=DARK,
            font=("Arial", 9)
        ).grid(
            row=row,
            column=1,
            sticky="w",
            padx=6,
            pady=3
        )

    def render_student_subject(username, subject, status_frame):
        for widget in status_frame.winfo_children():
            widget.destroy()

        matching = [
            grade for grade in grades_for_student(username)
            if grade.get("subject", "") == subject
        ]

        if not matching:
            tk.Label(
                status_frame,
                text="No grade records for this subject.",
                bg=WHITE,
                fg=GRAY
            ).pack(anchor="w", pady=8)
            return

        grade = matching[0]
        terms = grade.get("terms")

        if not isinstance(terms, dict):
            tk.Label(
                status_frame,
                text=(
                    "This older grade record has no separate "
                    "Prelim, Midterm, Semifinal, or Finals breakdown."
                ),
                bg=WHITE,
                fg=RED,
                wraplength=550,
                justify="left"
            ).pack(anchor="w", pady=5)

            legacy_columns = ("Assessment", "Saved Value")

            legacy_table = ttk.Treeview(
                status_frame,
                columns=legacy_columns,
                show="headings",
                height=5
            )

            legacy_table.heading(
                "Assessment",
                text="Assessment"
            )
            legacy_table.heading(
                "Saved Value",
                text="Saved Value"
            )

            legacy_table.column("Assessment", width=180)
            legacy_table.column("Saved Value", width=160)

            legacy_table.pack(fill="x", pady=5)

            legacy_items = [
                ("Quizzes", grade.get("quizzes", "—")),
                ("Activities", grade.get("activities", "—")),
                ("Midterm", grade.get("midterm", "—")),
                ("Final Exam", grade.get("final_exam", "—")),
                ("Final Grade", grade.get("final_grade", "—")),
            ]

            for item, value in legacy_items:
                legacy_table.insert(
                    "",
                    "end",
                    values=(item, value)
                )

            return

        columns = (
            "Assessment",
            "Prelim",
            "Midterm",
            "Semifinal",
            "Finals"
        )

        grade_table = ttk.Treeview(
            status_frame,
            columns=columns,
            show="headings",
            height=5
        )

        widths = (155, 82, 82, 92, 82)

        for column, width in zip(columns, widths):
            grade_table.heading(column, text=column)
            grade_table.column(
                column,
                width=width,
                anchor="center"
            )

        grade_table.pack(fill="x", pady=(3, 7))

        for key in ASSESSMENT_NAMES:
            values = [ASSESSMENT_LABELS[key]]

            for term in TERM_NAMES:
                value = terms.get(term, {}).get(key, "—")

                if isinstance(value, (int, float)):
                    value = f"{value:.2f}"

                values.append(value)

            grade_table.insert(
                "",
                "end",
                values=values
            )

        term_values = ["Term Grade"]

        for term in TERM_NAMES:
            value = terms.get(term, {}).get("term_grade", "—")

            if isinstance(value, (int, float)):
                value = f"{value:.2f}"

            term_values.append(value)

        grade_table.insert(
            "",
            "end",
            values=term_values
        )

        overall = grade.get("final_grade", 0)

        tk.Label(
            status_frame,
            text=(
                f"Overall Grade: {float(overall):.2f}    "
                f"| Record ID: {grade.get('id', '—')}"
            ),
            bg=WHITE,
            fg=DARK,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=4)

    def show_selected_account(event=None):
        selected = account_table.selection()

        if not selected:
            return

        selected_values = account_table.item(
            selected[0],
            "values"
        )

        username = selected_values[0]

        user = next(
            (
                account for account in data_store["users"]
                if account.get("username") == username
            ),
            None
        )

        if user is None:
            return

        clear_details()

        info = tk.Frame(right, bg=WHITE)
        info.pack(fill="x", anchor="n")

        detail_line(info, "Account ID", user.get("id"), 0)
        detail_line(info, "Full Name", user.get("full_name"), 1)
        detail_line(info, "Username", user.get("username"), 2)
        detail_line(info, "Role", user.get("role"), 3)

        if account_type == "Teacher":
            records = grades_for_teacher(username)

            subjects = sorted({
                record.get("subject", "")
                for record in records
                if record.get("subject")
            })

            tk.Label(
                right,
                text=f"Grade records submitted: {len(records)}",
                bg=WHITE,
                fg=BLUE,
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(12, 4))

            tk.Label(
                right,
                text=(
                    "Subjects: "
                    + (", ".join(subjects) if subjects else "None yet")
                ),
                bg=WHITE,
                fg=DARK,
                wraplength=570,
                justify="left"
            ).pack(anchor="w", pady=3)

            if records:
                tk.Label(
                    right,
                    text="Recent Grade Submissions",
                    bg=WHITE,
                    fg=DARK,
                    font=("Arial", 10, "bold")
                ).pack(anchor="w", pady=(10, 4))

                recent_table = ttk.Treeview(
                    right,
                    columns=("Student", "Subject", "Overall Grade"),
                    show="headings",
                    height=9
                )

                for col, width in (
                    ("Student", 150),
                    ("Subject", 210),
                    ("Overall Grade", 120)
                ):
                    recent_table.heading(col, text=col)
                    recent_table.column(
                        col,
                        width=width,
                        anchor="w"
                    )

                recent_table.pack(fill="x", pady=3)

                for record in records[:10]:
                    overall = record.get("final_grade", "—")

                    if isinstance(overall, (int, float)):
                        overall = f"{overall:.2f}"

                    recent_table.insert(
                        "",
                        "end",
                        values=(
                            record.get("student_username", ""),
                            record.get("subject", ""),
                            overall
                        )
                    )
            else:
                tk.Label(
                    right,
                    text=(
                        "No grade submissions are linked "
                        "to this teacher account yet."
                    ),
                    bg=WHITE,
                    fg=GRAY,
                    wraplength=560,
                    justify="left"
                ).pack(anchor="w", pady=12)

        else:
            records = grades_for_student(username)

            subjects = sorted({
                record.get("subject", "")
                for record in records
                if record.get("subject")
            })

            tk.Label(
                right,
                text="Select a subject to view assessment details:",
                bg=WHITE,
                fg=DARK,
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(10, 4))

            subject_box = ttk.Combobox(
                right,
                values=subjects,
                state="readonly",
                width=42
            )
            subject_box.pack(anchor="w", pady=(0, 8))

            status_frame = tk.Frame(right, bg=WHITE)
            status_frame.pack(
                fill="both",
                expand=True,
                anchor="w"
            )

            if subjects:
                subject_box.set(subjects[0])

                subject_box.bind(
                    "<<ComboboxSelected>>",
                    lambda event: render_student_subject(
                        username,
                        subject_box.get(),
                        status_frame
                    )
                )

                render_student_subject(
                    username,
                    subjects[0],
                    status_frame
                )
            else:
                tk.Label(
                    status_frame,
                    text="This student has no grade records yet.",
                    bg=WHITE,
                    fg=GRAY
                ).pack(anchor="w", pady=8)

    accounts = sorted(
        [
            user for user in data_store["users"]
            if user.get("role", "").lower() == account_type.lower()
        ],
        key=lambda user: user.get("full_name", "").lower()
    )

    for user in accounts:
        account_table.insert(
            "",
            "end",
            values=(
                user.get("username", ""),
                user.get("full_name", "")
            )
        )

    account_table.bind(
        "<<TreeviewSelect>>",
        show_selected_account
    )

    if accounts:
        first = account_table.get_children()[0]
        account_table.selection_set(first)
        account_table.focus(first)
        show_selected_account()
    else:
        tk.Label(
            right,
            text=f"No {account_type.lower()} accounts found.",
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w", padx=10, pady=10)


# --------------------------------------------------
# TEACHER DASHBOARD
# --------------------------------------------------

def show_teacher_dashboard(full_name, teacher_username):
    clear_screen()
    build_header("TEACHER DASHBOARD", full_name)

    content = tk.Frame(root, bg=LIGHT)
    content.place(
        x=0,
        y=70,
        width=WINDOW_WIDTH,
        height=630
    )

    tk.Label(
        content,
        text="Grade Management",
        font=("Arial", 19, "bold"),
        bg=LIGHT,
        fg=DARK
    ).pack(anchor="w", padx=20, pady=(8, 5))

    form = tk.LabelFrame(
        content,
        text="Enter Student Assessment Scores",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        padx=10,
        pady=7
    )

    form.pack(fill="x", padx=20, pady=4)

    identity = tk.Frame(form, bg=WHITE)
    identity.pack(fill="x", pady=(0, 5))

    tk.Label(
        identity,
        text="Student Username:",
        bg=WHITE
    ).grid(
        row=0,
        column=0,
        padx=5,
        pady=4,
        sticky="w"
    )

    student_entry = make_entry(identity, width=25)
    student_entry.grid(
        row=0,
        column=1,
        padx=5,
        pady=4
    )

    tk.Label(
        identity,
        text="Subject:",
        bg=WHITE
    ).grid(
        row=0,
        column=2,
        padx=(18, 5),
        pady=4,
        sticky="w"
    )

    subject_entry = make_entry(identity, width=28)
    subject_entry.grid(
        row=0,
        column=3,
        padx=5,
        pady=4
    )

    score_frame = tk.Frame(form, bg=WHITE)
    score_frame.pack(fill="x")

    tk.Label(
        score_frame,
        text="Assessment",
        bg=WHITE,
        font=("Arial", 9, "bold"),
        width=19,
        anchor="w"
    ).grid(
        row=0,
        column=0,
        padx=4,
        pady=3,
        sticky="w"
    )

    for col, term in enumerate(TERM_NAMES, start=1):
        tk.Label(
            score_frame,
            text=term,
            bg=WHITE,
            fg=BLUE,
            font=("Arial", 9, "bold"),
            width=15
        ).grid(
            row=0,
            column=col,
            padx=4,
            pady=3
        )

    score_entries = {
        term: {} for term in TERM_NAMES
    }

    for row, key in enumerate(ASSESSMENT_NAMES, start=1):
        tk.Label(
            score_frame,
            text=ASSESSMENT_LABELS[key],
            bg=WHITE,
            width=19,
            anchor="w"
        ).grid(
            row=row,
            column=0,
            padx=4,
            pady=3,
            sticky="w"
        )

        for col, term in enumerate(TERM_NAMES, start=1):
            entry = make_entry(score_frame, width=13)
            entry.grid(
                row=row,
                column=col,
                padx=4,
                pady=3,
                ipady=2
            )
            score_entries[term][key] = entry

    tk.Label(
        form,
        text=(
            "Enter scores from 0 to 100. The four assessment types "
            "have equal weight within each term."
        ),
        bg=WHITE,
        fg=GRAY,
        font=("Arial", 8)
    ).pack(anchor="w", padx=5, pady=(3, 5))

    table_frame = tk.LabelFrame(
        content,
        text="Submitted Grade Records",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        padx=6,
        pady=6
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=7
    )

    columns = (
        "Student",
        "Subject",
        "Prelim",
        "Midterm",
        "Semifinal",
        "Finals",
        "Overall Grade"
    )

    grade_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=8
    )

    widths = (125, 180, 95, 95, 95, 95, 115)

    for column, width in zip(columns, widths):
        grade_table.heading(column, text=column)
        grade_table.column(
            column,
            width=width,
            anchor="center"
        )

    grade_table.pack(fill="both", expand=True)

    def refresh_grade_table():
        grade_table.delete(*grade_table.get_children())

        teacher_records = grades_for_teacher(teacher_username)

        for grade in teacher_records:
            terms = grade.get("terms", {})
            term_grades = []

            for term in TERM_NAMES:
                value = terms.get(term, {}).get("term_grade")

                if isinstance(value, (int, float)):
                    term_grades.append(f"{value:.2f}")
                else:
                    term_grades.append("Legacy")

            overall = grade.get("final_grade", "—")

            if isinstance(overall, (int, float)):
                overall = f"{overall:.2f}"

            grade_table.insert(
                "",
                "end",
                values=(
                    grade.get("student_username", ""),
                    grade.get("subject", ""),
                    *term_grades,
                    overall
                )
            )

    def handle_save_grade():
        student = student_entry.get().strip()
        subject = subject_entry.get().strip()

        if not student or not subject:
            messagebox.showerror(
                "Missing Information",
                "Enter the student's username and subject.",
                parent=root
            )
            return

        assessments = {}

        try:
            for term in TERM_NAMES:
                assessments[term] = {}

                for key in ASSESSMENT_NAMES:
                    value = score_entries[term][key].get().strip()
                    assessments[term][key] = float(value)

        except ValueError:
            messagebox.showerror(
                "Invalid Scores",
                "Enter all 16 assessment scores as numbers.",
                parent=root
            )
            return

        success, message = add_grade(
            student,
            subject,
            assessments,
            teacher_username=teacher_username
        )

        if success:
            messagebox.showinfo(
                "Grades Saved",
                message,
                parent=root
            )

            student_entry.delete(0, tk.END)
            subject_entry.delete(0, tk.END)

            for term in TERM_NAMES:
                for key in ASSESSMENT_NAMES:
                    score_entries[term][key].delete(0, tk.END)

            refresh_grade_table()

        else:
            messagebox.showerror(
                "Grade Error",
                message,
                parent=root
            )

    make_button(
        form,
        "CALCULATE AND SAVE GRADES",
        handle_save_grade,
        BLUE
    ).pack(anchor="e", padx=5, pady=(2, 0))

    refresh_grade_table()


# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

def show_student_dashboard(student_username, full_name):
    clear_screen()
    build_header("STUDENT DASHBOARD", full_name)

    content = tk.Frame(root, bg=LIGHT)
    content.place(
        x=0,
        y=70,
        width=WINDOW_WIDTH,
        height=630
    )

    tk.Label(
        content,
        text="My Academic Performance",
        font=("Arial", 20, "bold"),
        bg=LIGHT,
        fg=DARK
    ).pack(anchor="w", padx=24, pady=(12, 6))

    records = grades_for_student(student_username)

    subjects = sorted({
        record.get("subject", "")
        for record in records
        if record.get("subject")
    })

    selector = tk.Frame(content, bg=LIGHT)
    selector.pack(fill="x", padx=24, pady=4)

    tk.Label(
        selector,
        text="Choose Subject:",
        bg=LIGHT,
        fg=DARK,
        font=("Arial", 10, "bold")
    ).pack(side="left", padx=(0, 8))

    subject_box = ttk.Combobox(
        selector,
        values=subjects,
        state="readonly",
        width=35
    )
    subject_box.pack(side="left")

    detail = tk.LabelFrame(
        content,
        text="Assessment Details",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        padx=10,
        pady=10
    )

    detail.pack(
        fill="both",
        expand=True,
        padx=24,
        pady=10
    )

    def render_subject(event=None):
        for widget in detail.winfo_children():
            widget.destroy()

        subject = subject_box.get()

        matching = [
            grade for grade in records
            if grade.get("subject") == subject
        ]

        if not matching:
            tk.Label(
                detail,
                text="No grades are available for this subject.",
                bg=WHITE,
                fg=GRAY
            ).pack(anchor="w")
            return

        grade = matching[0]
        terms = grade.get("terms")

        if not isinstance(terms, dict):
            tk.Label(
                detail,
                text=(
                    "This older record does not contain separate "
                    "term assessment details."
                ),
                bg=WHITE,
                fg=RED
            ).pack(anchor="w")

            tk.Label(
                detail,
                text=(
                    f"Quizzes: {grade.get('quizzes', '—')}   "
                    f"Activities: {grade.get('activities', '—')}   "
                    f"Midterm: {grade.get('midterm', '—')}   "
                    f"Final Exam: {grade.get('final_exam', '—')}   "
                    f"Final Grade: {grade.get('final_grade', '—')}"
                ),
                bg=WHITE,
                fg=DARK,
                wraplength=950,
                justify="left"
            ).pack(anchor="w", pady=10)

            return

        columns = (
            "Assessment",
            "Prelim",
            "Midterm",
            "Semifinal",
            "Finals"
        )

        table = ttk.Treeview(
            detail,
            columns=columns,
            show="headings",
            height=7
        )

        for column, width in zip(
            columns,
            (210, 150, 150, 150, 150)
        ):
            table.heading(column, text=column)
            table.column(
                column,
                width=width,
                anchor="center"
            )

        table.pack(fill="x", pady=5)

        for key in ASSESSMENT_NAMES:
            values = [ASSESSMENT_LABELS[key]]

            for term in TERM_NAMES:
                value = terms.get(term, {}).get(key, "—")

                if isinstance(value, (int, float)):
                    value = f"{value:.2f}"

                values.append(value)

            table.insert("", "end", values=values)

        term_values = ["Term Grade"]

        for term in TERM_NAMES:
            value = terms.get(term, {}).get("term_grade", "—")

            if isinstance(value, (int, float)):
                value = f"{value:.2f}"

            term_values.append(value)

        table.insert("", "end", values=term_values)

        overall = float(grade.get("final_grade", 0))

        status = "PASSED" if overall >= 75 else "FAILED"

        tk.Label(
            detail,
            text=(
                f"Overall Grade: {overall:.2f}    "
                f"Status: {status}"
            ),
            bg=WHITE,
            fg=DARK,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=12)

        tk.Label(
            detail,
            text=(
                "Each assessment type has equal weight within its term. "
                "The four term grades have equal weight in the overall grade."
            ),
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 9),
            wraplength=950,
            justify="left"
        ).pack(anchor="w")

    subject_box.bind(
        "<<ComboboxSelected>>",
        render_subject
    )

    if subjects:
        subject_box.set(subjects[0])
        render_subject()
    else:
        tk.Label(
            detail,
            text="No grades have been entered for your account yet.",
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w")


# --------------------------------------------------
# CLOSE APPLICATION
# --------------------------------------------------

def close_application():
    try:
        save_data()
    except OSError as error:
        messagebox.showerror(
            "Save Error",
            f"Unable to save data: {error}",
            parent=root
        )

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)

show_login_selection()

root.mainloop()