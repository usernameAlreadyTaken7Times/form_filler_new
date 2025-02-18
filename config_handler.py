import json

def unused(func) -> None:
    '''Use this function to decorate a function that is not used'''
    setattr(func, "unused", True)
    return func


def load_config_from_json(json_file_path: str) -> dict:
    '''This function reads the input json file and returns all config settings from it. '''
    file_path = json_file_path
    with open(file_path, "r", encoding="utf-8") as file:
        data: dict = json.load(file)
    return data


class ConfigSingleton():
    '''This class stores the config information in .json file
    These information should be read by program starting up and can be called by the data_handler or other underlying codes.'''
    _config = {'':''}

    @classmethod
    def validate_config(cls, config: dict):
        required_keys = ['input_data_xlsx_filepath',
                         'input_data_sheet_name',
                         'input_key_xlsx_filepath',
                         'input_key_sheet_name',
                         'output_data_xlsx_filepath',
                         'output_data_sheet_name',
                         'output_key_xlsx_filepath',
                         'output_key_sheet_name',
                         'use_shortcuts']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"Missing required config keys: {', '.join(missing_keys)}")

    @classmethod
    def initialize(cls, json_path: str):
        if cls._config == {'':''}:
            config = load_config_from_json(json_path)
            cls.validate_config(config)
            cls._config: dict[str, str] = config
            
    @unused
    @classmethod
    def get_all_config(cls) -> dict:
        return cls._config
    
    @classmethod
    def get_input_data_dict_config(cls) -> tuple[str, str]:
        '''return the input data_dict filepath and sheet name'''
        return cls._config['input_data_xlsx_filepath'], cls._config['input_data_sheet_name']

    @classmethod
    def get_input_key_dict_config(cls) -> tuple[str, str]:
        '''return the input key_dict filepath and sheet name'''
        return cls._config['input_key_xlsx_filepath'], cls._config['input_key_sheet_name']
    
    @classmethod
    def get_output_data_dict_config(cls) -> tuple[str, str]:
        '''return the output data_dict filepath and sheet name'''
        return cls._config['output_data_xlsx_filepath'], cls._config['output_data_sheet_name']

    @classmethod
    def get_output_key_dict_config(cls) -> tuple[str, str]:
        '''return the output key_dict filepath and sheet name'''
        return cls._config['output_key_xlsx_filepath'], cls._config['output_key_sheet_name']

    @unused
    @classmethod
    def get_shortcut_config(cls) -> str:
        '''return the config about weather use keyboard shortcuts'''
        return cls._config['use_shortcuts']

