"""Frontend for the SMCII Grade Calculation Performance System."""

import os
import math
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageEnhance

from backend import (
    data_store,
    save_data,
    authenticate_user,
    add_user,
    update_user,
    reset_password,
    set_user_active,
    delete_user,
    add_grade,
    save_term_grade,
    delete_grade,
    grades_for_student,
    grades_for_teacher,
    all_grade_records,
    users_by_role,
    find_user,
    find_grade_record,
    list_subjects,
    add_subject,
    remove_subject,
    subject_usage,
    subjects_for_teacher,
    teachers_for_subject,
    teacher_assignments,
    assign_subject_to_teacher,
    remove_subject_from_teacher,
    student_performance,
    teacher_subject_report,
    system_statistics,
    activity_entries,
    clear_activity_log,
    add_announcement,
    delete_announcement,
    all_announcements,
    announcements_for,
    ANNOUNCEMENT_AUDIENCES,
    find_student_by_reference,
    student_id_of,
    build_user_report,
    build_grade_report,
    build_statistics_report,
    build_activity_report,
    write_text_report,
    compute_term_grade,
    assessment_type_average,
    overall_grade_for_terms,
    completed_term_grades,
    calculate_assessment_percentage,
    add_assessment_score,
    edit_assessment_score,
    delete_assessment_score,
    assessment_records_for_student,
    assessment_records_for_teacher,
    tally_term_grade_for_student,
    grade_point_equivalent,
    SEMESTER_NAMES,
    current_school_year,
    semester_status_for,
    semester_open_for_entry,
    semester_completion_status,
    start_semester,
    complete_semester,
    reopen_semester,
    TERM_NAMES,
    ASSESSMENT_NAMES,
    ASSESSMENT_LABELS,
    ASSESSMENT_ITEMS,
    ASSESSMENT_WEIGHTS,
    ASSESSMENT_WEIGHT_LABELS,
    ROLES,
    PASSING_GRADE,
    format_display_time,
)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

BASE_WIDTH = 1100
BASE_HEIGHT = 700

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_FILE = os.path.join(BASE_DIR, "background.jpg")

BACKGROUND_ANIMATION = False
BACKGROUND_FPS = 60
BACKGROUND_ZOOM = 1.4
BACKGROUND_ORBIT_SPEED = 0.35
BACKGROUND_GLASS_REFRESH = 1
GLASS_BLUR_RADIUS = 15

BLUE = "#2563EB"
GREEN = "#16A34A"
PURPLE = "#9333EA"
RED = "#DC2626"
GRAY = "#475569"

ROLE_COLORS = {
    "Admin": BLUE,
    "Teacher": GREEN,
    "Student": PURPLE,
}

THEME_PALETTES = {
    "light": {
        "header_bg": "#10213F",
        "page_bg": "#EEF3FA",
        "surface": "#FFFFFF",
        "surface_alt": "#E8EEF7",
        "surface_alt_hover": "#DCE6F5",
        "text": "#14233B",
        "muted": "#52647A",
        "border": "#CCD6E2",
        "on_accent": "#FFFFFF",
        "glass": (255, 255, 255, 115),
        "shadow": "#AAB7C8"
    },
    "dark": {
        "header_bg": "#0B1220",
        "page_bg": "#0F172A",
        "surface": "#1E293B",
        "surface_alt": "#273549",
        "surface_alt_hover": "#334155",
        "text": "#F8FAFC",
        "muted": "#CBD5E1",
        "border": "#475569",
        "on_accent": "#F8FAFC",
        "glass": (10, 16, 30, 165),
        "shadow": "#060B16"
    }
}

THEME = "light"

HEADER_BG = THEME_PALETTES["light"]["header_bg"]
PAGE_BG = THEME_PALETTES["light"]["page_bg"]
SURFACE = THEME_PALETTES["light"]["surface"]
SURFACE_ALT = THEME_PALETTES["light"]["surface_alt"]
SURFACE_ALT_HOVER = THEME_PALETTES["light"]["surface_alt_hover"]
TEXT = THEME_PALETTES["light"]["text"]
MUTED = THEME_PALETTES["light"]["muted"]
BORDER = THEME_PALETTES["light"]["border"]
ON_ACCENT = THEME_PALETTES["light"]["on_accent"]
GLASS_TINT = THEME_PALETTES["light"]["glass"]
CANVAS_SHADOW = THEME_PALETTES["light"]["shadow"]

CURRENT_SCREEN = None

root = tk.Tk()
root.title("AUTOMATED GRADE CALCULATION PERFORMANCE SYSTEM")
root.configure(bg=PAGE_BG)

SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()

SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)

WINDOW_WIDTH = SCREEN_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT

HEADER_HEIGHT = int(round(70 * SCALE))

root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.attributes("-fullscreen", True)
root.resizable(False, False)


def sx(value):
    return int(round(value * SCALE_X))


def sy(value):
    return int(round(value * SCALE_Y))


def sfont(size, weight="bold"):
    return ("Arial", max(7, int(round(size * SCALE))), weight)


def spad(value):
    return int(round(value * SCALE))


def place_scaled(widget, x=0, y=0, width=None, height=None):
    options = {
        "x": sx(x),
        "y": sy(y)
    }

    if width is not None:
        options["width"] = sx(width)

    if height is not None:
        options["height"] = sy(height)

    widget.place(**options)


class ScaledCanvas(tk.Canvas):
    def create_text(self, x, y, *args, **kwargs):
        return super().create_text(sx(x), sy(y), *args, **kwargs)

    def create_image(self, x, y, *args, **kwargs):
        return super().create_image(sx(x), sy(y), *args, **kwargs)

    def create_line(self, *args, **kwargs):
        scaled = []

        for index, arg in enumerate(args):
            if isinstance(arg, (int, float)):
                scaled.append(sx(arg) if index % 2 == 0 else sy(arg))
            else:
                scaled.append(arg)

        return super().create_line(*scaled, **kwargs)

    def create_polygon(self, *args, **kwargs):
        scaled = []

        for arg in args:
            if isinstance(arg, (list, tuple)):
                scaled.append([
                    sx(value) if index % 2 == 0 else sy(value)
                    for index, value in enumerate(arg)
                ])
            else:
                scaled.append(arg)

        return super().create_polygon(*scaled, **kwargs)


# --------------------------------------------------
# BACKGROUND
# --------------------------------------------------

base_background = Image.new(
    "RGB",
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    "#DCE8F7"
)

background_source = None

if os.path.exists(BACKGROUND_FILE):
    try:
        background_source = Image.open(
            BACKGROUND_FILE
        ).convert("RGB")

        base_background = background_source.resize(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            Image.Resampling.LANCZOS
        )

    except (OSError, ValueError):
        background_source = None

display_source = None
blurred_source = None

background_photo = None

