import keyboard, pyperclip, time
from data_handler import Data_Handler

def get_datapath():
    '''tem function, should be deleted after test.'''
    # TODO: this function should be deleted after test
    return r'C:\Users\86781\VS_Code_Project\form_filler_new\assets\xlsx_database.xlsx'


class ServiceStatusError(Exception):
    '''This Error means there is problem with service status.'''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class KeyNotFoundError(Exception):
    '''This Error means the given key does not match any result.'''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)




class Business_Handler:
    '''This Business_Handler handles the stored data in data_handler corresponsly.'''
    def __init__(self):
        self.basic_service_running = False # basic service means the main program
        self.working_service_running = False # working service means the extended copy/paste service

        # TODO: the datapath should be returned from GUI layer and should be obtained from .json file.
        data_handler = Data_Handler(get_datapath()) 
        self.data_handler = data_handler

        self.character_list = []
        self.active_character_index = 0
        self.active_character = ''

        self.key_list = []
        self.active_key_index = 0
        self.active_key = ''
        self.active_value = ''
        self.active_alias = ''


    # start/stop services or init functions
    def start_basic_service(self):
        self.basic_service_running = True
    
    def stop_basic_service(self):
        self.basic_service_running = False
    
    def init_listening(self): 
        '''This function aims to listen to the keyboard shortcut input at the very beginning
          to tell if the service is started or not.'''
        if keyboard.is_pressed('ctrl+r') and self.basic_service_running is False:
            self.start_basic_service()
        elif keyboard.is_pressed('ctrl+t') and self.basic_service_running is True:
            self.stop_basic_service()
    
    def start_working_service(self):
        '''This function starts the working service (the extended copy/paste service).
        It should only be called when the basic service is on.'''
        if self.get_basic_service_status() and not self.get_working_service_status():
            self.working_service_running = True

            self.character_list = self.data_handler.get_character_list() # character list init
            self.active_character = self.character_list[self.active_character_index] # default character as the first one

            self.key_list = self.data_handler.get_key_list() # get default key list
            self.active_key = self.key_list[self.active_key_index] # default key as the first one
            self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key) # upudate active value
        else:
            raise ServiceStatusError('there is problem with service status')
        
    def stop_working_service(self):
        '''This function stops the working service (the extended copy/paste service).
        It should only be called when the basic service is on.'''
        if self.get_basic_service_status() and self.get_working_service_status():
            self.working_service_running = False

            self.character_list = [] # clean up character list
            self.active_character = '' # clean up character memory
            self.active_character_index = 0 # reset

            self.key_list = []
            self.active_key_index = 0
            self.active_key = ''
            self.active_value = ''
            self.active_alias = '' # reset
        else:
            raise ServiceStatusError('there is problem with service status')


    # check service status functions
    def get_basic_service_status(self) -> bool:
        '''return if the basic service is running'''
        return self.basic_service_running
    
    def get_working_service_status(self) -> bool:
        '''return if the working service is running,
        noted: working service should only run under basic service running'''
        return self.working_service_running and self.basic_service_running


    # ui navigate functions
    def change_active_character_keyboard(self, direction: int):
        '''This function can be used to change active character once a time based on the input direction vector.
        It should be called when UP/DOWN direction arrow key is selected.\n
        direction=1 -> forward; direction=-1 -> backward'''
        if direction not in [-1, 1]:
            raise KeyError
        if direction == 1:
            self.active_character_index += 1
            if self.active_character_index >= len(self.character_list): # actually, only change one time, '=' alone should be enough
                self.active_character_index = 0
            self.active_character = self.character_list[self.active_character_index] # update character
        else: # direction = -1
            self.active_character_index -= 1
            if self.active_character_index <= -1: # same as above
                self.active_character_index = len(self.character_list) - 1
            self.active_character = self.character_list[self.active_character_index] # update character

    def change_active_character_select_box(self, index: int):
        '''This function can be used to change active character quickly.
        it is often be called by a select box from ui_handler.'''
        if index not in range(len(self.character_list)):
            raise KeyError
        self.active_character_index = index # overwrite the character index
        self.active_character = self.character_list[self.active_character_index] # update character

    def change_active_key_value_pair_keyboard(self, direction: int):
        '''This function can be used to change active key-value pair once a time based on the input direction vector.
        It should be called when RIGHT/LEFT direction arrow key is selected.\n 
        direction=1 -> forward(right); direction=-1 -> backward(left)'''
        if direction not in [-1, 1]:
            raise KeyError
        if direction == 1:
            self.active_key_index += 1
            if self.active_key_index >= len(self.key_list): # actually, only change one time, '=' alone should be enough
                self.active_key_index = 0
            self.active_key = self.key_list[self.active_key_index] # update key
            self.active_value = self.data_handler.get_value_from_key(self.active_key) # update value
        else: # direction = -1
            self.active_key_index -= 1
            if self.active_key_index <= -1: # same as above
                self.active_key_index = len(self.key_list) - 1
            self.active_key = self.key_list[self.active_key_index] # update key
            self.active_value = self.data_handler.get_value_from_key(self.active_key) # update value

    def change_active_key_value_pair_select_box(self, index: int):
        '''This function can be used to change active key-value pair quickly.
        it is often be called by a select box from ui_handler.'''
        if index not in range(len(self.key_list)):
            raise KeyError
        self.active_key_index = index # overwrite the character index
        self.active_key = self.key_list[self.active_key_index] # update key
        self.active_value = self.data_handler.get_value_from_key(self.active_key) # update value


    # key/value/alias modification functions
    def add_alias_to_existing_key_value_pair(self, alias: str, key: str):
        '''This function adds an alias to the existing key-value pair for the current character
        (Other characters also share such alias). '''
        self.data_handler.add_alias_for_existing_key(key, alias)

    def del_alias_to_existing_key_value_pair(self, alias: str, key: str):
        '''This function deletes an alias to the existing key-value pair for the current character
        (Other characters also share such alias). '''
        self.data_handler.del_alias_for_existing_key(key, alias)

    def add_empty_key_value_pair_for_all_characters(self, key: str):
        '''add an empty value-pair for all characters.'''
        self.data_handler.add_empty_key_value_pair(self.active_character, key) # write new key-value pair in data_handler
        self.key_list = self.data_handler.get_key_list() # update key list
        self.active_key_index = self.key_list.index(self.active_key) # update active key index

    def set_key_value_pair_for_active_character(self, character: str, key: str, value: str):
        '''set value based on the given character and key'''
        self.data_handler.set_value_from_key_value_pair(character, key, value)

    def del_key_value_pair_for_all_characters(self, key: str):
        '''delete the given key-value pair for all characters'''
        for character in self.character_list:
            self.data_handler.del_key_value_pair(character, key)

        self.key_list = self.data_handler.get_key_list() # update key list
        if self.active_key == key: # if the deleted key is excatly the active one
            self.active_key = self.key_list[0] # then select the first key as active one
            self.active_key_index = self.key_list.index(self.active_key) # rebuild index
        else:
            self.active_key_index = self.key_list.index(self.active_key) # update active key index
        
    def add_character(self, new_character: str):
        '''adds a new character to the database, and set all default values as 'None'.'''
        self.data_handler.add_empty_person(new_character)
        self.character_list = self.data_handler.get_character_list() # update character list
        self.active_character_index = self.character_list.index(self.active_character) # update active character index
    
    def del_character(self, del_character: str):
        '''deletes a character from the database'''
        self.data_handler.del_person(del_character)
        self.character_list = self.data_handler.get_character_list() # update character list

        if self.active_character == del_character: # if the deleted character is excatly the active one
            self.active_character = self.character_list[0] # then select the first character as active one
            self.active_character_index = self.character_list.index(self.active_character) # rebuild index
        else:
            self.active_character_index = self.character_list.index(self.active_character) # update active character index


    # working service component functions
    def get_ecp_value(self) -> str:
        '''return the value from data_dict of data_handler(if exist),
        should be called when 'Ctrl+C' are pressed or equivalent activity'''
        if not self.get_working_service_status:
            raise ServiceStatusError
        
        text = self.get_clipboard_content()
        if text in self.key_list:
            # success found in key-value pair
            self.active_key = text
            self.active_key_index = self.key_list.index(self.active_key)
            self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key)
            return self.active_value
        else:
            key = self.data_handler.find_key_from_alias(text)
            if key is not None: # success found in alias, search in key-value pairs with corresponding key
                self.active_key = key
                self.active_alias = text
                self.active_key_index = self.key_list.index(self.active_key)
                self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key)
                return self.active_value
        
            # neither in key-value pairs nor in alias
            return None



# import sys
# print(sys.path)

# kh = Keyboard_Handler('a')
# kh.start_listening_init()
# pass