import tkinter as tk

from src.Calpkg.__pycache__.calculator import add,subtract
from src.Calpkg.gamepkg.game_center import GameApp


def run_calculator():
    print("\n=== เครื่องคิดเลข ===")
    a = float(input("ใส่ตัวเลขที่ 1: "))
    b = float(input("ใส่ตัวเลขที่ 2: "))
    print(f"บวก: {add(a, b)}")
    print(f"ลบ: {subtract(a, b)}")


def run_game():
    print("\n=== เปิด Game Center ===")
    root = tk.Tk()
    GameApp(root)
    root.mainloop()


def main():
    print("=== เลือกโปรแกรมที่ต้องการใช้งาน ===")
    print("1. เครื่องคิดเลข")
    print("2. เกม (Game Center)")
    choice = input("พิมพ์เลข 1 หรือ 2 แล้ว Enter: ").strip()

    if choice == "1":
        run_calculator()
    elif choice == "2":
        run_game()
    else:
        print("กรุณาใส่ 1 หรือ 2 เท่านั้น")


if __name__ == "__main__":
    main()