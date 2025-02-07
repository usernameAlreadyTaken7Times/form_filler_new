import PySimpleGUI as sg
from error_list import Errors
from config_handler import ConfigSingleton

from shared_queue import shared_queue
import threading


class UI_Handler(threading.Thread):
    '''This UI_Handler deals with interacting with Users directly, including receiving graphic rendering commands.
    It should be in the same layer as keyboard & business module.
    Meantime, the config file is also loaded here, from ui interface. It can then be used in other modules.
    '''
    def __init__(self, config_filepath: str): 
        
        # vairables
        self.config_filepath = config_filepath
        self.window_running = False

        self.data_dict: dict
        self.key_dict: dict
        self.data_dict, self.key_dict = self.get_dicts_content_from_data_handler()

        # define main GUI window
        main_window_layout = [
            [sg.Text("Form_Filler v0.3", font=("Arial", 12, "bold"), text_color="white")],
            [sg.Text("an extended copy/paste service", font=("Arial", 9), text_color="white")],
            [sg.HorizontalSeparator()],

            [sg.Text("Please confirm/load a config file.", font=("Arial", 9), text_color="white", key="TEXT_config_status")],
            [sg.Checkbox("use default config", key="CHECK_use_default_config", enable_events=True, default=True)],
            [sg.Button('Confirm', size=(9, 1), font=("Arial", 8), key="kEY_switch_config"), 
              sg.Button('Cancel', size=(9, 1), font=("Arial", 8), key="kEY_cancel_config")],
            [sg.HorizontalSeparator()],
            
            [sg.Text("Run/Terminate", font=("Arial", 9), text_color="white")],
            [sg.Button("Run", size=(8, 1), font=("Arial", 9), key="KEY_run"), 
              sg.Button("Terminate", size=(8, 1), font=("Arial", 9), key="KEY_terminate")],
            [sg.Text("or Ctrl+R / Ctrl+T", font=("Arial", 8), text_color="white")],
            [sg.HorizontalSeparator()],

            [sg.Text("Modifier", font=("Arial", 9), text_color="white")],
            [sg.Button("data", size=(8, 1), font=("Arial", 9), key="KEY_data_modifier"),
             sg.Button("alias", size=(8, 1), font=("Arial", 9), key="KEY_alias_modifier")],

            [sg.Text("test____test", font=("Arial", 8), text_color="blue")]
        ]
        self.window = sg.Window("FFv0.3",
                                 main_window_layout,
                                 resizable=True,
                                 keep_on_top=True,
                                 finalize=True)

        # window init setting
        self.window['kEY_cancel_config'].update(disabled=True)

    # start/stop functions
    def start_GUI(self):
        '''starts the GUI program and show the window'''
        if not self.window_running:
            self.window_running = True
            self.run_ui()
        else:
            raise Errors.ServiceStatusError('GUI status error')
        
    def stop_GUI(self):
        '''stops the GUI program and hide the window'''
        if self.window_running:
            self.window_running = False
            self.window.close()

    # ui main thread
    def run_ui(self):
        '''ui main thread, controls the ui logic.'''
        while True:
            event, values = self.window.read()

            # confirm/load config file related
            if event == 'CHECK_use_default_config':
                new_text = 'confirm' if values['CHECK_use_default_config'] else 'load'
                self.window['kEY_switch_config'].update(new_text)

            if event == 'kEY_switch_config':
                if values['CHECK_use_default_config']:
                    try:
                        ConfigSingleton.initialize(self.config_filepath)  # load default config file
                        self.window['CHECK_use_default_config'].update(disabled=True) # disable load/confirm button
                        self.window['kEY_switch_config'].update(disabled=True)
                        self.window['kEY_cancel_config'].update(disabled=False)
                        self.window['TEXT_config_status'].update('Config file successfully loaded.')
                    except:
                        raise KeyError # error loading .json file
                else:
                    self.config_filepath = self.popup_config_choose(self.config_filepath)
                    try:
                        ConfigSingleton.initialize(self.config_filepath)  # load new config file
                        self.window['CHECK_use_default_config'].update(disabled=True) # disable load/confirm button
                        self.window['kEY_switch_config'].update(disabled=True)
                        self.window['kEY_cancel_config'].update(disabled=False)
                        self.window['TEXT_config_status'].update('Config file successfully loaded.')
                    except:
                        raise KeyError # error loading .json file
                
                print(self.config_filepath)

            if event == 'kEY_cancel_config': # should only be called when the KEY_switch_config is disabled
                self.window['CHECK_use_default_config'].update(disabled=False) # enable load/confirm button
                self.window['kEY_switch_config'].update(disabled=False)
                self.window['kEY_cancel_config'].update(disabled=True)
                self.window['TEXT_config_status'].update('Please confirm/load config file.')

            if event == 'KEY_data_modifier':
                self.popup_data_dict_modifier()
                self.set_data_dict_content_to_data_handler() # sync the data_dict and key_dict with updates
            
            if event == 'KEY_key_modifier':
                self.popup_key_dict_modifier()
                self.set_key_dict_content_to_data_handler() # sync

            # terminate GUI program
            if event == 'KEY_terminate':
                self.stop_GUI()
                break
 
    # thread related functions
    def popup_config_choose(self, default_json_path: str):
        '''pop up a subwindow to get new .json config file path, and return the .json path back'''

        popup_window_layout = [
            [sg.Text("choose a .json config file")],
            [sg.InputText(default_text=default_json_path, key="TEXT_json_config_file"), sg.FileBrowse(initial_folder=default_json_path)],
            [sg.Button("confirm", key="KEY_confirm")]
        ]

        config_window = sg.Window('choose .json config file', popup_window_layout, keep_on_top=True, finalize=True)
        config_window.force_focus()

        while True:
            event, values = config_window.read()
            if event is sg.WIN_CLOSED:
                sg.popup_ok('Use default config file instead', title='confirm', keep_on_top=True)
                selected_file = default_json_path
                break
            elif event == "KEY_confirm":
                config_window['TEXT_json_config_file'].update(values["TEXT_json_config_file"])
                selected_file: str = values["TEXT_json_config_file"]
                if selected_file.endswith('.json'):
                    break
                else:
                    sg.popup_error('please choose a .json config file', title='Error', keep_on_top=True)

        config_window.close()
        return selected_file

    def get_dicts_content_from_data_handler(self):
        '''use queue to request data_dict and key_dict from data_handler, should be called by init'''
        # shared_queue.put({{'source':'ui','command':'get_dicts', 'content': ''}})
        # while True:
        #     tmp_news = shared_queue.get()
        #     if tmp_news['source'] == 'business' and tmp_news['command'] == 'send_dicts':
        #         break
        # return tmp_news['content']

        # for test only
        data = {
            "张三": {"年龄": 25, "学历": "本科", "职业": "工程师"},
            "李四": {"年龄": 30, "学历": "硕士", "职业": "教师"},
            "王五": {"年龄": 28, "学历": "博士", "职业": "研究员"},
        }
        key = {}
        return data, key

    def set_dicts_content_to_data_handler(self):
        '''use queue to send data_dict and key_dict to data_handler, should be called every time the dicts are changed from modifier'''
        # shared_queue.put({'source': 'ui', 'coommand': 'set_dicts', 'content': (self.data_dict, self.key_dict)})

        # for test only
        pass

    def set_data_dict_content_to_data_handler(self):
        '''use queue to send data_dict to data_handler, should be called every time the dict changed from modifier'''
        # shared_queue.put({'source': 'ui', 'coommand': 'set_data_dict', 'content': self.data_dict})

        # for test only
        pass

    def set_key_dict_content_to_data_handler(self):
        '''use queue to send key_dict to data_handler, should be called every time the dict changed from modifier'''
        # shared_queue.put({'source': 'ui', 'coommand': 'set_key_dict', 'content': self.key_dict})

        # for test only
        pass


    def popup_data_dict_modifier(self):
        '''pop up a new data_dict modifier window'''

        tmp_data_dict: dict[str, dict]
        tmp_data_dict = self.data_dict.copy() # create a copy of data_dict for in-function use
        selected_character = None
        selected_key = None
        key = list(next(iter(tmp_data_dict.values())).keys())

        # popup data_dict modifier window layout
        popup_window_layout = [
            [sg.Text("characters", font=("Arial", 9), text_color="white", size=(10, 1)),
             sg.Text("keys", font=("Arial", 9), text_color="white", size=(10, 1)),
             sg.Text("values", font=("Arial", 9), text_color="white", size=(20, 1))],
            [sg.Listbox(values=list(tmp_data_dict.keys()), size=(10, 10), key="KEY_character", enable_events=True),
             sg.Listbox(values=key, size=(10, 10), key="KEY_key", enable_events=True),
             sg.Multiline("", size=(20, 10), key="KEY_value", enable_events=True)],
            [sg.Button("character_add", key="KEY_add_character"),
             sg.Button("character_del", key="KEY_del_character"),
             sg.Button("key_add", key="KEY_add_key"),
             sg.Button("key_del", key="KEY_del_key")],
            [sg.Button("update", key="KEY_update")]
         ]
        
        data_window = sg.Window('data_dict modifier', popup_window_layout, keep_on_top=True, finalize=True)
        data_window.force_focus()

        # run loop
        while True:
            event, values = data_window.read()
            
            if event == sg.WINDOW_CLOSED:
                break
            
            if event == "KEY_character":
                selected_character = values["KEY_character"][0] if values["KEY_character"] else None
                if selected_character:
                    data_window["KEY_key"].update(values=key)
                    selected_key = None
                    data_window["KEY_value"].update("")
            
            if event == "KEY_key" and selected_character:
                selected_key = values["KEY_key"][0] if values["KEY_key"] else None
                if selected_key:
                    data_window["KEY_value"].update(tmp_data_dict[selected_character][selected_key])
            
            if event == "KEY_value" and selected_character and selected_key:
                tmp_data_dict[selected_character][selected_key] = values["KEY_value"]
                data_window["KEY_value"].update(tmp_data_dict[selected_character][selected_key])
            
            if event == "KEY_update" and selected_character and selected_key:
                tmp_data_dict[selected_character][selected_key] = values["KEY_value"]
                data_window["KEY_value"].update(tmp_data_dict[selected_character][selected_key])

                # test weather all character has value for the new added key
                is_perfect_dict = True
                for character in tmp_data_dict:
                    if '' in tmp_data_dict[character].values():
                        sg.popup('Some character\'s key has empty value, please check', keep_on_top=True)
                        is_perfect_dict = False
                        break
                
                if is_perfect_dict: # then save the current dict into self.data_dict, and use queue sync to data_handler
                    self.data_dict = tmp_data_dict
                    sg.popup("data updated", keep_on_top=True)
                    

            if event == "KEY_add_character":
                new_person = sg.popup_get_text("new character:", keep_on_top=True)
                if new_person and new_person not in tmp_data_dict:
                    tmp_data_dict[new_person] = {attr: "" for attr in key}
                    data_window["KEY_character"].update(values=list(tmp_data_dict.keys()))
            
            if event == "KEY_del_character" and selected_character:
                del tmp_data_dict[selected_character]
                selected_character = None
                data_window["KEY_character"].update(values=list(tmp_data_dict.keys()))
                data_window["KEY_key"].update(values=[])
                data_window["KEY_value"].update("")
            
            if event == "KEY_add_key":
                new_attr = sg.popup_get_text("new key:", keep_on_top=True)
                if new_attr and new_attr not in key:
                    key.append(new_attr)
                    for person in tmp_data_dict:
                        tmp_data_dict[person][new_attr] = ""
                    data_window["KEY_key"].update(values=key)
            
            if event == "KEY_del_key" and selected_key:
                key.remove(selected_key)
                for person in tmp_data_dict:
                    del tmp_data_dict[person][selected_key]
                selected_key = None
                data_window["KEY_key"].update(values=key)
                data_window["KEY_value"].update("")

    def popup_key_dict_modifier(self):
        '''pop up a new key_dict modifier window'''

        tmp_key_dict: dict[str, str]
        tmp_data_dict = self.key_dict.copy() # create a copy of key_dict for in-function use
        selected_key = None

        

A = UI_Handler(r'C:\Users\86781\VS_Code_Project\form_filler_new\config.json')
A.start_GUI()
pass