background_canvas = ScaledCanvas(
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
background_canvas.glass_panels = []


def apply_theme_tint(image):
    """Apply the active theme tint to a background image."""

    if THEME == "dark":
        dimmed = ImageEnhance.Brightness(
            image
        ).enhance(0.45)

        tint = Image.new(
            "RGB",
            image.size,
            (8, 13, 26)
        )

        return Image.blend(
            dimmed,
            tint,
            0.45
        )

    return image


def build_display_source():
    """Build the oversized background and the blurred copy used by the glass.

    The background is rendered once, larger than the window, so that the
    animation only has to slide it around instead of redrawing the photo
    on every frame. That keeps the movement smooth.
    """

    global display_source, blurred_source, background_photo

    if background_source is not None:
        source = background_source.resize(
            (
                max(WINDOW_WIDTH, int(WINDOW_WIDTH * BACKGROUND_ZOOM)),
                max(WINDOW_HEIGHT, int(WINDOW_HEIGHT * BACKGROUND_ZOOM))
            ),
            Image.Resampling.LANCZOS
        )

    else:
        source = base_background.copy()

    display_source = apply_theme_tint(source)

    half = display_source.resize(
        (
            max(1, display_source.width // 2),
            max(1, display_source.height // 2)
        ),
        Image.Resampling.BILINEAR
    )

    blurred_source = half.filter(
        ImageFilter.GaussianBlur(
            GLASS_BLUR_RADIUS * SCALE * BACKGROUND_ZOOM / 2
        )
    ).resize(
        display_source.size,
        Image.Resampling.BILINEAR
    )

    background_photo = ImageTk.PhotoImage(display_source)




def draw_background():
    for item in background_canvas.find_withtag("background"):
        background_canvas.delete(item)

    offset_x, offset_y = background_offset()

    background_item = tk.Canvas.create_image(
        background_canvas,
        -offset_x,
        -offset_y,
        image=background_photo,
        anchor="nw",
        tags="background"
    )
    background_canvas.tag_lower(background_item)



def refresh_background():
    """Rebuild the background image for the active theme while preserving glass panels."""
    build_display_source()
    draw_background()
    refresh_glass_panels(background_canvas)


# --------------------------------------------------
# MOVING BACKGROUND
# --------------------------------------------------

background_animation = {
    "running": False,
    "job": None,
    "frame": 0,
    "time": 0.0,
    "last": 0.0
}


def background_offset(moment=None):
    """Return the pixel offset of the moving background.

    The photo travels along a slow ellipse, so it never stalls on a single
    pixel and never jumps: the horizontal and vertical parts of the drift
    keep the image moving at the same time and the path always closes
    smoothly on itself.
    """

    if display_source is None:
        return 0, 0

    if not BACKGROUND_ANIMATION:
        travel_x = max(0, display_source.width - WINDOW_WIDTH)
        travel_y = max(0, display_source.height - WINDOW_HEIGHT)
        return (
            int(round(travel_x / 2)),
            int(round(travel_y / 2))
        )

    if moment is None:
        moment = background_animation["time"]

    travel_x = max(0, display_source.width - WINDOW_WIDTH)
    travel_y = max(0, display_source.height - WINDOW_HEIGHT)

    angle = moment * BACKGROUND_ORBIT_SPEED

    offset_x = int(round(
        travel_x * 0.5 + travel_x * 0.5 * math.cos(angle)
    ))

    offset_y = int(round(
        travel_y * 0.5 + travel_y * 0.5 * math.sin(angle)
    ))

    return offset_x, offset_y


def animate_background():
    """Slide the background to its next position."""

    if not background_animation["running"]:
        return

    background_animation["job"] = root.after(
        int(round(1000 / BACKGROUND_FPS)),
        animate_background
    )

    now = time.perf_counter()

    if background_animation["last"]:
        background_animation["time"] += now - background_animation["last"]

    background_animation["last"] = now

    offset_x, offset_y = background_offset()

    item = background_canvas.find_withtag("background")

    if item:
        background_canvas.coords(
            item[0],
            -offset_x,
            -offset_y
        )

    background_animation["frame"] += 1

    if background_animation["frame"] % BACKGROUND_GLASS_REFRESH == 0:
        refresh_glass_panels(background_canvas)


def start_background_animation():
    """Start the slow moving background."""

    if not BACKGROUND_ANIMATION:
        return

    if background_animation["running"]:
        return

    background_animation["running"] = True
    background_animation["frame"] = 0
    background_animation["last"] = 0.0

    animate_background()


def stop_background_animation():
    """Stop the moving background."""

    background_animation["running"] = False
    background_animation["last"] = 0.0

    job = background_animation["job"]

    if job is not None:
        try:
            root.after_cancel(job)

        except (tk.TclError, ValueError):
            pass

        background_animation["job"] = None


def clear_glass_panels():
    """Remove only the frosted glass overlay for a full screen refresh."""
    for panel in list(getattr(background_canvas, "glass_panels", [])):
        try:
            background_canvas.delete(panel["item"])
        except (tk.TclError, ValueError):
            pass

        previous = panel.get("photo")
        if previous is not None:
            try:
                background_canvas.glass_images.remove(previous)
            except ValueError:
                pass

    background_canvas.glass_panels = []


def clear_screen():
    stop_background_animation()

    for widget in root.winfo_children():
        if widget is not background_canvas:
            widget.destroy()

    clear_glass_panels()
    draw_background()


# --------------------------------------------------
# GLASS PANEL
# --------------------------------------------------

GLASS_OVERLAYS = {}


def glass_overlay(panel_width, panel_height, radius):
    """Return the cached tint and rounded mask for a glass panel."""

    key = (
        panel_width,
        panel_height,
        radius,
        GLASS_TINT[:3]
    )

    cached = GLASS_OVERLAYS.get(key)

    if cached is None:
        tint = Image.new(
            "RGB",
            (panel_width, panel_height),
            GLASS_TINT[:3]
        )

        mask = Image.new(
            "L",
            (panel_width, panel_height),
            0
        )

        ImageDraw.Draw(mask).rounded_rectangle(
            (
                0,
                0,
                panel_width - 1,
                panel_height - 1
            ),
            radius=max(1, int(round(radius * SCALE))),
            fill=255
        )

        cached = (tint, mask)

        GLASS_OVERLAYS[key] = cached

    return cached


def build_glass_panel_image(
    panel_x,
    panel_y,
    panel_width,
    panel_height,
    radius
):
    """Build the frosted glass image for a region of the moving background."""

    offset_x, offset_y = background_offset()

    crop = blurred_source.crop(
        (
            offset_x + panel_x,
            offset_y + panel_y,
            offset_x + panel_x + panel_width,
            offset_y + panel_y + panel_height
        )
    )

    tint, mask = glass_overlay(
        panel_width,
        panel_height,
        radius
    )

    glass_panel = Image.blend(
        crop,
        tint,
        GLASS_TINT[3] / 255
    ).convert("RGBA")

    glass_panel.putalpha(mask)

    return glass_panel


def create_glass_panel(
    canvas,
    x,
    y,
    width,
    height,
    radius=32
):
    panel_x = sx(x)
    panel_y = sy(y)
    panel_width = sx(width)
    panel_height = sy(height)

    glass_panel = build_glass_panel_image(
        panel_x,
        panel_y,
        panel_width,
        panel_height,
        radius
    )

    panel_photo = ImageTk.PhotoImage(glass_panel)

    item = canvas.create_image(
        x,
        y,
        image=panel_photo,
        anchor="nw"
    )

    canvas.glass_images.append(panel_photo)

    if not hasattr(canvas, "glass_panels"):
        canvas.glass_panels = []

    canvas.glass_panels.append({
        "item": item,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "radius": radius,
        "photo": panel_photo
    })

    return panel_photo


def refresh_glass_panels(canvas):
    """Redraw the glass panels so they follow the moving background."""

    for panel in getattr(canvas, "glass_panels", []):
        if not canvas.find_withtag(panel["item"]):
            continue

        glass_panel = build_glass_panel_image(
            sx(panel["x"]),
            sy(panel["y"]),
            sx(panel["width"]),
            sy(panel["height"]),
            panel["radius"]
        )

        photo = ImageTk.PhotoImage(glass_panel)

        canvas.itemconfigure(
            panel["item"],
            image=photo
        )

        previous = panel.get("photo")

        if previous is not None:
            try:
                canvas.glass_images.remove(previous)

            except ValueError:
                pass

        panel["photo"] = photo

        canvas.glass_images.append(photo)


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
    font=sfont(12)
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
        fill=CANVAS_SHADOW,
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
        fill=ON_ACCENT,
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
    font = kwargs.pop("font", sfont(10))

    return tk.Button(
        parent,
        text=text,
        command=command,
        font=font,
        bg=color,
        fg=ON_ACCENT,
        activebackground=darken_color(color),
        activeforeground=ON_ACCENT,
        relief="flat",
        cursor="hand2",
        padx=spad(10),
        pady=spad(6),
        **kwargs
    )


def make_entry(parent, width=24, show=None, textvariable=None):
    options = {
        "font": sfont(10, "normal"),
        "relief": "solid",
        "bd": 1,
        "highlightthickness": 1,
        "highlightbackground": BORDER,
        "highlightcolor": BLUE,
        "bg": SURFACE,
        "fg": TEXT,
        "insertbackground": TEXT,
        "disabledbackground": SURFACE_ALT,
        "disabledforeground": MUTED,
        "selectbackground": BLUE,
        "selectforeground": ON_ACCENT,
    }

    if show is not None:
        options["show"] = show

    if textvariable is not None:
        options["textvariable"] = textvariable

    return tk.Entry(parent, width=width, **options)


def format_assessment(value):
    """Format a stored assessment score for the tables."""

    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"

    if isinstance(value, (list, tuple)) and value:
        scores = [
            float(item) for item in value
            if isinstance(item, (int, float))
        ]

        if not scores:
            return "—"

        average = sum(scores) / len(scores)

        if len(scores) == 1:
            return f"{average:.2f}"

        detail = " / ".join(f"{score:.2f}" for score in scores)

        return f"{detail} ({average:.2f})"

    return "—"


def format_grade_point(value):
    """Display the official SMCII grade-point equivalent for a percentage."""

    if not isinstance(value, (int, float)):
        return "—"

    point = grade_point_equivalent(float(value))

    if point is None:
        return "—"

    return f"{point:.2f}"


def format_overall_grade_display(value):
    """Display the final percentage alongside the official grade point."""

    if not isinstance(value, (int, float)):
        return "—"

    return (
        f"{float(value):.2f}% | Grade Point: {format_grade_point(value)}"
    )


def make_stat_card(parent, title, value, row, column, color=BLUE):
    card = tk.Frame(
        parent,
        bg=SURFACE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.grid(
        row=row,
        column=column,
        padx=spad(8),
        pady=spad(8),
        sticky="nsew"
    )

    tk.Label(
        card,
        text=title.upper(),
        font=sfont(8),
        bg=SURFACE,
        fg=MUTED
    ).pack(pady=(spad(10), spad(0)))

    tk.Label(
        card,
        text=str(value),
        font=sfont(20),
        bg=SURFACE,
        fg=color
    ).pack(pady=(spad(0), spad(10)))

    return card


def make_module_card(parent, title, description, color, command, row, column):
    card = tk.Frame(
        parent,
        bg=SURFACE,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.grid(
        row=row,
        column=column,
        padx=spad(10),
        pady=spad(10),
        sticky="nsew"
    )

    top = tk.Frame(card, bg=SURFACE)
    top.pack(
        fill="x",
        padx=spad(14),
        pady=(spad(10), 0)
    )

    make_button(
        top,
        "OPEN",
        command,
        color
    ).pack(side="right")

    tk.Label(
        top,
        text=title,
        font=sfont(11),
        bg=SURFACE,
        fg=color
    ).pack(side="left")

    tk.Label(
        card,
        text=description,
        font=sfont(9, "normal"),
        bg=SURFACE,
        fg=MUTED,
        wraplength=sx(250),
        justify="left"
    ).pack(
        anchor="w",
        padx=spad(14),
        pady=(spad(4), spad(12))
    )

    return card


def admin_module_data(full_name, admin_username):
    return [
        (
            "USER MANAGEMENT",
            "Create, edit, deactivate, reset or delete accounts",
            BLUE,
            lambda: show_user_management(full_name, admin_username)
        ),
        (
            "TEACHER ASSIGNMENT",
            "Assign teachers to the subjects they are allowed to grade",
            GREEN,
            lambda: show_teacher_assignments(full_name, admin_username)
        ),
        (
            "ACCOUNT BROWSER",
            "Browse teacher and student accounts with grade history",
            PURPLE,
            lambda: show_accounts(full_name, admin_username, "Teacher")
        ),
        (
            "ALL GRADE RECORDS",
            "Search every grade record across all students and subjects",
            RED,
            lambda: show_all_grades(full_name, admin_username)
        ),
        (
            "SUBJECT MANAGEMENT",
            "Define the subjects teachers can assign to students",
            GRAY,
            lambda: show_subjects(full_name, admin_username)
        ),
        (
            "ANNOUNCEMENTS",
            "Post notices for students and teachers",
            BLUE,
            lambda: show_announcements(full_name, admin_username)
        ),
        (
            "ACTIVITY LOG",
            "Review every account, subject and grade action",
            BLUE,
            lambda: show_activity_log(full_name, admin_username)
        ),
        (
            "EXPORT REPORTS",
            "Save text reports of accounts, grades and analytics",
            GREEN,
            lambda: show_exports(full_name, admin_username)
        )
    ]


def build_announcement_view(parent, role, height=6, username=""):
    """Build a read-only announcement feed for a role."""

    notices = announcements_for(role, username)

    scroll = ttk.Scrollbar(parent, orient="vertical")
    scroll.pack(side="right", fill="y")

    view = tk.Text(
        parent,
        height=height,
        wrap="word",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9, "normal"),
        bd=0,
        highlightthickness=0,
        padx=spad(2),
        pady=spad(2),
        cursor="arrow",
        yscrollcommand=scroll.set
    )

    scroll.configure(command=view.yview)

    view.tag_configure(
        "title",
        font=sfont(10),
        foreground=TEXT,
        spacing3=spad(2)
    )
    view.tag_configure(
        "meta",
        font=sfont(8, "normal"),
        foreground=MUTED,
        spacing3=spad(8)
    )
    view.tag_configure(
        "body",
        font=sfont(9, "normal"),
        foreground=TEXT,
        spacing3=spad(12)
    )

    view.pack(side="left", fill="both", expand=True)

    if notices:
        for notice in notices[:10]:
            view.insert(
                "end",
                notice.get("title", "Announcement") + "\n",
                "title"
            )
            view.insert(
                "end",
                (
                    f"{notice.get('audience', 'Everyone')}  |  "
                    f"{format_display_time(notice.get('timestamp', ''))}\n"
                ),
                "meta"
            )
            view.insert(
                "end",
                notice.get("body", "").strip() + "\n\n",
                "body"
            )
    else:
        view.insert(
            "end",
            "No announcements yet. Check back later.",
            "meta"
        )

    view.configure(state="disabled")

    return view


def build_app_menu_button(menu_title, menu_items):
    """Place a menu button in the upper-left corner of the header.

    Clicking it slides out a panel that lists every module of the current
    role, so the user can jump anywhere from any screen and log out.
    """

    holder = tk.Frame(root, bg=HEADER_BG)
    holder.place(
        x=spad(12),
        y=0,
        width=spad(52),
        height=HEADER_HEIGHT
    )

    menu_open = {"value": False}
    panel = {"frame": None}

    def close_menu():
        frame = panel["frame"]

        if frame is not None:
            frame.destroy()
            panel["frame"] = None

        menu_open["value"] = False
        button.configure(text="\u2630")

    def open_menu():
        frame = tk.Frame(
            root,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        frame.place(
            x=spad(12),
            y=HEADER_HEIGHT,
            width=sx(260)
        )

        panel["frame"] = frame
        menu_open["value"] = True
        button.configure(text="\u2715")

        tk.Label(
            frame,
            text=menu_title,
            font=sfont(9),
            bg=SURFACE,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=spad(14),
            pady=(spad(12), spad(6))
        )

        for title, color, command in menu_items:
            def open_module(command=command):
                close_menu()
                command()

            row = tk.Frame(frame, bg=SURFACE, cursor="hand2")
            row.pack(fill="x", padx=spad(8), pady=spad(2))

            stripe = tk.Frame(row, bg=color, width=spad(4))
            stripe.pack(side="left", fill="y")

            label = tk.Label(
                row,
                text=title,
                font=sfont(10),
                bg=SURFACE,
                fg=TEXT,
                anchor="w",
                padx=spad(10),
                pady=spad(9),
                cursor="hand2"
            )
            label.pack(side="left", fill="x", expand=True)

            def enter(event, row=row, label=label):
                row.configure(bg=SURFACE_ALT)
                label.configure(bg=SURFACE_ALT)

            def leave(event, row=row, label=label):
                row.configure(bg=SURFACE)
                label.configure(bg=SURFACE)

            for widget in (row, stripe, label):
                widget.bind("<Button-1>", lambda e, c=command: open_module(c))

            row.bind("<Enter>", enter)
            row.bind("<Leave>", leave)
            label.bind("<Enter>", enter)
            label.bind("<Leave>", leave)

        tk.Frame(
            frame,
            bg=BORDER,
            height=1
        ).pack(fill="x", padx=spad(8), pady=(spad(8), spad(2)))

        def log_out():
            close_menu()
            logout()

        make_button(
            frame,
            "LOGOUT",
            log_out,
            RED
        ).pack(fill="x", padx=spad(8), pady=spad(2))

        make_button(
            frame,
            "CLOSE MENU",
            close_menu,
            GRAY
        ).pack(fill="x", padx=spad(8), pady=(spad(2), spad(10)))

    def toggle_menu():
        if menu_open["value"]:
            close_menu()
        else:
            open_menu()

    button = tk.Button(
        holder,
        text="\u2630",
        command=toggle_menu,
        font=sfont(16),
        bg=HEADER_BG,
        fg=ON_ACCENT,
        activebackground=HEADER_BG,
        activeforeground=ON_ACCENT,
        relief="flat",
        bd=0,
        cursor="hand2"
    )

    button.pack(side="left", padx=spad(4), pady=spad(12))


def build_admin_menu_button(full_name, admin_username):
    """Open the administration menu from the header."""

    build_app_menu_button(
        "ADMINISTRATION MODULES",
        [
            (title, color, command)
            for title, description, color, command in admin_module_data(
                full_name,
                admin_username
            )
        ]
    )


def center_window(window, width, height):
    window.update_idletasks()

    scaled_width = sx(width)
    scaled_height = sy(height)

    x = root.winfo_rootx() + (root.winfo_width() - scaled_width) // 2
    y = root.winfo_rooty() + (root.winfo_height() - scaled_height) // 2

    window.geometry(f"{scaled_width}x{scaled_height}+{x}+{y}")


def show_form_dialog(title, fields):
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.configure(bg=SURFACE)
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    widgets = {}

    for index, (key, label, value, kind) in enumerate(fields):
        tk.Label(
            dialog,
            text=label + ":",
            bg=SURFACE,
            fg=TEXT,
            font=sfont(10, "normal"),
            anchor="w"
        ).grid(
            row=index,
            column=0,
            padx=(spad(14), spad(10)),
            pady=spad(7),
            sticky="w"
        )

        if kind == "combo":
            widget = ttk.Combobox(
                dialog,
                values=value,
                state="readonly",
                width=30
            )

            widget.current(0)

        else:
            widget = tk.Entry(
                dialog,
                width=32,
                font=sfont(10, "normal"),
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground=BORDER,
                highlightcolor=BLUE
            )

            if kind == "password":
                widget.configure(show="*")

            widget.insert(0, value)

        widget.grid(
            row=index,
            column=1,
            padx=(spad(0), spad(14)),
            pady=spad(7),
            sticky="w"
        )

        widgets[key] = widget

    result = {}

    def submit():
        for key, widget in widgets.items():
            result[key] = widget.get().strip()

        dialog.destroy()

    def cancel():
        result.clear()
        dialog.destroy()

    button_row = tk.Frame(dialog, bg=SURFACE)
    button_row.grid(
        row=len(fields),
        column=0,
        columnspan=2,
        padx=spad(14),
        pady=(spad(4), spad(14)),
        sticky="e"
    )

    make_button(
        button_row,
        "SAVE",
        submit,
        BLUE
    ).pack(side="right", padx=spad(6))

    make_button(
        button_row,
        "CANCEL",
        cancel,
        GRAY
    ).pack(side="right")

    dialog.protocol("WM_DELETE_WINDOW", cancel)
    dialog.bind("<Escape>", lambda event: cancel())

    focus_widget = widgets.get("full_name") or widgets.get("password")

    if focus_widget is not None:
        focus_widget.focus_set()

    center_window(dialog, 520, 90 + 62 * len(fields))
    dialog.wait_window(dialog)

    return result or None


# --------------------------------------------------
# THEME ENGINE
# --------------------------------------------------

def configure_ttk_styles():
    """Apply the active theme to the ttk widgets."""

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT,
        borderwidth=0,
        rowheight=spad(20) + 6
    )

    style.configure(
        "Treeview.Heading",
        background=HEADER_BG,
        foreground=ON_ACCENT,
        relief="flat",
        font=sfont(9)
    )

    style.configure(
        "Treeview",
        background=SURFACE,
        foreground=TEXT,
        fieldbackground=SURFACE,
        rowheight=int(round(28 * SCALE))
    )

    style.map(
        "Treeview.Heading",
        background=[("active", HEADER_BG)],
        foreground=[("active", ON_ACCENT), ("selected", ON_ACCENT)]
    )

    style.configure(
        "Treeview.Heading",
        background=HEADER_BG,
        foreground=ON_ACCENT
    )

    style.map(
        "Treeview",
        background=[("selected", BLUE)],
        foreground=[("selected", ON_ACCENT), ("!disabled", TEXT)]
    )

    style.configure(
        "TCombobox",
        fieldbackground=SURFACE,
        background=SURFACE,
        foreground=TEXT,
        arrowcolor=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        insertcolor=TEXT
    )

    style.map(
        "TCombobox",
        fieldbackground=[("readonly", SURFACE)],
        foreground=[("readonly", TEXT)],
        selectbackground=[("readonly", SURFACE)],
        selectforeground=[("readonly", TEXT)],
        bordercolor=[("focus", BLUE)],
        arrowcolor=[("disabled", MUTED)]
    )

    root.option_add("*TCombobox*Listbox.background", SURFACE)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", BLUE)
    root.option_add("*TCombobox*Listbox.selectForeground", ON_ACCENT)


def map_theme_color(value, old_palette, new_palette):
    """Map a color from the current theme palette to the new one."""
    if not value:
        return None

    for key, old_color in old_palette.items():
        if value.lower() == str(old_color).lower():
            return new_palette.get(key, value)

    return value


def collect_theme_widgets(root_widget):
    """Collect each visible widget exactly once for one-pass theme recoloring."""
    visited = set()
    stack = [root_widget]
    widgets = []

    while stack:
        widget = stack.pop()
        widget_id = id(widget)
        if widget_id in visited:
            continue
        visited.add(widget_id)
        widgets.append(widget)
        try:
            children = widget.winfo_children()
        except Exception:
            continue
        stack.extend(reversed(children))

    return widgets


def apply_theme_to_widget(widget, old_palette, new_palette):
    """Refresh an already-created widget to match the active theme."""
    if widget is None:
        return

    for option in ("bg", "background"):
        try:
            current = widget.cget(option)
        except (TypeError, tk.TclError):
            continue
        mapped = map_theme_color(current, old_palette, new_palette)
        if mapped is not None and mapped != current:
            try:
                widget.configure(**{option: mapped})
            except (tk.TclError, TypeError):
                pass

    for option in ("fg", "foreground", "activeforeground", "insertbackground", "selectforeground", "disabledforeground", "highlightbackground", "highlightcolor", "troughcolor", "arrowcolor"):
        try:
            current = widget.cget(option)
        except (TypeError, tk.TclError):
            continue
        mapped = map_theme_color(current, old_palette, new_palette)
        if mapped is not None and mapped != current:
            try:
                widget.configure(**{option: mapped})
            except (tk.TclError, TypeError):
                pass

    for option in ("activebackground", "selectbackground", "disabledbackground", "fieldbackground"):
        try:
            current = widget.cget(option)
        except (TypeError, tk.TclError):
            continue
        mapped = map_theme_color(current, old_palette, new_palette)
        if mapped is not None and mapped != current:
            try:
                widget.configure(**{option: mapped})
            except (tk.TclError, TypeError):
                pass


def apply_theme_to_canvas(canvas, old_palette, new_palette):
    """Refresh canvas-drawn text and shapes to match the active theme."""
    if canvas is None:
        return

    color_options = (
        "fill",
        "outline",
        "activefill",
        "activeoutline",
        "stipple"
    )

    for item in canvas.find_all():
        for option in color_options:
            try:
                current = canvas.itemcget(item, option)
            except (TypeError, tk.TclError):
                continue
            mapped = map_theme_color(current, old_palette, new_palette)
            if mapped is not None and mapped != current:
                try:
                    canvas.itemconfigure(item, **{option: mapped})
                except (tk.TclError, TypeError):
                    pass


def apply_theme(name, rebuild=None):
    """Switch the interface between the light and dark theme."""

    global THEME, HEADER_BG, PAGE_BG, SURFACE, SURFACE_ALT
    global SURFACE_ALT_HOVER, TEXT, MUTED, BORDER, ON_ACCENT
    global GLASS_TINT, CANVAS_SHADOW

    if name == THEME:
        return

    previous_name = THEME if THEME in THEME_PALETTES else "light"
    old_palette = THEME_PALETTES.get(previous_name, THEME_PALETTES["light"])
    palette = THEME_PALETTES.get(name, THEME_PALETTES["light"])

    THEME = name
    HEADER_BG = palette["header_bg"]
    PAGE_BG = palette["page_bg"]
    SURFACE = palette["surface"]
    SURFACE_ALT = palette["surface_alt"]
    SURFACE_ALT_HOVER = palette["surface_alt_hover"]
    TEXT = palette["text"]
    MUTED = palette["muted"]
    BORDER = palette["border"]
    ON_ACCENT = palette["on_accent"]
    GLASS_TINT = palette["glass"]
    CANVAS_SHADOW = palette["shadow"]

    root.configure(bg=PAGE_BG)
    for widget in collect_theme_widgets(root):
        if isinstance(widget, tk.Canvas):
            apply_theme_to_canvas(widget, old_palette, palette)
        apply_theme_to_widget(widget, old_palette, palette)
    refresh_background()
    configure_ttk_styles()

    settings = data_store.setdefault("settings", {})
    settings["theme"] = name

    try:
        save_data()
    except OSError:
        pass

    if rebuild is not None:
        rebuild()


def toggle_theme():
    """Flip between the dark and the light theme."""

    next_theme = "dark" if THEME == "light" else "light"

    apply_theme(next_theme)


def theme_symbol():
    """Return the symbol key that matches the active theme."""

    if THEME == "light":
        return "light"

    return "dark"


def draw_theme_glyph(
    canvas,
    cx,
    cy,
    radius,
    mode,
    mask_color,
    tags=""
):
    """Draw a sun or a moon symbol centred on a canvas position.

    The coordinates are given in pixels so the same drawing works on the
    header widget canvas and on the full screen background canvas.
    """

    cx = int(round(cx))
    cy = int(round(cy))
    radius = max(6, int(round(radius)))

    items = []

    if mode == "light":
        disk = max(3, int(round(radius * 0.28)))

        items.append(tk.Canvas.create_oval(
            canvas,
            cx - disk,
            cy - disk,
            cx + disk,
            cy + disk,
            fill=ON_ACCENT,
            outline="",
            tags=tags
        ))

        inner = radius * 0.52
        outer = radius * 0.82

        for index in range(8):
            angle = math.radians(index * 45)

            items.append(tk.Canvas.create_line(
                canvas,
                cx + inner * math.cos(angle),
                cy + inner * math.sin(angle),
                cx + outer * math.cos(angle),
                cy + outer * math.sin(angle),
                fill=ON_ACCENT,
                width=max(2, int(round(radius * 0.13))),
                capstyle="round",
                tags=tags
            ))

    else:
        body = int(round(radius * 0.60))

        items.append(tk.Canvas.create_oval(
            canvas,
            cx - body,
            cy - body,
            cx + body,
            cy + body,
            fill=ON_ACCENT,
            outline="",
            tags=tags
        ))

        mask = int(round(radius * 0.56))
        offset = int(round(radius * 0.30))

        items.append(tk.Canvas.create_oval(
            canvas,
            cx + offset - mask,
            cy - offset - mask,
            cx + offset + mask,
            cy - offset + mask,
            fill=mask_color,
            outline="",
            tags=tags
        ))

    return items


def make_theme_toggle(parent, background=None):
    """Create the small round button that switches the theme."""

    size = spad(40)

    if background is None:
        background = parent.cget("bg")

    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        bg=background,
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    def render():
        canvas.delete("all")

        tk.Canvas.create_oval(
            canvas,
            2,
            2,
            size - 2,
            size - 2,
            fill=PURPLE,
            outline=""
        )

        draw_theme_glyph(
            canvas,
            size / 2,
            size / 2,
            (size / 2 - 3) * 0.82,
            theme_symbol(),
            PURPLE
        )

    render()

    canvas.bind("<Button-1>", lambda event: toggle_theme())

    return canvas


def draw_theme_toggle_on_canvas(canvas, x, y, size=46):
    """Draw the round theme button on a canvas and make it clickable."""

    cx = sx(x + size / 2)
    cy = sy(y + size / 2)
    radius = max(8, int(round(size / 2 * SCALE)) - 2)

    items = [
        tk.Canvas.create_oval(
            canvas,
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=PURPLE,
            outline="",
            tags="theme_toggle"
        )
    ]

    items += draw_theme_glyph(
        canvas,
        cx,
        cy,
        radius * 0.82,
        theme_symbol(),
        PURPLE,
        tags="theme_toggle"
    )

    def enter(event):
        canvas.configure(cursor="hand2")

    def leave(event):
        canvas.configure(cursor="")

    def click(event):
        toggle_theme()

    for item in items:
        canvas.tag_bind(item, "<Button-1>", click)
        canvas.tag_bind(item, "<Enter>", enter)
        canvas.tag_bind(item, "<Leave>", leave)

    return items


# --------------------------------------------------
# HEADER
# --------------------------------------------------

def build_header(
    title,
    full_name,
    admin_menu=False,
    admin_username=None,
    menu_title=None,
    menu_items=None
):
    header = tk.Frame(root, bg=HEADER_BG, height=HEADER_HEIGHT)
    header.place(
        x=0,
        y=0,
        width=WINDOW_WIDTH,
        height=HEADER_HEIGHT
    )

    if admin_menu:
        build_admin_menu_button(full_name, admin_username)
    elif menu_items is not None:
        build_app_menu_button(
            menu_title or "MENU",
            menu_items
        )

    has_menu = admin_menu or menu_items is not None

    tk.Label(
        header,
        text=title,
        font=sfont(18),
        bg=HEADER_BG,
        fg=ON_ACCENT
    ).pack(
        side="left",
        padx=(spad(70) if has_menu else spad(24), spad(24)),
        pady=spad(18)
    )

    tk.Label(
        header,
        text=full_name,
        font=sfont(10, "normal"),
        bg=HEADER_BG,
        fg=ON_ACCENT
    ).pack(side="left", padx=spad(12))

    make_theme_toggle(header, HEADER_BG).pack(
        side="right",
        padx=spad(10),
        pady=spad(14)
    )

    if not has_menu:
        make_button(
            header,
            "LOGOUT",
            logout,
            RED
        ).pack(side="right", padx=spad(4), pady=spad(14))


# --------------------------------------------------
# LOGIN TYPE SELECTION
# --------------------------------------------------

def logout():
    show_login_selection()


def show_login_selection():
    show_login()


# --------------------------------------------------
# LOGIN FORM
# --------------------------------------------------

def show_login(role=None):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_login(role)
    clear_screen()

    create_glass_panel(
        background_canvas,
        300,
        90,
        500,
        560,
        radius=32
    )

    background_canvas.create_text(
        550,
        135,
        text="GRADING",
        font=sfont(42),
        fill=TEXT
    )

    background_canvas.create_text(
        550,
        180,
        text="SYSTEM",
        font=sfont(42),
        fill=BLUE
    )

    background_canvas.create_text(
        550,
        226,
        text="Automated Grade Calculation\nPerformance System",
        font=sfont(13, "normal"),
        fill=MUTED,
        justify="center"
    )

    background_canvas.create_line(
        390,
        255,
        710,
        255,
        fill=BLUE,
        width=2
    )

    login_title = f"{role.upper()} LOGIN" if role else "LOGIN"

    background_canvas.create_text(
        550,
        290,
        text=login_title,
        font=sfont(28),
        fill=TEXT
    )

    background_canvas.create_text(
        550,
        330,
        text="Enter your account details",
        font=sfont(12, "normal"),
        fill=MUTED
    )

    background_canvas.create_text(
        390,
        370,
        text="Username",
        font=sfont(11),
        fill=TEXT,
        anchor="w"
    )

    username_entry = tk.Entry(
        root,
        font=sfont(13, "normal"),
        bg=SURFACE,
        fg=TEXT,
        relief="flat",
        bd=0,
        highlightthickness=2,
        highlightbackground=BORDER,
        highlightcolor=BLUE
    )

    place_scaled(
        username_entry,
        390,
        390,
        320,
        38
    )

    background_canvas.create_text(
        390,
        445,
        text="Password",
        font=sfont(11),
        fill=TEXT,
        anchor="w"
    )

    password_entry = tk.Entry(
        root,
        font=sfont(13, "normal"),
        show="*",
        bg=SURFACE,
        fg=TEXT,
        relief="flat",
        bd=0,
        highlightthickness=2,
        highlightbackground=BORDER,
        highlightcolor=BLUE
    )

    place_scaled(
        password_entry,
        390,
        465,
        270,
        38
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
        font=sfont(8),
        bg=SURFACE_ALT,
        fg=BLUE,
        activebackground=SURFACE_ALT_HOVER,
        relief="flat",
        bd=0,
        cursor="hand2"
    )

    place_scaled(
        eye_button,
        665,
        465,
        45,
        38
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

        selected_role = role
        user = None

        if selected_role is None:
            for candidate_role in ["Admin", "Teacher", "Student"]:
                user = authenticate_user(username, password, candidate_role)
                if user is not None:
                    selected_role = candidate_role
                    break
        else:
            user = authenticate_user(username, password, selected_role)

        if user is None:
            messagebox.showerror(
                "Login Failed",
                "Invalid username, password, or account details.",
                parent=root
            )

            password_entry.delete(0, tk.END)
            password_entry.focus_set()
            return

        account_username = user.get("username", username)
        full_name = user.get("full_name", username)

        if selected_role == "Admin":
            show_admin_dashboard(
                full_name,
                account_username
            )
        elif selected_role == "Teacher":
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
        520,
        320,
        45,
        "LOGIN",
        BLUE,
        login
    )

    rounded_button(
        background_canvas,
        450,
        580,
        200,
        35,
        "EXIT APPLICATION",
        GRAY,
        close_application,
        font=sfont(10)
    )

    background_canvas.create_text(
        550,
        630,
        text="SMCII SECURE LOGIN",
        font=sfont(10, "normal"),
        fill=MUTED
    )

    draw_theme_toggle_on_canvas(background_canvas, 898, 28)

    username_entry.bind(
        "<Return>",
        lambda event: password_entry.focus_set()
    )

    password_entry.bind(
        "<Return>",
        lambda event: login()
    )

    username_entry.focus_set()

    start_background_animation()


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

def show_admin_dashboard(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_admin_dashboard(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(25),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="System Overview",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    tk.Label(
        title_row,
        text=f"{full_name}  |  ",
        font=sfont(9, "normal"),
        bg=PAGE_BG,
        fg=MUTED
    ).pack(side="left", padx=spad(14))

    make_button(
        title_row,
        "REFRESH",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    stats = system_statistics()

    cards = tk.Frame(content, bg=PAGE_BG)
    cards.pack(
        fill="x",
        expand=True,
        padx=spad(20),
        pady=(spad(2), spad(24))
    )

    for column in range(5):
        cards.grid_columnconfigure(
            column,
            weight=1,
            uniform="statcards"
        )

    card_data = [
        ("Total Accounts", stats["total_users"], BLUE),
        ("Teachers", stats["teachers"], GREEN),
        ("Students", stats["students"], PURPLE),
        ("Grade Records", stats["total_grades"], BLUE),
        ("Class Average", f"{stats['average_grade']:.2f}", GREEN),
        ("Pass Rate", f"{stats['pass_rate']:.2f}%", PURPLE),
        ("Subjects Offered", stats["subjects_offered"], BLUE),
        (
            "Teacher Assignments",
            stats["subject_assignments"],
            PURPLE
        ),
        (
            "Teachers Without Subject",
            stats["unassigned_teachers"],
            RED
        ),
        ("Inactive Accounts", stats["inactive_users"], GRAY)
    ]

    for index, (label, value, color) in enumerate(card_data):
        make_stat_card(
            cards,
            label,
            value,
            index // 5,
            index % 5,
            color
        )

    semester_panel = tk.LabelFrame(
        content,
        text="Semester Management",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(12),
        pady=spad(8)
    )
    semester_panel.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(0), spad(18))
    )

    tk.Label(
        semester_panel,
        text=f"School Year: {data_store.get('settings', {}).get('school_year', current_school_year())}",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(anchor="w", pady=(0, spad(6)))

    for semester in SEMESTER_NAMES:
        status = semester_status_for(semester)
        first_status = semester_status_for("First Semester")
        row = tk.Frame(semester_panel, bg=SURFACE)
        row.pack(fill="x", pady=spad(4))

        tk.Label(
            row,
            text=f"{semester}: {status}",
            bg=SURFACE,
            fg=BLUE if status == "Completed" else TEXT,
            font=sfont(10)
        ).pack(side="left")

        if semester == "First Semester":
            if status == "Not Started":
                tk.Label(
                    row,
                    text="Awaiting semester start",
                    bg=SURFACE,
                    fg=MUTED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))

                def start_handler(selected_semester=semester):
                    confirm = messagebox.askyesno(
                        "Start Semester",
                        f"Start {selected_semester}? This will allow teachers to begin entering grades.",
                        parent=root
                    )
                    if not confirm:
                        return

                    success, message = start_semester(
                        selected_semester,
                        admin_username,
                        "Administrator-approved semester start"
                    )
                    if success:
                        messagebox.showinfo(
                            "Semester Started",
                            message,
                            parent=root
                        )
                        show_admin_dashboard(full_name, admin_username)
                    else:
                        messagebox.showerror(
                            "Start Failed",
                            message,
                            parent=root
                        )

                make_button(
                    row,
                    "START FIRST SEMESTER",
                    start_handler,
                    GREEN
                ).pack(side="right")
            elif status == "In Progress":
                checklist = semester_completion_status(semester)
                missing_count = len(checklist["missing"])
                tk.Label(
                    row,
                    text=f"Missing grades: {missing_count}",
                    bg=SURFACE,
                    fg=MUTED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))

                def complete_handler(selected_semester=semester):
                    confirm = messagebox.askyesno(
                        "Complete Semester",
                        f"Complete {selected_semester}? This will lock the semester and prevent further teacher edits.",
                        parent=root
                    )
                    if not confirm:
                        return

                    success, message = complete_semester(
                        selected_semester,
                        admin_username,
                        "Administrator-approved completion"
                    )
                    if success:
                        messagebox.showinfo(
                            "Semester Completed",
                            message,
                            parent=root
                        )
                        show_admin_dashboard(full_name, admin_username)
                    else:
                        messagebox.showerror(
                            "Completion Blocked",
                            message,
                            parent=root
                        )

                make_button(
                    row,
                    "COMPLETE FIRST SEMESTER",
                    complete_handler,
                    GREEN
                ).pack(side="right")
            elif status == "Completed":
                tk.Label(
                    row,
                    text="Grade entry is locked for this semester.",
                    bg=SURFACE,
                    fg=MUTED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))
            elif status == "Reopened":
                tk.Label(
                    row,
                    text="Grade entry has been reopened by the administrator.",
                    bg=SURFACE,
                    fg=RED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))
        else:
            if first_status != "Completed":
                tk.Label(
                    row,
                    text="LOCKED — Complete First Semester First",
                    bg=SURFACE,
                    fg=RED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))
            elif status == "Not Started":
                def start_handler(selected_semester=semester):
                    confirm = messagebox.askyesno(
                        "Start Semester",
                        f"Start {selected_semester}? This will allow teachers to begin entering grades.",
                        parent=root
                    )
                    if not confirm:
                        return

                    success, message = start_semester(
                        selected_semester,
                        admin_username,
                        "Administrator-approved semester start"
                    )
                    if success:
                        messagebox.showinfo(
                            "Semester Started",
                            message,
                            parent=root
                        )
                        show_admin_dashboard(full_name, admin_username)
                    else:
                        messagebox.showerror(
                            "Start Failed",
                            message,
                            parent=root
                        )

                make_button(
                    row,
                    "START SECOND SEMESTER",
                    start_handler,
                    GREEN
                ).pack(side="right")
            elif status == "In Progress":
                def complete_handler(selected_semester=semester):
                    confirm = messagebox.askyesno(
                        "Complete Semester",
                        f"Complete {selected_semester}? This will lock the semester and prevent further teacher edits.",
                        parent=root
                    )
                    if not confirm:
                        return

                    success, message = complete_semester(
                        selected_semester,
                        admin_username,
                        "Administrator-approved completion"
                    )
                    if success:
                        messagebox.showinfo(
                            "Semester Completed",
                            message,
                            parent=root
                        )
                        show_admin_dashboard(full_name, admin_username)
                    else:
                        messagebox.showerror(
                            "Completion Blocked",
                            message,
                            parent=root
                        )

                make_button(
                    row,
                    "COMPLETE SECOND SEMESTER",
                    complete_handler,
                    GREEN
                ).pack(side="right")
            elif status == "Completed":
                tk.Label(
                    row,
                    text="Grade entry is locked for this semester.",
                    bg=SURFACE,
                    fg=MUTED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))
            elif status == "Reopened":
                tk.Label(
                    row,
                    text="Grade entry has been reopened by the administrator.",
                    bg=SURFACE,
                    fg=RED,
                    font=sfont(8, "normal")
                ).pack(side="left", padx=spad(12))

        if status == "Completed":
            def reopen_handler(selected_semester=semester):
                reason = simpledialog.askstring(
                    "Reopen Semester",
                    f"Enter the reason for reopening {selected_semester}:",
                    parent=root
                )
                if not reason or not reason.strip():
                    if reason is not None:
                        messagebox.showwarning(
                            "Reason Required",
                            "A reopening reason is required before the semester can be reopened.",
                            parent=root
                        )
                    return

                success, message = reopen_semester(
                    selected_semester,
                    admin_username,
                    reason.strip()
                )
                if success:
                    messagebox.showinfo(
                        "Semester Reopened",
                        message,
                        parent=root
                    )
                    show_admin_dashboard(full_name, admin_username)
                else:
                    messagebox.showerror(
                        "Reopen Failed",
                        message,
                        parent=root
                    )

            make_button(
                row,
                f"REOPEN {semester.upper()}",
                reopen_handler,
                RED
            ).pack(side="right")


