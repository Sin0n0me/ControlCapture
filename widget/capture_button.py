import pyautogui
from tkinter import Tk, messagebox
from .abstract_widget import *
from control_capture_thread import ControlCaptureThread
from capture_device.abstract_capture_device import AbstractCaptureDevice

class CaptureButton(AbstractWidget): 
    def __init__(self, root: Tk):
        super().__init__(root)

        # 親ウィンドウの位置変更を監視
        self.root.bind('<Configure>', self.on_move_main_window)
    
        self.capture_thread = ControlCaptureThread()
        # キャプチャ内容表示用ウィンドウ
        self.capture_log_window = None
        
        # キャプチャ開始ボタン
        self.start_button = tkinter.Button(self.root, text='キャプチャ開始', command=self.start_capture, font=('', 20))
        self.start_button.pack(fill='both', expand=True)
        
        # キャプチャ終了ボタン
        self.stop_button = tkinter.Button(self.root, text='キャプチャ終了', command=self.stop_capture, font=('', 20))
        self.stop_button.pack(fill='both', expand=True)        


    def on_close(self):
        self.capture_thread.stop_capture()
    
    def start_capture(self):
        if AbstractWidget.capture_flag:
            return
        
        # 開始を通知
        self.notify_capture_flag(True)
        self.notify_process_start(True)
        
        # Falseに変更された場合はなにもしない
        if not AbstractWidget.process_start:
            return
        
        # キャプチャ情報描画ウィンドウを作成
        self.create_capture_window()

        # キャプチャ用スレッドを開始
        self.capture_thread.start_capture()
            
    def stop_capture(self):
        if not AbstractWidget.capture_flag:
            return
        
        self.notify_capture_flag(False)
        self.notify_process_start(False)

        # キーが押されるまでスレッドがブロッキングされるので解除
        pyautogui.press('shift')
        
        # キャプチャ停止
        self.capture_thread.stop_capture()
                    

    def on_move_main_window(self, event):
        # キャプチャログウィンドウを生成していなければ何もしない
        if not self.capture_log_window:
            return
        
        if event.widget == self.root:
            x = self.root.winfo_x() + self.offset_x
            y = self.root.winfo_y() + self.offset_y
            self.capture_log_window.geometry(f'+{x}+{y}')


    def create_capture_window(self):
        # 再生成する
        if self.capture_log_window:
            self.capture_log_window.destroy()
        self.capture_log_window = tkinter.Toplevel(self.root)
                
        # 最前面にする(他ウィンドウに隠れて裏で実行され続けることを防ぐ)
        self.capture_log_window.attributes('-topmost', True)
            
        # offsetの計算
        self.offset_x = self.root.winfo_x()
        self.offset_y = self.root.winfo_y() + self.root.winfo_height() + 32
        self.capture_log_window.geometry(f'{WINDOW_WIDTH}x400+{self.offset_x}+{self.offset_y}')
        self.capture_log_window.title('キャプチャデータ')
        text = tkinter.Text(self.capture_log_window)
        text.config(state='disabled')
        self.capture_log_window.bind('<Configure>', self.on_move_text_window)
        text.pack(fill='both', expand=True)        
        
        AbstractCaptureDevice.text = text

    def on_move_text_window(self, event):
        if event.widget == self.capture_log_window:
            self.offset_x = self.capture_log_window.winfo_x() - self.root.winfo_x()
            self.offset_y = self.capture_log_window.winfo_y() - self.root.winfo_y()
