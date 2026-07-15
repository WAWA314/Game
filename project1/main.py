import tkinter as tk
from src.Calpkg.gamepkg.game_center import GameApp
def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
if __name__ == "__main__":
    main()