def show_user_management(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_user_management(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(25),
        pady=(spad(12), spad(8))
    )

    tk.Label(
        title_row,
        text="User Management",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "ACCOUNT BROWSER",
        lambda: show_accounts(
            full_name,
            admin_username,
            "Teacher"
        ),
        GREEN
    ).pack(side="right")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right", padx=spad(8))

    create_container = tk.Frame(content, bg=PAGE_BG)
    create_container.pack(
        fill="x",
        padx=spad(25),
        pady=spad(4)
    )

    create_state = {"role": None}
    create_form_frame = {"frame": None}

    def show_role_selection():
        if create_form_frame["frame"] is not None:
            create_form_frame["frame"].destroy()
            create_form_frame["frame"] = None

        create_state["role"] = None

        selector = tk.LabelFrame(
            create_container,
            text="Create Account - Choose Account Type",
            font=sfont(10),
            bg=SURFACE,
            fg=TEXT,
            padx=spad(16),
            pady=spad(12)
        )
        selector.pack(fill="x")
        create_form_frame["frame"] = selector


        btn_row = tk.Frame(selector, bg=SURFACE)
        btn_row.pack(anchor="w", padx=spad(6))

        make_button(
            btn_row,
            "STUDENT",
            lambda: show_create_form("Student"),
            PURPLE
        ).pack(side="left", padx=(0, spad(10)))

        make_button(
            btn_row,
            "TEACHER",
            lambda: show_create_form("Teacher"),
            GREEN
        ).pack(side="left")

       

    def show_create_form(role):
        if create_form_frame["frame"] is not None:
            create_form_frame["frame"].destroy()

        create_state["role"] = role

        form = tk.LabelFrame(
            create_container,
            text=f"Create Account - {role}",
            font=sfont(10),
            bg=SURFACE,
            fg=TEXT,
            padx=spad(12),
            pady=spad(8)
        )
        form.pack(fill="x")
        create_form_frame["frame"] = form

        entries = {}
        role_choice = {"role": role}

        field_layout = [
            ("Username", 0, 0),
            ("Password", 0, 2),
            ("Full Name", 1, 0),
        ]

        for name, row, col in field_layout:
            tk.Label(
                form,
                text=name + ":",
                bg=SURFACE,
                fg=TEXT
            ).grid(
                row=row,
                column=col,
                padx=spad(8),
                pady=spad(6),
                sticky="w"
            )

            entry = make_entry(form, width=23)
            entry.grid(
                row=row,
                column=col + 1,
                padx=spad(8),
                pady=spad(6),
                sticky="w"
            )

            entries[name] = entry

        if role == "Student":
            tk.Label(
                form,
                text="ID Number:",
                bg=SURFACE,
                fg=TEXT
            ).grid(
                row=2,
                column=0,
                padx=spad(8),
                pady=spad(6),
                sticky="w"
            )

            id_entry = make_entry(form, width=23)
            id_entry.grid(
                row=2,
                column=1,
                padx=spad(8),
                pady=spad(6),
                sticky="w"
            )

            entries["ID Number"] = id_entry
            subject_list = None
        else:
            tk.Label(
                form,
                text="Subjects:",
                bg=SURFACE,
                fg=TEXT
            ).grid(
                row=2,
                column=0,
                padx=spad(8),
                pady=spad(6),
                sticky="nw"
            )

            subject_list = tk.Listbox(
                form,
                selectmode="extended",
                height=4,
                width=28,
                font=sfont(9, "normal"),
                bg=SURFACE,
                fg=TEXT,
                selectbackground=BLUE,
                selectforeground=ON_ACCENT,
                highlightthickness=1,
                highlightbackground=BORDER,
                relief="solid",
                bd=1
            )

            for subject in list_subjects():
                subject_list.insert("end", subject)

            subject_list.grid(
                row=2,
                column=1,
                padx=spad(8),
                pady=spad(6),
                sticky="w"
            )

            id_entry = None

        role_hint = tk.Label(
            form,
            text=(
                ""
                if role == "Student"
                else "Hold Ctrl to select several subjects. "
                     
            ),
            bg=SURFACE,
            fg=MUTED,
            font=sfont(8, "normal"),
            wraplength=sx(520),
            justify="left"
        )

        role_hint.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=spad(8),
            pady=(spad(2), spad(6)),
            sticky="w"
        )

        action_row_form = tk.Frame(form, bg=SURFACE)
        action_row_form.grid(
            row=4,
            column=0,
            columnspan=4,
            sticky="w",
            padx=spad(8),
            pady=spad(6)
        )

        def create_account_from_form():
            selected_subjects = []

            if subject_list is not None:
                selected_subjects = [
                    subject_list.get(index)
                    for index in subject_list.curselection()
                ]

            current_role = create_state["role"] or role

            student_id = ""

            if current_role == "Student" and id_entry is not None:
                student_id = id_entry.get().strip()

            success, message = add_user(
                entries["Username"].get(),
                entries["Password"].get(),
                entries["Full Name"].get(),
                current_role,
                admin_username,
                subjects=selected_subjects,
                student_id=student_id
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    message,
                    parent=root
                )

                for entry in entries.values():
                    entry.delete(0, tk.END)

                if id_entry is not None:
                    id_entry.delete(0, tk.END)

                if subject_list is not None:
                    subject_list.selection_clear(0, tk.END)

                refresh_users()
            else:
                messagebox.showerror(
                    "Account Error",
                    message,
                    parent=root
                )

        make_button(
            action_row_form,
            "ADD ACCOUNT",
            create_account_from_form,
            BLUE
        ).pack(side="left", padx=(0, spad(8)))

        make_button(
            action_row_form,
            "BACK",
            show_role_selection,
            GRAY
        ).pack(side="left")

    table_frame = tk.LabelFrame(
        content,
        text="Registered Accounts",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(8)
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=spad(25),
        pady=(spad(8), spad(12))
    )

    search_row = tk.Frame(table_frame, bg=SURFACE)
    search_row.pack(fill="x", pady=(spad(0), spad(6)))

    tk.Label(
        search_row,
        text="Search:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(2), spad(6)))

    search_entry = make_entry(search_row, width=26)
    search_entry.pack(side="left")

    make_button(
        search_row,
        "CLEAR",
        lambda: search_entry.delete(0, tk.END),
        GRAY
    ).pack(side="left", padx=spad(6))

    tk.Label(
        search_row,
        text=(
            "Type a name, username, ID number or role to filter the list."
        ),
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(side="left", padx=spad(6))

    columns = (
        "_id",
        "ID Number",
        "Username",
        "Full Name",
        "Role",
        "Status"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )
    table["displaycolumns"] = (
        "ID Number",
        "Username",
        "Full Name",
        "Role",
        "Status"
    )

    table.column("_id", width=0, stretch=False)

    for column, width in zip(
        columns[1:],
        (140, 190, 330, 120, 110)
    ):
        table.heading(column, text=column)
        table.column(column, width=sx(width), anchor="w")

    table.pack(fill="both", expand=True)

    def refresh_users():
        table.delete(*table.get_children())

        needle = search_entry.get().strip().lower()

        for user in sorted(
            data_store["users"],
            key=lambda item: item.get("id", 0)
        ):
            if user.get("role", "").lower() == "admin":
                continue

            if needle:
                haystack = " ".join([
                    str(user.get("username", "")),
                    str(user.get("full_name", "")),
                    str(user.get("role", "")),
                    str(user.get("student_id", ""))
                ]).lower()

                if needle not in haystack:
                    continue

            table.insert(
                "",
                "end",
                values=(
                    user.get("id", ""),
                    user.get("student_id", "") or "—",
                    user.get("username", ""),
                    user.get("full_name", ""),
                    user.get("role", ""),
                    "Active" if user.get("active", True) else "Inactive"
                )
            )

    search_entry.bind(
        "<KeyRelease>",
        lambda event: refresh_users()
    )

    def selected_user():
        selection = table.selection()

        if not selection:
            messagebox.showwarning(
                "No Account Selected",
                "Select an account from the table first.",
                parent=root
            )
            return None

        values = table.item(selection[0], "values")
        selected_id = str(values[0]).strip()

        user = next(
            (
                user for user in data_store["users"]
                if str(user.get("id", "")).strip() == selected_id
            ),
            None
        )

        if user is None:
            messagebox.showerror(
                "Account Not Found",
                (
                    "The selected account could not be found. "
                    "Click REFRESH and try again."
                ),
                parent=root
            )

        return user

    def create_account():
        selected_subjects = [
            subject_list.get(index)
            for index in subject_list.curselection()
        ]

        role = role_choice["role"]

        student_id = ""

        if role == "Student":
            student_id = entries["ID Number"].get().strip()

        success, message = add_user(
            entries["Username"].get(),
            entries["Password"].get(),
            entries["Full Name"].get(),
            role,
            admin_username,
            subjects=selected_subjects,
            student_id=student_id
        )

        if success:
            messagebox.showinfo(
                "Success",
                message,
                parent=root
            )

            for entry in entries.values():
                entry.delete(0, tk.END)

            subject_list.selection_clear(0, tk.END)

            refresh_users()

        else:
            messagebox.showerror(
                "Account Error",
                message,
                parent=root
            )

    def handle_edit_account():
        user = selected_user()

        if user is None:
            return

        current_role = user.get("role", "Teacher")
        role_options = [current_role]

        if current_role != "Admin":
            role_options += [
                role for role in ROLES
                if role != "Admin" and role != current_role
            ]

        fields = [
            ("full_name", "Full Name", user.get("full_name", ""), "text"),
            ("username", "Username", user.get("username", ""), "text"),
            ("role", "Role", role_options, "combo"),
            (
                "student_id",
                "ID Number (student only)",
                user.get("student_id", ""),
                "text"
            ),
            ("password", "New Password (blank keeps current)", "", "password")
        ]

        if current_role == "Teacher":
            fields.append((
                "subjects",
                "Assigned Subjects (comma separated)",
                ", ".join(subjects_for_teacher(user.get("username", ""))),
                "text"
            ))

        result = show_form_dialog("Edit Account", fields)

        if result is None:
            return

        subjects = None

        if "subjects" in result:
            subjects = [
                item.strip()
                for item in result["subjects"].split(",")
                if item.strip()
            ]

        student_id = None

        if "student_id" in result:
            student_id = result["student_id"].strip()

        success, message = update_user(
            user.get("id"),
            full_name=result.get("full_name", ""),
            username=result.get("username", ""),
            role=result.get("role", ""),
            password=result.get("password", ""),
            actor=admin_username,
            subjects=subjects,
            student_id=student_id
        )

        if success:
            messagebox.showinfo(
                "Account Updated",
                message,
                parent=root
            )

            refresh_users()
        else:
            messagebox.showerror(
                "Update Error",
                message,
                parent=root
            )

    def handle_reset_password():
        user = selected_user()

        if user is None:
            return

        result = show_form_dialog(
            "Reset Password",
            [
                ("password", "New Password", "", "password")
            ]
        )

        if result is None:
            return

        success, message = reset_password(
            user.get("id"),
            result.get("password", ""),
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Password Reset",
                message,
                parent=root
            )
        else:
            messagebox.showerror(
                "Reset Error",
                message,
                parent=root
            )

    def handle_toggle_active():
        user = selected_user()

        if user is None:
            return

        active = user.get("active", True)

        success, message = set_user_active(
            user.get("id"),
            not active,
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Account Updated",
                message,
                parent=root
            )

            refresh_users()
        else:
            messagebox.showerror(
                "Update Error",
                message,
                parent=root
            )

    def handle_delete_account():
        user = selected_user()

        if user is None:
            return

        confirmed = messagebox.askyesno(
            "Delete Account",
            (
                f"Delete the account for "
                f"{user.get('full_name', '')} "
                f"({user.get('username', '')})?\n\n"
                "Any grade records saved for this student "
                "will be removed as well."
            ),
            parent=root
        )

        if not confirmed:
            return

        success, message = delete_user(
            user.get("id"),
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Account Deleted",
                message,
                parent=root
            )

            refresh_users()
        else:
            messagebox.showerror(
                "Delete Error",
                message,
                parent=root
            )

    action_row = tk.Frame(table_frame, bg=SURFACE)
    action_row.pack(fill="x", pady=(spad(8), spad(0)))

    make_button(
        action_row,
        "EDIT ACCOUNT",
        handle_edit_account,
        BLUE
    ).pack(side="left", padx=(spad(0), spad(6)))

    make_button(
        action_row,
        "RESET PASSWORD",
        handle_reset_password,
        PURPLE
    ).pack(side="left", padx=spad(6))

    make_button(
        action_row,
        "ACTIVATE / DEACTIVATE",
        handle_toggle_active,
        GREEN
    ).pack(side="left", padx=spad(6))

    make_button(
        action_row,
        "DELETE ACCOUNT",
        handle_delete_account,
        RED
    ).pack(side="left", padx=spad(6))

    make_button(
        action_row,
        "REFRESH",
        refresh_users,
        GRAY
    ).pack(side="right")

    show_role_selection()
    refresh_users()


# --------------------------------------------------
# ADMIN ACCOUNTS
# --------------------------------------------------

def show_accounts(
    admin_full_name,
    admin_username,
    account_type="Teacher"
):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_accounts(admin_full_name,
    admin_username,
    account_type="Teacher")
    clear_screen()
    build_header(
        "ADMIN ACCOUNTS",
        admin_full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    top = tk.Frame(content, bg=PAGE_BG)
    top.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(8))
    )

    tk.Label(
        top,
        text="Accounts",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left", padx=(spad(0), spad(12)))

    make_button(
        top,
        "TEACHERS",
        lambda: show_accounts(
            admin_full_name,
            admin_username,
            "Teacher"
        ),
        BLUE if account_type == "Teacher" else GRAY
    ).pack(side="left", padx=spad(4))

    make_button(
        top,
        "STUDENTS",
        lambda: show_accounts(
            admin_full_name,
            admin_username,
            "Student"
        ),
        BLUE if account_type == "Student" else GRAY
    ).pack(side="left", padx=spad(4))

    make_button(
        top,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(
            admin_full_name,
            admin_username
        ),
        GRAY
    ).pack(side="right")

    body = tk.Frame(content, bg=PAGE_BG)
    body.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(14))
    )

    left = tk.LabelFrame(
        body,
        text=f"{account_type} Accounts",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10),
        padx=spad(6),
        pady=spad(6)
    )

    place_scaled(
        left,
        0,
        0,
        415,
        520
    )

    if account_type == "Student":
        account_columns = (
            "ID Number",
            "Username",
            "Full Name",
            "Status"
        )

        account_widths = (95, 95, 145, 70)
    else:
        account_columns = ("Username", "Full Name", "Status")

        account_widths = (120, 195, 70)

    account_table = ttk.Treeview(
        left,
        columns=account_columns,
        show="headings"
    )

    for column, width in zip(account_columns, account_widths):
        account_table.heading(column, text=column)
        account_table.column(column, width=sx(width), anchor="w")

    account_table.column("Status", width=sx(70), anchor="center")

    search_frame = tk.Frame(left, bg=SURFACE)
    search_frame.pack(
        fill="x",
        pady=(spad(6), spad(0))
    )

    tk.Label(
        search_frame,
        text="Search:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(2), spad(4)))

    account_search = make_entry(search_frame, width=18)
    account_search.pack(side="left")

    make_button(
        search_frame,
        "CLEAR",
        lambda: (
            account_search.delete(0, tk.END),
            refresh_accounts()
        ),
        GRAY
    ).pack(side="left", padx=spad(6))

    tk.Label(
        search_frame,
        text=(
            "Name, username or ID number"
            if account_type == "Student"
            else "Name or username"
        ),
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(side="left", padx=spad(4))

    account_table.pack(fill="both", expand=True)

    right = tk.LabelFrame(
        body,
        text="Account Details",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10),
        padx=spad(10),
        pady=spad(8)
    )

    place_scaled(
        right,
        430,
        0,
        630,
        520
    )

    def clear_details():
        for widget in right.winfo_children():
            widget.destroy()

    def detail_line(parent, label, value, row):
        tk.Label(
            parent,
            text=label + ":",
            bg=SURFACE,
            fg=MUTED,
            font=sfont(9)
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=spad(6),
            pady=spad(3)
        )

        tk.Label(
            parent,
            text=str(value if value not in (None, "") else "—"),
            bg=SURFACE,
            fg=TEXT,
            font=sfont(9, "normal")
        ).grid(
            row=row,
            column=1,
            sticky="w",
            padx=spad(6),
            pady=spad(3)
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
                bg=SURFACE,
                fg=MUTED
            ).pack(anchor="w", pady=spad(8))
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
                bg=SURFACE,
                fg=RED,
                wraplength=550,
                justify="left"
            ).pack(anchor="w", pady=spad(5))

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

            legacy_table.column("Assessment", width=sx(180))
            legacy_table.column("Saved Value", width=sx(160))

            legacy_table.pack(fill="x", pady=spad(5))

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
                width=sx(width),
                anchor="center"
            )

        grade_table.pack(fill="x", pady=(spad(3), spad(7)))

        for key in ASSESSMENT_NAMES:
            values = [ASSESSMENT_LABELS[key]]

            for term in TERM_NAMES:
                block = terms.get(term)

                value = "—"

                if isinstance(block, dict):
                    value = format_assessment(block.get(key))

                values.append(value)

            grade_table.insert(
                "",
                "end",
                values=values
            )

        term_values = ["Term Grade"]

        for term in TERM_NAMES:
            block = terms.get(term)

            value = "—"

            if isinstance(block, dict):
                value = format_assessment(block.get("term_grade"))

            term_values.append(value)

        grade_table.insert(
            "",
            "end",
            values=term_values
        )

        overall = grade.get("final_grade")

        if not isinstance(overall, (int, float)):
            overall = overall_grade_for_terms(terms)

        if isinstance(overall, (int, float)):
            overall_text = format_overall_grade_display(overall)
        else:
            overall_text = "—"

        tk.Label(
            status_frame,
            text=(
                f"Overall Grade: {overall_text}    "
                f"| Record ID: {grade.get('id', '—')}"
            ),
            bg=SURFACE,
            fg=TEXT,
            font=sfont(10)
        ).pack(anchor="w", pady=spad(4))

    def show_selected_account(event=None):
        selected = account_table.selection()

        if not selected:
            return

        selected_values = account_table.item(
            selected[0],
            "values"
        )

        username = selected_values[account_columns.index("Username")]

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

        info = tk.Frame(right, bg=SURFACE)
        info.pack(fill="x", anchor="n")

        detail_line(info, "Full Name", user.get("full_name"), 0)
        detail_line(info, "Username", user.get("username"), 1)
        detail_line(info, "Role", user.get("role"), 2)

        if user.get("role", "").lower() == "student":
            detail_line(
                info,
                "ID Number",
                user.get("student_id", ""),
                3
            )

        detail_line(
            info,
            "Status",
            "Active" if user.get("active", True) else "Inactive",
            4 if user.get("role", "").lower() == "student" else 3
        )

        if account_type == "Teacher":
            records = grades_for_teacher(username)

            subjects = sorted({
                record.get("subject", "")
                for record in records
                if record.get("subject")
            })

            assigned = subjects_for_teacher(username)

            tk.Label(
                right,
                text=f"Grade records submitted: {len(records)}",
                bg=SURFACE,
                fg=BLUE,
                font=sfont(10)
            ).pack(anchor="w", pady=(spad(12), spad(4)))

            tk.Label(
                right,
                text=(
                    "Assigned subjects: "
                    + (", ".join(assigned) if assigned else "None yet")
                ),
                bg=SURFACE,
                fg=GREEN,
                wraplength=570,
                justify="left"
            ).pack(anchor="w", pady=spad(3))

            tk.Label(
                right,
                text=(
                    "Graded subjects: "
                    + (", ".join(subjects) if subjects else "None yet")
                ),
                bg=SURFACE,
                fg=TEXT,
                wraplength=570,
                justify="left"
            ).pack(anchor="w", pady=spad(3))

            if records:
                tk.Label(
                    right,
                    text="Recent Grade Submissions",
                    bg=SURFACE,
                    fg=TEXT,
                    font=sfont(10)
                ).pack(anchor="w", pady=(spad(10), spad(4)))

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
                        width=sx(width),
                        anchor="w"
                    )

                recent_table.pack(fill="x", pady=spad(3))

                for record in records[:10]:
                    overall = record.get("final_grade", "—")

                    if isinstance(overall, (int, float)):
                        overall = format_overall_grade_display(overall)

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
                    bg=SURFACE,
                    fg=MUTED,
                    wraplength=560,
                    justify="left"
                ).pack(anchor="w", pady=spad(12))

        elif account_type == "Student":
            records = grades_for_student(username)

            subjects = sorted({
                record.get("subject", "")
                for record in records
                if record.get("subject")
            })

            tk.Label(
                right,
                text="Select a subject to view assessment details:",
                bg=SURFACE,
                fg=TEXT,
                font=sfont(10)
            ).pack(anchor="w", pady=(spad(10), spad(4)))

            subject_box = ttk.Combobox(
                right,
                values=subjects,
                state="readonly",
                width=42
            )
            subject_box.pack(anchor="w", pady=(spad(0), spad(8)))

            status_frame = tk.Frame(right, bg=SURFACE)
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
                    bg=SURFACE,
                    fg=MUTED
                ).pack(anchor="w", pady=spad(8))

        else:
            stats = system_statistics()

            tk.Label(
                right,
                text="Administrator account",
                bg=SURFACE,
                fg=BLUE,
                font=sfont(10)
            ).pack(anchor="w", pady=(spad(12), spad(4)))

            tk.Label(
                right,
                text=(
                    "This system runs with a single administrator "
                    "account. The administrator manages accounts, "
                    "subjects, grade records, reports and the "
                    "activity log."
                ),
                bg=SURFACE,
                fg=TEXT,
                wraplength=570,
                justify="left"
            ).pack(anchor="w", pady=spad(3))

            tk.Label(
                right,
                text=(
                    f"Accounts: {stats['total_users']}  |  "
                    f"Grade records: {stats['total_grades']}  |  "
                    f"Class average: {stats['average_grade']:.2f}  |  "
                    f"Pass rate: {stats['pass_rate']:.2f}%"
                ),
                bg=SURFACE,
                fg=TEXT,
                wraplength=570,
                justify="left"
            ).pack(anchor="w", pady=spad(8))

    def refresh_accounts():
        """Fill the account table with the accounts that match the search."""

        account_table.delete(*account_table.get_children())

        needle = account_search.get().strip().lower()

        accounts = sorted(
            [
                user for user in data_store["users"]
                if user.get("role", "").lower() == account_type.lower()
            ],
            key=lambda user: user.get("full_name", "").lower()
        )

        for user in accounts:
            if needle:
                haystack = " ".join([
                    str(user.get("username", "")),
                    str(user.get("full_name", "")),
                    str(user.get("student_id", ""))
                ]).lower()

                if needle not in haystack:
                    continue

            if account_type == "Student":
                values = (
                    user.get("student_id", "") or "—",
                    user.get("username", ""),
                    user.get("full_name", ""),
                    "Active" if user.get("active", True) else "Inactive"
                )
            else:
                values = (
                    user.get("username", ""),
                    user.get("full_name", ""),
                    "Active" if user.get("active", True) else "Inactive"
                )

            account_table.insert(
                "",
                "end",
                values=values
            )

        children = account_table.get_children()

        if children:
            first = children[0]
            account_table.selection_set(first)
            account_table.focus(first)
            show_selected_account()

        else:
            clear_details()

            tk.Label(
                right,
                text=f"No {account_type.lower()} accounts found.",
                bg=SURFACE,
                fg=MUTED
            ).pack(anchor="w", padx=spad(10), pady=spad(10))

    account_search.bind(
        "<KeyRelease>",
        lambda event: refresh_accounts()
    )

    account_table.bind(
        "<<TreeviewSelect>>",
        show_selected_account
    )

    refresh_accounts()


