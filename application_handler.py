from keyboard_handler import Keyboard_Handler
from business_handler import Business_Handler
from ui_handler import UI_Handler

class Application_Handler():
    '''This application class is in the highest layer.
    It controls UI, keyboard and business classes.'''
    def __init__(self, config_filepath: str) -> None:
        
        keyboard_handler = Keyboard_Handler()
        self.keyboard_handler = keyboard_handler

        ui_handler = UI_Handler(config_filepath)
        self.ui_handler = ui_handler

        business_handler = Business_Handler()
        self.business_handler = business_handler
        
        self.app_running = False

    # switch on/off the application, including the keyboard & business module
    def start_application(self) -> None:
        '''start the application, should be called when 'Ctrl+R' is pressed.'''
        if not self.app_running:
            self.app_running = True
            self.keyboard_handler.start_basic_service() # keyboard_handler's listening service should be triggered in ui_handler
            self.business_handler.start_basic_service()
            self.business_handler.start_business_service()
            self.ui_handler.start_GUI()
            self.ui_handler.run_ui() # other threads's starting signal are run function, while ui is the main thread
