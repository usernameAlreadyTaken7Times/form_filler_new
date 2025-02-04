from io_handler import prehandle_xlsx, write_xlsx

# Error types
class OverwriteError(Exception):
    '''This Error means you are trying to rewrite the value stored in the dict.'''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class RowdataError(Exception):
    '''This Error means the loaded .xlsx data contains error, for example, the
    main keys are different in the sheets.'''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NoMatchError(Exception):
    '''This Error means there is no match key for the given alias.'''
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Data_Handler:
    '''This class works as a database during the program running, and is called by Data_Handler.
        Functions in it are called to modify the data inside database only.'''
    # init
    def __init__(self, data_path):
        self.data_path = data_path

        self.data_loaded = False

        self.data_dict = {}
        self.key_dict = {}

        self.load_data_xlsx()
        self.check_data_validity()

    # init check
    def check_data_validity(self):
        '''This function checks weather the loaded dicts(value_dict&key_dict) are valid, 
        for example, weather they have the same keys. If not, throw out a RowdataError.
        If there are any replicates in key_dict, it repairs them.'''

        # check if the key from data_dict the same as that from key_dict
        if self.data_dict.keys() != self.key_dict.keys():
            raise RowdataError('loaded .xlsx data contains error')
        
        # delete replicates if there are any same alias in key_dict
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
    def load_data_xlsx(self):
        self.key_dict, self.data_dict = prehandle_xlsx(self.data_path)
        self.data_loaded = True

    def write_data_xlsx(self):
        write_xlsx(self.key_dict, self.data_dict)
        self.data_loaded = False


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

    def add_empty_key_value_pair(self, person: str, key: str):
        '''add a new empty key-value pair for the given person, modify both data sheets(value_dict & key_dict).\n
        default value=None. '''
        if key not in self.data_dict[person].keys():
            # add such key-value pair for all person, but with 'TBA(to be assgined) as value for other characters.
            # modifications should be made to other characters' such key-value, please call function 'set_value_from_key_value_pair.'
            for name_key in self.data_dict.keys():
                self.data_dict[name_key][key] = None
            self.key_dict[key] = [] # create a empty alias list 
        else:
            raise OverwriteError("You are trying to rewrite the value stored in the dict.")
    
    def del_key_value_pair(self, person: str, key: str):
        '''delete an existing key-value pair for all people, modify both data sheets(value_dict & key_dict).'''
        if self.has_key(person, key):
            for key_name in self.data_dict.keys():
                del self.data_dict[key_name][key]
            del self.key_dict[key] # delete the alias list for this key
        else:
            raise KeyError

    def set_value_from_key_value_pair(self, person: str, key, new_value: str):
        '''change the given key-value pair's value into new value.\n
        Noted: This function should only be called after a new key-value pair is created.
        This function assumes the person does exist.'''
        if key in self.data_dict[person].keys():
            self.data_dict[person][key] = new_value

    def add_empty_person(self, new_person: str):
        '''add a new person in the data_dict'''
        if new_person not in self.data_dict.keys():
            self.data_dict[new_person] = self.data_dict[list(self.data_dict.keys())[0]] # copy the parameter from the first character
            for key in self.data_dict[new_person]:
                self.data_dict[new_person][key] = None # set all values of this person as None as default
        else:
            raise NoMatchError('Error chosing person.')

    def del_person(self, del_person: str):
        '''delete a person from data_dict'''
        if del_person not in self.data_dict.keys():
            raise NoMatchError('Error chosing person.')
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
    def key_has_any_alias(self, key_name: str) -> bool:
        '''Return weather the given key has any alias or not.'''
        if self.has_key(key_name): # test if key valid
            if len(self.key_dict[key_name]) != 0:
                return True
            else:
                return False
        else:
            raise KeyError
    
    def key_has_given_alias(self, key_name: str, alias_name: str) -> bool:
        '''Return weather the given key has the given alias.'''
        if self.has_key(key_name): # test if key valid
            return True if alias_name in self.key_dict[key_name] else False
        else:
            raise KeyError
            
    def add_alias_for_existing_key(self, key_name: str, alias_name: str):
        '''add an alias for existing key, modify the key sheet,
        to ensure the key does exist in two dicts and the given alias is not already there.'''
        if self.has_key(key_name): # test if key valid
            if self.key_has_given_alias(key_name, alias_name): # test if the alias already exist
                raise KeyError
            else:
                self.key_dict[key_name].append(alias_name)
        else:
            raise KeyError

    def del_alias_for_existing_key(self, key_name: str, alias_name: str):
        '''delete an alias for existing key, modify the key sheet,
        to ensure the key does exist in two dicts and the given alias is not already there.'''
        if self.has_key(key_name): # test if key valid
            if self.key_has_given_alias(key_name, alias_name): # test if the alias already exist
                self.key_dict[key_name].remove(alias_name)
            else:
                raise KeyError
        else:
            raise KeyError


    # search alias and match key
    def find_key_from_alias(self, alias_name: str) -> str:
        '''This function trys to find the key name based on the given alias name,
        then the found key can use function 'get_value_from_key' to retrive value for further use.'''
        # test if given alias has any match for each key name
        for key in self.key_dict.keys():
            if self.key_has_given_alias(key, alias_name):
                return key
        return None # match no alias for any keys
        
