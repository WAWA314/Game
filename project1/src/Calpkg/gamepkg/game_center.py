import tkinter as tk
import random

# ================= Shared Theme =================
BG_COLOR = "#0f172a"
BOARD_COLOR = "#1e293b"
CELL_COLOR = "#1e1b4b"
CELL_HOVER = "#312e81"
CANVAS_BG = "#1e1b4b"
X_COLOR = "#38bdf8"
O_COLOR = "#f472b6"
WIN_COLOR = "#166534"
TEXT_COLOR = "#f1f5f9"
MUTED_COLOR = "#94a3b8"
ACCENT_COLOR = "#8b5cf6"
GRID_LINE_COLOR = "#27245a"
SNAKE_HEAD_COLOR = "#38bdf8"
SNAKE_BODY_COLOR = "#0ea5e9"
FOOD_COLOR = "#f472b6"

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

CELL_SIZE = 24
GRID_W = 20
GRID_H = 20
GAME_WIDTH = CELL_SIZE * GRID_W
GAME_HEIGHT = CELL_SIZE * GRID_H

SPEED_LEVELS = {"ช้า": 160, "ปกติ": 110, "เร็ว": 70}


# ================= App Shell =================
class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Game Center")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        self.current_frame = None
        self.show_menu()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.root.unbind("<Key>")

    def show_menu(self):
        self.clear_container()

        title = tk.Label(
            self.container, text="MINI GAME CENTER", font=("Segoe UI", 24, "bold"),
            bg=BG_COLOR, fg=ACCENT_COLOR
        )
        title.pack(pady=(40, 4))

        subtitle = tk.Label(
            self.container, text="เลือกเกมที่อยากเล่น", font=("Segoe UI", 11),
            bg=BG_COLOR, fg=MUTED_COLOR
        )
        subtitle.pack(pady=(0, 30))

        card_frame = tk.Frame(self.container, bg=BG_COLOR)
        card_frame.pack(padx=30)

        self.make_menu_card(
            card_frame, "❌⭕", "OX GAME", "Tic-Tac-Toe เกม X O",
            X_COLOR, lambda: self.show_ox_game(), 0
        )
        self.make_menu_card(
            card_frame, "🐍", "SNAKE GAME", "งูกินหาง คลาสสิก",
            SNAKE_HEAD_COLOR, lambda: self.show_snake_game(), 1
        )

        footer = tk.Label(
            self.container, text="เลือกเกม แล้วกด 'กลับเมนู' เพื่อสลับได้ตลอดเวลา",
            font=("Segoe UI", 9), bg=BG_COLOR, fg=MUTED_COLOR
        )
        footer.pack(pady=(30, 20))

    def make_menu_card(self, parent, icon, title, desc, color, command, row):
        card = tk.Frame(parent, bg=BOARD_COLOR, padx=24, pady=20, cursor="hand2")
        card.grid(row=row, column=0, pady=8, sticky="ew")
        parent.grid_columnconfigure(0, weight=1)

        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 26), bg=BOARD_COLOR, fg=color)
        icon_label.pack()

        title_label = tk.Label(card, text=title, font=("Segoe UI", 15, "bold"), bg=BOARD_COLOR, fg=TEXT_COLOR)
        title_label.pack(pady=(6, 0))

        desc_label = tk.Label(card, text=desc, font=("Segoe UI", 9), bg=BOARD_COLOR, fg=MUTED_COLOR)
        desc_label.pack(pady=(2, 10))

        play_btn = tk.Button(
            card, text="เล่นเลย ▶", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_COLOR, fg="white", relief="flat", padx=16, pady=6,
            activebackground="#7c3aed", command=command
        )
        play_btn.pack()

        for widget in (card, icon_label, title_label, desc_label):
            widget.bind("<Button-1>", lambda e: command())

    def show_ox_game(self):
        self.clear_container()
        OXGame(self.container, back_callback=self.show_menu)

    def show_snake_game(self):
        self.clear_container()
        SnakeGame(self.container, root_ref=self.root, back_callback=self.show_menu)


