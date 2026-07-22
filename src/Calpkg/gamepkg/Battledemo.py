#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle Demo - หน้าจอต่อสู้แบบ CTB (Conditional Turn-Based) สไตล์เกม JRPG คลาสสิก
สร้างด้วย Python + tkinter

รายละเอียดระบบ:
- คิวเทิร์น (Turn Order) คำนวณจากค่า SPD ของตัวละคร/มอนสเตอร์ทุกตัว แสดงล่วงหน้า
- ปาร์ตี้ผู้เล่น 3 คน แต่ละคนมี HP / MP bar
- มอนสเตอร์ฝั่งตรงข้ามหลายตัว คลิกที่ตัวมอนสเตอร์บนสนามรบเพื่อเลือกเป้าหมาย
- เมนูคำสั่ง: Attack (โจมตี), Skill (สกิล), Special (ท่าไม้ตาย เก็บพลังจากการโจมตี)
- กล่องคำอธิบาย (HELP) ด้านบนอธิบายคำสั่งที่ชี้อยู่ เหมือนเกม JRPG คลาสสิก

หมายเหตุ: ตัวละคร/มอนสเตอร์/ชื่อทั้งหมดเป็นผลงานต้นฉบับ ไม่ได้ใช้เนื้อหาลิขสิทธิ์จากเกมใดๆ
"""

import tkinter as tk
import random

# ---------------------------------------------------------
# ธีมสี
# ---------------------------------------------------------
COL_BG        = "#0d1520"
COL_SKY_TOP   = "#4a90c2"
COL_SKY_BOT   = "#bcdff0"
COL_GROUND    = "#5a8a4a"
COL_GROUND2   = "#4a7a3a"
COL_PANEL     = "#131b2e"
COL_PANEL_ALT = "#1c2740"
COL_BORDER    = "#3a5a8a"
COL_GOLD      = "#f0c860"
COL_TEXT      = "#eef2ff"
COL_DIM       = "#8fa3c8"
COL_HP        = "#4ad86a"
COL_HP_LOW    = "#e8483a"
COL_MP        = "#4aa8ff"
COL_HPBG      = "#1a2a1a"
COL_MPBG      = "#152238"
COL_SEL       = "#f0c860"
COL_CMD_BG    = "#1a2440"
COL_CMD_HI    = "#f0a830"
COL_ENEMY_HP  = "#e05a4a"
COL_HELP_BG   = "#0a0f1a"

FONT_HELP  = ("Georgia", 12)
FONT_NAME  = ("Consolas", 11, "bold")
FONT_STAT  = ("Consolas", 10, "bold")
FONT_CMD   = ("Georgia", 13, "bold")
FONT_SMALL = ("Consolas", 9)

W, H = 1000, 620

# ---------------------------------------------------------
# ข้อมูลตัวละคร / มอนสเตอร์ (ต้นฉบับทั้งหมด)
# ---------------------------------------------------------
COMMANDS = [
    {"name": "Attack",  "desc": "โจมตีศัตรูด้วยอาวุธที่ติดตั้งอยู่"},
    {"name": "Skill",   "desc": "ใช้สกิลพิเศษประจำตัว สิ้นเปลือง MP"},
    {"name": "Special", "desc": "ปลดปล่อยท่าไม้ตายเมื่อเกจ Overdrive เต็ม"},
]

SKILL_LIST = {
    "Ren":   {"name": "Twin Slash", "mp": 8,  "mult": 1.9, "target": "single"},
    "Sera":  {"name": "Blizzara",   "mp": 12, "mult": 2.4, "target": "single"},
    "Kade":  {"name": "Guard Break","mp": 6,  "mult": 1.6, "target": "single"},
}

SPECIAL_LIST = {
    "Ren":   {"name": "Blade Fury",     "mult": 4.2},
    "Sera":  {"name": "Frozen Requiem", "mult": 4.8},
    "Kade":  {"name": "Titan's Wrath",  "mult": 3.8},
}


class Unit:
    def __init__(self, name, max_hp, max_mp, atk, df, spd, is_enemy=False, icon="?", color="#cccccc"):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = max_mp
        self.mp = max_mp
        self.atk = atk
        self.df = df
        self.spd = spd
        self.is_enemy = is_enemy
        self.icon = icon
        self.color = color
        self.overdrive = 0          # 0-100 เกจท่าไม้ตาย
        self.ct = 0.0                # เวลาสะสมสำหรับคิวเทิร์น (ยิ่งน้อยยิ่งได้เทิร์นเร็ว)
        self.alive = True

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        if self.hp == 0:
            self.alive = False

    def turn_cost(self):
        return 1000.0 / max(1, self.spd)


def make_party():
    return [
        Unit("Ren",  90,  20, 22, 8,  14, icon="🗡", color="#e07a3a"),
        Unit("Sera", 60,  55, 14, 5,  11, icon="🔮", color="#7a6ae0"),
        Unit("Kade", 130, 15, 18, 14, 9,  icon="🛡", color="#4a90c2"),
    ]


def make_enemies():
    return [
        Unit("Flare Wisp",  55, 0, 16, 3, 12, is_enemy=True, icon="🔥", color="#e0603a"),
        Unit("Flare Wisp",  55, 0, 16, 3, 13, is_enemy=True, icon="🔥", color="#e0603a"),
        Unit("Stone Fang",  180, 0, 20, 9, 7,  is_enemy=True, icon="🔱", color="#9a8a70"),  # เปลี่ยนเป็นช้อนกัน (pitchfork)
    ]


# ---------------------------------------------------------
# Animation Helpers
# ---------------------------------------------------------
def float_animation(offset, amplitude=6):
    """Update floating animation offset - bounces up and down"""
    offset[0] += offset[1]  # increment by direction
    if offset[0] > amplitude or offset[0] < -amplitude:
        offset[1] *= -1  # reverse direction
    return offset[0]


# ---------------------------------------------------------
# แอปหลัก
# ---------------------------------------------------------
class BattleDemo:
    def __init__(self, root, parent=None, back_callback=None):
        """
        root: หน้าต่างหลัก (ใช้สำหรับ .after() เพื่อหน่วงเวลา)
        parent: widget ที่จะใส่ canvas ลงไป (ถ้าไม่ระบุ จะใช้ root แทน
                 เพื่อให้ยังรันเดี่ยวๆ ผ่าน main() ได้เหมือนเดิม)
        back_callback: ฟังก์ชันที่เรียกเมื่อกดปุ่ม "กลับเมนู" (ถ้ามี)
        """
        self.root = root
        container = parent if parent is not None else root
        self.back_callback = back_callback

        if parent is None:
            self.root.title("⚔ Battle Demo - CTB Turn Order System")
            self.root.configure(bg=COL_BG)
            self.root.resizable(False, False)

        self.party = make_party()
        self.enemies = make_enemies()
        self.all_units = self.party + self.enemies

        self.phase = "select_command"   # select_command | select_skill | select_target | enemy_turn | busy | end
        self.current_unit = None
        self.pending_action = None       # {"type": "attack"/"skill"/"special", "data": ...}
        self.help_text = COMMANDS[0]["desc"]
        self.log_lines = []
        self.target_index = 0

        # Floating animation state
        self.float_offset = 0
        self.float_direction = 1

        self.canvas = tk.Canvas(container, width=W, height=H, highlightthickness=0, bg=COL_BG)
        self.canvas.pack()

        if self.back_callback is not None:
            back_btn = tk.Button(
                container, text="◀ กลับเมนู", font=("Consolas", 9, "bold"),
                bg=COL_PANEL, fg=COL_TEXT, relief="flat", padx=10, pady=4,
                activebackground="#334155", command=self.back_callback
            )
            back_btn.pack(pady=(6, 10))

        self.enemy_hit_areas = []  # [(x0,y0,x1,y1, unit)]
        self.cmd_hit_areas = []

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)

        self.advance_to_next_turn()
        self.render()
        self.animate_floating()

    def animate_floating(self):
        """Run floating animation loop"""
        self.float_offset += self.float_direction
        if self.float_offset > 6 or self.float_offset < -6:
            self.float_direction *= -1
        # Re-render sprites with float offset (always, even in end phase)
        self._redraw_sprites()
        self.root.after(50, self.animate_floating)

    def _redraw_sprites(self):
        """Redraw just the sprites (enemies + party) with float animation"""
        c = self.canvas
        c.delete("sprite")  # Clear old sprites only
        # Redraw enemies with float (เสมอ - แม้ใน end phase ก็ยังทำอนิเมชั่น)
        n = len(self.enemies)
        spacing = 200
        start_x = W // 2 - (spacing * (n - 1)) // 2
        for i, e in enumerate(self.enemies):
            cx = start_x + i * spacing
            cy = 230 + self.float_offset * (-1 if i % 2 else 1)
            active = (self.current_unit is e and self.phase == "enemy_turn")
            targetable = self.phase == "select_target"

            if not e.is_alive():
                c.create_text(cx, cy, text="💨", font=("Consolas", 30), fill=COL_DIM, tags="sprite")
                continue

            ring_color = COL_SEL if (active or targetable) else ""
            if ring_color:
                c.create_oval(cx-52, cy-52, cx+52, cy+52, outline=ring_color, width=3, tags="sprite")
            c.create_text(cx, cy, text=e.icon, font=("Consolas", 46), tags="sprite")

        # Redraw party with float
        spacing = 110
        for i, p in enumerate(self.party):
            cx = W - 260 + i * spacing
            cy = 330 + self.float_offset
            active = (self.current_unit is p and self.phase in ("select_command", "select_target"))
            if active:
                c.create_oval(cx-38, cy-38, cx+38, cy+38, outline=COL_SEL, width=3, tags="sprite")
            alpha_icon = p.icon if p.is_alive() else "🪦"
            c.create_text(cx, cy, text=alpha_icon, font=("Consolas", 34), tags="sprite")

    # ---------------- TURN QUEUE ----------------
    def build_turn_preview(self, n=8):
        """คืนรายชื่อ unit ตามลำดับคิวเทิร์นล่วงหน้า n เทิร์น (ไม่กระทบ ct จริง)"""
        sim = [(u.ct, u) for u in self.all_units if u.is_alive()]
        preview = []
        for _ in range(n):
            sim.sort(key=lambda t: t[0])
            ct, u = sim.pop(0)
            preview.append(u)
            sim.append((ct + u.turn_cost(), u))
        return preview

    def advance_to_next_turn(self):
        alive_party = [u for u in self.party if u.is_alive()]
        alive_enemies = [u for u in self.enemies if u.is_alive()]
        if not alive_party:
            self.phase = "end"
            self.log("💀 ปาร์ตี้ของคุณพ่ายแพ้...")
            return
        if not alive_enemies:
            self.phase = "end"
            self.log("🏆 ชนะการต่อสู้! ศัตรูทั้งหมดถูกกำจัด")
            return

        living = [u for u in self.all_units if u.is_alive()]
        living.sort(key=lambda u: u.ct)
        actor = living[0]
        # เดินเวลาของทุกตัวไปจนถึงเทิร์นของ actor แล้วหักออก เพื่อไม่ให้ ct โตไม่สิ้นสุด
        base = actor.ct
        for u in self.all_units:
            u.ct -= base

        self.current_unit = actor
        if actor.is_enemy:
            self.phase = "enemy_turn"
            self.root.after(650, self.do_enemy_turn)
        else:
            self.phase = "select_command"
            self.help_text = COMMANDS[0]["desc"]

    def finish_actor_turn(self):
        self.current_unit.ct += self.current_unit.turn_cost()
        self.advance_to_next_turn()
        self.render()

    # ---------------- ACTIONS ----------------
    def player_attack(self, target):
        actor = self.current_unit
        dmg = max(1, actor.atk - target.df + random.randint(-3, 4))
        target.take_damage(dmg)
        actor.overdrive = min(100, actor.overdrive + 18)
        self.log(f"⚔ {actor.name} โจมตี {target.name} ทำดาเมจ {dmg}")
        self.after_action_check(target)

    def player_skill(self, target):
        actor = self.current_unit
        sk = SKILL_LIST[actor.name]
        actor.mp -= sk["mp"]
        dmg = max(1, int(actor.atk * sk["mult"]) - target.df + random.randint(-2, 5))
        target.take_damage(dmg)
        actor.overdrive = min(100, actor.overdrive + 12)
        self.log(f"✨ {actor.name} ใช้ {sk['name']}! ทำดาเมจ {dmg} ให้ {target.name}")
        self.after_action_check(target)

    def player_special(self, target):
        actor = self.current_unit
        sp = SPECIAL_LIST[actor.name]
        dmg = max(1, int(actor.atk * sp["mult"]) - target.df + random.randint(0, 8))
        target.take_damage(dmg)
        actor.overdrive = 0
        self.log(f"💥 {actor.name} ปลดปล่อยท่าไม้ตาย {sp['name']}! ดาเมจมหาศาล {dmg}")
        self.after_action_check(target)

    def after_action_check(self, target):
        if not target.is_alive():
            self.log(f"☠ {target.name} ถูกกำจัด!")
        self.pending_action = None
        self.finish_actor_turn()

    def do_enemy_turn(self):
        actor = self.current_unit
        targets = [u for u in self.party if u.is_alive()]
        if not targets:
            self.finish_actor_turn()
            return
        target = min(targets, key=lambda u: u.hp)  # ล่าตัวเลือดน้อยสุด
        dmg = max(1, actor.atk - target.df + random.randint(-2, 3))
        target.take_damage(dmg)
        self.log(f"💢 {actor.name} โจมตี {target.name} ได้รับความเสียหาย {dmg}")
        if not target.is_alive():
            self.log(f"⚠ {target.name} ล้มลง!")
        self.finish_actor_turn()

    def log(self, text):
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-4:]

    # ---------------- INPUT HANDLING ----------------
    def on_motion(self, event):
        if self.phase != "select_command":
            return
        for (x0, y0, x1, y1, idx) in self.cmd_hit_areas:
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                self.help_text = COMMANDS[idx]["desc"]
                self.render()
                return

    def on_click(self, event):
        if self.phase == "select_command":
            for (x0, y0, x1, y1, idx) in self.cmd_hit_areas:
                if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                    self.choose_command(idx)
                    return

        elif self.phase == "select_target":
            for (x0, y0, x1, y1, unit) in self.enemy_hit_areas:
                if x0 <= event.x <= x1 and y0 <= event.y <= y1 and unit.is_alive():
                    self.execute_pending(unit)
                    return

        elif self.phase == "end":
            self.restart()

    def choose_command(self, idx):
        cmd = COMMANDS[idx]["name"]
        actor = self.current_unit
        if cmd == "Attack":
            self.pending_action = {"type": "attack"}
            self.phase = "select_target"
        elif cmd == "Skill":
            if actor.mp < SKILL_LIST[actor.name]["mp"]:
                self.log("⚠ MP ไม่พอสำหรับ Skill!")
                self.render()
                return
            self.pending_action = {"type": "skill"}
            self.phase = "select_target"
        elif cmd == "Special":
            if actor.overdrive < 100:
                self.log("⚠ เกจ Overdrive ยังไม่เต็ม!")
                self.render()
                return
            self.pending_action = {"type": "special"}
            self.phase = "select_target"
        self.render()

    def execute_pending(self, target):
        t = self.pending_action["type"]
        if t == "attack":
            self.player_attack(target)
        elif t == "skill":
            self.player_skill(target)
        elif t == "special":
            self.player_special(target)

    def restart(self):
        self.party = make_party()
        self.enemies = make_enemies()
        self.all_units = self.party + self.enemies
        self.log_lines = []
        self.advance_to_next_turn()
        self.render()

    # ---------------- RENDER ----------------
    def render(self):
        c = self.canvas
        c.delete("all")
        self.enemy_hit_areas = []
        self.cmd_hit_areas = []

        self._draw_background()
        self._draw_enemies()
        self._draw_party_sprites()
        self._draw_help_box()
        self._draw_turn_queue()
        self._draw_party_status()
        self._draw_log()

        if self.phase == "select_command":
            self._draw_command_menu()
        elif self.phase == "select_target":
            self._draw_target_hint()
        elif self.phase == "end":
            self._draw_end_banner()

    def _draw_background(self):
        c = self.canvas
        for i in range(0, 360, 4):
            t = i / 360
            r = int(int(COL_SKY_TOP[1:3],16)*(1-t) + int(COL_SKY_BOT[1:3],16)*t)
            g = int(int(COL_SKY_TOP[3:5],16)*(1-t) + int(COL_SKY_BOT[3:5],16)*t)
            b = int(int(COL_SKY_TOP[5:7],16)*(1-t) + int(COL_SKY_BOT[5:7],16)*t)
            c.create_line(0, i, W, i, fill=f"#{r:02x}{g:02x}{b:02x}")
        c.create_rectangle(0, 360, W, H, fill=COL_GROUND, outline="")
        for i in range(14):
            x = (i * 97) % W
            y = 380 + (i * 53) % (H - 400)
            c.create_oval(x, y, x + 40, y + 14, fill=COL_GROUND2, outline="")

    def _draw_enemies(self):
        c = self.canvas
        n = len(self.enemies)
        spacing = 200
        start_x = W // 2 - (spacing * (n - 1)) // 2
        for i, e in enumerate(self.enemies):
            cx = start_x + i * spacing
            cy = 230 + self.float_offset * (-1 if i % 2 else 1)  # Floating effect
            active = (self.current_unit is e and self.phase == "enemy_turn")
            targetable = self.phase == "select_target"

            if not e.is_alive():
                c.create_text(cx, cy, text="💨", font=("Consolas", 30), fill=COL_DIM)
                continue

            ring_color = COL_SEL if (active or targetable) else ""
            if ring_color:
                c.create_oval(cx-52, cy-52, cx+52, cy+52, outline=ring_color, width=3)

            c.create_text(cx, cy, text=e.icon, font=("Consolas", 46))
            # hp bar เหนือหัว
            bw = 90
            c.create_rectangle(cx-bw/2, cy-70, cx+bw/2, cy-58, fill=COL_ENEMY_HP if False else "#3a1010", outline=COL_BORDER)
            ratio = e.hp / e.max_hp
            c.create_rectangle(cx-bw/2, cy-70, cx-bw/2+bw*ratio, cy-58, fill=COL_ENEMY_HP, outline="")
            c.create_text(cx, cy-92, text=e.name, font=FONT_SMALL, fill=COL_TEXT)

            self.enemy_hit_areas.append((cx-55, cy-95, cx+55, cy+55, e))

    def _draw_party_sprites(self):
        c = self.canvas
        n = len(self.party)
        spacing = 110
        start_x = W - 230
        for i, p in enumerate(self.party):
            cx = start_x + i * 0
            cx = W - 260 + i * spacing
            cy = 330 + self.float_offset  # Floating effect
            active = (self.current_unit is p and self.phase in ("select_command", "select_target"))
            if active:
                c.create_oval(cx-38, cy-38, cx+38, cy+38, outline=COL_SEL, width=3)
            alpha_icon = p.icon if p.is_alive() else "🪦"
            c.create_text(cx, cy, text=alpha_icon, font=("Consolas", 34))
            c.create_text(cx, cy+38, text=p.name, font=FONT_SMALL, fill=COL_TEXT)

    def _draw_help_box(self):
        c = self.canvas
        c.create_rectangle(20, 16, 560, 62, fill=COL_HELP_BG, outline=COL_BORDER, width=2)
        label = "HELP" if self.phase == "select_command" else ("TARGET" if self.phase=="select_target" else "BATTLE")
        c.create_text(34, 26, text=label, anchor="w", font=("Consolas", 9, "bold"), fill=COL_GOLD)
        txt = self.help_text if self.phase == "select_command" else (
            "เลือกศัตรูที่ต้องการโจมตี (คลิกที่ตัวมอนสเตอร์)" if self.phase == "select_target" else
            (self.log_lines[-1] if self.log_lines else "")
        )
        c.create_text(34, 46, text=txt, anchor="w", font=FONT_HELP, fill=COL_TEXT)

    def _draw_turn_queue(self):
        c = self.canvas
        x0, y0 = W - 60, 90
        c.create_rectangle(x0-14, y0-14, x0+58, y0+14+38*7, fill=COL_PANEL, outline=COL_BORDER, width=2)
        preview = self.build_turn_preview(7)
        for i, u in enumerate(preview):
            y = y0 + i * 38
            box_color = COL_PANEL_ALT if not u.is_enemy else "#3a1a1a"
            highlight = (i == 0)
            c.create_rectangle(x0-8, y-16, x0+50, y+16, fill=box_color,
                                outline=COL_GOLD if highlight else COL_BORDER, width=2 if highlight else 1)
            c.create_text(x0+21, y, text=u.icon, font=("Consolas", 16))
        c.create_text(x0+21, y0-28, text="TURN", font=("Consolas", 8, "bold"), fill=COL_DIM)

    def _draw_party_status(self):
        c = self.canvas
        x0 = W - 330
        y0 = H - 150
        c.create_rectangle(x0-10, y0-10, W-70, H-20, fill=COL_PANEL, outline=COL_BORDER, width=2)
        for i, p in enumerate(self.party):
            y = y0 + i * 42
            active = (self.current_unit is p and self.phase in ("select_command","select_target"))
            name_col = COL_GOLD if active else COL_TEXT
            c.create_text(x0+6, y, text=p.name, anchor="w", font=FONT_NAME, fill=name_col)

            # HP bar
            bx0 = x0 + 90
            bw = 90
            c.create_rectangle(bx0, y-8, bx0+bw, y+2, fill=COL_HPBG, outline=COL_BORDER)
            ratio = p.hp / p.max_hp if p.max_hp else 0
            hp_color = COL_HP if ratio > 0.3 else COL_HP_LOW
            c.create_rectangle(bx0, y-8, bx0+bw*ratio, y+2, fill=hp_color, outline="")
            c.create_text(bx0+bw+34, y-3, text=f"{p.hp}/{p.max_hp}", font=FONT_SMALL, fill=COL_TEXT)

            # MP bar
            my = y + 12
            c.create_rectangle(bx0, my-6, bx0+bw*0.7, my+2, fill=COL_MPBG, outline=COL_BORDER)
            mratio = (p.mp / p.max_mp) if p.max_mp else 0
            c.create_rectangle(bx0, my-6, bx0+bw*0.7*mratio, my+2, fill=COL_MP, outline="")
            c.create_text(bx0+bw*0.7+30, my-2, text=f"{p.mp}/{p.max_mp}", font=FONT_SMALL, fill=COL_DIM)

            # Overdrive gauge
            oy = y - 18
            ow = 60
            c.create_rectangle(x0+6, oy-4, x0+6+ow, oy+2, fill="#332200", outline=COL_BORDER)
            orat = p.overdrive / 100
            c.create_rectangle(x0+6, oy-4, x0+6+ow*orat, oy+2, fill=COL_CMD_HI, outline="")

    def _draw_log(self):
        c = self.canvas
        x0, y0 = 20, H - 100
        c.create_rectangle(x0-6, y0-6, x0+430, H-20, fill=COL_PANEL, outline=COL_BORDER, width=1)
        for i, line in enumerate(self.log_lines[-4:]):
            c.create_text(x0+4, y0 + i*18, text=line, anchor="w", font=FONT_SMALL, fill=COL_DIM)

    def _draw_command_menu(self):
        c = self.canvas
        x0, y0 = 20, 400
        w, h = 220, 150
        c.create_rectangle(x0, y0, x0+w, y0+h, fill=COL_CMD_BG, outline=COL_GOLD, width=2)
        actor = self.current_unit
        c.create_text(x0+w/2, y0-16, text=f"▶ {actor.name} 's Turn", font=("Georgia", 12, "bold"), fill=COL_GOLD)

        for i, cmd in enumerate(COMMANDS):
            cy = y0 + 26 + i*40
            disabled = False
            if cmd["name"] == "Special" and actor.overdrive < 100:
                disabled = True
            if cmd["name"] == "Skill" and actor.mp < SKILL_LIST[actor.name]["mp"]:
                disabled = True
            text_color = COL_DIM if disabled else COL_TEXT
            c.create_rectangle(x0+10, cy-16, x0+w-10, cy+16, fill=COL_PANEL_ALT, outline=COL_BORDER)
            c.create_polygon(x0+20, cy-6, x0+20, cy+6, x0+30, cy, fill=COL_GOLD)
            c.create_text(x0+40, cy, text=cmd["name"], anchor="w", font=FONT_CMD, fill=text_color)
            self.cmd_hit_areas.append((x0+10, cy-16, x0+w-10, cy+16, i))

    def _draw_target_hint(self):
        c = self.canvas
        c.create_text(W/2, 60, text="🎯 เลือกเป้าหมาย", font=("Georgia", 16, "bold"), fill=COL_GOLD)

    def _draw_end_banner(self):
        c = self.canvas
        c.create_rectangle(0, H/2-60, W, H/2+60, fill="#000000", stipple="gray50", outline="")
        alive_party = any(u.is_alive() for u in self.party)
        msg = "🏆 VICTORY!" if alive_party else "💀 GAME OVER"
        color = COL_GOLD if alive_party else COL_HP_LOW
        c.create_text(W/2, H/2-14, text=msg, font=("Georgia", 30, "bold"), fill=color)
        c.create_text(W/2, H/2+22, text="คลิกที่หน้าจอเพื่อเริ่มต่อสู้ใหม่", font=FONT_HELP, fill=COL_TEXT)


def main():
    root = tk.Tk()
    app = BattleDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()