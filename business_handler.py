from data_handler import Data_Handler
from error_list import Errors

import threading
from shared_queue import broadcaster
from queue import Queue



class Business_Handler(threading.Thread):
    '''This Business_Handler handles the stored data in data_handler corresponsly,
    and answers to upper App layer.'''
    def __init__(self):
        self.basic_service_running = False # basic service means the main program
        self.business_service_running = False # business service means the extended copy/paste service

        data_handler = Data_Handler()
        self.data_handler = data_handler

        self.character_list = []
        self.active_character_index = 0
        self.active_character = ''

        self.key_list = []
        self.active_key_index = 0
        self.active_key = ''
        self.active_value = ''
        self.active_alias = ''

        self.queue_business: Queue = broadcaster.register('business')


    # start/stop services or init functions
    def start_basic_service(self) -> None:
        if not self.basic_service_running:
            self.basic_service_running = True
        else:
            raise Errors.ServiceStatusError('wrong business service status')
    
    def stop_basic_service(self) -> None:
        if self.basic_service_running:
            self.basic_service_running = False
        else:
            raise Errors.ServiceStatusError('wrong business service status')
    
    def start_business_service(self) -> None:
        '''This function starts the business service (the extended copy/paste service).
        It should only be called when the basic service is on.'''
        if self.get_basic_service_status() and not self.get_business_service_status():
            self.business_service_running = True

            self.character_list = self.data_handler.get_character_list() # character list init
            self.active_character = self.character_list[self.active_character_index] # default character as the first one

            self.key_list = self.data_handler.get_key_list() # get default key list
            self.active_key = self.key_list[self.active_key_index] # default key as the first one
            self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key) # upudate active value
        
            threading.Thread(target=self.run_business, daemon=True).start() # main thread start

        else:
            raise Errors.ServiceStatusError('there is problem with service status')
        
    def stop_business_service(self) -> None:
        '''This function stops the business service (the extended copy/paste service).
        It should only be called when the basic service is on.'''
        if self.get_basic_service_status() and self.get_business_service_status():
            self.business_service_running = False

            self.character_list = [] # clean up character list
            self.active_character = '' # clean up character memory
            self.active_character_index = 0 # reset

            self.key_list = []
            self.active_key_index = 0
            self.active_key = ''
            self.active_value = ''
            self.active_alias = '' # reset
        else:
            raise Errors.ServiceStatusError('there is problem with service status')


    # business main thread
    def run_business(self):
        '''business main thread, should running in background'''
        while True:

            try:
                tmp_news = self.queue_business.get(timeout=0.3)
                self.queue_business.task_done()
                print(f'[business]: {tmp_news['command']} from {tmp_news['source']}\n')
                pass
            except:
                tmp_news = None


            # receive signals
            if tmp_news and tmp_news['source'] == 'ui' and tmp_news['command'] == 'get_dicts':
                self.send_dicts()
            elif tmp_news and tmp_news['source'] == 'keyboard' and tmp_news['command'] == 'get_default_parameter':
                self.send_default_parameter()
            
            elif tmp_news and tmp_news['source'] == 'ui' and tmp_news['command'] == 'set_dicts':
                self.data_handler.data_dict, self.data_handler.key_dict = tmp_news['content']

            elif tmp_news and tmp_news['source'] == 'ui' and tmp_news['command'] == 'set_data_dict':
                self.data_handler.data_dict = tmp_news['content']
            
            elif tmp_news and tmp_news['source'] == 'ui' and tmp_news['command'] == 'set_key_dict':
                self.data_handler.key_dict = tmp_news['content']
            
            elif tmp_news and tmp_news['command'] == 'get_ecp_value':
                tmp_text, character = tmp_news['content']
                tmp_return_value, tmp_return_alias= self.get_ecp_value(tmp_text, character)
                if tmp_return_value:
                    self.send_message('info_ecp_value', (tmp_return_value, tmp_return_alias))
                else: # return value is '', means no key/alias is match the input
                    self.send_message('no_info_value_found', '')
            
            elif tmp_news and tmp_news['command'] == 'stop_service':
                self.data_handler.write_data_xlsx()
                self.stop_business_service()
                self.stop_basic_service()
                break





    # check service status functions
    def get_basic_service_status(self) -> bool:
        '''return if the basic service is running'''
        return self.basic_service_running
    
    def get_business_service_status(self) -> bool:
        '''return if the business service is running,
        noted: business service should only run under basic service running'''
        return self.business_service_running and self.basic_service_running


    # ui navigate functions
    def change_active_character_keyboard(self, direction: int) -> None:
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

    def change_active_character_select_box(self, index: int) -> None:
        '''This function can be used to change active character quickly.
        it is often be called by a select box from ui_handler.'''
        if index not in range(len(self.character_list)):
            raise KeyError
        self.active_character_index = index # overwrite the character index
        self.active_character = self.character_list[self.active_character_index] # update character

    def change_active_key_value_pair_keyboard(self, direction: int) -> None:
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
            self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key) # update value
        else: # direction = -1
            self.active_key_index -= 1
            if self.active_key_index <= -1: # same as above
                self.active_key_index = len(self.key_list) - 1
            self.active_key = self.key_list[self.active_key_index] # update key
            self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key) # update value

    def change_active_key_value_pair_select_box(self, index: int) -> None:
        '''This function can be used to change active key-value pair quickly.
        it is often be called by a select box from ui_handler.'''
        if index not in range(len(self.key_list)):
            raise KeyError
        self.active_key_index = index # overwrite the character index
        self.active_key = self.key_list[self.active_key_index] # update key
        self.active_value = self.data_handler.get_value_from_key(self.active_character, self.active_key) # update value


    # key/value/alias modification functions
    def add_alias_to_existing_key_value_pair(self, alias: str, key: str) -> None:
        '''This function adds an alias to the existing key-value pair for the current character
        (Other characters also share such alias). '''
        self.data_handler.add_alias_for_existing_key(key, alias)

    def del_alias_to_existing_key_value_pair(self, alias: str, key: str) -> None:
        '''This function deletes an alias to the existing key-value pair for the current character
        (Other characters also share such alias). '''
        self.data_handler.del_alias_for_existing_key(key, alias)

    def add_empty_key_value_pair_for_all_characters(self, key: str) -> None:
        '''add an empty value-pair for all characters.'''
        self.data_handler.add_empty_key_value_pair(self.active_character, key) # write new key-value pair in data_handler
        self.key_list = self.data_handler.get_key_list() # update key list
        self.active_key_index = self.key_list.index(self.active_key) # update active key index

    def set_key_value_pair_for_active_character(self, character: str, key: str, value: str) -> None:
        '''set value based on the given character and key'''
        self.data_handler.set_value_from_key_value_pair(character, key, value)

    def del_key_value_pair_for_all_characters(self, key: str) -> None:
        '''delete the given key-value pair for all characters'''
        for character in self.character_list:
            self.data_handler.del_key_value_pair(character, key)

        self.key_list = self.data_handler.get_key_list() # update key list
        if self.active_key == key: # if the deleted key is excatly the active one
            self.active_key = self.key_list[0] # then select the first key as active one
            self.active_key_index = self.key_list.index(self.active_key) # rebuild index
        else:
            self.active_key_index = self.key_list.index(self.active_key) # update active key index
        
    def add_character(self, new_character: str) -> None:
        '''adds a new character to the database, and set all default values as 'None'.'''
        self.data_handler.add_empty_person(new_character)
        self.character_list = self.data_handler.get_character_list() # update character list
        self.active_character_index = self.character_list.index(self.active_character) # update active character index
    
    def del_character(self, del_character: str) -> None:
        '''deletes a character from the database'''
        self.data_handler.del_person(del_character)
        self.character_list = self.data_handler.get_character_list() # update character list

        if self.active_character == del_character: # if the deleted character is excatly the active one
            self.active_character = self.character_list[0] # then select the first character as active one
            self.active_character_index = self.character_list.index(self.active_character) # rebuild index
        else:
            self.active_character_index = self.character_list.index(self.active_character) # update active character index


    # comm functions
    def send_dicts(self) -> None:
        '''send data_dict and key_dict to the queue'''
        self.send_message('send_dicts', (self.data_handler.data_dict, self.data_handler.key_dict))

    def send_default_parameter(self) -> None:
        '''send the first character and key for keyboard's self_active_character when init'''
        self.send_message('send_default_parameter', (list(self.data_handler.data_dict.keys())[0], list(self.data_handler.key_dict.keys())[0]))

    def send_message(self, command: str, content: str) -> None:
        '''send a message from business subfunction to broadcast queue'''
        broadcaster.broadcast({'source': 'business', 'command': command, 'content': content})



    # get key value function
    def get_ecp_value(self, text: str, character: str) -> str:
        '''return the value from data_dict of data_handler(if exist),
        should be called when 'Ctrl+C' are pressed or equivalent activity'''
        if not self.get_business_service_status():
            raise Errors.ServiceStatusError
        
        if text in self.key_list: # success found in key-value pair
            self.active_key = text
            self.active_key_index = self.key_list.index(self.active_key)
            self.active_value = self.data_handler.get_value_from_key(character, self.active_key)
            return self.active_value, ''
        else:
            key = self.data_handler.find_key_from_alias(text)
            if key is not None: # success found in alias, in key-value pairs with corresponding key
                self.active_key = key
                self.active_alias = text
                self.active_key_index = self.key_list.index(self.active_key)
                self.active_value = self.data_handler.get_value_from_key(character, self.active_key)
                return self.active_value, key
        
            # neither in key-value pairs nor in alias
            return None, ''
        