# --------------------------------------------------
# ADMIN ALL GRADE RECORDS
# --------------------------------------------------

ALL_SUBJECTS = "All Subjects"
ALL_TEACHERS = "All Teachers"


def show_all_grades(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_all_grades(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="All Grade Records",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    filters = tk.LabelFrame(
        content,
        text="Filters",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(6)
    )

    filters.pack(fill="x", padx=spad(20), pady=(spad(0), spad(8)))

    tk.Label(
        filters,
        text="Student (username or ID No.):",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(4), spad(4)))

    student_entry = make_entry(filters, width=20)
    student_entry.pack(side="left", padx=(spad(0), spad(12)))

    tk.Label(
        filters,
        text="Subject:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(0), spad(4)))

    subject_box = ttk.Combobox(
        filters,
        values=[ALL_SUBJECTS] + sorted(
            list_subjects(),
            key=str.lower
        ),
        state="readonly",
        width=20
    )

    subject_box.pack(side="left", padx=(spad(0), spad(12)))
    subject_box.set(ALL_SUBJECTS)

    tk.Label(
        filters,
        text="Teacher:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(0), spad(4)))

    teacher_names = sorted({
        grade.get("teacher_username", "")
        for grade in data_store["grades"]
        if grade.get("teacher_username")
    })

    teacher_box = ttk.Combobox(
        filters,
        values=[ALL_TEACHERS] + teacher_names,
        state="readonly",
        width=18
    )

    teacher_box.pack(side="left", padx=(spad(0), spad(12)))
    teacher_box.set(ALL_TEACHERS)

    def apply_filters():
        refresh_records()
        render_record()

    make_button(
        filters,
        "APPLY",
        apply_filters,
        BLUE
    ).pack(side="left", padx=spad(4))

    make_button(
        filters,
        "RESET",
        lambda: (
            student_entry.delete(0, tk.END),
            subject_box.set(ALL_SUBJECTS),
            teacher_box.set(ALL_TEACHERS),
            refresh_records(),
            render_record()
        ),
        GRAY
    ).pack(side="left", padx=spad(4))

    records_frame = tk.LabelFrame(
        content,
        text="Grade Records",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(6),
        pady=spad(6)
    )

    records_frame.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(6))
    )

    columns = (
        "ID",
        "ID No.",
        "Student",
        "Subject",
        "Prelim",
        "Midterm",
        "Semifinal",
        "Finals",
        "Overall",
        "Status",
        "Teacher"
    )

    widths = (45, 110, 130, 140, 70, 70, 80, 65, 70, 70, 125)

    table = ttk.Treeview(
        records_frame,
        columns=columns,
        show="headings",
        height=10
    )

    for column, width in zip(columns, widths):
        table.heading(column, text=column)
        table.column(column, width=sx(width), anchor="center")

    table.pack(fill="both", expand=True)

    detail_frame = tk.LabelFrame(
        content,
        text="Assessment Breakdown",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(6)
    )

    detail_frame.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(0), spad(14))
    )

    def refresh_records():
        table.delete(*table.get_children())

        subject_filter = subject_box.get()
        teacher_filter = teacher_box.get()

        records = all_grade_records(
            student_entry.get(),
            "" if subject_filter == ALL_SUBJECTS else subject_filter,
            "" if teacher_filter == ALL_TEACHERS else teacher_filter
        )

        for record in records:
            terms = record.get("terms", {})
            term_values = []

            for term in TERM_NAMES:
                value = terms.get(term, {}).get("term_grade")

                if isinstance(value, (int, float)):
                    term_values.append(f"{value:.2f}")
                else:
                    term_values.append("Legacy")

            overall = record.get("final_grade")

            if isinstance(overall, (int, float)):
                overall_text = format_grade_point(overall)

                status = (
                    "PASSED"
                    if float(overall) >= PASSING_GRADE
                    else "FAILED"
                )
            else:
                overall_text = "—"
                status = "—"

            table.insert(
                "",
                "end",
                values=(
                    record.get("id", ""),
                    student_id_of(record.get("student_username", "")) or "—",
                    record.get("student_username", ""),
                    record.get("subject", ""),
                    *term_values,
                    overall_text,
                    status,
                    record.get("teacher_username", "") or "(Unassigned)"
                )
            )

        if not records:
            tk.Label(
                records_frame,
                text="No grade records match the current filters.",
                bg=SURFACE,
                fg=MUTED
            ).pack(anchor="w", padx=spad(6))

    def render_record(event=None):
        for widget in detail_frame.winfo_children():
            widget.destroy()

        selection = table.selection()

        if not selection:
            tk.Label(
                detail_frame,
                text="Select a grade record to see its assessment breakdown.",
                bg=SURFACE,
                fg=MUTED
            ).pack(anchor="w", padx=spad(4))
            return

        values = table.item(selection[0], "values")

        record = next(
            (
                grade for grade in data_store["grades"]
                if str(grade.get("id", "")) == str(values[0])
            ),
            None
        )

        if record is None:
            return

        summary = tk.Frame(detail_frame, bg=SURFACE)
        summary.pack(fill="x", anchor="w")

        overall = record.get("final_grade")

        if isinstance(overall, (int, float)):
            overall_text = format_grade_point(overall)

            status = (
                "PASSED"
                if float(overall) >= PASSING_GRADE
                else "FAILED"
            )
        else:
            overall_text = "—"
            status = "—"

        tk.Label(
            summary,
            text=(
                f"Record {record.get('id', '—')}  |  "
                f"Student: {record.get('student_username', '—')}  |  "
                f"Subject: {record.get('subject', '—')}  |  "
                f"Teacher: "
                f"{record.get('teacher_username', '') or '(Unassigned)'}  |  "
                f"Overall: {overall_text}  |  Status: {status}"
            ),
            bg=SURFACE,
            fg=TEXT,
            font=sfont(9)
        ).pack(anchor="w")

        terms = record.get("terms")

        if not isinstance(terms, dict):
            tk.Label(
                detail_frame,
                text=(
                    "This older record has no separate term "
                    "assessment breakdown."
                ),
                bg=SURFACE,
                fg=RED
            ).pack(anchor="w", padx=spad(4), pady=spad(4))
            return

        breakdown_columns = ("Assessment",) + tuple(TERM_NAMES)
        breakdown_widths = (170, 110, 110, 120, 100)

        breakdown = ttk.Treeview(
            detail_frame,
            columns=breakdown_columns,
            show="headings",
            height=5
        )

        for column, width in zip(breakdown_columns, breakdown_widths):
            breakdown.heading(column, text=column)
            breakdown.column(column, width=sx(width), anchor="center")

        breakdown.pack(fill="x", pady=spad(4))

        for key in ASSESSMENT_NAMES:
            row_values = [ASSESSMENT_LABELS[key]]

            for term in TERM_NAMES:
                block = terms.get(term)

                value = "—"

                if isinstance(block, dict):
                    value = format_assessment(block.get(key))

                row_values.append(value)

            breakdown.insert("", "end", values=row_values)

        term_values = ["Term Grade"]

        for term in TERM_NAMES:
            block = terms.get(term)

            value = "—"

            if isinstance(block, dict):
                value = format_assessment(block.get("term_grade"))

            term_values.append(value)

        breakdown.insert("", "end", values=term_values)

    table.bind("<<TreeviewSelect>>", render_record)

    student_entry.bind("<Return>", lambda event: apply_filters())

    refresh_records()
    render_record()


