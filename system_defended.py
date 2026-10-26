
import tkinter as tk

# =========================
# COLORS
# =========================
BG = "#07111F"
CARD = "#101F34"
BORDER = "#29415D"
CYAN = "#20E6D0"
WHITE = "#F8FAFC"
MUTED = "#A8BEDA"
GREEN = "#00E58A"

# =========================
# FULL-SCREEN WINDOW
# =========================
root = tk.Tk()
root.title("System Defended")
root.configure(bg=BG)
root.attributes("-fullscreen", True)

def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)
    root.state("zoomed")

root.bind("<Escape>", exit_fullscreen)
root.bind(
    "<F11>",
    lambda event: root.attributes(
        "-fullscreen", not root.attributes("-fullscreen")
    )
)

# =========================
# BACKGROUND
# =========================
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

def draw_background(event=None):
    canvas.delete("decoration")
    w = root.winfo_width()
    h = root.winfo_height()

    canvas.create_oval(
        w - 300, -200, w + 120, 220,
        fill="#102943", outline="", tags="decoration"
    )
    canvas.create_oval(
        -220, h - 220, 220, h + 220,
        fill="#0B2839", outline="", tags="decoration"
    )
    canvas.create_oval(
        w - 220, h - 120, w + 180, h + 280,
        fill="#0B2839", outline="", tags="decoration"
    )

canvas.bind("<Configure>", draw_background)

# =========================
# CENTER CONTENT
# =========================
content = tk.Frame(root, bg=BG)
content.place(relx=0.5, rely=0.48, anchor="center")

# Larger project heading
tk.Label(
    content,
    text="SMCII   •   PROJECT MILESTONE",
    font=("Segoe UI", 22, "bold"),
    fg=CYAN,
    bg=BG
).pack(pady=(0, 40))

# Larger main card
card = tk.Frame(
    content,
    bg=CARD,
    highlightbackground=BORDER,
    highlightthickness=2,
    padx=85,
    pady=55
)
card.pack()

# Success icon
icon_canvas = tk.Canvas(
    card,
    width=145,
    height=145,
    bg=CARD,
    highlightthickness=0
)
icon_canvas.pack(pady=(0, 25))

icon_canvas.create_oval(
    8, 8, 137, 137,
    outline=CYAN,
    width=3,
    fill="#103A3C"
)

icon_canvas.create_line(
    43, 75, 62, 96, 103, 48,
    fill=CYAN,
    width=7,
    capstyle=tk.ROUND,
    joinstyle=tk.ROUND
)

# Much larger title
tk.Label(
    card,
    text="SYSTEM DEFENDED",
    font=("Segoe UI", 48, "bold"),
    fg=WHITE,
    bg=CARD
).pack(pady=(0, 18))

# Cyan divider
tk.Frame(
    card,
    bg=CYAN,
    height=5,
    width=440
).pack(pady=(0, 35))

# Larger subtitle
tk.Label(
    card,
    text="The hard work paid off.",
    font=("Segoe UI", 28),
    fg=MUTED,
    bg=CARD
).pack(pady=(0, 25))

# Larger project name
tk.Label(
    card,
    text="SMCII Automated Grading System",
    font=("Segoe UI", 24, "bold"),
    fg=WHITE,
    bg=CARD
).pack(pady=(0, 35))

# Larger milestone badge
badge = tk.Label(
    card,
    text="✓   MILESTONE ACHIEVED",
    font=("Segoe UI", 22, "bold"),
    fg=GREEN,
    bg="#103A32",
    padx=35,
    pady=20
)
badge.pack()


root.mainloop()
