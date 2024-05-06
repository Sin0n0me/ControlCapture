import tkinter as tk
from pynput import keyboard
from tkinter import messagebox
from control_capture_thread import ControlCaptureThread
from capture_device import *
from widget import *

SLEEP_TIME = 1.0 / 60.0

class GameControlCapture:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('ゲーム操作キャプチャくん')
        self.root.geometry(f'{WINDOW_WIDTH}x360+0+0') 
        self.root.attributes('-topmost', True)      # 最前面にする
        self.root.attributes("-toolwindow", True)   # 最小化禁止にする(windows限定)
        self.root.resizable(False, False)           # サイズの変更不可にする

        # Xボタンが押された時の動作を設定
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)        
    
        self.widget:list[AbstractWidget] = [
            CaptureButton(self.root),
            StartProcess(self.root),
            CaptureConfig(self.root)
        ]
                
    def on_close(self): 
        for widget in self.widget:            
            widget.on_close()
                    
        self.root.destroy()
                        
    def run(self):
        self.capture_surveillance()
        self.root.mainloop()

    def capture_surveillance(self):
        ControlCaptureThread.update()
        
        # 1秒ごとにチェックする
        self.root.after(1000, self.capture_surveillance)

if __name__ == '__main__':  
    app = GameControlCapture()
    app.run()