# --------------------------------------------------
# ADMIN SUBJECT MANAGEMENT
# --------------------------------------------------

def show_subjects(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_subjects(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="Subject Management",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    form = tk.LabelFrame(
        content,
        text="Add Subject",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(6)
    )

    form.pack(fill="x", padx=spad(20), pady=(spad(0), spad(8)))

    tk.Label(
        form,
        text="Subject Name:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left", padx=(spad(4), spad(6)))

    subject_entry = make_entry(form, width=34)
    subject_entry.pack(side="left")

    def add_new_subject():
        success, message = add_subject(
            subject_entry.get(),
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Subject Added",
                message,
                parent=root
            )

            subject_entry.delete(0, tk.END)
            refresh_subjects()

        else:
            messagebox.showerror(
                "Subject Error",
                message,
                parent=root
            )

    make_button(
        form,
        "ADD SUBJECT",
        add_new_subject,
        BLUE
    ).pack(side="left", padx=spad(10))

    tk.Label(
        form,
        text=(
            "Teachers pick from this list when saving grades. "
            "Removing a subject keeps existing grade records."
        ),
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(side="left", padx=spad(6))

    table_frame = tk.LabelFrame(
        content,
        text="Subjects Offered",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(8)
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    columns = ("Subject", "Assigned Teachers", "Grade Records")

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=14
    )

    table.heading("Subject", text="Subject")
    table.heading("Assigned Teachers", text="Assigned Teachers")
    table.heading("Grade Records", text="Grade Records")
    table.column("Subject", width=sx(320), anchor="w")
    table.column("Assigned Teachers", width=sx(360), anchor="w")
    table.column("Grade Records", width=sx(160), anchor="center")

    table.pack(fill="both", expand=True)

    def refresh_subjects():
        table.delete(*table.get_children())

        for subject in list_subjects():
            assigned = teachers_for_subject(subject)

            table.insert(
                "",
                "end",
                values=(
                    subject,
                    ", ".join(assigned) if assigned else "No teacher assigned",
                    subject_usage(subject)
                )
            )

    def remove_selected_subject():
        selection = table.selection()

        if not selection:
            messagebox.showwarning(
                "No Subject Selected",
                "Select a subject from the table first.",
                parent=root
            )
            return

        values = table.item(selection[0], "values")
        subject = values[0]

        confirmed = messagebox.askyesno(
            "Remove Subject",
            (
                f"Remove '{subject}' from the subject list?\n\n"
                "Existing grade records that use this subject "
                "are kept."
            ),
            parent=root
        )

        if not confirmed:
            return

        success, message = remove_subject(subject, admin_username)

        if success:
            messagebox.showinfo(
                "Subject Removed",
                message,
                parent=root
            )

            refresh_subjects()

        else:
            messagebox.showerror(
                "Subject Error",
                message,
                parent=root
            )

    action_row = tk.Frame(table_frame, bg=SURFACE)
    action_row.pack(fill="x", pady=(spad(8), spad(0)))

    make_button(
        action_row,
        "REMOVE SELECTED SUBJECT",
        remove_selected_subject,
        RED
    ).pack(side="left", padx=(spad(0), spad(6)))

    make_button(
        action_row,
        "REFRESH",
        refresh_subjects,
        GRAY
    ).pack(side="left", padx=spad(6))

    subject_entry.bind("<Return>", lambda event: add_new_subject())

    refresh_subjects()


# --------------------------------------------------
# ADMIN ANNOUNCEMENTS
# --------------------------------------------------

def show_announcements(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_announcements(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="Announcements",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    form = tk.LabelFrame(
        content,
        text="Post Announcement",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(6)
    )

    form.pack(fill="x", padx=spad(20), pady=(spad(0), spad(8)))

    meta_row = tk.Frame(form, bg=SURFACE)
    meta_row.pack(fill="x", pady=(0, spad(6)))

    tk.Label(
        meta_row,
        text="Title:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left", padx=(spad(4), spad(6)))

    title_entry = make_entry(meta_row, width=46)
    title_entry.pack(side="left")

    tk.Label(
        meta_row,
        text="Audience:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left", padx=(spad(18), spad(6)))

    audience_box = ttk.Combobox(
        meta_row,
        values=list(ANNOUNCEMENT_AUDIENCES),
        state="readonly",
        width=14
    )

    audience_box.set("Everyone")
    audience_box.pack(side="left")

    body_row = tk.Frame(form, bg=SURFACE)
    body_row.pack(fill="x")

    message_text = tk.Text(
        body_row,
        height=4,
        wrap="word",
        font=sfont(10, "normal"),
        bg=SURFACE_ALT,
        fg=TEXT,
        insertbackground=TEXT,
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=BLUE,
        padx=spad(6),
        pady=spad(4)
    )

    message_text.pack(side="left", fill="both", expand=True)

    post_side = tk.Frame(body_row, bg=SURFACE)
    post_side.pack(side="left", fill="y", padx=(spad(10), 0))

    def post_announcement():
        success, message = add_announcement(
            title_entry.get(),
            message_text.get("1.0", "end"),
            audience_box.get(),
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Announcement Posted",
                message,
                parent=root
            )

            title_entry.delete(0, tk.END)
            message_text.delete("1.0", "end")
            audience_box.set("Everyone")
            title_entry.focus_set()

            refresh_announcements()

        else:
            messagebox.showerror(
                "Announcement Error",
                message,
                parent=root
            )

    make_button(
        post_side,
        "POST ANNOUNCEMENT",
        post_announcement,
        BLUE
    ).pack(anchor="n")

    tk.Label(
        post_side,
        text="Title max 90 chars\nMessage max 2000 chars",
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal"),
        justify="left"
    ).pack(anchor="w", pady=(spad(6), 0))

    table_frame = tk.LabelFrame(
        content,
        text="Posted Announcements",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(8)
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    columns = (
        "ID",
        "Title",
        "Audience",
        "Posted By",
        "When",
        "Message"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        displaycolumns=(
            "Title",
            "Audience",
            "Posted By",
            "When",
            "Message"
        ),
        height=12
    )

    table.heading("Title", text="Title")
    table.heading("Audience", text="Audience")
    table.heading("Posted By", text="Posted By")
    table.heading("When", text="When")
    table.heading("Message", text="Message")
    table.column("Title", width=sx(260), anchor="w")
    table.column("Audience", width=sx(100), anchor="center")
    table.column("Posted By", width=sx(150), anchor="w")
    table.column("When", width=sx(210), anchor="center")
    table.column("Message", width=sx(560), anchor="w")

    table.pack(fill="both", expand=True)

    def refresh_announcements():
        table.delete(*table.get_children())

        for notice in all_announcements():
            body = " ".join(notice.get("body", "").split())

            if len(body) > 120:
                body = body[:117] + "..."

            table.insert(
                "",
                "end",
                values=(
                    notice.get("id", ""),
                    notice.get("title", ""),
                    notice.get("audience", ""),
                    notice.get("author", ""),
                    format_display_time(notice.get("timestamp", "")),
                    body
                )
            )

    def delete_selected_announcement():
        selection = table.selection()

        if not selection:
            messagebox.showwarning(
                "No Announcement Selected",
                "Select an announcement from the table first.",
                parent=root
            )
            return

        values = table.item(selection[0], "values")

        confirmed = messagebox.askyesno(
            "Delete Announcement",
            (
                f"Delete '{values[1]}'?\n\n"
                "It will disappear from every dashboard immediately."
            ),
            parent=root
        )

        if not confirmed:
            return

        success, message = delete_announcement(
            values[0],
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Announcement Deleted",
                message,
                parent=root
            )

            refresh_announcements()

        else:
            messagebox.showerror(
                "Announcement Error",
                message,
                parent=root
            )

    action_row = tk.Frame(table_frame, bg=SURFACE)
    action_row.pack(fill="x", pady=(spad(8), 0))

    make_button(
        action_row,
        "DELETE SELECTED ANNOUNCEMENT",
        delete_selected_announcement,
        RED
    ).pack(side="left", padx=(spad(0), spad(6)))

    make_button(
        action_row,
        "REFRESH",
        refresh_announcements,
        GRAY
    ).pack(side="left", padx=spad(6))

    title_entry.bind(
        "<Return>",
        lambda event: message_text.focus_set()
    )

    refresh_announcements()


# --------------------------------------------------
# ADMIN TEACHER ASSIGNMENT
# --------------------------------------------------

def show_teacher_assignments(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_teacher_assignments(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="Teacher Subject Assignment",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    form = tk.LabelFrame(
        content,
        text="Assign a Teacher to a Subject",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(10),
        pady=spad(8)
    )

    form.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(0), spad(8))
    )

    teacher_names = [
        user.get("username", "")
        for user in users_by_role("Teacher")
    ]

    subject_names = list_subjects()

    tk.Label(
        form,
        text="Teacher:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left", padx=(spad(4), spad(6)))

    teacher_box = ttk.Combobox(
        form,
        values=teacher_names,
        state="readonly",
        width=24
    )

    teacher_box.pack(side="left")

    if teacher_names:
        teacher_box.set(teacher_names[0])

    tk.Label(
        form,
        text="Subject:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left", padx=(spad(18), spad(6)))

    subject_box = ttk.Combobox(
        form,
        values=subject_names,
        state="readonly",
        width=26
    )

    subject_box.pack(side="left")

    if subject_names:
        subject_box.set(subject_names[0])

    def assign_teacher():
        teacher = teacher_box.get().strip()
        subject = subject_box.get().strip()

        if not teacher or not subject:
            messagebox.showerror(
                "Missing Information",
                "Choose a teacher and a subject.",
                parent=root
            )
            return

        success, message = assign_subject_to_teacher(
            teacher,
            subject,
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Subject Assigned",
                message,
                parent=root
            )

            refresh_teachers()
            refresh_assignments()

        else:
            messagebox.showerror(
                "Assignment Error",
                message,
                parent=root
            )

    make_button(
        form,
        "ASSIGN",
        assign_teacher,
        BLUE
    ).pack(side="left", padx=spad(14))

    tk.Label(
        form,
        text=(
            "A teacher can handle several subjects and a subject can be "
            "handled by several teachers."
        ),
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(side="left", padx=spad(4))

    body = tk.Frame(content, bg=PAGE_BG)
    body.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    body.grid_columnconfigure(0, weight=1, uniform="assignbody")
    body.grid_columnconfigure(1, weight=1, uniform="assignbody")
    body.rowconfigure(0, weight=1)

    teachers_panel = tk.LabelFrame(
        body,
        text="Teacher Accounts",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(6),
        pady=spad(6)
    )

    teachers_panel.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, spad(6))
    )

    teacher_columns = ("Username", "Full Name", "Assigned Subjects")
    teacher_widths = (150, 200, 320)

    teacher_table = ttk.Treeview(
        teachers_panel,
        columns=teacher_columns,
        show="headings",
        height=12
    )

    for column, width in zip(teacher_columns, teacher_widths):
        teacher_table.heading(column, text=column)
        teacher_table.column(column, width=sx(width), anchor="w")

    teacher_table.pack(fill="both", expand=True)

    def refresh_teachers():
        teacher_table.delete(*teacher_table.get_children())

        for user in users_by_role("Teacher"):
            assigned = subjects_for_teacher(user.get("username", ""))

            teacher_table.insert(
                "",
                "end",
                values=(
                    user.get("username", ""),
                    user.get("full_name", ""),
                    ", ".join(assigned) if assigned else "Not assigned yet"
                )
            )

    assignments_panel = tk.LabelFrame(
        body,
        text="Current Assignments",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(6),
        pady=spad(6)
    )

    assignments_panel.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(spad(6), 0)
    )

    assignment_columns = ("Teacher", "Subject", "Grade Records")
    assignment_widths = (200, 260, 130)

    assignment_table = ttk.Treeview(
        assignments_panel,
        columns=assignment_columns,
        show="headings",
        height=12
    )

    for column, width in zip(assignment_columns, assignment_widths):
        assignment_table.heading(column, text=column)
        assignment_table.column(column, width=sx(width), anchor="w")

    assignment_table.pack(fill="both", expand=True)

    def refresh_assignments():
        assignment_table.delete(*assignment_table.get_children())

        for item in teacher_assignments():
            assignment_table.insert(
                "",
                "end",
                values=(
                    f"{item['teacher_name']} "
                    f"({item['teacher_username']})",
                    item["subject"],
                    item["records"]
                )
            )

    def remove_assignment():
        selection = assignment_table.selection()

        if not selection:
            messagebox.showwarning(
                "No Assignment Selected",
                "Select an assignment from the table first.",
                parent=root
            )
            return

        values = assignment_table.item(selection[0], "values")

        teacher_username = values[0].split("(")[-1].rstrip(")")
        subject = values[1]

        confirmed = messagebox.askyesno(
            "Remove Assignment",
            (
                f"Remove {subject} from {values[0]}?\n\n"
                "Grade records that were already saved are kept."
            ),
            parent=root
        )

        if not confirmed:
            return

        success, message = remove_subject_from_teacher(
            teacher_username,
            subject,
            admin_username
        )

        if success:
            messagebox.showinfo(
                "Assignment Removed",
                message,
                parent=root
            )

            refresh_teachers()
            refresh_assignments()

        else:
            messagebox.showerror(
                "Assignment Error",
                message,
                parent=root
            )

    actions = tk.Frame(assignments_panel, bg=SURFACE)
    actions.pack(fill="x", pady=(spad(8), 0))

    make_button(
        actions,
        "REMOVE SELECTED ASSIGNMENT",
        remove_assignment,
        RED
    ).pack(side="left")

    make_button(
        actions,
        "REFRESH",
        lambda: (refresh_teachers(), refresh_assignments()),
        GRAY
    ).pack(side="left", padx=spad(6))

    refresh_teachers()
    refresh_assignments()

# --------------------------------------------------
# ADMIN ACTIVITY LOG
# --------------------------------------------------

def show_activity_log(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_activity_log(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="Activity Log",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    table_frame = tk.LabelFrame(
        content,
        text="Recorded Administrative Actions",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(8)
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(10))
    )

    columns = ("Timestamp", "Actor", "Action", "Detail")

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=16
    )

    widths = (220, 160, 200, 420)

    for column, width in zip(columns, widths):
        table.heading(column, text=column)
        table.column(column, width=sx(width), anchor="w")

    table.pack(fill="both", expand=True)

    def refresh_log():
        table.delete(*table.get_children())

        entries = activity_entries()

        if not entries:
            tk.Label(
                table_frame,
                text="No activity has been recorded yet.",
                bg=SURFACE,
                fg=MUTED
            ).pack(anchor="w", padx=spad(6))
            return

        for entry in entries:
            table.insert(
                "",
                "end",
                values=(
                    format_display_time(entry.get("timestamp", "")),
                    entry.get("actor", ""),
                    entry.get("action", ""),
                    entry.get("detail", "")
                )
            )

    def clear_log():
        confirmed = messagebox.askyesno(
            "Clear Activity Log",
            "Clear every entry in the activity log?",
            parent=root
        )

        if not confirmed:
            return

        success, message = clear_activity_log(admin_username)

        if success:
            messagebox.showinfo(
                "Activity Log",
                message,
                parent=root
            )

            refresh_log()

        else:
            messagebox.showerror(
                "Activity Log",
                message,
                parent=root
            )

    action_row = tk.Frame(table_frame, bg=SURFACE)
    action_row.pack(fill="x", pady=(spad(8), spad(0)))

    make_button(
        action_row,
        "REFRESH",
        refresh_log,
        GRAY
    ).pack(side="left", padx=(spad(0), spad(6)))

    make_button(
        action_row,
        "CLEAR LOG",
        clear_log,
        RED
    ).pack(side="left", padx=spad(6))

    refresh_log()


# --------------------------------------------------
# ADMIN EXPORT REPORTS
# --------------------------------------------------

def show_exports(full_name, admin_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_exports(full_name, admin_username)
    clear_screen()
    build_header(
        "ADMIN DASHBOARD",
        full_name,
        admin_menu=True,
        admin_username=admin_username
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(10), spad(6))
    )

    tk.Label(
        title_row,
        text="Export Reports",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_admin_dashboard(full_name, admin_username),
        GRAY
    ).pack(side="right")

    tk.Label(
        content,
        text=(
            "Reports are saved as plain text files that can be opened "
            "in any text editor or spreadsheet program."
        ),
        bg=PAGE_BG,
        fg=MUTED,
        font=sfont(9, "normal")
    ).pack(anchor="w", padx=spad(24), pady=(spad(2), spad(8)))

    panel = tk.LabelFrame(
        content,
        text="Available Reports",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(12),
        pady=spad(12)
    )

    panel.pack(
        fill="both",
        expand=True,
        padx=spad(24),
        pady=(spad(0), spad(16))
    )

    def export_report(builder, default_name):
        path = filedialog.asksaveasfilename(
            parent=root,
            title="Save Report",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return

        success, message = write_text_report(path, builder())

        if success:
            messagebox.showinfo(
                "Report Saved",
                f"Report saved to:\n{message}",
                parent=root
            )
        else:
            messagebox.showerror(
                "Export Error",
                message,
                parent=root
            )

    report_data = [
        (
            "USER ACCOUNTS REPORT",
            "Every account with its username, full name, role and status.",
            BLUE,
            build_user_report,
            "smcii_user_accounts.txt"
        ),
        (
            "ALL GRADE RECORDS REPORT",
            "Every grade record with term grades, overall grade and status.",
            GREEN,
            build_grade_report,
            "smcii_grade_records.txt"
        ),
        (
            "SYSTEM ANALYTICS SUMMARY",
            "Account counts, class average, pass rate, per subject "
            "breakdown and top students.",
            PURPLE,
            build_statistics_report,
            "smcii_analytics_summary.txt"
        ),
        (
            "ACTIVITY LOG REPORT",
            "The full activity trail of account, subject and grade actions.",
            RED,
            build_activity_report,
            "smcii_activity_log.txt"
        )
    ]

    for index, (title, description, color, builder, default_name) in enumerate(report_data):
        card = tk.Frame(
            panel,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card.pack(
            fill="x",
            pady=spad(6),
            padx=spad(6)
        )

        tk.Label(
            card,
            text=title,
            font=sfont(12),
            bg=SURFACE,
            fg=color
        ).pack(anchor="w", padx=spad(14), pady=(spad(10), spad(2)))

        tk.Label(
            card,
            text=description,
            font=sfont(9, "normal"),
            bg=SURFACE,
            fg=MUTED,
            wraplength=760,
            justify="left"
        ).pack(anchor="w", padx=spad(14))

        make_button(
            card,
            "SAVE AS TEXT FILE",
            lambda builder=builder, default_name=default_name: export_report(
                builder,
                default_name
            ),
            color
        ).pack(anchor="w", padx=spad(14), pady=(spad(6), spad(12)))


# --------------------------------------------------
# TEACHER DASHBOARD
# --------------------------------------------------

def teacher_menu_items(full_name, teacher_username):
    return [
        (
            "ASSESSMENT SCORES",
            BLUE,
            lambda: show_teacher_assessments(full_name, teacher_username)
        ),
        (
            "CLASS PERFORMANCE",
            PURPLE,
            lambda: show_teacher_performance(full_name, teacher_username)
        ),
        (
            "SUBJECTS",
            GREEN,
            lambda: show_teacher_subjects(full_name, teacher_username)
        )
    ]


def teacher_screen(title, full_name, teacher_username):
    """Build the header and the empty content area of a teacher screen."""

    clear_screen()

    build_header(
        title,
        full_name,
        menu_title="TEACHER MENU",
        menu_items=teacher_menu_items(full_name, teacher_username)
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    return content


def show_teacher_dashboard(full_name, teacher_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_teacher_dashboard(full_name, teacher_username)

    content = teacher_screen(
        "TEACHER DASHBOARD",
        full_name,
        teacher_username
    )

    assigned_subjects = subjects_for_teacher(teacher_username)
    teacher_records = grades_for_teacher(teacher_username)

    graded_students = {
        record.get("student_username", "")
        for record in teacher_records
    }

    class_report = teacher_subject_report(teacher_username)

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(8), spad(4))
    )

    tk.Label(
        title_row,
        text="Grade Management",
        font=sfont(19),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    tk.Label(
        title_row,
        text=(
            "Assigned subjects: "
            + (
                ", ".join(assigned_subjects)
                if assigned_subjects
                else "none assigned yet"
            )
        ),
        font=sfont(9, "normal"),
        bg=PAGE_BG,
        fg=MUTED
    ).pack(side="left", padx=spad(12))

    make_button(
        title_row,
        "REFRESH",
        lambda: show_teacher_dashboard(full_name, teacher_username),
        GRAY
    ).pack(side="right")

    cards = tk.Frame(content, bg=PAGE_BG)
    cards.pack(fill="x", padx=spad(20), pady=(spad(0), spad(6)))

    for column in range(4):
        cards.grid_columnconfigure(
            column,
            weight=1,
            uniform="teachercards"
        )

    class_average = class_report["class_average"]

    card_data = [
        ("Assigned Subjects", len(assigned_subjects), BLUE),
        ("Grade Records", len(teacher_records), PURPLE),
        ("Students Graded", len(graded_students), GREEN),
        (
            "Class Average",
            f"{class_average:.2f}" if class_average is not None else "—",
            RED
        )
    ]

    for index, (label, value, color) in enumerate(card_data):
        make_stat_card(
            cards,
            label,
            value,
            0,
            index,
            color
        )

    notices_frame = tk.LabelFrame(
        content,
        text="Announcements",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(10),
        pady=spad(6)
    )

    notices_frame.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(0), spad(8))
    )

    build_announcement_view(notices_frame, "Teacher", height=4, username=teacher_username)

    build_teacher_records(content, teacher_username)


def show_teacher_assessments(full_name, teacher_username, selected_semester=None):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_teacher_assessments(
        full_name,
        teacher_username,
        selected_semester
    )

    school_year = data_store.get("settings", {}).get("school_year", current_school_year())
    selected_semester = selected_semester or data_store.get("settings", {}).get("current_semester", SEMESTER_NAMES[0])

    content = teacher_screen(
        "ASSESSMENT SCORES",
        full_name,
        teacher_username
    )

    assigned_subjects = subjects_for_teacher(teacher_username)

    students = [
        user.get("username", "")
        for user in users_by_role("Student")
    ]

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(8), spad(4))
    )

    tk.Label(
        title_row,
        text="Assessment Scores",
        font=sfont(19),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    tk.Label(
        title_row,
        text=(
            "Assigned subjects: "
            + (
                ", ".join(assigned_subjects)
                if assigned_subjects
                else "none assigned yet"
            )
        ),
        font=sfont(9, "normal"),
        bg=PAGE_BG,
        fg=MUTED
    ).pack(side="left", padx=spad(12))

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_teacher_dashboard(full_name, teacher_username),
        GRAY
    ).pack(side="right")

    entry_panel = tk.LabelFrame(
        content,
        text="Assessment Scores",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(6)
    )

    entry_panel.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    selector_row = tk.Frame(entry_panel, bg=SURFACE)
    selector_row.pack(fill="x")

    tk.Label(
        selector_row,
        text="Student (username or ID No.):",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(2), spad(4)))

    student_box = ttk.Combobox(
        selector_row,
        values=students,
        state="normal",
        width=22
    )

    student_box.pack(side="left", padx=(0, spad(10)))

    tk.Label(
        selector_row,
        text="Subject:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(0, spad(4)))

    subject_box = ttk.Combobox(
        selector_row,
        values=assigned_subjects,
        state="readonly",
        width=20
    )

    subject_box.pack(side="left", padx=(0, spad(10)))

    tk.Label(
        selector_row,
        text="Semester:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(0, spad(4)))

    semester_box = ttk.Combobox(
        selector_row,
        values=SEMESTER_NAMES,
        state="readonly",
        width=20
    )
    semester_box.set(selected_semester)
    semester_box.pack(side="left", padx=(0, spad(10)))
    semester_box.bind(
        "<<ComboboxSelected>>",
        lambda event: show_teacher_assessments(
            full_name,
            teacher_username,
            semester_box.get()
        )
    )

    tk.Label(
        selector_row,
        text="Term:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(0, spad(4)))

    term_box = ttk.Combobox(
        selector_row,
        values=list(TERM_NAMES),
        state="readonly",
        width=12
    )

    term_box.pack(side="left")

    if assigned_subjects:
        subject_box.set(assigned_subjects[0])

    term_box.set(TERM_NAMES[0])

    student_status = tk.Label(
        entry_panel,
        text="",
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal"),
        anchor="w"
    )

    student_status.pack(
        fill="x",
        pady=(spad(4), spad(0))
    )

    def refresh_student_status():
        """Show the student that matches the typed username or ID number."""

        reference = student_box.get().strip()

        if not reference:
            student_status.configure(
                text=(
                    "Type a student username or ID number to find "
                    "the student."
                ),
                fg=MUTED
            )

            return

        student = find_student_by_reference(reference)

        if student is None:
            student_status.configure(
                text=f"No student matches '{reference}'.",
                fg=RED
            )

            return

        student_status.configure(
            text=(
                f"Selected: {student.get('full_name', '')}  |  "
                f"Username: {student.get('username', '')}  |  "
                f"ID Number: {student.get('student_id', '') or '—'}"
            ),
            fg=GREEN
        )

    semester_open, semester_message = semester_open_for_entry(selected_semester, school_year)
    tk.Label(
        entry_panel,
        text=(
            f"Semester status: {semester_status_for(selected_semester, school_year)}  |  School year: {school_year}"
            if assigned_subjects else
            "The administrator has not assigned you a subject yet. Ask the administrator to assign your subject before entering grades."
        ),
        bg=SURFACE,
        fg=GREEN if semester_open else RED,
        font=sfont(8, "normal"),
        wraplength=sx(540),
        justify="left"
    ).pack(
        anchor="w",
        pady=(spad(6), spad(2))
    )

    tk.Label(
        entry_panel,
        text=(
            "Pick a term, enter every score of that term and calculate it. Activities and quizzes are combined as written works (30%), the exam is 30% and the performance task is 40% of the term grade. The saved terms build the overall grade."
            if assigned_subjects else
            ""
        ),
        bg=SURFACE,
        fg=MUTED if assigned_subjects else RED,
        font=sfont(8, "normal"),
        wraplength=sx(540),
        justify="left"
    ).pack(
        anchor="w",
        pady=(spad(2), spad(2))
    )

    if not semester_open:
        tk.Label(
            entry_panel,
            text=semester_message,
            bg=SURFACE,
            fg=RED,
            font=sfont(9, "bold"),
            wraplength=sx(540),
            justify="left"
        ).pack(anchor="w", pady=(spad(2), spad(4)))

    score_frame = tk.Frame(entry_panel, bg=SURFACE)
    score_frame.pack(fill="x", pady=(spad(4), spad(2)))

    table_columns = [
        ("No.", 56),
        ("Type", 120),
        ("Assessment / Item", 200),
        ("Points Earned", 112),
        ("Points Possible", 112),
        ("Score %", 110),
        ("", 92),
    ]

    header_row = tk.Frame(score_frame, bg=SURFACE)
    header_row.pack(fill="x", pady=(0, spad(4)))

    header_label_fg = ON_ACCENT if THEME == "dark" else TEXT

    for col_index, (text, width) in enumerate(table_columns):
        label = tk.Label(
            header_row,
            text=text,
            bg=SURFACE,
            fg=header_label_fg,
            font=sfont(8, "bold"),
            anchor="center",
            justify="center",
            width=max(8, width // 8)
        )
        label.grid(row=0, column=col_index, sticky="ew", padx=0, pady=0)
        header_row.grid_columnconfigure(col_index, minsize=width, weight=0)
        header_row.columnconfigure(col_index, weight=0)

    table_canvas = tk.Canvas(
        score_frame,
        bg=SURFACE,
        highlightthickness=0,
        height=spad(28)
    )
    table_scrollbar = ttk.Scrollbar(
        score_frame,
        orient="vertical",
        command=table_canvas.yview
    )
    table_canvas.configure(yscrollcommand=table_scrollbar.set)
    table_scrollbar.pack_forget()
    table_canvas.pack(side="left", fill="x", expand=True)

    rows_container = tk.Frame(table_canvas, bg=SURFACE)
    rows_container_id = table_canvas.create_window((0, 0), window=rows_container, anchor="nw")

    for col_index, (_, width) in enumerate(table_columns):
        rows_container.grid_columnconfigure(col_index, minsize=width, weight=1)

    def sync_table_width():
        header_width = max(header_row.winfo_reqwidth(), 1)
        rows_width = max(rows_container.winfo_reqwidth(), 1)
        target_width = max(header_width, rows_width)
        rows_container.configure(width=target_width)
        table_canvas.itemconfig(rows_container_id, width=target_width)

    def apply_table_scrollregion():
        rows_container.update_idletasks()
        table_canvas.update_idletasks()
        canvas_width = max(rows_container.winfo_reqwidth(), rows_container.winfo_width(), header_row.winfo_reqwidth(), table_canvas.winfo_width(), 1)
        rows_height = max(rows_container.winfo_reqheight(), rows_container.winfo_height(), 1)
        table_canvas.configure(scrollregion=(0, 0, canvas_width, rows_height + 8))
        table_canvas.itemconfig(rows_container_id, width=canvas_width)

    def update_assessment_table_view():
        row_count = len(assessment_rows)
        visible_rows = 5
        if assessment_rows:
            row_height = max(32, max(row_meta["frame"].winfo_reqheight() for row_meta in assessment_rows))
        else:
            row_height = 32

        header_height = max(header_row.winfo_reqheight(), 20)
        padding = spad(12)

        if row_count <= visible_rows:
            target_height = header_height + (row_height * row_count) + padding
            table_canvas.configure(height=target_height)
            table_scrollbar.pack_forget()
            table_canvas.configure(yscrollcommand=None)
        else:
            target_height = header_height + (row_height * visible_rows) + padding
            table_canvas.configure(height=target_height)
            table_scrollbar.pack(side="right", fill="y")
            table_canvas.configure(yscrollcommand=table_scrollbar.set)

        rows_container.update_idletasks()
        sync_table_width()
        apply_table_scrollregion()

        if row_count <= visible_rows:
            table_canvas.yview_moveto(0)

    def on_canvas_mousewheel(event):
        if table_scrollbar.winfo_ismapped():
            table_canvas.yview_scroll(int(event.delta / 120), "units")

    table_canvas.bind("<MouseWheel>", on_canvas_mousewheel)
    table_canvas.bind("<Button-4>", lambda event: table_canvas.yview_scroll(-1, "units"))
    table_canvas.bind("<Button-5>", lambda event: table_canvas.yview_scroll(1, "units"))

    def on_table_configure(event):
        sync_table_width()
        table_canvas.itemconfig(rows_container_id, width=max(event.width, 1))

    table_canvas.bind("<Configure>", on_table_configure)

    assessment_rows = []

    globals()["table_canvas"] = table_canvas
    globals()["table_scrollbar"] = table_scrollbar
    globals()["rows_container"] = rows_container
    globals()["assessment_rows"] = assessment_rows

    def parse_row_record(row_meta):
        name = row_meta["name"].get().strip()
        if not name:
            return None

        category = row_meta["type"].get().strip() or "Activity"
        raw_earned = row_meta["earned"].get().strip()
        raw_possible = row_meta["possible"].get().strip()

        try:
            earned = float(raw_earned)
        except (TypeError, ValueError):
            return None

        try:
            possible = float(raw_possible)
        except (TypeError, ValueError):
            return None

        if earned < 0 or possible <= 0 or earned > possible:
            return None

        return {
            "category": category,
            "assessment_name": name,
            "points_earned": earned,
            "possible_points": possible,
            "percentage": calculate_assessment_percentage(earned, possible),
        }

    def refresh_row_percent(row_meta):
        payload = parse_row_record(row_meta)
        if payload is None:
            row_meta["percent"].configure(text="—")
            row_meta["percent"].configure(fg=MUTED)
            return

        row_meta["percent"].configure(
            text=f"{payload['percentage']:.2f}%"
        )
        row_meta["percent"].configure(fg=TEXT)

    def sync_row_numbers():
        for index, row_meta in enumerate(assessment_rows, start=1):
            row_meta["number"].configure(text=str(index))

    def delete_row(row_meta):
        record_id = row_meta.get("record_id")
        if record_id is not None:
            success, message = delete_assessment_score(record_id, actor=teacher_username)
            if not success:
                messagebox.showerror("Delete Failed", message, parent=root)
                return

        row_meta["frame"].destroy()
        assessment_rows.remove(row_meta)
        sync_row_numbers()
        update_assessment_table_view()
        refresh_gradebook_summary()

    def add_assessment_row(initial_data=None):
        row_frame = tk.Frame(rows_container, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row_frame.grid(row=len(assessment_rows), column=0, columnspan=7, sticky="ew", padx=spad(2), pady=spad(2))

        for col_index, (_, width) in enumerate(table_columns):
            row_frame.grid_columnconfigure(col_index, minsize=width, weight=0)
            row_frame.columnconfigure(col_index, weight=0)

        row_meta = {
            "frame": row_frame,
            "record_id": None,
            "number": tk.Label(row_frame, text="1", bg=SURFACE, fg=TEXT, font=sfont(9), anchor="center", width=4),
            "type": ttk.Combobox(row_frame, values=["Activity", "Quiz", "Performance Task", "Exam"], state="readonly", width=12),
            "name": make_entry(row_frame, width=18),
            "earned": make_entry(row_frame, width=10),
            "possible": make_entry(row_frame, width=10),
            "percent": tk.Label(row_frame, text="—", bg=SURFACE, fg=MUTED, font=sfont(9, "bold"), anchor="center", width=10),
        }

        row_meta["number"].grid(row=0, column=0, padx=0, sticky="nsew")
        row_meta["type"].grid(row=0, column=1, padx=0, sticky="nsew")
        row_meta["name"].grid(row=0, column=2, padx=0, sticky="nsew")
        row_meta["earned"].grid(row=0, column=3, padx=0, sticky="nsew")
        row_meta["possible"].grid(row=0, column=4, padx=0, sticky="nsew")
        row_meta["percent"].grid(row=0, column=5, padx=0, sticky="nsew")

        row_meta["type"].set("Activity")
        row_meta["name"].bind("<KeyRelease>", lambda event: refresh_gradebook_summary())
        row_meta["earned"].bind("<KeyRelease>", lambda event: refresh_gradebook_summary())
        row_meta["possible"].bind("<KeyRelease>", lambda event: refresh_gradebook_summary())
        row_meta["type"].bind("<<ComboboxSelected>>", lambda event: refresh_gradebook_summary())

        delete_button = make_button(row_frame, "DELETE", lambda selected=row_meta: delete_row(selected), RED, width=10)
        delete_button.grid(row=0, column=6, padx=0, sticky="nsew")
        row_meta["delete"] = delete_button

        if initial_data is not None:
            row_meta["record_id"] = initial_data.get("id")
            row_meta["type"].set(initial_data.get("category", "Activity"))
            row_meta["name"].insert(0, initial_data.get("assessment_name", ""))
            row_meta["earned"].insert(0, str(initial_data.get("points_earned", "")))
            row_meta["possible"].insert(0, str(initial_data.get("possible_points", "")))
            refresh_row_percent(row_meta)
        else:
            refresh_row_percent(row_meta)

        assessment_rows.append(row_meta)
        sync_row_numbers()
        update_assessment_table_view()
        apply_table_scrollregion()
        refresh_gradebook_summary()
        globals()["add_assessment_row"] = add_assessment_row
        globals()["update_assessment_table_view"] = update_assessment_table_view
        globals()["refresh_gradebook_summary"] = refresh_gradebook_summary
        return row_meta

    def load_gradebook_rows():
        student_ref = student_box.get().strip()
        if not student_ref:
            for row_meta in list(assessment_rows):
                row_meta["frame"].destroy()
            assessment_rows.clear()
            add_assessment_row()
            update_assessment_table_view()
            refresh_gradebook_summary()
            return

        student = find_student_by_reference(student_ref)
        student_username = student.get("username", student_ref) if student else student_ref
        subject = subject_box.get().strip()
        period = term_box.get().strip() or TERM_NAMES[0]
        selected_semester = semester_box.get().strip() or selected_semester

        for row_meta in list(assessment_rows):
            row_meta["frame"].destroy()
        assessment_rows.clear()

        saved_records = []
        if student_username and subject:
            saved_records = assessment_records_for_student(
                student_username,
                subject=subject,
                semester=selected_semester,
                school_year=school_year,
                grading_period=period,
            )

        if saved_records:
            for record in saved_records:
                add_assessment_row(record)
        else:
            add_assessment_row()

        update_assessment_table_view()
        refresh_gradebook_summary()

    def refresh_gradebook_summary():
        refresh_student_status()

        valid_records = []
        for row_meta in assessment_rows:
            payload = parse_row_record(row_meta)
            if payload is not None:
                valid_records.append(payload)

        category_totals = {
            "Activity": {"earned": 0.0, "possible": 0.0},
            "Quiz": {"earned": 0.0, "possible": 0.0},
            "Performance Task": {"earned": 0.0, "possible": 0.0},
            "Exam": {"earned": 0.0, "possible": 0.0},
        }

        for item in valid_records:
            category = item["category"]
            category_totals.setdefault(category, {"earned": 0.0, "possible": 0.0})
            category_totals[category]["earned"] += item["points_earned"]
            category_totals[category]["possible"] += item["possible_points"]

        category_labels = {
            "Activity": activity_percentage_label,
            "Quiz": quiz_percentage_label,
            "Performance Task": performance_percentage_label,
            "Exam": exam_percentage_label,
        }

        for key in category_totals:
            total = category_totals[key]
            percentage = None
            if total["possible"] > 0:
                percentage = (total["earned"] / total["possible"]) * 100.0
            category_labels[key].configure(
                text=(
                    f"{total['earned']:.2f} / {total['possible']:.2f}  |  {percentage:.2f}%"
                    if total["possible"] > 0 and percentage is not None
                    else "0.00 / 0.00  |  —"
                )
            )

        required_categories = ["Activity", "Quiz", "Exam", "Performance Task"]
        missing = [category for category in required_categories if category_totals.get(category, {}).get("possible", 0) <= 0]

        if not valid_records:
            term_result.configure(text="Weighted term grade (term): —")
            overall_result.configure(text="Equivalent college grade: —")
            saved_result.configure(text="Assessment rows: 0 valid entries")
            return

        activity_pct = (category_totals["Activity"]["earned"] / category_totals["Activity"]["possible"]) * 100.0 if category_totals["Activity"]["possible"] > 0 else None
        quiz_pct = (category_totals["Quiz"]["earned"] / category_totals["Quiz"]["possible"]) * 100.0 if category_totals["Quiz"]["possible"] > 0 else None
        exam_pct = (category_totals["Exam"]["earned"] / category_totals["Exam"]["possible"]) * 100.0 if category_totals["Exam"]["possible"] > 0 else None
        performance_pct = (category_totals["Performance Task"]["earned"] / category_totals["Performance Task"]["possible"]) * 100.0 if category_totals["Performance Task"]["possible"] > 0 else None

        if any(value is None for value in (activity_pct, quiz_pct, exam_pct, performance_pct)):
            term_result.configure(text="Weighted term grade (term): Need all required categories to compute")
            overall_result.configure(text="Equivalent college grade: —")
            saved_result.configure(text=(
                "Missing category data: " + ", ".join(missing)
                if missing else "Assessment rows need to be completed"
            ))
            return

        written_component = ((activity_pct + quiz_pct) / 2.0) * 0.30
        exam_component = exam_pct * 0.30
        performance_component = performance_pct * 0.40
        weighted_grade = written_component + exam_component + performance_component
        weighted_grade = round(weighted_grade, 2)
        grade_point = grade_point_equivalent(weighted_grade)

        term_result.configure(
            text=f"Weighted term grade ({term_box.get().strip() or 'term'}): {weighted_grade:.2f}%"
        )
        overall_result.configure(
            text=(
                f"Equivalent college grade: {grade_point:.2f}"
                if grade_point is not None
                else "Equivalent college grade: —"
            )
        )
        saved_result.configure(text=f"Assessment rows: {len(valid_records)} valid record(s)")

    def save_gradebook_rows():
        student_ref = student_box.get().strip()
        if not student_ref:
            messagebox.showerror("Missing Student", "Choose a student before saving assessment rows.", parent=root)
            return

        student = find_student_by_reference(student_ref)
        if student is None:
            messagebox.showerror("Missing Student", f"No student matches '{student_ref}'.", parent=root)
            return

        subject = subject_box.get().strip()
        if not subject:
            messagebox.showerror("Missing Subject", "Choose a subject before saving assessment rows.", parent=root)
            return

        allowed, reason = semester_open_for_entry(semester_box.get().strip(), school_year)
        if not allowed:
            messagebox.showerror("Semester Locked", reason, parent=root)
            return

        valid_count = 0
        for row_meta in list(assessment_rows):
            payload = parse_row_record(row_meta)
            if payload is None:
                continue

            valid_count += 1
            record_id = row_meta.get("record_id")
            result = (
                edit_assessment_score(
                    record_id,
                    student.get("username", student_ref),
                    subject,
                    payload["assessment_name"],
                    payload["category"],
                    payload["points_earned"],
                    payload["possible_points"],
                    teacher_username=teacher_username,
                    actor=teacher_username,
                    semester=semester_box.get().strip(),
                    school_year=school_year,
                    grading_period=term_box.get().strip() or TERM_NAMES[0],
                )
                if record_id is not None
                else add_assessment_score(
                    student.get("username", student_ref),
                    subject,
                    payload["assessment_name"],
                    payload["category"],
                    payload["points_earned"],
                    payload["possible_points"],
                    teacher_username=teacher_username,
                    actor=teacher_username,
                    semester=semester_box.get().strip(),
                    school_year=school_year,
                    grading_period=term_box.get().strip() or TERM_NAMES[0],
                )
            )
            if not result[0]:
                messagebox.showerror("Save Failed", result[1], parent=root)
                return

            if record_id is None:
                row_meta["record_id"] = next(
                    item.get("id")
                    for item in reversed(data_store.get("assessment_scores", []))
                    if item.get("student_username", "").lower() == student.get("username", student_ref).lower()
                    and item.get("subject", "").lower() == subject.lower()
                    and item.get("assessment_name", "").strip().lower() == payload["assessment_name"].lower()
                )

        if valid_count == 0:
            messagebox.showwarning("No Valid Rows", "Enter at least one valid assessment row before saving.", parent=root)
            return

        messagebox.showinfo("Assessment Gradebook Saved", f"Saved {valid_count} assessment record(s).", parent=root)
        load_gradebook_rows()

    def clear_gradebook_rows():
        for row_meta in list(assessment_rows):
            row_meta["frame"].destroy()
        assessment_rows.clear()
        add_assessment_row()
        update_assessment_table_view()
        refresh_gradebook_summary()

    def update_preview():
        refresh_student_status()
        refresh_gradebook_summary()

    average_frame = tk.Frame(entry_panel, bg=SURFACE)
    average_frame.pack(fill="x", pady=(spad(4), spad(2)))

    category_labels = {}
    category_names = [
        ("Activity", "activity_percentage_label"),
        ("Quiz", "quiz_percentage_label"),
        ("Performance Task", "performance_percentage_label"),
        ("Exam", "exam_percentage_label"),
    ]

    for label_text, variable_name in category_names:
        cell = tk.Frame(average_frame, bg=SURFACE)
        cell.pack(side="left", padx=spad(10), expand=True, fill="x")

        tk.Label(
            cell,
            text=label_text,
            bg=SURFACE,
            fg=MUTED,
            font=sfont(8)
        ).pack(anchor="w")

        value_label = tk.Label(
            cell,
            text="0.00 / 0.00  |  —",
            bg=SURFACE,
            fg=TEXT,
            font=sfont(10, "bold")
        )
        value_label.pack(anchor="w")
        category_labels[variable_name] = value_label

    activity_percentage_label = category_labels["activity_percentage_label"]
    quiz_percentage_label = category_labels["quiz_percentage_label"]
    performance_percentage_label = category_labels["performance_percentage_label"]
    exam_percentage_label = category_labels["exam_percentage_label"]

    result_frame = tk.LabelFrame(
        entry_panel,
        text="Calculation",
        font=sfont(9),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(4)
    )

    result_frame.pack(fill="x", pady=(spad(4), spad(2)))

    term_result = tk.Label(
        result_frame,
        text="Weighted term grade (term): —",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(11)
    )
    term_result.pack(anchor="w")

    tk.Label(
        result_frame,
        text=(
            "Weight: "
            + "  |  ".join(
                f"{ASSESSMENT_WEIGHT_LABELS[key]} {weight:.0%}"
                for key, weight in ASSESSMENT_WEIGHTS.items()
            )
        ),
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(anchor="w")

    overall_result = tk.Label(
        result_frame,
        text="Equivalent college grade: —",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(11)
    )
    overall_result.pack(anchor="w")

    saved_result = tk.Label(
        result_frame,
        text="Assessment rows: 0 valid record(s)",
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    )
    saved_result.pack(anchor="w", pady=(spad(2), 0))

    button_row = tk.Frame(entry_panel, bg=SURFACE)
    button_row.pack(fill="x", pady=(spad(6), spad(2)))

    make_button(
        button_row,
        "+ ADD ASSESSMENT ROW",
        lambda: add_assessment_row(),
        GREEN
    ).pack(side="left", padx=(0, spad(6)))

    make_button(
        button_row,
        "SAVE ASSESSMENTS",
        save_gradebook_rows,
        BLUE
    ).pack(side="left", padx=(0, spad(6)))

    make_button(
        button_row,
        "LOAD SAVED",
        load_gradebook_rows,
        PURPLE
    ).pack(side="left", padx=(0, spad(6)))

    make_button(
        button_row,
        "CLEAR",
        clear_gradebook_rows,
        GRAY
    ).pack(side="left")

    subject_box.bind(
        "<<ComboboxSelected>>",
        lambda event: load_gradebook_rows()
    )

    student_box.bind(
        "<KeyRelease>",
        lambda event: (refresh_student_status(), load_gradebook_rows())
    )

    student_box.bind(
        "<<ComboboxSelected>>",
        lambda event: load_gradebook_rows()
    )

    term_box.bind(
        "<<ComboboxSelected>>",
        lambda event: load_gradebook_rows()
    )

    semester_box.bind(
        "<<ComboboxSelected>>",
        lambda event: load_gradebook_rows()
    )

    load_gradebook_rows()


def show_teacher_performance(full_name, teacher_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_teacher_performance(
        full_name,
        teacher_username
    )

    content = teacher_screen(
        "CLASS PERFORMANCE",
        full_name,
        teacher_username
    )

    assigned_subjects = subjects_for_teacher(teacher_username)

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(8), spad(4))
    )

    tk.Label(
        title_row,
        text="Class Performance",
        font=sfont(19),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_teacher_dashboard(full_name, teacher_username),
        GRAY
    ).pack(side="right")

    performance_panel = tk.LabelFrame(
        content,
        text="Class Performance",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(6),
        pady=spad(6)
    )

    performance_panel.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    selector_row = tk.Frame(performance_panel, bg=SURFACE)
    selector_row.pack(fill="x", pady=(0, spad(4)))

    tk.Label(
        selector_row,
        text="Subject:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9)
    ).pack(side="left", padx=(spad(2), spad(4)))

    performance_subject_box = ttk.Combobox(
        selector_row,
        values=assigned_subjects,
        state="readonly",
        width=24
    )

    performance_subject_box.pack(side="left")

    if assigned_subjects:
        performance_subject_box.set(assigned_subjects[0])

    tk.Label(
        selector_row,
        text="Pick a subject to see every student graded in it.",
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(side="left", padx=spad(10))

    class_stats_label = tk.Label(
        performance_panel,
        text="No grade records yet.",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(9),
        justify="left"
    )

    class_stats_label.pack(anchor="w", pady=(0, spad(4)))

    class_columns = (
        "ID No.",
        "Student",
        "Prelim",
        "Midterm",
        "Semifinal",
        "Finals",
        "Overall",
        "Status"
    )

    class_widths = (80, 85, 45, 50, 58, 45, 58, 54)

    class_table = ttk.Treeview(
        performance_panel,
        columns=class_columns,
        show="headings",
        height=9
    )

    for column, width in zip(class_columns, class_widths):
        class_table.heading(column, text=column)
        class_table.column(column, width=sx(width), anchor="center")

    class_table.pack(fill="both", expand=True)

    def refresh_class_table():
        class_table.delete(*class_table.get_children())

        subject = performance_subject_box.get().strip()
        report = teacher_subject_report(teacher_username, subject)

        if report["class_average"] is None:
            class_stats_label.configure(
                text="No grade records for this subject yet."
            )
        else:
            class_stats_label.configure(
                text=(
                    f"Class average: {report['class_average']:.2f}   |   "
                    f"Highest: {report['highest']:.2f}   |   "
                    f"Lowest: {report['lowest']:.2f}   |   "
                    f"Passed: {report['passing']}   |   "
                    f"Failed: {report['failing']}"
                )
            )

        for row in report["rows"]:
            values = [
                row.get("student_id", "") or "—",
                row["student_username"]
            ]

            for term in TERM_NAMES:
                value = row["terms"].get(term)

                if isinstance(value, (int, float)):
                    values.append(f"{value:.2f}")
                else:
                    values.append("—")

            overall = row["overall"]

            if isinstance(overall, (int, float)):
                values.append(format_overall_grade_display(overall))
            else:
                values.append("—")

            values.append(row["status"])

            class_table.insert("", "end", values=values)

    performance_subject_box.bind(
        "<<ComboboxSelected>>",
        lambda event: refresh_class_table()
    )

    refresh_class_table()


def build_teacher_records(parent, teacher_username):
    """Build the submitted grade records table of a teacher."""

    records_frame = tk.LabelFrame(
        parent,
        text="Submitted Grade Records",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(6),
        pady=spad(6)
    )

    records_frame.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    record_columns = (
        "ID",
        "Student",
        "Subject",
        "Prelim",
        "Midterm",
        "Semifinal",
        "Finals",
        "Overall",
        "Status"
    )

    record_widths = (45, 150, 190, 80, 80, 90, 75, 85, 85)

    records_table = ttk.Treeview(
        records_frame,
        columns=record_columns,
        show="headings",
        height=10
    )

    for column, width in zip(record_columns, record_widths):
        records_table.heading(column, text=column)
        records_table.column(column, width=sx(width), anchor="center")

    records_table.pack(fill="both", expand=True)

    def refresh_records():
        records_table.delete(*records_table.get_children())

        for grade in grades_for_teacher(teacher_username):
            terms = grade.get("terms", {})
            term_grades = []

            for term in TERM_NAMES:
                value = terms.get(term, {}).get("term_grade")

                if isinstance(value, (int, float)):
                    term_grades.append(f"{value:.2f}")
                else:
                    term_grades.append("—")

            overall = grade.get("final_grade")

            if not isinstance(overall, (int, float)):
                overall = overall_grade_for_terms(terms)

            if isinstance(overall, (int, float)):
                overall_text = format_overall_grade_display(overall)
                status = (
                    "PASSED"
                    if float(overall) >= PASSING_GRADE
                    else "FAILED"
                )
            else:
                overall_text = "—"
                status = "—"

            records_table.insert(
                "",
                "end",
                values=(
                    grade.get("id", ""),
                    grade.get("student_username", ""),
                    grade.get("subject", ""),
                    *term_grades,
                    overall_text,
                    status
                )
            )

    def handle_delete_record():
        selection = records_table.selection()

        if not selection:
            messagebox.showwarning(
                "No Record Selected",
                "Select a grade record from the table first.",
                parent=root
            )
            return

        values = records_table.item(selection[0], "values")

        confirmed = messagebox.askyesno(
            "Delete Grade Record",
            (
                f"Delete the {values[2]} record of {values[1]}?\n\n"
                "All term scores of this record will be removed."
            ),
            parent=root
        )

        if not confirmed:
            return

        record_id = values[0]

        try:
            record_id = int(record_id)
        except (TypeError, ValueError):
            pass

        success, message = delete_grade(
            record_id,
            teacher_username
        )

        if success:
            messagebox.showinfo(
                "Record Deleted",
                message,
                parent=root
            )

            refresh_records()

        else:
            messagebox.showerror(
                "Delete Error",
                message,
                parent=root
            )

    record_actions = tk.Frame(records_frame, bg=SURFACE)
    record_actions.pack(fill="x", pady=(spad(6), 0))

    make_button(
        record_actions,
        "DELETE SELECTED RECORD",
        handle_delete_record,
        RED
    ).pack(side="left")

    make_button(
        record_actions,
        "REFRESH",
        refresh_records,
        GRAY
    ).pack(side="left", padx=spad(6))

    refresh_records()


def show_teacher_subjects(full_name, teacher_username):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_teacher_subjects(
        full_name,
        teacher_username
    )

    content = teacher_screen(
        "MY SUBJECTS",
        full_name,
        teacher_username
    )

    assigned_subjects = subjects_for_teacher(teacher_username)

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(20),
        pady=(spad(8), spad(4))
    )

    tk.Label(
        title_row,
        text="My Subjects",
        font=sfont(19),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    tk.Label(
        title_row,
        text=f"{len(assigned_subjects)} subject(s) assigned to you",
        font=sfont(9, "normal"),
        bg=PAGE_BG,
        fg=MUTED
    ).pack(side="left", padx=spad(12))

    make_button(
        title_row,
        "BACK TO OVERVIEW",
        lambda: show_teacher_dashboard(full_name, teacher_username),
        GRAY
    ).pack(side="right")

    body = tk.Frame(content, bg=PAGE_BG)
    body.pack(
        fill="both",
        expand=True,
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    body.grid_columnconfigure(0, weight=1)
    body.grid_columnconfigure(1, weight=4)
    body.grid_rowconfigure(0, weight=1)

    subjects_panel = tk.LabelFrame(
        body,
        text="Assigned Subjects",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(8)
    )

    subjects_panel.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, spad(8))
    )

    subject_list = tk.Listbox(
        subjects_panel,
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        selectbackground=BLUE,
        selectforeground=ON_ACCENT,
        highlightthickness=0,
        bd=0,
        activestyle="none",
        exportselection=False
    )

    subject_list.pack(fill="both", expand=True)

    for subject in assigned_subjects:
        subject_list.insert("end", subject)

    if not assigned_subjects:
        tk.Label(
            subjects_panel,
            text=(
                "The administrator has not assigned you a subject yet."
            ),
            bg=SURFACE,
            fg=MUTED,
            font=sfont(9, "normal"),
            wraplength=sx(200),
            justify="left"
        ).pack(anchor="w", pady=(spad(6), 0))

    students_panel = tk.LabelFrame(
        body,
        text="Students in Subject",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(8),
        pady=spad(8)
    )

    students_panel.grid(
        row=0,
        column=1,
        sticky="nsew"
    )

    students_title = tk.Label(
        students_panel,
        text="Select a subject to see its students.",
        bg=SURFACE,
        fg=MUTED,
        font=sfont(9),
        anchor="w",
        justify="left"
    )

    students_title.pack(fill="x", pady=(0, spad(4)))

    student_columns = (
        "ID No.",
        "Student",
        "Username",
        "Overall",
        "Status"
    )

    student_widths = (110, 230, 170, 90, 90)

    students_table = ttk.Treeview(
        students_panel,
        columns=student_columns,
        show="headings",
        height=12
    )

    for column, width in zip(student_columns, student_widths):
        students_table.heading(column, text=column)
        students_table.column(column, width=sx(width), anchor="w")

    students_table.pack(fill="both", expand=True)

    def show_subject_students(event=None):
        selection = subject_list.curselection()

        if not selection:
            return

        subject = subject_list.get(selection[0])
        report = teacher_subject_report(teacher_username, subject)

        students_table.delete(*students_table.get_children())

        for row in report["rows"]:
            overall = row["overall"]

            students_table.insert(
                "",
                "end",
                values=(
                    row.get("student_id", "") or "—",
                    row.get("student_name", "") or row["student_username"],
                    row["student_username"],
                    (
                        format_overall_grade_display(overall)
                        if isinstance(overall, (int, float))
                        else "—"
                    ),
                    row["status"]
                )
            )

        count = len(report["rows"])

        if count:
            students_title.configure(
                text=f"{subject}: {count} student(s) with a grade record",
                fg=TEXT
            )
        else:
            students_title.configure(
                text=(
                    f"{subject}: no students have a grade record in "
                    "this subject yet."
                ),
                fg=MUTED
            )

    subject_list.bind("<<ListboxSelect>>", show_subject_students)

    if assigned_subjects:
        subject_list.selection_set(0)
        show_subject_students()

# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

def student_menu_items(student_username, full_name, section="overview"):
    return [
        (
            "ANNOUNCEMENTS",
            PURPLE,
            lambda: show_student_dashboard(
                student_username,
                full_name,
                "overview"
            )
        ),
        (
            "SUBJECT SUMMARY",
            BLUE,
            lambda: show_student_dashboard(
                student_username,
                full_name,
                "summary"
            )
        ),
        (
            "ASSESSMENT DETAILS",
            GREEN,
            lambda: show_student_dashboard(
                student_username,
                full_name,
                "details"
            )
        )
    ]


def show_student_dashboard(student_username, full_name, section="overview", selected_semester=None):
    global CURRENT_SCREEN
    CURRENT_SCREEN = lambda: show_student_dashboard(
        student_username,
        full_name,
        section,
        selected_semester
    )
    clear_screen()
    build_header(
        "STUDENT DASHBOARD",
        full_name,
        menu_title="STUDENT MENU",
        menu_items=student_menu_items(student_username, full_name, section)
    )

    content = tk.Frame(root, bg=PAGE_BG)
    content.place(
        x=0,
        y=HEADER_HEIGHT,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT - HEADER_HEIGHT
    )

    school_year = data_store.get("settings", {}).get("school_year", current_school_year())
    selected_semester = selected_semester or data_store.get("settings", {}).get("current_semester", SEMESTER_NAMES[0])
    performance = student_performance(student_username, selected_semester, school_year)
    subjects = performance["subjects"]

    title_row = tk.Frame(content, bg=PAGE_BG)
    title_row.pack(
        fill="x",
        padx=spad(22),
        pady=(spad(10), spad(4))
    )

    tk.Label(
        title_row,
        text="My Academic Performance",
        font=sfont(20),
        bg=PAGE_BG,
        fg=TEXT
    ).pack(side="left")

    tk.Label(
        title_row,
        text=(
            f"{full_name}  |  {student_username}  |  "
            f"ID No. {student_id_of(student_username) or '—'}"
        ),
        font=sfont(9, "normal"),
        bg=PAGE_BG,
        fg=MUTED
    ).pack(side="left", padx=spad(12))

    semester_row = tk.Frame(content, bg=PAGE_BG)
    semester_row.pack(fill="x", padx=spad(22), pady=(0, spad(8)))

    tk.Label(
        semester_row,
        text=f"Selected Semester: {selected_semester}  |  School Year: {school_year}",
        bg=PAGE_BG,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left")

    semester_box = ttk.Combobox(
        semester_row,
        values=SEMESTER_NAMES,
        state="readonly",
        width=20
    )
    semester_box.set(selected_semester)
    semester_box.pack(side="left", padx=spad(10))
    semester_box.bind(
        "<<ComboboxSelected>>",
        lambda event: show_student_dashboard(
            student_username,
            full_name,
            section,
            semester_box.get()
        )
    )

    make_button(
        semester_row,
        "REFRESH",
        lambda: show_student_dashboard(student_username, full_name, section, selected_semester),
        GRAY
    ).pack(side="right")

    general_average = performance["general_average"]

    best_subject = "—"

    graded = [
        item for item in subjects
        if isinstance(item["overall"], (int, float))
    ]

    if graded:
        best_subject = max(
            graded,
            key=lambda item: item["overall"]
        )["subject"]

    cards = tk.Frame(content, bg=PAGE_BG)
    cards.pack(fill="x", padx=spad(20), pady=(spad(0), spad(6)))

    for column in range(5):
        cards.grid_columnconfigure(
            column,
            weight=1,
            uniform="studentcards"
        )

    card_data = [
        (
            "General Average",
            f"{general_average:.2f}"
            if general_average is not None else "—",
            BLUE
        ),
        ("Subjects", performance["subjects_count"], PURPLE),
        ("Passed", performance["passed"], GREEN),
        ("Needs Support", performance["failed"], RED),
        ("Best Subject", best_subject, GRAY)
    ]

    for index, (label, value, color) in enumerate(card_data):
        make_stat_card(
            cards,
            label,
            value,
            0,
            index,
            color
        )

    summary_frame = tk.LabelFrame(
        content,
        text=f"Subject Summary - {selected_semester}",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(6),
        pady=spad(6)
    )

    summary_columns = (
        "Subject",
        "Teacher",
        "Prelim",
        "Midterm",
        "Semifinal",
        "Finals",
        "Overall",
        "Trend",
        "Class Avg",
        "Rank",
        "Status",
        "Remark"
    )

    summary_widths = (
        140, 140, 75, 80, 90, 70, 85, 80, 90, 60, 85, 110
    )

    summary_table = ttk.Treeview(
        summary_frame,
        columns=summary_columns,
        show="headings",
        height=6
    )

    for column, width in zip(summary_columns, summary_widths):
        summary_table.heading(column, text=column)
        summary_table.column(column, width=sx(width), anchor="center")

    summary_table.pack(fill="x")

    if not subjects:
        tk.Label(
            summary_frame,
            text="No grades available for this semester yet.",
            bg=SURFACE,
            fg=MUTED,
            font=sfont(10, "normal")
        ).pack(anchor="w", pady=spad(6))
    else:
        for item in subjects:
            values = [
                item["subject"],
                item["teacher_name"] or "—"
            ]

            for term in TERM_NAMES:
                value = item["terms"].get(term)

                if isinstance(value, (int, float)):
                    values.append(f"{value:.2f}")
                else:
                    values.append("—")

            overall = item["overall"]
            class_average = item["class_average"]

            values.append(
                format_overall_grade_display(overall)
                if isinstance(overall, (int, float))
                else "—"
            )

            completed = [
                item["terms"][term]
                for term in TERM_NAMES
                if isinstance(item["terms"].get(term), (int, float))
            ]

            if len(completed) >= 2:
                delta = completed[-1] - completed[-2]

                if delta > 0.004:
                    values.append(f"▲ {delta:.2f}")
                elif delta < -0.004:
                    values.append(f"▼ {abs(delta):.2f}")
                else:
                    values.append("= 0.00")
            else:
                values.append("—")

            values.append(
                f"{class_average:.2f}"
                if isinstance(class_average, (int, float)) else "—"
            )

            values.append(
                f"{item['rank']} of {item['class_size']}"
                if item["rank"] else "—"
            )

            values.append(item["status"])
            values.append(item["remark"])

            summary_table.insert("", "end", values=values)

    detail_frame = tk.LabelFrame(
        content,
        text="Assessment Details",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(10),
        pady=spad(8)
    )

    if section == "details":
        detail_frame.pack(
            fill="both",
            expand=True,
            padx=spad(20),
            pady=(spad(0), spad(6))
        )
    elif section == "summary":
        summary_frame.pack(
            fill="both",
            expand=True,
            padx=spad(20),
            pady=(spad(0), spad(6))
        )

    announcements_frame = tk.LabelFrame(
        content,
        text="Announcements",
        font=sfont(10),
        bg=SURFACE,
        fg=TEXT,
        padx=spad(10),
        pady=spad(8)
    )

    announcements_frame.pack(
        fill="both" if section == "overview" else "x",
        expand=section == "overview",
        padx=spad(20),
        pady=(spad(0), spad(12))
    )

    build_announcement_view(
        announcements_frame,
        "Student",
        height=5 if section != "overview" else 10,
        username=student_username
    )

    selector_row = tk.Frame(detail_frame, bg=SURFACE)
    selector_row.pack(fill="x", pady=(0, spad(6)))

    tk.Label(
        selector_row,
        text="Choose Subject:",
        bg=SURFACE,
        fg=TEXT,
        font=sfont(10)
    ).pack(side="left", padx=(0, spad(8)))

    subject_box = ttk.Combobox(
        selector_row,
        values=[item["subject"] for item in subjects],
        state="readonly",
        width=32
    )

    subject_box.pack(side="left")

    breakdown_host = tk.Frame(detail_frame, bg=SURFACE)
    breakdown_host.pack(fill="both", expand=True)

    def render_detail(event=None):
        for widget in breakdown_host.winfo_children():
            widget.destroy()

        subject = subject_box.get().strip()

        record = None

        if subject:
            record = find_grade_record(student_username, subject)

        if record is None:
            tk.Label(
                breakdown_host,
                text="No grades are available for this subject yet.",
                bg=SURFACE,
                fg=MUTED
            ).pack(anchor="w")
            return

        terms = record.get("terms", {})

        columns = ("Assessment",) + tuple(TERM_NAMES) + ("Average",)
        widths = (170, 110, 110, 120, 100, 100)

        table = ttk.Treeview(
            breakdown_host,
            columns=columns,
            show="headings",
            height=len(ASSESSMENT_ITEMS) + 2
        )

        for column, width in zip(columns, widths):
            table.heading(column, text=column)
            table.column(column, width=sx(width), anchor="center")

        table.pack(fill="x")

        for key, index, label in ASSESSMENT_ITEMS:
            values = [label]
            collected = []

            for term in TERM_NAMES:
                block = terms.get(term)

                scores = None

                if isinstance(block, dict):
                    scores = block.get(key)

                value = None

                if isinstance(scores, (list, tuple)):
                    if index < len(scores):
                        value = scores[index]
                elif isinstance(scores, (int, float)):
                    value = scores

                if isinstance(value, (int, float)):
                    values.append(f"{float(value):.2f}")
                    collected.append(float(value))
                else:
                    values.append("—")

            if collected:
                values.append(
                    f"{sum(collected) / len(collected):.2f}"
                )
            else:
                values.append("—")

            table.insert("", "end", values=values)

        term_values = ["Term Grade"]

        for term in TERM_NAMES:
            block = terms.get(term)

            value = None

            if isinstance(block, dict):
                value = block.get("term_grade")

            if isinstance(value, (int, float)):
                term_values.append(f"{float(value):.2f}")
            else:
                term_values.append("—")

        overall = overall_grade_for_terms(terms)

        term_values.append(
            format_overall_grade_display(overall)
            if isinstance(overall, (int, float))
            else "—"
        )

        table.insert("", "end", values=term_values)

        summary_row = tk.Frame(breakdown_host, bg=SURFACE)
        summary_row.pack(fill="x", pady=(spad(8), 0))

        for key in ASSESSMENT_NAMES:
            collected = []

            for term in TERM_NAMES:
                block = terms.get(term)

                if not isinstance(block, dict):
                    continue

                average = assessment_type_average(block, key)

                if isinstance(average, (int, float)):
                    collected.append(float(average))

            cell = tk.Frame(summary_row, bg=SURFACE)
            cell.pack(side="left", padx=spad(14))

            tk.Label(
                cell,
                text=ASSESSMENT_LABELS[key],
                bg=SURFACE,
                fg=MUTED,
                font=sfont(8)
            ).pack(anchor="w")

            tk.Label(
                cell,
                text=(
                    f"{sum(collected) / len(collected):.2f}"
                    if collected else "—"
                ),
                bg=SURFACE,
                fg=TEXT,
                font=sfont(12)
            ).pack(anchor="w")

        info = student_performance(student_username)

        current = next(
            (
                item for item in info["subjects"]
                if item["subject"] == subject
            ),
            None
        )

        if current is not None:
            note = tk.Label(
                breakdown_host,
                text=(
                    f"Overall grade: "
                    f"{format_overall_grade_display(current['overall'])}   |   "
                    f"Status: {current['status']}   |   "
                    f"Remark: {current['remark']}   |   "
                    f"Teacher: {current['teacher_name'] or '—'}   |   "
                    f"Terms completed: {current['terms_completed']} of 4   |   "
                    f"Class average: "
                    + (
                        f"{current['class_average']:.2f}"
                        if isinstance(
                            current["class_average"],
                            (int, float)
                        ) else "—"
                    )
                    + (
                        f"   |   Rank: {current['rank']} "
                        f"of {current['class_size']}"
                        if current["rank"] else ""
                    )
                ),
                bg=SURFACE,
                fg=TEXT,
                font=sfont(10)
            )

            note.pack(anchor="w", pady=(spad(8), 0))

        planner = tk.Frame(breakdown_host, bg=SURFACE)
        planner.pack(fill="x", pady=(spad(10), 0))

        planner_row = tk.Frame(planner, bg=SURFACE)
        planner_row.pack(fill="x")

        tk.Label(
            planner_row,
            text="Target overall grade:",
            bg=SURFACE,
            fg=TEXT,
            font=sfont(10)
        ).pack(side="left")

        target_var = tk.StringVar(value="90")

        target_entry = make_entry(
            planner_row,
            width=6,
            textvariable=target_var
        )
        target_entry.pack(side="left", padx=spad(8))

        tk.Label(
            planner_row,
            text="Enter a target from 0 to 100 to see what you need.",
            bg=SURFACE,
            fg=MUTED,
            font=sfont(8, "normal")
        ).pack(side="left", padx=(spad(4), 0))

        target_result = tk.Label(
            planner,
            text="",
            bg=SURFACE,
            fg=MUTED,
            font=sfont(9, "normal"),
            anchor="w",
            justify="left",
            wraplength=sx(680)
        )

        target_result.pack(fill="x", pady=(spad(4), 0))

        def update_target(*args):
            raw = target_var.get().strip().replace(",", ".")

            try:
                target = float(raw)
            except ValueError:
                target_result.configure(
                    text="Enter a number between 0 and 100.",
                    fg=MUTED
                )
                return

            if target < 0 or target > 100:
                target_result.configure(
                    text="Target must be between 0 and 100.",
                    fg=MUTED
                )
                return

            completed = completed_term_grades(terms)

            done = {name for name, _ in completed}

            remaining = [
                name for name in TERM_NAMES
                if name not in done
            ]

            if not remaining:
                target_result.configure(
                    text=(
                        "All terms are recorded, so the overall grade is "
                        f"fixed at {overall:.2f}."
                    ),
                    fg=MUTED
                )
                return

            total = sum(value for _, value in completed)

            needed = (
                target * len(TERM_NAMES) - total
            ) / len(remaining)

            if needed <= 0:
                target_result.configure(
                    text=(
                        "Target already secured - any score on the "
                        f"remaining {len(remaining)} term(s) keeps you at "
                        f"or above {target:.2f}."
                    ),
                    fg=GREEN
                )

            elif needed > 100:
                target_result.configure(
                    text=(
                        f"You would need {needed:.2f} on average across "
                        f"the remaining {len(remaining)} term(s) to finish "
                        f"at {target:.2f} - above the 100.00 maximum."
                    ),
                    fg=RED
                )

            else:
                target_result.configure(
                    text=(
                        f"You need {needed:.2f} on average across the "
                        f"remaining {len(remaining)} term(s) "
                        f"({', '.join(remaining)}) to finish at "
                        f"{target:.2f}."
                    ),
                    fg=TEXT
                )

        target_entry.target_var = target_var

        target_var.trace_add("write", update_target)
        update_target()

    subject_box.bind("<<ComboboxSelected>>", render_detail)

    if subjects:
        subject_box.set(subjects[0]["subject"])
        render_detail()

    else:
        tk.Label(
            breakdown_host,
            text="No grades have been entered for your account yet.",
            bg=SURFACE,
            fg=MUTED
        ).pack(anchor="w")

    tk.Label(
        detail_frame,
        text=(
            "Each term uses written works (activities and quizzes) at 30%, "
            "the exam at 30% and the performance task at 40%. Every "
            "completed term has an equal weight in the overall grade."
        ),
        bg=SURFACE,
        fg=MUTED,
        font=sfont(8, "normal")
    ).pack(anchor="w")

# --------------------------------------------------
# CLOSE APPLICATION
# --------------------------------------------------

def close_application():
    stop_background_animation()

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

root.bind(
    "<Escape>",
    lambda event: close_application()
)

saved_theme = data_store.get("settings", {}).get("theme", "light")

if saved_theme in THEME_PALETTES:
    palette = THEME_PALETTES[saved_theme]

    THEME = saved_theme
    HEADER_BG = palette["header_bg"]
    PAGE_BG = palette["page_bg"]
    SURFACE = palette["surface"]
    SURFACE_ALT = palette["surface_alt"]
    SURFACE_ALT_HOVER = palette["surface_alt_hover"]
    TEXT = palette["text"]
    MUTED = palette["muted"]
    BORDER = palette["border"]
    ON_ACCENT = palette["on_accent"]
    GLASS_TINT = palette["glass"]
    CANVAS_SHADOW = palette["shadow"]

    root.configure(bg=PAGE_BG)

refresh_background()

configure_ttk_styles()


def start():
    """Start the interface."""

    show_login_selection()

    root.mainloop()


if __name__ == "__main__":
    start()