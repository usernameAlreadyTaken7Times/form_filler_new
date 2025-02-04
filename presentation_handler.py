from keyboard_handler import Keyboard_Handler
from business_handler import Business_Handler
import PySimpleGUI as sg


class Presentation_Handler():
    '''This Presentation_Handler deals with interacting with Users directly,
    containing monitering Keyboard inputs (without parsing them) and generating GUI.'''
    def __init__(self):

        keyboard_handler = Keyboard_Handler()
        self.keyboard_handler = keyboard_handler

        business_handler = Business_Handler()
        self.business_handler = business_handler

        # defind main GUI window
        main_window_layout = [
            [sg.Text("按下 Ctrl+A / Ctrl+B / Ctrl+C 以打开不同窗口", font=("Arial", 14))],
            [sg.Text("无论何时，按 Ctrl+K 可打开窗口 K", font=("Arial", 12), text_color="blue")],
            [sg.Text("接收窗口 C 的文本：", font=("Arial", 12)), sg.Text("", size=(30, 1), font=("Arial", 12), key="-MAIN_TEXT-")],
            [sg.Button("退出", size=(10, 1), font=("Arial", 12), key="-EXIT-"), 
                sg.Button("按钮 1", size=(10, 1), font=("Arial", 12), key="-BTN1-"),
                sg.Button("按钮 2", size=(10, 1), font=("Arial", 12), key="-BTN2-")]
        ]
        self.window = sg.Window("主窗口", main_window_layout, finalize=True)

    def run(self):
        while True:
            event, values = self.window.read()


test_handler = Presentation_Handler()
test_handler.run()
pass
