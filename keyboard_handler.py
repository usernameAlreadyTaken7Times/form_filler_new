import keyboard, time, pyperclip


class Keyboard_Handler():
    '''This Application_Handler handles keyboard-related works.
    It involves the calling for functions from business_handler layer when detect different shortcuts.'''
    def __init__(self):
        pass
    

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

    
    
