import pandas as pd
from config_handler import ConfigSingleton
from error_list import Errors

from typing import Tuple, Optional

def unused(func) -> None:
    '''Use this function to decorate a function that is not used'''
    setattr(func, "unused", True)
    return func


def load_and_prehandle_xlsx(data_path: str, data_sheet: str, key_path: str, key_sheet: str) -> Tuple[dict[str,list[str]], dict[str,dict[str,str]]]:
    '''Prehandle the .xlsx file as the data source for further use. 
    The .xlsx file should contain two sheets named "key" and "data".
    The content in these two sheets are returned in dicts.'''

    data_sheets: dict[str, pd.DataFrame] = pd.read_excel(data_path, sheet_name=[data_sheet])
    key_sheets: dict[str, pd.DataFrame] = pd.read_excel(key_path, sheet_name=[key_sheet])

    # replace the `_x000D_` in sheets, such sign is annoying from Office and Windows system
    df_key = key_sheets['key'].map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)
    df_data = data_sheets['data'].map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)

    key_dict: dict = {}
    df_key.fillna('', inplace=True) # fill all missing alias
    key_dict = df_key.set_index(df_key.columns[0]).T.to_dict('list')
    for key in key_dict:
        for _ in range(len(key_dict[key])):
            if key_dict[key][-1] == '':
                key_dict[key] = key_dict[key][:-1]
            else:
                break
    
    data_dict: dict = {}
    data_dict = {
        row['姓名']: {
            **row.to_dict(),  # change the row to a dict
            "姓名": row['姓名'],  # adds a column with given name
        }
        for _, row in df_data.iterrows()
    }
    return key_dict, data_dict

def write_xlsx(key_dict: dict, data_dict: dict,
               data_path: str, data_sheet: str, key_path: str, key_sheet: str) -> None:
    '''Write the dicts in Data_Handler back to the .xlsx file. Should be called when terminating the program.'''
    key_list = []
    max_length = max(len(v) for v in key_dict.values()) if key_dict else 0
    for key, values in key_dict.items():
        while len(values) < max_length:
            values.append('')
        key_list.append([key] + values)

    df_key = pd.DataFrame(key_list)
    df_key.fillna('', inplace=True)

    header_row = ["keys"] + [""] * (df_key.shape[1] - 1)
    df_key = pd.concat([pd.DataFrame([header_row]), df_key], ignore_index=True)

    df_data = pd.DataFrame.from_dict(data_dict, orient='index')

    # df_key = df_key.map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)
    # df_data = df_data.map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)

    with pd.ExcelWriter(key_path) as writer:
        df_key.to_excel(writer, sheet_name=key_sheet, index=False, header=False)
        df_data.to_excel(writer, sheet_name=data_sheet, index=False)

def backup_xlsx_file(data_path: str, data_sheet: str, key_path: str, key_sheet: str, backup_file_path: str):
    df_data = pd.read_excel(data_path, sheet_name=data_sheet)
    df_key = pd.read_excel(key_path, sheet_name=key_sheet)

    with pd.ExcelWriter(backup_file_path) as writer:
        df_data.to_excel(writer, sheet_name=data_sheet, index=False)
        df_key.to_excel(writer, sheet_name=key_sheet, index=False)


