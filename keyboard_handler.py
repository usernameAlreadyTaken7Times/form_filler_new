from typing import Tuple
import keyboard, time, pyperclip
from error_list import Errors

from shared_queue import broadcaster
import threading
from queue import Queue # only for ide's static analysis
from typing import Optional, Any


class Keyboard_Handler(threading.Thread):
    '''This Keyboard_Handler handles keyboard-related signals.
    It involves monitoring keyboard input shortcuts and answering to upper UI layer.'''
    def __init__(self):
        self.basic_service = False
        self.keyboard_listening_service = False
        self.queue_keyboard: Queue = broadcaster.register('keyboard')
        self.active_character: str = ''
        self.active_key: str = ''
        

    # start/stop functions
    def start_basic_service(self) -> None:
        '''start keyboard_handler basic service'''
        if not self.basic_service:
            self.basic_service = True
            threading.Thread(target=self.run_keyboard, daemon=True).start()
        else:
            raise Errors.ServiceStatusError('keyboard basic service already started')
    
    def stop_basic_service(self) -> None:
        '''stop keyboard_handler basic service'''
        if self.basic_service:
            self.basic_service = False
        else:
            raise Errors.ServiceStatusError('keyboard basic service already stopped')


    def start_listening_service(self) -> None:
        '''start keyboard listening service'''
        if not self.keyboard_listening_service and self.basic_service:
            self.keyboard_listening_service = True

            self.active_character, self.active_key = self.get_default_parameter()
            
        else:
            raise Errors.ServiceStatusError('keyboard listening service already started')
    
    def stop_listening_service(self) -> None:
        '''stop keyboard listening service'''
        if self.keyboard_listening_service and self.basic_service:
            self.keyboard_listening_service = False
        else:
            raise Errors.ServiceStatusError('keyboard listening service already stopped')
     
    # listening main thread
    def run_keyboard(self) -> None:
        '''keyboard listening main thread, should running in background'''

        # define shortcuts
        keyboard.add_hotkey("ctrl+r",
                             lambda: self.send_message('start_main_thread', ''), suppress=False)
        keyboard.add_hotkey("ctrl+t",
                             lambda: self.send_message('stop_main_thread', ''), suppress=False)
        keyboard.add_hotkey("ctrl+c",
                             lambda: self.get_ecp_value() if self.keyboard_listening_service else None, suppress=False)
        keyboard.add_hotkey("up",
                             lambda: self.switch_character(1) if self.keyboard_listening_service else None, suppress=False)
        keyboard.add_hotkey("down",
                             lambda: self.switch_character(-1) if self.keyboard_listening_service else None, suppress=False)
        keyboard.add_hotkey("left",
                             lambda: self.switch_key(-1) if self.keyboard_listening_service else None, suppress=False)
        keyboard.add_hotkey("right",
                             lambda: self.switch_key(1) if self.keyboard_listening_service else None, suppress=False)

        while True:
            try:
                tmp_news = self.queue_keyboard.get(timeout=0.3)
                self.queue_keyboard.task_done() # just assume the task done in this loop
                print(f'[keyboard]: {tmp_news['command']} from {tmp_news['source']}\n')
                pass
            except:
                tmp_news = None

            if tmp_news and tmp_news['source'] == 'ui' and tmp_news['command'] == 'start_keyboard_listening':
                self.start_listening_service()
            elif tmp_news and tmp_news['source'] == 'ui' and tmp_news['command'] == 'stop_keyboard_listening':
                self.stop_listening_service()
            
            elif tmp_news and tmp_news['command'] == 'info_ecp_value':
                self.set_clipboard_content(tmp_news['content'][0])

            elif tmp_news and tmp_news['command'] == 'info_active_character':
                self.active_character = tmp_news['content']
            elif tmp_news and tmp_news['command'] == 'info_active_key':
                self.active_key = tmp_news['content']
            elif tmp_news and tmp_news['command'] == 'info_update_value':
                self.set_clipboard_content(tmp_news['content'])
            elif tmp_news and tmp_news['command'] == 'stop_service':
                self.stop_basic_service()
                break
            
    # thread init related function
    def get_default_parameter(self) -> Tuple[str, str]:
        '''create a tmp receive channel for default character when init'''
        self.send_message('get_default_parameter', '')
        while True:
            try:
                tmp_news = self.queue_keyboard.get(timeout=0.3)
                print(f'[keyboard_init]: {tmp_news['command']} from {tmp_news['source']}\n')
            except:
                tmp_news = None
            
            if tmp_news and tmp_news['source'] == 'business' and tmp_news['command'] == 'send_default_parameter':
                default_character, default_key = tmp_news['content']
                break
        
        return default_character, default_key


    # clipboard related functions
    def get_clipboard_content(self) -> Optional[str]:
        """get content from clipboard"""
        try:
            time.sleep(0.1)  # wait for clipboard refresh
            text = pyperclip.paste()
            return text if text else None
        except Exception as e:
            print(f"Error loading flipboardcontent: {e}")
            return None

    def set_clipboard_content(self, text: str) -> None:
        '''set clipboard content from given string'''
        if text is not None:
            pyperclip.copy(text)
        else:
            raise KeyError


    # keyboard-direction related functions
    def switch_key(self, direction: int) -> None:
        '''use this function to send cooresponding key switch message'''
        if direction not in [-1, 1]:
            raise Errors.KeyNotFoundError('wrong direction in key selection')
        elif direction == 1:
            self.send_message('switch_key_right', '')
        else:
            self.send_message('switch_key_left', '')

    def switch_character(self, direction: int) -> None:
        '''use this function to send cooresponding character switch message'''
        if direction not in [-1, 1]:
            raise Errors.KeyNotFoundError('wrong direction in character selection')
        elif direction == 1:
            self.send_message('switch_character_up', '')
        else:
            self.send_message('switch_character_down', '')


    # ecp related signals/functions
    def get_ecp_content_signal(self, text: str, character: str) -> None: 
        '''send signal to queue for ecp content'''
        self.send_message('get_ecp_value', (text, character))

    def get_ecp_value(self) -> None:
        '''get ecp value from queue'''
        copy_text = self.get_clipboard_content()
        if copy_text:
            self.get_ecp_content_signal(copy_text, self.active_character)

    
    # comm function
    def send_message(self, command: str, content: Any) -> None:
        '''send a message from keyboard subfunction to broadcast queue'''
        broadcaster.broadcast({'source': 'keyboard', 'command': command, 'content': content})
        