import os
import sys

def get_assets_path():
    """Returns the path to the assets directory."""
    # Check if running in a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, "com", "mhire", "assets")
    else:
        # Running in a normal Python environment
        current_dir = os.path.dirname(os.path.abspath(__file__))  # utils directory
        com_dir = os.path.dirname(current_dir)  # com directory
        return os.path.join(com_dir, "assets")