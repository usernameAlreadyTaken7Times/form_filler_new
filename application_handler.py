from keyboard_handler import Keyboard_Handler
from business_handler import Business_Handler
from ui_handler import UI_Handler
from error_list import Errors

from shared_queue import broadcaster
import threading



class Application_Handler():
    '''This application class is in the highest layer.
    It controls UI, keyboard and business classes.'''
    def __init__(self, config_filepath: str): # TBD: determine where to get config file path (hard-coded or choose box from UI)
        
        keyboard_handler = Keyboard_Handler()
        self.keyboard_handler = keyboard_handler

        business_handler = Business_Handler()
        self.business_handler = business_handler
        
        ui_handler = UI_Handler()
        self.ui_handler = ui_handler
        
        self.app_running = False

    # switch on/off the application, including the keyboard & business module
    def start_application(self):
        '''start the application, should be called when 'Ctrl+R' is pressed.'''
        if not self.app_running:
            self.app_running = True


    
    def stop_application(self):
        '''stop the application, should be called when 'Ctrl+T' is pressed.'''
        if self.app_running:
            self.app_running = False
            # TODO: stop three subsystems
    