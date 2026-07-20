import tkinter as tk

from src.Calpkg.calculator import add, subtract
from src.Calpkg.gamepkg.game_center import GameApp
from src.Calpkg.gamepkg.Battledemo import BattleDemo

# ================= Theme (ให้เข้าชุดกับ Game Center) =================
BG_COLOR = "#0f172a"
BOARD_COLOR = "#1e293b"
TEXT_COLOR = "#f1f5f9"
MUTED_COLOR = "#94a3b8"
ACCENT_COLOR = "#8b5cf6"
CALC_COLOR = "#38bdf8"
GAME_COLOR = "#f472b6"
BATTLE_COLOR = "#f0c860"
EXIT_COLOR = "#7f1d1d"


class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมของฉัน")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        self.show_main_menu()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ================= หน้าเมนูหลัก =================
    def show_main_menu(self):
        self.clear_container()

        tk.Label(
            self.container, text="โปรแกรมของฉัน", font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR
        ).pack(pady=(40, 4))

        tk.Label(
            self.container, text="เลือกโปรแกรมที่ต้องการใช้งาน", font=("Segoe UI", 11),
            bg=BG_COLOR, fg=MUTED_COLOR
        ).pack(pady=(0, 30))

        card_frame = tk.Frame(self.container, bg=BG_COLOR)
        card_frame.pack(padx=30)

        self.make_menu_card(
            card_frame, "🧮", "เครื่องคิดเลข", "บวก และ ลบ ตัวเลข",
            CALC_COLOR, self.show_calculator, 0
        )
        self.make_menu_card(
            card_frame, "🎮", "เกม", "OX, Snake",
            GAME_COLOR, self.show_games, 1
        )
        self.make_menu_card(
            card_frame, "⚔", "Battle Demo", "ต่อสู้ CTB สไตล์ JRPG",
            BATTLE_COLOR, self.show_battle_demo, 2
        )

        tk.Frame(self.container, bg=BG_COLOR, height=10).pack()

        tk.Button(
            self.container, text="✖ ออกจากโปรแกรม", font=("Segoe UI", 10, "bold"),
            bg=EXIT_COLOR, fg="white", relief="flat", padx=16, pady=8,
            activebackground="#991b1b", command=self.root.destroy
        ).pack(pady=(10, 30))

    def make_menu_card(self, parent, icon, title, desc, color, command, col):
        card = tk.Frame(parent, bg=BOARD_COLOR, padx=26, pady=22, cursor="hand2")
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 30), bg=BOARD_COLOR, fg=color)
        icon_label.pack()

        title_label = tk.Label(card, text=title, font=("Segoe UI", 16, "bold"), bg=BOARD_COLOR, fg=TEXT_COLOR)
        title_label.pack(pady=(8, 0))

        desc_label = tk.Label(card, text=desc, font=("Segoe UI", 9), bg=BOARD_COLOR, fg=MUTED_COLOR)
        desc_label.pack(pady=(2, 12))

        play_btn = tk.Button(
            card, text="เปิด ▶", font=("Segoe UI", 10, "bold"),
            bg=color, fg="black" if color in (GAME_COLOR, BATTLE_COLOR) else "white",
            relief="flat", padx=18, pady=6,
            command=command
        )
        play_btn.pack()

        for widget in (card, icon_label, title_label, desc_label):
            widget.bind("<Button-1>", lambda e: command())

    # ================= เครื่องคิดเลข (GUI) =================
    def show_calculator(self):
        self.clear_container()

        tk.Label(
            self.container, text="🧮 เครื่องคิดเลข", font=("Segoe UI", 20, "bold"),
            bg=BG_COLOR, fg=CALC_COLOR
        ).pack(pady=(30, 4))

        tk.Label(
            self.container, text="กรอกตัวเลข 2 จำนวน แล้วกดบวก หรือ ลบ", font=("Segoe UI", 10),
            bg=BG_COLOR, fg=MUTED_COLOR
        ).pack(pady=(0, 20))

        form = tk.Frame(self.container, bg=BOARD_COLOR, padx=24, pady=20)
        form.pack(padx=30)

        tk.Label(form, text="ตัวเลขที่ 1", font=("Segoe UI", 10), bg=BOARD_COLOR, fg=MUTED_COLOR).grid(row=0, column=0, sticky="w")
        self.entry_a = tk.Entry(form, font=("Segoe UI", 14), width=14, justify="center")
        self.entry_a.grid(row=1, column=0, padx=(0, 12), pady=(2, 14))
        self.entry_a.insert(0, "0")

        tk.Label(form, text="ตัวเลขที่ 2", font=("Segoe UI", 10), bg=BOARD_COLOR, fg=MUTED_COLOR).grid(row=0, column=1, sticky="w")
        self.entry_b = tk.Entry(form, font=("Segoe UI", 14), width=14, justify="center")
        self.entry_b.grid(row=1, column=1, pady=(2, 14))
        self.entry_b.insert(0, "0")

        btn_frame = tk.Frame(form, bg=BOARD_COLOR)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 14))

        tk.Button(
            btn_frame, text="➕ บวก", font=("Segoe UI", 11, "bold"),
            bg=ACCENT_COLOR, fg="white", relief="flat", padx=18, pady=8,
            activebackground="#7c3aed", command=lambda: self.calculate(add)
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            btn_frame, text="➖ ลบ", font=("Segoe UI", 11, "bold"),
            bg=ACCENT_COLOR, fg="white", relief="flat", padx=18, pady=8,
            activebackground="#7c3aed", command=lambda: self.calculate(subtract)
        ).grid(row=0, column=1, padx=6)

        self.result_label = tk.Label(
            form, text="ผลลัพธ์: -", font=("Segoe UI", 14, "bold"),
            bg=BOARD_COLOR, fg=TEXT_COLOR
        )
        self.result_label.grid(row=3, column=0, columnspan=2)

        self.make_bottom_bar(self.show_main_menu)

    def calculate(self, operation):
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            result = operation(a, b)
            symbol = "+" if operation is add else "-"
            self.result_label.configure(text=f"ผลลัพธ์: {a} {symbol} {b} = {result}", fg=CALC_COLOR)
        except ValueError:
            self.result_label.configure(text="⚠ กรุณาใส่ตัวเลขให้ถูกต้อง", fg="#ef4444")

    # ================= เกม =================
    def show_games(self):
        self.clear_container()
        GameApp(self.root, home_callback=self.show_main_menu, container=self.container)

    # ================= Battle Demo (เกมแยกอิสระ) =================
    def show_battle_demo(self):
        self.clear_container()
        self.root.title("⚔ Battle Demo - CTB Turn Order System")
        BattleDemo(self.root, parent=self.container, back_callback=self.show_main_menu)

    # ================= แถบล่าง (กลับเมนูหลัก + ออก) ใช้กับหน้าเครื่องคิดเลข =================
    def make_bottom_bar(self, back_command):
        bottom_frame = tk.Frame(self.container, bg=BG_COLOR)
        bottom_frame.pack(pady=(10, 24))

        tk.Button(
            bottom_frame, text="🏠 เมนูหลัก", font=("Segoe UI", 10, "bold"),
            bg=BOARD_COLOR, fg=TEXT_COLOR, relief="flat", padx=14, pady=6,
            activebackground="#334155", command=back_command
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            bottom_frame, text="✖ ออกจากโปรแกรม", font=("Segoe UI", 10, "bold"),
            bg=EXIT_COLOR, fg="white", relief="flat", padx=14, pady=6,
            activebackground="#991b1b", command=self.root.destroy
        ).grid(row=0, column=1, padx=6)


def main():
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()