from dataclasses import dataclass

@dataclass(frozen=True)
class Errors():

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
