from keyboard_handler import Keyboard_Handler
from business_handler import Business_Handler
from ui_handler import UI_Handler
# from config_handler import ConfigSingleton
from error_list import Errors



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

            # TODO: UI_handler start 

    
    def stop_application(self):
        '''stop the application, should be called when 'Ctrl+T' is pressed.'''
        if self.app_running:
            self.app_running = False
            # TODO: UI_handler stop

        # main app function
    def get_ecp_value(self) -> str:
        '''return the value from data_dict of data_handler(if exist),
        should be called when 'Ctrl+C' are pressed or equivalent activity'''
        if not self.get_business_service_status():
            raise Errors.ServiceStatusError
        
        # FIXME functions name
        text = self.get_clipboard_content()
        if text in self.key_list:
            # success found in key-value pair
            self.active_key = text
            self.active_key_index = self.key_list.index(self.active_key)
            self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key)
            return self.active_value
        else:
            key = self.data_handler.find_key_from_alias(text)
            if key is not None: # success found in alias, in key-value pairs with corresponding key
                self.active_key = key
                self.active_alias = text
                self.active_key_index = self.key_list.index(self.active_key)
                self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key)
                return self.active_value
        
            # neither in key-value pairs nor in alias
            return None