class Data_Handler():
    '''This class works as a database during the program running, and is called by Data_Handler.
        Functions in it are called to modify the data inside database only.'''
    # init
    def __init__(self) -> None:
        '''database_dict should contain the path and sheet name of data_sheet and key_sheet.'''
        self.data_path = ConfigSingleton.get_input_data_dict_config()[0]
        self.data_sheetname = ConfigSingleton.get_input_data_dict_config()[1]
        self.key_path = ConfigSingleton.get_input_key_dict_config()[0]
        self.key_sheetname = ConfigSingleton.get_input_key_dict_config()[1]

        self.output_data_path = ConfigSingleton.get_output_data_dict_config()[0]
        self.output_data_sheetname = ConfigSingleton.get_output_data_dict_config()[1]
        self.output_key_path = ConfigSingleton.get_output_key_dict_config()[0]
        self.output_key_sheetname = ConfigSingleton.get_output_key_dict_config()[1]

        self.backup_path = ConfigSingleton.get_backup_xlsx_path()

        self.data_loaded = False

        self.data_dict: dict[str, dict]
        self.key_dict: dict[str, list]
        self.data_dict = {}
        self.key_dict = {}

        self.setup_backup_xlsx_file() # save key and data sheets into backup file to prevent data lose
        self.load_data_xlsx()
        self.check_data_validity()

    # init check
    def check_data_validity(self) -> None:
        '''This function checks weather the loaded dicts(value_dict&key_dict) are valid, 
        for example, weather they have the same keys. If not, throw out a RowdataError.
        If there are any replicates in key_dict, it repairs them.'''

        # garentee at least one character is available in data_dict
        if len(self.data_dict.items()) >= 1:
            pass
        else:
            raise Errors.RowdataError('No character in imported data.') 

        # check if all characters have the same keys
        tmp_keys = self.data_dict[list(self.data_dict.keys())[0]].keys()
        for character in self.data_dict:
            if self.data_dict[character].keys() == tmp_keys:
                pass
            else:
                raise Errors.RowdataError(f'character {character} has different keys. Please check imported data.')

        # check if the key from data_dict the same as that from key_dict
        if tmp_keys != self.key_dict.keys():
            raise Errors.RowdataError('loaded .xlsx data contains error, key_dict and data_dict have different key list.')
        
        # delete replicates if there are any same alias in key_dict
        # here no Error or jumping out, but try to repair alias dict by deleting replicates,
        # because the alias does not affects the stability of the program.
        temp_key_dict = {}
        seen_alias = set()
        for keys, values in self.key_dict.items():
            unique_alias = []
            for v in values:
                if v not in seen_alias:
                    seen_alias.add(v)
                    unique_alias.append(v)
            if unique_alias:
                temp_key_dict[keys] = unique_alias

        self.key_dict = temp_key_dict # overwrite and delete
        del temp_key_dict


    # io
    def load_data_xlsx(self) -> None:
        '''load data_dict and key_dict from .xlsx file'''
        self.key_dict, self.data_dict = load_and_prehandle_xlsx(self.data_path, self.data_sheetname, self.key_path, self.key_sheetname)
        self.data_loaded = True

    def write_data_xlsx(self) -> None:
        '''write data_dict and key_dict back to .xlsx file'''
        print('write data into xlsx file')
        write_xlsx(self.key_dict, self.data_dict,
                    self.output_data_path, self.output_data_sheetname,
                    self.output_key_path, self.output_key_sheetname)
        self.data_loaded = False

    def setup_backup_xlsx_file(self) -> None:
        '''copy and save a xlsx backup file when init, prevent losing data by running'''
        backup_xlsx_file(self.data_path, self.data_sheetname, self.key_path, self.key_sheetname, self.backup_path)

    # value_dict related functions
    def has_key(self, person: str, key: str) -> bool:
        '''test if the given key exists in the data_dict for specific person or not'''
        if key in self.data_dict[person].keys():
            return True
        else:
            return False
    
    def get_value_from_key(self, person: str, key: str) -> str:
        '''retuen the value based on the given key'''
        return self.data_dict[person][key]

    def add_empty_key_value_pair(self, person: str, key: str) -> None:
        '''add a new empty key-value pair for the given person, modify both data sheets(value_dict & key_dict).\n
        default value=None. '''
        if key not in self.data_dict[person].keys():
            # add such key-value pair for all person, but with 'TBA(to be assgined) as value for other characters.
            # modifications should be made to other characters' such key-value, please call function 'set_value_from_key_value_pair.'
            for name_key in self.data_dict.keys():
                self.data_dict[name_key][key] = None
            self.key_dict[key] = [] # create a empty alias list 
        else:
            raise Errors.OverwriteError("You are trying to rewrite the value stored in the dict.")
    
    def del_key_value_pair(self, person: str, key: str) -> None:
        '''delete an existing key-value pair for all people, modify both data sheets(value_dict & key_dict).'''
        if self.has_key(person, key):
            for key_name in self.data_dict.keys():
                del self.data_dict[key_name][key]
            del self.key_dict[key] # delete the alias list for this key
        else:
            raise KeyError

    def set_value_from_key_value_pair(self, person: str, key, new_value: str) -> None:
        '''change the given key-value pair's value into new value.\n
        Noted: This function should only be called after a new key-value pair is created.
        This function assumes the person does exist.'''
        if key in self.data_dict[person].keys():
            self.data_dict[person][key] = new_value

    def add_empty_person(self, new_person: str) -> None:
        '''add a new person in the data_dict'''
        if new_person not in self.data_dict.keys():
            self.data_dict[new_person] = self.data_dict[list(self.data_dict.keys())[0]] # copy the parameter from the first character
            for key in self.data_dict[new_person]:
                self.data_dict[new_person][key] = None # set all values of this person as None as default
        else:
            raise Errors.NoMatchError('Error chosing person.')

    def del_person(self, del_person: str) -> None:
        '''delete a person from data_dict'''
        if del_person not in self.data_dict.keys():
            raise Errors.NoMatchError('Error chosing person.')
        else:
            del self.data_dict[del_person]

    def key_has_value(self, person: str, key: str) -> bool:
        '''return if the given key for specific person has any value in the data_dict or not'''
        if self.data_dict[person][key] is None:
            return False
        else:
            return True

    def get_character_list(self) -> list:
        '''return the character list from data_dict'''
        return list(self.data_dict.keys())
    
    def get_key_list(self) -> list:
        '''return the key list from data_dict,
        it is the same for all characters, so just return the key list for the first character.'''
        first_character = list(self.data_dict.keys())[0]
        return list(self.data_dict[first_character].keys())


    # alias_dict(key_dict) related functions
    @unused
    def key_has_any_alias(self, key_name: str) -> bool:
        '''Return weather the given key has any alias or not.'''
        if key_name in self.key_dict.keys(): # test if key valid
            if len(self.key_dict[key_name]) != 0:
                return True
            else:
                return False
        else:
            raise KeyError
    
    def key_has_given_alias(self, key_name: str, alias_name: str) -> bool:
        '''Return weather the given key has the given alias.'''
        if key_name in self.key_dict.keys(): # test if key valid
            return True if alias_name in self.key_dict[key_name] else False
        else:
            raise KeyError
    
    @unused
    def add_alias_for_existing_key(self, key_name: str, alias_name: str) -> None:
        '''add an alias for existing key, modify the key sheet,
        to ensure the key does exist in two dicts and the given alias is not already there.'''
        if key_name in self.key_dict.keys(): # test if key valid
            if self.key_has_given_alias(key_name, alias_name): # test if the alias already exist
                raise KeyError
            else:
                self.key_dict[key_name].append(alias_name)
        else:
            raise KeyError

    @unused
    def del_alias_for_existing_key(self, key_name: str, alias_name: str) -> None:
        '''delete an alias for existing key, modify the key sheet,
        to ensure the key does exist in two dicts and the given alias is not already there.'''
        if key_name in self.key_dict.keys(): # test if key valid
            if self.key_has_given_alias(key_name, alias_name): # test if the alias already exist
                self.key_dict[key_name].remove(alias_name)
            else:
                raise KeyError
        else:
            raise KeyError


    # search alias and match key
    def find_key_from_alias(self, alias_name: str) -> Optional[str]:
        '''This function trys to find the key name based on the given alias name,
        then the found key can use function 'get_value_from_key' to retrive value for further use.'''
        # test if given alias has any match for each key name
        for key in self.key_dict.keys():
            if self.key_has_given_alias(key, alias_name):
                return key
        return None # match no alias for any keys
        