import keyboard, time, pyperclip
from error_list import Errors

from shared_queue import broadcaster
import threading
from queue import Queue # only for ide's static analysis


class Keyboard_Handler(threading.Thread):
    '''This Keyboard_Handler handles keyboard-related signals.
    It involves monitoring keyboard input shortcuts and answering to upper UI layer.'''
    def __init__(self):
        self.keyboard_listening_service = False
        self.queue_keyboard: Queue = broadcaster.register('keyboard')
        

    # start/stop functions
    def start_listening_service(self):
        '''start keyboard listening service'''
        if not self.keyboard_listening_service:
            self.keyboard_listening_service = True
            threading.Thread(target=self.run_keyboard_listening, daemon=True).start()
    
    def stop_listening_service(self):
        '''stop keyboard listening service'''
        if self.keyboard_listening_service:
            self.keyboard_listening_service = False
     
    # listening main thread
    def run_keyboard_listening(self):
        '''keyboard listening main thread, should running in background'''
        while True:
            try:
                tmp_news = self.queue_keyboard.get(timeout=0.3)
            except:
                tmp_news = None

            # send signals
            if keyboard.is_pressed("ctrl+r"):
                self.send_message('start_main_thread', '')
            elif keyboard.is_pressed('ctrl+t'):
                self.send_message('stop_main_thread', '')
            
            elif keyboard.is_pressed('ctrl+c'): # copy shortcut, 
                tmp_text = self.get_clipboard_content()
                self.send_message('get_ecp_value', tmp_text)
    

            # mark queue task as done, as long as tmp_news is not None
            if isinstance(tmp_news, Queue):
                tmp_news.task_done()


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

    
    # comm function
    def send_message(self, command: str, content: str):
        '''send a message from keyboard subfunction to broadcast queue'''
        broadcaster.broadcast({'source': 'keyboard', 'command': command, 'content': content})