def make_back_button(parent, command):
    back_btn = tk.Button(
        parent, text="◀ กลับเมนู", font=("Segoe UI", 9, "bold"),
        bg=BOARD_COLOR, fg=TEXT_COLOR, relief="flat", padx=10, pady=4,
        activebackground="#334155", command=command
    )
    back_btn.pack(pady=(8, 0))


# ================= OX Game =================
class OXGame:
    def __init__(self, parent, back_callback):
        self.parent = parent
        self.back_callback = back_callback

        self.board = [None] * 9
        self.current_player = "X"
        self.game_active = True
        self.mode = tk.StringVar(value="pvp")
        self.scores = {"X": 0, "O": 0, "DRAW": 0}
        self.buttons = []

        self.build_ui()

    def build_ui(self):
        title = tk.Label(self.parent, text="OX GAME", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        title.pack(pady=(16, 0))

        subtitle = tk.Label(self.parent, text="Tic-Tac-Toe เกม X O", font=("Segoe UI", 10), bg=BG_COLOR, fg=MUTED_COLOR)
        subtitle.pack(pady=(0, 10))

        mode_frame = tk.Frame(self.parent, bg=BG_COLOR)
        mode_frame.pack(pady=(0, 10))

        tk.Radiobutton(
            mode_frame, text="เล่น 2 คน", variable=self.mode, value="pvp",
            command=self.restart_game, font=("Segoe UI", 10, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=CELL_COLOR,
            activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
            indicatoron=False, width=12, pady=6, relief="flat", highlightthickness=0
        ).grid(row=0, column=0, padx=4)

        tk.Radiobutton(
            mode_frame, text="เล่นกับ AI", variable=self.mode, value="ai",
            command=self.restart_game, font=("Segoe UI", 10, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=CELL_COLOR,
            activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
            indicatoron=False, width=12, pady=6, relief="flat", highlightthickness=0
        ).grid(row=0, column=1, padx=4)

        self.status_label = tk.Label(
            self.parent, text="ตาของ X", font=("Segoe UI", 13, "bold"),
            bg=BOARD_COLOR, fg=X_COLOR, width=26, pady=10
        )
        self.status_label.pack(pady=(0, 12))

        board_frame = tk.Frame(self.parent, bg=BOARD_COLOR, padx=10, pady=10)
        board_frame.pack()

        for i in range(9):
            btn = tk.Button(
                board_frame, text="", font=("Segoe UI", 28, "bold"),
                width=4, height=2, bg=CELL_COLOR, fg=TEXT_COLOR,
                activebackground=CELL_HOVER, relief="flat",
                command=lambda idx=i: self.handle_click(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: self.on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_hover(b, False))
            self.buttons.append(btn)

        score_frame = tk.Frame(self.parent, bg=BG_COLOR)
        score_frame.pack(pady=14, fill="x", padx=20)

        self.score_x_label = self.make_score_card(score_frame, "X ชนะ", X_COLOR, 0)
        self.score_draw_label = self.make_score_card(score_frame, "เสมอ", "#facc15", 1)
        self.score_o_label = self.make_score_card(score_frame, "O ชนะ", O_COLOR, 2)

        action_frame = tk.Frame(self.parent, bg=BG_COLOR)
        action_frame.pack(pady=(0, 8))

        tk.Button(
            action_frame, text="🔄 เริ่มใหม่", font=("Segoe UI", 11, "bold"),
            bg=ACCENT_COLOR, fg="white", relief="flat", padx=16, pady=8,
            activebackground="#7c3aed", command=self.restart_game
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            action_frame, text="🗑️ ล้างคะแนน", font=("Segoe UI", 11, "bold"),
            bg=CELL_COLOR, fg=TEXT_COLOR, relief="flat", padx=16, pady=8,
            activebackground=CELL_HOVER, command=self.reset_scores
        ).grid(row=0, column=1, padx=6)

        make_back_button(self.parent, self.back_callback)
        tk.Frame(self.parent, bg=BG_COLOR, height=16).pack()

    def make_score_card(self, parent, label, color, col):
        frame = tk.Frame(parent, bg=CELL_COLOR, padx=10, pady=8)
        frame.grid(row=0, column=col, padx=4, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(frame, text=label, font=("Segoe UI", 9), bg=CELL_COLOR, fg=MUTED_COLOR).pack()
        value_label = tk.Label(frame, text="0", font=("Segoe UI", 16, "bold"), bg=CELL_COLOR, fg=color)
        value_label.pack()
        return value_label

    def on_hover(self, btn, entering):
        if btn["text"] == "" and self.game_active:
            btn.configure(bg=CELL_HOVER if entering else CELL_COLOR)

    def handle_click(self, index):
        if not self.game_active or self.board[index] is not None:
            return
        if self.mode.get() == "ai" and self.current_player == "O":
            return

        self.make_move(index, self.current_player)

        if self.game_active and self.mode.get() == "ai" and self.current_player == "O":
            self.set_board_enabled(False)
            self.parent.after(400, self.ai_move)

    def make_move(self, index, player):
        self.board[index] = player
        color = X_COLOR if player == "X" else O_COLOR
        self.buttons[index].configure(text=player, fg=color, bg=CELL_COLOR)

        winner, line = self.check_winner()
        if winner:
            self.end_game(winner, line)
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status()

    def ai_move(self):
        if not self.game_active:
            return
        idx = self.get_best_move()
        self.make_move(idx, "O")
        self.set_board_enabled(True)

    def set_board_enabled(self, enabled):
        for btn in self.buttons:
            if btn["text"] == "":
                btn.configure(state="normal" if enabled else "disabled")

    def update_status(self):
        color = X_COLOR if self.current_player == "X" else O_COLOR
        self.status_label.configure(text=f"ตาของ {self.current_player}", fg=color)

    def check_winner(self):
        for a, b, c in WIN_LINES:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a], (a, b, c)
        if all(self.board):
            return "DRAW", None
        return None, None

    def end_game(self, winner, line):
        self.game_active = False
        for btn in self.buttons:
            btn.configure(state="disabled")

        if winner == "DRAW":
            self.status_label.configure(text="🤝 เสมอกัน!", fg="#facc15")
            self.scores["DRAW"] += 1
            self.score_draw_label.configure(text=str(self.scores["DRAW"]))
        else:
            for i in line:
                self.buttons[i].configure(bg=WIN_COLOR)
            label = "AI" if (self.mode.get() == "ai" and winner == "O") else winner
            color = X_COLOR if winner == "X" else O_COLOR
            self.status_label.configure(text=f"🎉 {label} ชนะ!", fg=color)
            self.scores[winner] += 1
            target = self.score_x_label if winner == "X" else self.score_o_label
            target.configure(text=str(self.scores[winner]))

    def restart_game(self):
        self.board = [None] * 9
        self.current_player = "X"
        self.game_active = True
        for btn in self.buttons:
            btn.configure(text="", bg=CELL_COLOR, state="normal")
        self.update_status()

    def reset_scores(self):
        self.scores = {"X": 0, "O": 0, "DRAW": 0}
        self.score_x_label.configure(text="0")
        self.score_o_label.configure(text="0")
        self.score_draw_label.configure(text="0")
        self.restart_game()

    def get_best_move(self):
        best_score = -999
        best_moves = []
        for i in range(9):
            if self.board[i] is None:
                self.board[i] = "O"
                score = self.minimax(self.board, 0, False)
                self.board[i] = None
                if score > best_score:
                    best_score = score
                    best_moves = [i]
                elif score == best_score:
                    best_moves.append(i)
        return random.choice(best_moves)

    def minimax(self, state, depth, is_maximizing):
        winner = self.check_winner_state(state)
        if winner == "O":
            return 10 - depth
        if winner == "X":
            return depth - 10
        if winner == "DRAW":
            return 0

        if is_maximizing:
            best = -999
            for i in range(9):
                if state[i] is None:
                    state[i] = "O"
                    best = max(best, self.minimax(state, depth + 1, False))
                    state[i] = None
            return best
        else:
            best = 999
            for i in range(9):
                if state[i] is None:
                    state[i] = "X"
                    best = min(best, self.minimax(state, depth + 1, True))
                    state[i] = None
            return best

    def check_winner_state(self, state):
        for a, b, c in WIN_LINES:
            if state[a] and state[a] == state[b] == state[c]:
                return state[a]
        if all(state):
            return "DRAW"
        return None


# ================= Snake Game =================
class SnakeGame:
    def __init__(self, parent, root_ref, back_callback):
        self.parent = parent
        self.root = root_ref
        self.back_callback = back_callback

        self.high_score = 0
        self.speed_name = tk.StringVar(value="ปกติ")
        self.game_active = False
        self.after_id = None

        self.build_ui()
        self.reset_state()
        self.draw_start_message()

        self.root.bind("<Key>", self.on_key)

    def build_ui(self):
        title = tk.Label(self.parent, text="SNAKE GAME", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        title.pack(pady=(16, 0))

        subtitle = tk.Label(
            self.parent, text="งูกินหาง ใช้ปุ่มลูกศรบังคับทิศทาง", font=("Segoe UI", 10),
            bg=BG_COLOR, fg=MUTED_COLOR
        )
        subtitle.pack(pady=(0, 10))

        speed_frame = tk.Frame(self.parent, bg=BG_COLOR)
        speed_frame.pack(pady=(0, 10))

        for i, level in enumerate(SPEED_LEVELS.keys()):
            tk.Radiobutton(
                speed_frame, text=level, variable=self.speed_name, value=level,
                command=self.restart_game, font=("Segoe UI", 10, "bold"),
                bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=BOARD_COLOR,
                activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
                indicatoron=False, width=8, pady=6, relief="flat", highlightthickness=0
            ).grid(row=0, column=i, padx=4)

        self.status_label = tk.Label(
            self.parent, text="กด SPACE หรือปุ่มลูกศรเพื่อเริ่ม",
            font=("Segoe UI", 13, "bold"), bg=BOARD_COLOR, fg=SNAKE_HEAD_COLOR, width=30, pady=10
        )
        self.status_label.pack(pady=(0, 12))

        board_frame = tk.Frame(self.parent, bg=BOARD_COLOR, padx=10, pady=10)
        board_frame.pack()

        self.canvas = tk.Canvas(board_frame, width=GAME_WIDTH, height=GAME_HEIGHT, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack()

        score_frame = tk.Frame(self.parent, bg=BG_COLOR)
        score_frame.pack(pady=14, fill="x", padx=20)

        self.score_label = self.make_score_card(score_frame, "คะแนน", SNAKE_HEAD_COLOR, 0)
        self.high_score_label = self.make_score_card(score_frame, "คะแนนสูงสุด", FOOD_COLOR, 1)

        action_frame = tk.Frame(self.parent, bg=BG_COLOR)
        action_frame.pack(pady=(0, 8))

        tk.Button(
            action_frame, text="🔄 เริ่มใหม่", font=("Segoe UI", 11, "bold"),
            bg=ACCENT_COLOR, fg="white", relief="flat", padx=16, pady=8,
            activebackground="#7c3aed", command=self.restart_game
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            action_frame, text="⏸ พัก/เล่นต่อ", font=("Segoe UI", 11, "bold"),
            bg=BOARD_COLOR, fg=TEXT_COLOR, relief="flat", padx=16, pady=8,
            activebackground="#334155", command=self.toggle_pause
        ).grid(row=0, column=1, padx=6)

        make_back_button(self.parent, self.go_back)
        tk.Frame(self.parent, bg=BG_COLOR, height=16).pack()

    def go_back(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.back_callback()

    def make_score_card(self, parent, label, color, col):
        frame = tk.Frame(parent, bg=BOARD_COLOR, padx=10, pady=8)
        frame.grid(row=0, column=col, padx=4, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(frame, text=label, font=("Segoe UI", 9), bg=BOARD_COLOR, fg=MUTED_COLOR).pack()
        value_label = tk.Label(frame, text="0", font=("Segoe UI", 16, "bold"), bg=BOARD_COLOR, fg=color)
        value_label.pack()
        return value_label

    def reset_state(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()
        self.score = 0
        self.game_active = False
        self.paused = False
        self.score_label.configure(text="0")

    def spawn_food(self):
        occupied = set(getattr(self, "snake", []))
        while True:
            pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
            if pos not in occupied:
                return pos

    def draw_start_message(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_snake_and_food()
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2,
            text="กด SPACE เพื่อเริ่มเกม", fill=TEXT_COLOR, font=("Segoe UI", 14, "bold")
        )

    def draw_grid(self):
        for x in range(0, GAME_WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, GAME_HEIGHT, fill=GRID_LINE_COLOR)
        for y in range(0, GAME_HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, GAME_WIDTH, y, fill=GRID_LINE_COLOR)

    def draw_snake_and_food(self):
        fx, fy = self.food
        self.canvas.create_oval(
            fx * CELL_SIZE + 3, fy * CELL_SIZE + 3,
            (fx + 1) * CELL_SIZE - 3, (fy + 1) * CELL_SIZE - 3,
            fill=FOOD_COLOR, outline=""
        )
        for i, (x, y) in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            self.canvas.create_rectangle(
                x * CELL_SIZE + 2, y * CELL_SIZE + 2,
                (x + 1) * CELL_SIZE - 2, (y + 1) * CELL_SIZE - 2,
                fill=color, outline=""
            )

    def render(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_snake_and_food()

    def on_key(self, event):
        key = event.keysym
        if key == "space":
            if not self.game_active:
                self.start_game()
            else:
                self.toggle_pause()
            return

        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if key in ("Up", "Down", "Left", "Right"):
            if not self.game_active:
                self.start_game()
            if opposite.get(key) != self.direction:
                self.next_direction = key

    def toggle_pause(self):
        if not self.game_active:
            return
        self.paused = not self.paused
        if self.paused:
            self.status_label.configure(text="⏸ หยุดชั่วคราว (กด SPACE เพื่อเล่นต่อ)", fg=MUTED_COLOR)
        else:
            self.status_label.configure(text=f"คะแนน: {self.score}", fg=SNAKE_HEAD_COLOR)
            self.schedule_tick()

    def start_game(self):
        self.reset_state()
        self.game_active = True
        self.status_label.configure(text=f"คะแนน: {self.score}", fg=SNAKE_HEAD_COLOR)
        self.schedule_tick()

    def restart_game(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.reset_state()
        self.draw_start_message()
        self.status_label.configure(text="กด SPACE หรือปุ่มลูกศรเพื่อเริ่ม", fg=SNAKE_HEAD_COLOR)

    def schedule_tick(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        delay = SPEED_LEVELS[self.speed_name.get()]
        self.after_id = self.root.after(delay, self.tick)

    def tick(self):
        if not self.game_active or self.paused:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}[self.direction]
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0 or new_head[0] >= GRID_W or
            new_head[1] < 0 or new_head[1] >= GRID_H or
            new_head in self.snake
        ):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.score_label.configure(text=str(self.score))
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.render()
        self.status_label.configure(text=f"คะแนน: {self.score}", fg=SNAKE_HEAD_COLOR)
        self.schedule_tick()

    def game_over(self):
        self.game_active = False
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_label.configure(text=str(self.high_score))

        self.status_label.configure(text=f"💥 เกมจบ! คะแนน: {self.score}", fg=FOOD_COLOR)
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 - 10,
            text="งูชนแล้ว!", fill=TEXT_COLOR, font=("Segoe UI", 18, "bold")
        )
        self.canvas.create_text(
            GAME_WIDTH // 2, GAME_HEIGHT // 2 + 20,
            text="กด SPACE เพื่อเริ่มใหม่", fill=MUTED_COLOR, font=("Segoe UI", 11)
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
