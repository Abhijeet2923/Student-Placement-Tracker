import tkinter as tk
import run_gui
import dbe

def main():
    dbe.setup_database()
    root = tk.Tk()
    app = run_gui.PlacementTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
