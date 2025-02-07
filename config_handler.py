import json


def load_config_from_json(json_file_path: str) -> dict:
    '''This function reads the input json file and returns all config settings from it. '''
    file_path = json_file_path
    with open(file_path, "r", encoding="utf-8") as file:
        data: dict = json.load(file)
    return data


class ConfigSingleton():
    '''This class stores the config information in .json file
    These information should be read by program starting up and can be called by the data_handler or other underlying codes.'''
    _config = None

    @classmethod
    def initialize(cls, json_path: str):
        if cls._config is None:
            cls._config = load_config_from_json(json_path)
    
    @classmethod
    def get_all_config(cls) -> dict:
        return cls._config
    
    @classmethod
    def get_data_dict_config(cls) -> tuple[str, str]:
        '''return the data_dict filepath and sheet name'''
        return cls._config.get('data_xlsx_filepath'), cls._config.get('data_sheet_name')
    
    @classmethod
    def get_key_dict_config(cls) -> tuple[str, str]:
        '''return the key_dict filepath and sheet name'''
        return cls._config.get('key_xlsx_filepath'), cls._config.get('key_sheet_name')
    
    @classmethod
    def get_shortcut_config(cls) -> bool:
        '''return the config about weather use keyboard shortcuts'''
        return cls._config.get('use_shortcuts')

