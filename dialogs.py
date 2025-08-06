# gui/dialogs.py
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from ttkbootstrap import Toplevel, Frame, Label
from datetime import datetime
from tkinter import messagebox

DEFAULT_DIALOG_WIDTH = 450
DEFAULT_DIALOG_HEIGHT = 280

class SettingsDialog(ttk.Toplevel):
    def __init__(self, parent, current_settings, apply_callback):
        super().__init__(parent)

        self.title("Configuration")
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.current_settings = current_settings
        self.apply_callback = apply_callback

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        DEFAULT_DIALOG_HEIGHT = 240
        pos_x = (screen_width - DEFAULT_DIALOG_WIDTH) // 2
        pos_y = (screen_height - DEFAULT_DIALOG_HEIGHT) // 2
        self.geometry(f"{DEFAULT_DIALOG_WIDTH}x{DEFAULT_DIALOG_HEIGHT}+{pos_x}+{pos_y}")

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=BOTH, expand=True)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        row_counter = 0

        # Confidence Threshold
        ttk.Label(frame, text="Confidence Threshold (0.0 - 1.0):").grid(row=row_counter, column=0, sticky=W, pady=(0, 2))
        self.confidence_scale = ttk.Scale(frame, from_=0.0, to=1.0, value=self.current_settings['confidence_threshold'],
                                         orient=HORIZONTAL, command=self._update_confidence_label, bootstyle="info")
        self.confidence_scale.grid(row=row_counter, column=1, sticky="ew", pady=(0, 2))
        row_counter += 1
        self.confidence_label = ttk.Label(frame, text=f"{self.current_settings['confidence_threshold']:.2f}")
        self.confidence_label.grid(row=row_counter, column=1, sticky=E, pady=(0, 10))
        row_counter += 1

        # Line Distance
        ttk.Label(frame, text="Line Distance (pixels):").grid(row=row_counter, column=0, sticky=W, pady=(0, 2))
        self.offset_scale = ttk.Scale(frame, from_=10, to=200, value=self.current_settings['line_offset'],
                                          orient=HORIZONTAL, command=self._update_offset_label, bootstyle="info")
        self.offset_scale.grid(row=row_counter, column=1, sticky="ew", pady=(0, 2))
        row_counter += 1
        self.offset_label = ttk.Label(frame, text=f"{self.current_settings['line_offset']} px")
        self.offset_label.grid(row=row_counter, column=1, sticky=E, pady=(0, 10))
        row_counter += 1

        # Line Orientation
        ttk.Label(frame, text="Line Orientation:").grid(row=row_counter, column=0, sticky=W, pady=(0, 5))
        orientation_frame = ttk.Frame(frame)
        orientation_frame.grid(row=row_counter, column=1, sticky="w", pady=(0, 10))
        self.orientation_var = tk.StringVar(value=self.current_settings['line_orientation'])
        ttk.Radiobutton(orientation_frame, text="Horizontal", variable=self.orientation_var, value="Horizontal", bootstyle="info").pack(side=LEFT, padx=5)
        ttk.Radiobutton(orientation_frame, text="Vertical", variable=self.orientation_var, value="Vertical", bootstyle="info").pack(side=LEFT, padx=5)
        row_counter += 1

        # Video Playback Speed
        ttk.Label(frame, text="Video Playback Speed:").grid(row=row_counter, column=0, sticky=W, pady=(0, 2))
        self.speed_scale = ttk.Scale(frame, from_=0.1, to=5.0, value=self.current_settings['video_playback_speed'],
                                          orient=HORIZONTAL, command=self._update_speed_label, bootstyle="info")
        self.speed_scale.grid(row=row_counter, column=1, sticky="ew", pady=(0, 2))
        row_counter += 1
        self.speed_label = ttk.Label(frame, text=f"{self.current_settings['video_playback_speed']:.1f}x")
        self.speed_label.grid(row=row_counter, column=1, sticky=E, pady=(0, 10))
        row_counter += 1

        ttk.Button(frame, text="Apply", command=self._on_apply, bootstyle="success", width=25).grid(row=row_counter, column=0, columnspan=2, pady=(5,0))

    def _update_confidence_label(self, val):
        self.confidence_label.config(text=f"{float(val):.2f}")

    def _update_offset_label(self, val):
        self.offset_label.config(text=f"{int(float(val))} px")

    def _update_speed_label(self, val):
        self.speed_label.config(text=f"{float(val):.1f}x")

    def _on_apply(self):
        new_confidence = round(self.confidence_scale.get(), 2)
        new_offset = int(self.offset_scale.get())
        new_orientation = self.orientation_var.get()
        new_speed = round(self.speed_scale.get(), 1)
        self.apply_callback(new_confidence, new_offset, new_orientation, new_speed)
        self.destroy()

