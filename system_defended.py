
import tkinter as tk

# =====================================================
# SMCII SYSTEM DEFENDED — FULL-SCREEN PRESENTATION
# ESC = Exit fullscreen | F11 = Toggle fullscreen
# =====================================================

BG = "#07111f"
CARD = "#101f34"
BORDER = "#29415e"
CYAN = "#2fe6d0"
CYAN_DARK = "#103b43"
WHITE = "#f5f8ff"
MUTED = "#a9bdd9"
GREEN = "#36e58c"
GREEN_BG = "#10392f"


class SystemDefendedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Defended")
        self.root.configure(bg=BG)
        self.root.minsize(700, 500)

        self.fullscreen = True
        self.root.attributes("-fullscreen", True)

        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Configure>", self.on_resize)

        self.canvas = tk.Canvas(
            root,
            bg=BG,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.redraw_job = None
        self.draw_screen()

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def on_resize(self, event=None):
        if self.redraw_job is not None:
            self.root.after_cancel(self.redraw_job)

        self.redraw_job = self.root.after(
            80, self.draw_screen
        )

    def rounded_rectangle(
        self, x1, y1, x2, y2, radius, **kwargs
    ):
        radius = max(
            1,
            min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        )

        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]

        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            **kwargs
        )

    def draw_screen(self):
        self.redraw_job = None
        self.canvas.delete("all")

        width = max(self.root.winfo_width(), 700)
        height = max(self.root.winfo_height(), 500)

        scale = max(
            0.65,
            min(width / 1440, height / 900)
        )

        def fs(size, minimum=10):
            return max(minimum, int(size * scale))

        # Decorative background circles
        self.canvas.create_oval(
            width - 280 * scale,
            -180 * scale,
            width + 120 * scale,
            230 * scale,
            fill="#0e2944",
            outline=""
        )

        self.canvas.create_oval(
            -170 * scale,
            height - 240 * scale,
            220 * scale,
            height + 160 * scale,
            fill="#0b2539",
            outline=""
        )

        self.canvas.create_oval(
            width - 170 * scale,
            height - 150 * scale,
            width + 70 * scale,
            height + 90 * scale,
            fill="#0b2539",
            outline=""
        )

        # Header
        self.canvas.create_text(
            width / 2,
            55 * scale,
            text="SMCII  •  PROJECT MILESTONE",
            fill=CYAN,
            font=("Segoe UI", fs(18), "bold")
        )

        # Responsive center card
        card_width = min(width * 0.82, 1120 * scale)
        card_height = min(height * 0.65, 590 * scale)

        card_width = max(card_width, 560 * scale)
        card_height = max(card_height, 370 * scale)

        cx = width / 2
        cy = height / 2

        x1 = cx - card_width / 2
        y1 = cy - card_height / 2
        x2 = cx + card_width / 2
        y2 = cy + card_height / 2

        self.rounded_rectangle(
            x1, y1, x2, y2,
            18 * scale,
            fill=CARD,
            outline=BORDER,
            width=max(1, int(2 * scale))
        )

        # Checkmark icon
        icon_y = y1 + card_height * 0.20
        icon_radius = 44 * scale

        self.canvas.create_oval(
            cx - icon_radius,
            icon_y - icon_radius,
            cx + icon_radius,
            icon_y + icon_radius,
            fill=CYAN_DARK,
            outline=CYAN,
            width=max(2, int(2 * scale))
        )

        self.canvas.create_line(
            cx - 19 * scale,
            icon_y + 1 * scale,
            cx - 5 * scale,
            icon_y + 16 * scale,
            cx + 23 * scale,
            icon_y - 16 * scale,
            fill=CYAN,
            width=max(4, int(6 * scale)),
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )

        # Main heading
        title_y = y1 + card_height * 0.43
        title_size = min(
            fs(66, 36),
            max(36, int(card_width / 12))
        )

        self.canvas.create_text(
            cx,
            title_y,
            text="SYSTEM DEFENDED",
            fill=WHITE,
            font=("Segoe UI", title_size, "bold")
        )

        # Turquoise underline
        line_width = min(
            300 * scale,
            card_width * 0.48
        )

        line_y = title_y + title_size * 0.75

        self.canvas.create_line(
            cx - line_width / 2,
            line_y,
            cx + line_width / 2,
            line_y,
            fill=CYAN,
            width=max(3, int(4 * scale)),
            capstyle=tk.ROUND
        )

        # Subtitle
        self.canvas.create_text(
            cx,
            line_y + 48 * scale,
            text="The hard work paid off.",
            fill=MUTED,
            font=("Segoe UI", fs(27, 18))
        )

        self.canvas.create_text(
            cx,
            line_y + 88 * scale,
            text="SMCII Automated Grading System",
            fill=WHITE,
            font=("Segoe UI", fs(23, 16), "bold")
        )

        # Achievement badge
        pill_width = 270 * scale
        pill_height = 43 * scale
        pill_y = line_y + 145 * scale

        self.rounded_rectangle(
            cx - pill_width / 2,
            pill_y - pill_height / 2,
            cx + pill_width / 2,
            pill_y + pill_height / 2,
            9 * scale,
            fill=GREEN_BG,
            outline="#176b53",
            width=1
        )

        dot_radius = 5 * scale
        dot_x = cx - 87 * scale

        self.canvas.create_oval(
            dot_x - dot_radius,
            pill_y - dot_radius,
            dot_x + dot_radius,
            pill_y + dot_radius,
            fill=GREEN,
            outline=""
        )

        self.canvas.create_text(
            cx + 10 * scale,
            pill_y,
            text="MILESTONE ACHIEVED",
            fill=GREEN,
            font=("Segoe UI", fs(14, 11), "bold")
        )

        # Footer
        self.canvas.create_text(
            width / 2,
            height - 30 * scale,
            text=(
                "Built with dedication  •  "
                "Press Esc to exit fullscreen  •  "
                "F11 to toggle"
            ),
            fill="#7896bd",
            font=("Segoe UI", fs(13, 10))
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemDefendedApp(root)
    root.mainloop()
