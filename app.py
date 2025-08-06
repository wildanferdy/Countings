import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from gui.main_window import VehicleDetectorApp


def main():
    """Main entry point of the application"""
    root = ttk.Window(themename="darkly")
    app = VehicleDetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()