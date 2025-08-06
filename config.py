import json
from tkinter import messagebox

from .constants import MAX_DISPLAY_WIDTH, MAX_DISPLAY_HEIGHT


class ConfigManager:
    def __init__(self):
        self.config_file = 'config.json'
        self.default_settings = {
            "confidence_threshold": 0.2,
            "line_offset": 50,
            "line_orientation": "Horizontal",
            "line1_y": (MAX_DISPLAY_HEIGHT // 2) - 25,
            "line1_x": (MAX_DISPLAY_WIDTH // 2) - 25,
            "video_playback_speed": 1.0,
            "start_timestamp_user": None
        }

    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_settings.copy()

    def save_config(self, settings):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Info", "Config saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving config: {e}")