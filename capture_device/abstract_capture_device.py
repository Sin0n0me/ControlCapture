import tkinter
from abc import ABC, abstractmethod
from .command_logger import CommandLogger
from .command_separator import *

WINDOW_WIDTH = 440

START_CAPTURE = 'start_capture'
STOP_CAPTURE = 'start_capture'

SLEEP_TIME = 0.00001

class AbstractCaptureDevice(ABC):
    capturing = False
    text:tkinter.Text = None
        
    def __init__(self, file_name):
        super().__init__()        
        self.logger = CommandLogger(file_name=file_name)        
    
    @staticmethod
    def add_capture_view(log:str):
        if not AbstractCaptureDevice.text:
            return
        
        if not log.endswith('\n'):
            log += '\n'

        AbstractCaptureDevice.text.config(state='normal')
        AbstractCaptureDevice.text.insert(tkinter.END, log)
        AbstractCaptureDevice.text.see(tkinter.END)
        AbstractCaptureDevice.text.config(state='disabled')
