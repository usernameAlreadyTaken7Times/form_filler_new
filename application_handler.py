from business_handler import Business_Handler



class Application_Handler():
    '''This Application_Handler handles the logic and cooperate the interacting between business layer & presentation layer.'''
    def __init__(self):
        
        business_handler = Business_Handler()
        self.business_handler = business_handler
    
    