class TimeDialog(Toplevel):
    def __init__(self, parent, current_timestamp_user, apply_callback):
        super().__init__(parent)
        self.title("Set Time and Date")
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.current_timestamp_user = current_timestamp_user
        self.apply_callback = apply_callback

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        DEFAULT_DIALOG_HEIGHT = 150

        pos_x = (screen_width - DEFAULT_DIALOG_WIDTH) // 2
        pos_y = (screen_height - DEFAULT_DIALOG_HEIGHT) // 2
        self.geometry(f"{DEFAULT_DIALOG_WIDTH}x{DEFAULT_DIALOG_HEIGHT}+{pos_x}+{pos_y}")

        frame = Frame(self, padding=15)
        frame.pack(fill="both", expand=True)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)

        row_counter = 0

        # --- Tanggal ---
        Label(frame, text="Select Date (DD/MM/YYYY):").grid(row=row_counter, column=0, sticky="w")
        date_frame = Frame(frame)
        date_frame.grid(row=row_counter, column=1, sticky="ew", pady=(0, 10))
        row_counter += 1

        now = datetime.now()

        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()

        days = [f"{i:02d}" for i in range(1, 32)]
        months = [f"{i:02d}" for i in range(1, 13)]
        years = [str(y) for y in range(now.year - 10, now.year + 11)]

        # Default value
        if self.current_timestamp_user:
            try:
                dt_obj = datetime.strptime(self.current_timestamp_user, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt_obj = now
        else:
            dt_obj = now

        self.day_var.set(f"{dt_obj.day:02d}")
        self.month_var.set(f"{dt_obj.month:02d}")
        self.year_var.set(str(dt_obj.year))

        ttk.Combobox(date_frame, textvariable=self.day_var, values=days, width=4, bootstyle="info").pack(side="left", padx=2)
        ttk.Combobox(date_frame, textvariable=self.month_var, values=months, width=4, bootstyle="info").pack(side="left", padx=2)
        ttk.Combobox(date_frame, textvariable=self.year_var, values=years, width=6, bootstyle="info").pack(side="left", padx=2)

        # --- Jam ---
        ttk.Label(frame, text="Set Time (HH:MM):").grid(row=row_counter, column=0, sticky="w")
        time_frame = Frame(frame)
        time_frame.grid(row=row_counter, column=1, sticky="w", pady=(0, 10))
        row_counter += 1

        self.hour_var = tk.StringVar(value=f"{dt_obj.hour:02d}")
        self.minute_var = tk.StringVar(value=f"{dt_obj.minute:02d}")

        ttk.Entry(time_frame, textvariable=self.hour_var, width=3).pack(side="left")
        ttk.Label(time_frame, text=":").pack(side="left")
        ttk.Entry(time_frame, textvariable=self.minute_var, width=3).pack(side="left")

        # --- Tombol Apply ---
        ttk.Button(frame, text="Apply", command=self._on_apply, bootstyle="success", width=25).grid(
            row=row_counter, column=0, columnspan=2, pady=(10, 0)
        )

    def _on_apply(self):
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            if not (1 <= day <= 31 and 1 <= month <= 12 and 0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid date or time input")

            result_dt = datetime(year, month, day, hour, minute)
            self.apply_callback(result_dt.strftime("%Y-%m-%d %H:%M:%S"))
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")