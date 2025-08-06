import tkinter as tk
from tkinter import messagebox

from gui.dialogs import SettingsDialog, TimeDialog
import datetime
import os


class MenuManager:
    def __init__(self, app):
        self.app = app

    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.app.root)
        self.app.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.app.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        # Source menu
        source_menu = tk.Menu(menubar, tearoff=0)
        source_menu.add_command(label="Load Video File", command=self.app.video_handler.load_video)
        source_menu.add_command(label="Use Webcam", command=self.app.video_handler.open_webcam_selection)
        menubar.add_cascade(label="Source", menu=source_menu)

        # Settings menu
        settings_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configuration", command=self.open_settings_dialog)
        settings_menu.add_command(label="Time", command=self.open_time_dialog)

    def open_settings_dialog(self):
        """Open settings configuration dialog"""
        def apply_settings_callback(confidence, offset, orientation, speed):
            self.app.settings['confidence_threshold'] = confidence
            self.app.settings['line_offset'] = offset
            self.app.settings['line_orientation'] = orientation
            self.app.settings['video_playback_speed'] = speed
            self.app.new_settings_to_send = self.app.settings.copy()

            # Only apply speed settings for video files, not webcam
            if (self.app.video_handler.video_source and 
                self.app.video_handler.video_fps > 0 and 
                not self.app.video_handler.is_webcam):
                self.app.video_handler.frame_delay = ((1.0 / self.app.video_handler.video_fps) / 
                                                     self.app.settings['video_playback_speed'])

            if self.app.detection_manager.running:
                messagebox.showinfo("Info", "Settings will be applied to the next frame.")
            elif self.app.video_handler.video_source:  # Only display if there's a video source
                self.app.video_handler.display_first_frame()

            self.app.config_manager.save_config(self.app.settings)

        SettingsDialog(self.app.root, self.app.settings.copy(), apply_settings_callback)

    def open_time_dialog(self):
        """Open time configuration dialog"""
        def apply_time_callback(timestamp_str):
            self.app.settings["start_timestamp_user"] = timestamp_str
            self.app.new_settings_to_send = self.app.settings.copy()
            self.app.config_manager.save_config(self.app.settings)

        # Handle webcam case
        if (self.app.video_handler.video_source and 
            isinstance(self.app.video_handler.video_source, str) and 
            os.path.exists(self.app.video_handler.video_source)):
            try:
                timestamp = os.path.getmtime(self.app.video_handler.video_source)
                video_time = datetime.datetime.fromtimestamp(timestamp)
                default_timestamp = video_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                default_timestamp = self.app.settings["start_timestamp_user"]
        else:
            default_timestamp = self.app.settings["start_timestamp_user"]

        TimeDialog(self.app.root, default_timestamp, apply_time_callback)