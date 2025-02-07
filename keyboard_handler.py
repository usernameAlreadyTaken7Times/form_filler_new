import keyboard, time, pyperclip
from error_list import Errors

from shared_queue import shared_queue
import threading


class Keyboard_Handler(threading.Thread):
    '''This Keyboard_Handler handles keyboard-related signals.
    It involves monitoring keyboard input shortcuts and answering to upper UI layer.'''
    def __init__(self):
        self.keyboard_listening_service = False

    # start/stop functions
    def start_listening_service(self):
        '''start keyboard listening service'''
        if not self.keyboard_listening_service:
            self.keyboard_listening_service = True
            # TBD: run listening function
    
    def stop_listening_service(self):
        '''stop keyboard listening service'''
        if self.keyboard_listening_service:
            self.keyboard_listening_service = False
     
    # listening main thread
    def run_keyboard_listening(self):
        '''keyboard listening main thread, should running in background'''
        while True:

            # send signals
            if keyboard.is_pressed("ctrl+r"):
                shared_queue.put({'source':'keyboard','command':'start_main_thread', 'content': ''})
            elif keyboard.is_pressed('ctrl+t'):
                shared_queue.put({'source':'keyboard','command':'stop_main_thread', 'content': ''})
    


    # clipboard related read/write functions
    def get_clipboard_content(self) -> str:
        """get content from clipboard"""
        try:
            time.sleep(0.1)  # wait for clipboard refresh
            text = pyperclip.paste()
            return text if text else None
        except Exception as e:
            print(f"Error loading flipboardcontent: {e}")
            return None

    def set_clipboard_content(self, text: str):
        '''set clipboard content from given string'''
        if text is not None:
            pyperclip.copy(text)
        else:
            raise KeyError

    
