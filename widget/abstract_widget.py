import tkinter
import threading
from abc import ABC, abstractmethod


WINDOW_WIDTH = 440

START_CAPTURE = 'start_capture'
STOP_CAPTURE = 'start_capture'

class AbstractWidget(ABC):

    capture_flag:bool = False
    process_start:bool = False
    
    notify_list_capture_flag =[]
    notify_list_process_start =[]    
        
    def __init__(self, root:tkinter.Tk):
        super().__init__()
        self.root = root
        self.notify_list_process_start.append(self)
        self.notify_list_capture_flag.append(self)
    
    @abstractmethod
    def on_close(self):
        pass

    def on_change_capture_flag(self, flag:bool):
        pass

    def on_change_process_start(self, flag:bool):
        pass

    def notify_capture_flag(self, flag:bool):
        AbstractWidget.capture_flag = flag
        
        for widget in self.notify_list_capture_flag:
            widget.on_change_capture_flag(flag)    
            
    def notify_process_start(self, flag:bool):
        AbstractWidget.process_start = flag
        
        for widget in self.notify_list_process_start:
            widget.on_change_process_start(flag)
