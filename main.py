import sys, os
from pathlib import Path

from application_handler import Application_Handler

def get_script_dir():
    '''this function returns the running path of the main script'''
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent

if __name__ == "__main__":
    config_path = os.path.join(get_script_dir(), 'config.json')
    app = Application_Handler(config_path)
    app.start_application()
