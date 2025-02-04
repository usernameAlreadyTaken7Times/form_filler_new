from application_handler import Application_Handler
import PySimpleGUI as sg


class Presentation_Handler():
    '''This Presentation_Handler deals with interacting with Users directly,
    containing monitering Keyboard inputs (without parsing them) and generating GUI.'''
    def __init__(self):
        application_handler = Application_Handler()
        self.application_handler = application_handler