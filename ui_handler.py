import PySimpleGUI as sg
from error_list import Errors
from config_handler import ConfigSingleton
import webbrowser

import threading
from shared_queue import broadcaster

import time
import copy
# from deepdiff import DeepDiff
import queue

from queue import Queue # only for ide's static analysis


class UI_Handler(threading.Thread):
    '''This UI_Handler deals with interacting with Users directly, including receiving graphic rendering commands.
    It should be in the same layer as keyboard & business module.
    Meantime, the config file is also loaded here, from ui interface. It can then be used in other modules.
    '''
    def __init__(self, config_filepath: str): 
        
        # vairables
        ConfigSingleton.initialize(config_filepath) # init config file and enable using anywhere in the whole program
        self.listening_service_running = False
        self.window_running = False
        
        self.active_character_index: int = 0
        self.active_character: str = ''
        self.active_key_index: int = 0
        self.active_key: str = ''
        self.active_alias_index: int = 0
        self.active_alias: str = ''


        # define main GUI window
        self.main_window_layout = [
            [sg.Text("Form_Filler v0.3", font=("Arial", 12, "bold"), text_color="white")],
            [sg.Text("extended copy/paste service", font=("Arial", 9, "italic"), text_color="white")],
            [sg.HorizontalSeparator()],
            
            [sg.Text("Run/Terminate", font=("Arial", 10, "bold", "underline"), text_color="white")],
            [sg.Button("Run", size=(8, 1), font=("Arial", 8),
                        key="KEY_run", tooltip=" start keyboard listening ", disabled=False), 
              sg.Button("Terminate", size=(8, 1), font=("Arial", 8),
                         key="KEY_terminate", tooltip=" terminate keyboard listening ", disabled=True)],
            [sg.Text("or Ctrl+R / Ctrl+T", font=("Arial", 8, "italic"), text_color="white")],
            [sg.HorizontalSeparator()],

            [sg.Text("Modifier", font=("Arial", 10, "bold", "underline"), text_color="white")],
            [sg.Button("Data", size=(8, 1), font=("Arial", 8),
                        key="KEY_main_data_modifier", tooltip=" view and edit data-key-value dictionary ", disabled=True),
             sg.Button("Alias", size=(8, 1), font=("Arial", 8),
                        key="KEY_main_alias_modifier", tooltip=" view and edit key-alias dictionary ", disabled=True)],
            [sg.HorizontalSeparator()], 

            [sg.Text("Clipboard cache:", font=("Arial", 10, "bold", "underline"), text_color="white")],
            [sg.Text("character:", font=("Arial", 9, "italic", "underline"),
                     tooltip=" use up/down arrow key to switch ", text_color="white")],
            [sg.Text(" --- ", key="TEXT_active_character",
                      tooltip=" the character's name ",
                      font=("Arial", 10), text_color="gold", enable_events=True)],
            [sg.Text("key:", font=("Arial", 9, "italic", "underline"),
                     tooltip=" use left/right arrow key to switch ", text_color="white")],
            [sg.Text(" --- ", key="TEXT_active_key",
                      tooltip=" the character's attribute ",
                      font=("Arial", 10), text_color="gold", enable_events=True)],
            [sg.Text("alias (if exist):", font=("Arial", 9, "italic", "underline"), text_color="white")],
            [sg.Text(" --- ", key="TEXT_active_alias",
                      tooltip=" attribute's alias, only available when text field matches ",
                      font=("Arial", 10), text_color="gold", enable_events=True)],
            [sg.Text("value:", font=("Arial", 9, "italic", "underline"), text_color="white")],
            [sg.Text(" --- ", key="TEXT_active_value",
                      tooltip=" the attribute's value ",
                      font=("Arial", 10), text_color="gold", enable_events=True)],
            [sg.HorizontalSeparator()],

            [sg.Text("Related", font=("Arial", 10, "bold", "underline"), text_color="white")],
            [sg.Button("About", size=(8, 1), font=("Arial", 8),
                        key="KEY_project_page", tooltip=" open project on Github page ", disabled=False),
             sg.Button("Bug", size=(8, 1), font=("Arial", 8),
                        key="KEY_bug_report", tooltip=" open Github page and report a bug ", disabled=False)]
        ]

        # window init setting
        self.queue_ui: Queue = broadcaster.register('ui')

        self.window = sg.Window("FF", self.main_window_layout, resizable=True, keep_on_top=True, finalize=True)

    # start/stop functions
    def start_GUI(self) -> None:
        '''starts the GUI program and show the window'''
        if not self.window_running:
            self.window_running = True
            # load replica from data_handler during first time loading GUI interface
            self.data_dict: dict[str, dict]
            self.key_dict: dict[str, list]
            self.data_dict, self.key_dict = self.get_dicts_content_from_data_handler()
            self.window.refresh()
        else:
            raise Errors.ServiceStatusError('GUI status error(already running)')
        
    def stop_GUI(self) -> None:
        '''stops the GUI program and hide the window'''
        if self.window_running:
            self.window_running = False
            self.set_dicts_content_to_data_handler() # write the dicts back to data_handler
            self.send_message('stop_service', '')
            self.window.close()
        else:
            raise Errors.ServiceStatusError('GUI status error(already closed)')
    
    def start_listening_service(self) -> None:
        '''starts the keyboard listening service, should be triggered when run/ctrl+r is pressed'''
        if not self.listening_service_running:
            self.listening_service_running = True
            self.window['KEY_run'].update(disabled=True) # type: ignore
            self.window['KEY_terminate'].update(disabled=False) # type: ignore
            self.window['KEY_main_data_modifier'].update(disabled=False) # type: ignore
            self.window['KEY_main_alias_modifier'].update(disabled=False) # type: ignore

            # setup lists to store characters and keys,
            # they should be updated from self.data_dict and self.key_dict
            # because they may be updated from modifier, and thus, when
            # change listening_service status these modifications can be loaded
            self.character_list = list(self.data_dict.keys())
            self.key_list = list(self.key_dict.keys())
            self.active_character_index = 0
            self.active_character = self.character_list[self.active_character_index]
            self.active_key_index = 0
            self.active_key = self.key_list[self.active_key_index]
            self.active_alias_index = 0
            self.active_alias = '' # alias should stay with '' unless it's found

            self.window['TEXT_active_character'].update(value=self.active_character) # type: ignore
            self.window['TEXT_active_key'].update(value=self.active_key) # type: ignore
            self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key]) # type: ignore

            # start keyboard listening from keyboard_handler level through news
            self.send_message('start_keyboard_listening', '')

    def stop_listening_service(self) -> None:
        '''stops the keyboard listening sevice, should be triggered when terminate/ctrl+t is pressed'''
        if self.listening_service_running:
            self.listening_service_running = False
            self.window['KEY_run'].update(disabled=False) # type: ignore
            self.window['KEY_terminate'].update(disabled=True) # type: ignore
            self.window['KEY_main_data_modifier'].update(disabled=True) # type: ignore
            self.window['KEY_main_alias_modifier'].update(disabled=True) # type: ignore

            self.window['TEXT_active_character'].update(value=" --- ") # type: ignore
            self.window['TEXT_active_key'].update(value=" --- ") # type: ignore
            self.window['TEXT_active_value'].update(value=" --- ") # type: ignore
            self.window['TEXT_active_alias'].update(value=" --- ") # type: ignore

            # stop keyboard listening from keyboard_handler level through news
            self.send_message('stop_keyboard_listening', '')


    # ui main thread
    def run_ui(self) -> None:
        '''ui main thread, controls the ui logic.'''
        
        while True:
            event, values = self.window.read(timeout=100)
            
            try:
                tmp_news = self.poll_messages()
                if tmp_news:
                    print(f'[ui]: {tmp_news['command']} from {tmp_news['source']}\n')
                    pass
            except:
                tmp_news = None

            # send signals


            # receive signals
            if tmp_news and tmp_news['command'] == 'info_ecp_value':
                self.window['TEXT_active_key'].update(tmp_news['content'][1]) # type: ignore
                if len(tmp_news['content'][0]) >= 11:
                    self.window['TEXT_active_value'].update(tmp_news['content'][0][:10]+'…') # type: ignore
                else:
                    self.window['TEXT_active_value'].update(tmp_news['content'][0]) # type: ignore
                if len(tmp_news['content']) == 3: # then has an alias
                    self.window['TEXT_active_alias'].update(tmp_news['content'][2]) # type: ignore
                else:
                    self.window['TEXT_active_alias'].update(value=' --- ') # type: ignore
            elif tmp_news and tmp_news['command'] == 'no_info_value_found':
                return_response = sg.popup_yes_no("no match key or alias. create one?", keep_on_top=True)
                if return_response == 'Yes':
                    self.stop_listening_service()
                    self.popup_alias_dict_modifier()
                    self.set_data_dict_content_to_data_handler() # sync the data_dict and key_dict with updates
                    self.set_key_dict_content_to_data_handler() # it's possible when key-alias changes toghther
                    self.start_listening_service() # keyboard_listening_service back online
                elif return_response == 'No' or return_response is None:
                    pass

            elif tmp_news and tmp_news['command'] == 'get_active_character':
                self.send_message('info_active_character', self.active_character)

            elif tmp_news and tmp_news['command'] == 'switch_key_right':
                self.active_key_index += 1
                if self.active_key_index == len(self.key_list):
                    self.active_key_index = 0
                self.active_key = self.key_list[self.active_key_index]
                self.window['TEXT_active_key'].update(value=self.active_key) # type: ignore
                if len(self.data_dict[self.active_character][self.active_key]) >= 11:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key][:10]+'…') # type: ignore
                else:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key]) # type: ignore
                self.window['TEXT_active_alias'].update(value=' --- ') # type: ignore
                self.update_key()
                self.update_value(self.data_dict[self.active_character][self.active_key])
            elif tmp_news and tmp_news['command'] == 'switch_key_left':
                self.active_key_index -= 1
                if self.active_key_index == -1:
                    self.active_key_index = len(self.key_list)-1
                self.active_key = self.key_list[self.active_key_index]
                self.window['TEXT_active_key'].update(value=self.active_key) # type: ignore
                if len(self.data_dict[self.active_character][self.active_key]) >= 11:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key][:10]+'…') # type: ignore
                else:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key]) # type: ignore
                self.window['TEXT_active_alias'].update(value=' --- ') # type: ignore
                self.update_key()
                self.update_value(self.data_dict[self.active_character][self.active_key])
            elif tmp_news and tmp_news['command'] == 'switch_character_down': # why dows 'down' mean next instead of last? 
                self.active_character_index += 1
                if self.active_character_index == len(self.character_list):
                    self.active_character_index = 0
                self.active_character = self.character_list[self.active_character_index]
                self.window['TEXT_active_character'].update(value=self.active_character) # type: ignore
                if len(self.data_dict[self.active_character][self.active_key]) >= 11:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key][:10]+'…') # type: ignore
                else:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key]) # type: ignore
                self.window['TEXT_active_alias'].update(value=' --- ') # type: ignore
                self.update_character()
                self.update_value(self.data_dict[self.active_character][self.active_key])
            elif tmp_news and tmp_news['command'] == 'switch_character_up':
                self.active_character_index -= 1
                if self.active_character_index == -1:
                    self.active_character_index = len(self.character_list)-1
                self.active_character = self.character_list[self.active_character_index]
                self.window['TEXT_active_character'].update(value=self.active_character) # type: ignore
                if len(self.data_dict[self.active_character][self.active_key]) >= 11:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key][:10]+'…') # type: ignore
                else:
                    self.window['TEXT_active_value'].update(self.data_dict[self.active_character][self.active_key]) # type: ignore
                self.window['TEXT_active_alias'].update(value=' --- ') # type: ignore
                self.update_character()
                self.update_value(self.data_dict[self.active_character][self.active_key])

            # confirm/load config file related
            elif event == 'KEY_main_data_modifier':
                # every time the modifier is opened, 
                # listening function should suspend to avoid affecting basic copy/paste function
                self.stop_listening_service()
                self.popup_data_dict_modifier()
                self.set_data_dict_content_to_data_handler() # sync the data_dict and key_dict with updates
                self.set_key_dict_content_to_data_handler() # it's possible when key-alias changes toghther
                self.start_listening_service() # keyboard_listening_service back online
            
            elif event == 'KEY_main_alias_modifier':
                self.stop_listening_service()
                self.popup_alias_dict_modifier()
                self.set_key_dict_content_to_data_handler() # sync
                self.start_listening_service() # keyboard_listening_service back online

            # start keyboard_listening
            elif event == 'KEY_run' or (tmp_news and tmp_news['source'] == 'keyboard' and tmp_news['command'] == 'start_main_thread'):
                if not self.listening_service_running:
                    sg.popup('keyboard_listening_startup', keep_on_top=True)
                    print('keyboard_listening_startup')
                    self.start_listening_service()
                else:
                    sg.popup('listening service already running', keep_on_top=True)
                    print('try to start again')
            

            # terminate keyboard_listening
            elif event == 'KEY_terminate' or (tmp_news and tmp_news['source'] == 'keyboard' and tmp_news['command'] == 'stop_main_thread'):
                if self.listening_service_running:
                    sg.popup('keyboard_listening_stop', keep_on_top=True)
                    # print('call stop_gui function and stop')
                    self.stop_listening_service()
                else:
                    sg.popup('listening service already terminated', keep_on_top=True)
                    print('try to terminate again')
            elif event == 'KEY_bug_report':
                webbrowser.open("https://github.com/usernameAlreadyTaken7Times/form_filler_new/issues")

            elif event == 'KEY_project_page':
                webbrowser.open("https://github.com/usernameAlreadyTaken7Times/form_filler_new")
            
            elif event == sg.WINDOW_CLOSED:
                self.listening_service_running = False
                self.stop_GUI()
                break


    # thread related functions
    def get_dicts_content_from_data_handler(self) -> tuple[dict, dict]: 
        '''use queue to request data_dict and key_dict from data_handler, should only be called by init'''
        self.send_message('get_dicts', '')
        while True:
            try:
                tmp_news = self.poll_messages()
            except:
                tmp_news = None
            
            if tmp_news and tmp_news['source'] == 'business' and tmp_news['command'] == 'send_dicts':
                # this message is from "business" handler message queue, and 'content' should be two dicts
                data_dict, key_dict = tmp_news['content'] # type: ignore
                break
        
        return data_dict, key_dict

    def set_dicts_content_to_data_handler(self) -> None:
        '''use queue to send data_dict and key_dict to data_handler, should be called every time the dicts are changed from modifier'''
        self.send_message('set_dicts', (self.data_dict, self.key_dict))


    def set_data_dict_content_to_data_handler(self) -> None:
        '''use queue to send data_dict to data_handler, should be called every time the dict changed from modifier'''
        self.send_message('set_data_dict', self.data_dict)

    def set_key_dict_content_to_data_handler(self) -> None:
        '''use queue to send key_dict to data_handler, should be called every time the dict changed from modifier'''
        self.send_message('set_key_dict', self.key_dict)



    # popup window functions
    def popup_data_dict_modifier(self) -> None:
        '''pop up a new data_dict modifier window'''

        tmp_data_dict: dict[str, dict]
        tmp_data_dict = copy.deepcopy(self.data_dict) # create a deepcopy of data_dict for in-function use
        selected_character = list(tmp_data_dict.keys())[0]
        selected_key = list(tmp_data_dict[selected_character].keys())[0]
        key = list(next(iter(tmp_data_dict.values())).keys())

        # popup data_dict modifier window layout
        popup_data_window_layout = [
            [sg.Text("characters", font=("Arial", 9), text_color="white", size=(10, 1)),
             sg.Text("keys", font=("Arial", 9), text_color="white", size=(12, 1)),
             sg.Text("values", font=("Arial", 9), text_color="white", size=(16, 1))],
            [sg.Listbox(values=list(tmp_data_dict.keys()), size=(8, 10), key="KEY_data_modifier_character", enable_events=True),
             sg.Listbox(values=key, size=(8, 10), key="KEY_data_modifier_key", enable_events=True),
             sg.Multiline("", size=(24, 10), key="KEY_data_modifier_value", enable_events=True)],
            [sg.Button("character_add", key="KEY_add_character"),
             sg.Button("character_del", key="KEY_del_character"),
             sg.Button("key_add", key="KEY_add_key"),
             sg.Button("key_del", key="KEY_del_key")],
            [sg.Button("update", key="KEY_data_modifier_update"), 
             sg.Button('exit', key='KEY_data_modifier_exit')]
         ]
        
        data_window = sg.Window('data_dict modifier', popup_data_window_layout, keep_on_top=True, finalize=True)
        data_window.force_focus()

        data_window['KEY_data_modifier_character'].update(set_to_index=[0]) # type: ignore
        data_window['KEY_data_modifier_key'].update(set_to_index=[0]) # type: ignore
        data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key]) # type: ignore

        # run loop
        while True:
            event, values = data_window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'KEY_data_modifier_exit':
                if tmp_data_dict == self.data_dict:
                    data_window.close()
                    break
                else:
                    response = sg.popup_yes_no("data not updated. continue to exit?", title='notice', keep_on_top=True)
                    if response == 'Yes' or response is None:
                        data_window.close()
                        break
            elif len(key) == 0:
                # key list is empty, can cause many problem
                sg.popup("key_list is empty, please add content to it", keep_on_top=True)

            elif event == "KEY_data_modifier_character":
                selected_character = values["KEY_data_modifier_character"][0] if values["KEY_data_modifier_character"] else None
                if selected_character:
                    data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key]) # type: ignore
            
            elif event == "KEY_data_modifier_key" and selected_character:
                selected_key = values["KEY_data_modifier_key"][0] if values["KEY_data_modifier_key"] else None
                if selected_key:
                    data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key]) # type: ignore
            
            if event == "KEY_data_modifier_value" and selected_character and selected_key:
                tmp_data_dict[selected_character][selected_key] = values["KEY_data_modifier_value"]
                data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key]) # type: ignore
            
            if event == "KEY_data_modifier_update":
            # if event == "KEY_data_modifier_update" and selected_character and selected_key: # two selected items necessary?
                # tmp_data_dict[selected_character][selected_key] = values["KEY_data_modifier_value"]
                # data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key])

                # test weather all character has value for the new added key
                is_perfect_dict = True
                for character in tmp_data_dict:
                    if '' in tmp_data_dict[character].values():
                        sg.popup('Some character\'s key has empty value, please check', keep_on_top=True)
                        is_perfect_dict = False
                        break
                if is_perfect_dict:
                    # if new key is added, then write the new key into key_dict as well
                    if self.key_dict.keys() == list(tmp_data_dict.values())[0].keys():
                        pass
                    else: # modification has been made to the keys, now the key-alias dict should be changed correspondingly
                        sg.popup('key list changed. changing key-alias dict as well.', keep_on_top=True)
                        tmp_key_dict = copy.deepcopy(self.key_dict) # cerate a operable replica dict
                        for tmp_key in self.key_dict.keys():
                            if tmp_key in list(tmp_data_dict.values())[0].keys():
                                pass
                            else:
                                del tmp_key_dict[tmp_key] # delete keys which exists in key_dict but not in tmp_data_dict
                        if set(list(tmp_data_dict.values())[0].keys()) - set(tmp_key_dict.keys()) is set():
                            pass # now these two dicts have same key
                        else: # there are still new key pairs added in tmp_data_dict
                            for i in (set(list(tmp_data_dict.values())[0].keys()) - set(tmp_key_dict.keys())):
                                tmp_key_dict[i] = [] # create new key-alias pair for each difference
                        
                        self.key_dict = tmp_key_dict # store the changes back into self.key_dict
                    
                    # then save the current dict into self.data_dict, and use queue sync to data_handler
                    self.data_dict = tmp_data_dict
                    sg.popup("data updated", keep_on_top=True)
                    

            if event == "KEY_add_character":
                new_character = sg.popup_get_text("new character:", keep_on_top=True)
                if new_character and new_character not in tmp_data_dict:
                    tmp_data_dict[new_character] = {attr: "" for attr in key}
                    data_window["KEY_data_modifier_character"].update(values=list(tmp_data_dict.keys())) # type: ignore
                    data_window["KEY_data_modifier_value"].update('') # type: ignore
            
            if event == "KEY_del_character" and selected_character:
                response = sg.popup_yes_no('delete character and all his/her keys?', keep_on_top=True)
                if response == 'Yes':
                    del tmp_data_dict[selected_character]
                    if len(tmp_data_dict) > 0:
                        selected_character = list(tmp_data_dict.keys())[0]
                        
                        data_window["KEY_data_modifier_character"].update(values=list(tmp_data_dict.keys()), # type: ignore
                                                     set_to_index=[list(tmp_data_dict.keys()).index(selected_character)])
                        # data_window["KEY_data_modifier_key"].update(values=[])
                        data_window["KEY_data_modifier_value"].update(tmp_data_dict[selected_character][selected_key]) # type: ignore
                    else:
                        sg.popup('no character left. please add a character', keep_on_top=True)
            
            elif event == "KEY_del_character" and not selected_character:
                sg.popup("please choose a character to delete", keep_on_top=True)

            if event == "KEY_add_key":
                new_key = sg.popup_get_text("new key:", keep_on_top=True)
                if new_key and new_key not in key:
                    key.append(new_key)
                    for person in tmp_data_dict:
                        tmp_data_dict[person][new_key] = ""
                    selected_key = new_key
                    data_window["KEY_data_modifier_key"].update(values=key, set_to_index=[key.index(selected_key)]) # type: ignore
                    data_window["KEY_data_modifier_value"].update('') # type: ignore

            if event == "KEY_del_key" and selected_key:
                response = sg.popup_yes_no('delete this key for all characters?', keep_on_top=True)
                if response == 'Yes':
                    key.remove(selected_key)
                    for person in tmp_data_dict:
                        del tmp_data_dict[person][selected_key]
                    if len(key) == 0:
                        selected_key = None
                        data_window["KEY_data_modifier_key"].update(values=key) # type: ignore
                        data_window["KEY_data_modifier_value"].update(value="") # type: ignore
                    else:
                        selected_key = key[0]
                        data_window["KEY_data_modifier_key"].update(values=key, set_to_index=[key.index(selected_key)]) # type: ignore
                        data_window["KEY_data_modifier_value"].update(value=tmp_data_dict[selected_character][selected_key]) # type: ignore

            elif event == "KEY_del_key" and not selected_key:
                sg.popup("please choose a key to delete", keep_on_top=True)

    def popup_alias_dict_modifier(self) -> None:
        '''pop up a new key_dict modifier window'''

        tmp_key_dict: dict[str, list]
        tmp_key_dict = copy.deepcopy(self.key_dict) # create a copy of key_dict for in-function use
        selected_key: str = list(tmp_key_dict.keys())[0]
        selected_alias = (tmp_key_dict[selected_key][0] if len(tmp_key_dict[selected_key])>0 else None)

        # popup key_dict modifier window layout
        popup_key_window_layout = [
            [sg.Text("keys", font=("Arial", 9), text_color="white", size=(10, 1)),
             sg.Text("alias", font=("Arial", 9), text_color="white", size=(10, 1))],
            [sg.Listbox(values=list(tmp_key_dict.keys()), size=(10, 10), key="KEY_alias_modifier_key", enable_events=True), 
             sg.Listbox(values=tmp_key_dict[list(tmp_key_dict.keys())[0]], size=(10, 10), key="KEY_alias_modifier_alias", enable_events=True)],
            [sg.Button("alias_add", key="KEY_add_alias"),
             sg.Button("alias_del", key="KEY_del_alias")],
            [sg.Button("update", key="KEY_alias_modifier_update"), 
             sg.Button('exit', key='KEY_alias_modifier_exit')]
         ]
        
        key_window = sg.Window('key_dict modifier', popup_key_window_layout, keep_on_top=True, finalize=True)
        key_window.force_focus()

        key_window['KEY_alias_modifier_key'].update(set_to_index=[0]) # type: ignore
        key_window['KEY_alias_modifier_alias'].update(set_to_index=[0]) # type: ignore

        # run loop
        while True:
            event, values = key_window.read()
            
            if event == sg.WINDOW_CLOSED or event == 'KEY_alias_modifier_exit':
                if tmp_key_dict == self.key_dict:
                    key_window.close()
                    break
                else:
                    response = sg.popup_yes_no("data not updated. continue to exit?", title='notice', keep_on_top=True)
                    if response == 'Yes' or response is None:
                        key_window.close()
                        break
                    
            
            if event == "KEY_alias_modifier_key":
                selected_key = values["KEY_alias_modifier_key"][0] if values["KEY_alias_modifier_key"] else ''
                if selected_key != '':
                    if len(tmp_key_dict[selected_key]) == 0:
                        key_window["KEY_alias_modifier_alias"].update(values=tmp_key_dict[selected_key]) # type: ignore
                        selected_alias = None
                    else:
                        key_window["KEY_alias_modifier_alias"].update(values=tmp_key_dict[selected_key], set_to_index=[0]) # type: ignore
                        selected_alias = tmp_key_dict[selected_key][0]
            
            if event == "KEY_alias_modifier_alias":
                selected_alias = values["KEY_alias_modifier_alias"][0] if values["KEY_alias_modifier_alias"] else None
            
            
            if event == "KEY_alias_modifier_update":

                # verify if deplicate in alias
                has_deplica = False
                seen = set()
                for values in tmp_key_dict.values():
                    for value in values:
                        if value in seen:
                            has_deplica = True
                        else:
                            seen.add(value)
                if has_deplica:
                    sg.popup('deplication in alias. please check.', keep_on_top=True)
                else:
                    self.key_dict = tmp_key_dict
                    sg.popup("data updated", keep_on_top=True)
                    # key_window["KEY_alias_modifier_alias"].update(tmp_key_dict[selected_key])
                    
            
            if event == "KEY_add_alias" and selected_key:
                new_alias = sg.popup_get_text("new alias:", keep_on_top=True)
                if new_alias and new_alias not in tmp_key_dict[selected_key]:
                    tmp_key_dict[selected_key].append(new_alias)
                    selected_alias = new_alias
                    key_window["KEY_alias_modifier_alias"].update(values=tmp_key_dict[selected_key]) # type: ignore
            
            elif event == "KEY_add_alias" and not selected_key:
                sg.popup("please choose a key to add alias", keep_on_top=True)
            
            if event == "KEY_del_alias" and selected_alias:
                tmp_key_dict[selected_key].remove(selected_alias)
                if len(tmp_key_dict[selected_key]) == 0:
                    selected_alias = None
                    key_window["KEY_alias_modifier_alias"].update(values=[]) # type: ignore
                else:
                    selected_alias = tmp_key_dict[selected_key][0]
                    key_window["KEY_alias_modifier_alias"].update(tmp_key_dict[selected_key], # type: ignore
                                                 set_to_index=[tmp_key_dict[selected_key].index(selected_alias)])
            
            elif event == "KEY_del_alias" and not selected_alias:
                sg.popup("please choose an alias to delete", keep_on_top=True)
        


    # comm functions
    def send_message(self, command: str, content) -> None:
        '''send a message from ui subfunction to broadcast queue'''
        broadcaster.broadcast({'source': 'ui', 'command': command, 'content': content})
    
    def poll_messages(self) -> None:
        """ues another way to check news list to avoid high concurrency"""
        try:
            while not self.queue_ui.empty():
                news = self.queue_ui.get_nowait()
                self.queue_ui.task_done()
                return news
        except queue.Empty:
            return None

    def update_character(self) -> None:
        '''use this function to update active character with keyboard_handler'''
        self.send_message('info_active_character', self.active_character)
    
    def update_key(self) -> None:
        '''use this function to update active key with keyboard handler'''
        self.send_message('info_active_key', self.active_key)

    def update_value(self, value: str) -> None:
        '''use this function to update active value with keyboard handler,
        and this value then write to clipboard for paste'''
        self.send_message('info_update_value', value)

