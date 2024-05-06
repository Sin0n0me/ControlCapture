from pynput import keyboard
from tkinter import Tk
from .abstract_widget import *
from capture_device import *

class CaptureConfig(AbstractWidget):
    
    def __init__(self, root: Tk):
        super().__init__(root)

        # 情報用ラベル
        option_label = tkinter.Label(self.root, text='オプション')        
        option_label.pack(fill='both', expand=True)

        # チェックボックスの状態を保持するための変数
        self.mouse_checkbox_flag_var = tkinter.BooleanVar(value=CaptureMouse.record_move_mouse_flag)
        mouse_checkbox = tkinter.Checkbutton(self.root, text='マウス移動時の座標を記録する', variable=self.mouse_checkbox_flag_var, command=self.on_check)
        mouse_checkbox.pack(fill='both', expand=True)

        # 開始キー設定        
        self.start_and_stop_key = CaptureKeyboard.start_and_stop_key
        start_and_stop_key_frame = tkinter.Frame(self.root)
        start_and_stop_key_frame.pack(fill='both', expand=True)
        set_start_and_stop_key_button = tkinter.Button(start_and_stop_key_frame, width=40, text='設定(ボタンクリック後設定したいキーを押下してください)', command=self.change_start_and_stop_key)
        set_start_and_stop_key_button.pack(side=tkinter.LEFT, fill='y', expand=True)
        start_and_stop_key_label = tkinter.Label(start_and_stop_key_frame, width=8, text='開始キー:')
        start_and_stop_key_label.pack(side=tkinter.LEFT, fill='y', expand=True) 
        self.start_and_stop_key_label = tkinter.Label(start_and_stop_key_frame, width=16, text=self.start_and_stop_key)
        self.start_and_stop_key_label.pack(side=tkinter.LEFT, fill='y', expand=True, anchor=tkinter.W)

        # デッドゾーン設定
        # バリデーションコマンドの設定
        vcmd = (root.register(self.validate), '%P')
        self.default_dead_zone_string_var = tkinter.StringVar(value=CaptureGamePad.dead_zone)
        default_dead_zone_frame = tkinter.Frame(self.root)
        default_dead_zone_frame.pack(fill='both', expand=True)
        default_dead_zone_label = tkinter.Label(default_dead_zone_frame, text='デッドゾーン(0~1の範囲に設定してください):')
        default_dead_zone_label.pack(side=tkinter.LEFT)
        default_dead_zone_entry = tkinter.Entry(default_dead_zone_frame, textvariable=self.default_dead_zone_string_var,validate="key", validatecommand=vcmd)
        default_dead_zone_entry.pack(side=tkinter.LEFT, fill='both', expand=True)

    def on_close(self):
        pass
        
    def validate(self, input):
        # 入力が空の場合は許可(削除のため)
        if input.strip() == "":
            return True

        try:
            # 入力をfloatに変換し,範囲をチェック
            value = float(input)
            if 0.0 <= value <= 1.0:
                return True
            else:
                return False
        except ValueError:
            # 入力が数値に変換できない場合は拒否
            return False
        
    def on_check(self):
        CaptureMouse.record_move_mouse_flag = self.mouse_checkbox_flag_var.get()
        
    def on_press_change_start_key(self, key):
        try:
            self.start_and_stop_key = key.char
        except AttributeError:
            self.start_and_stop_key = key.name

        # キーが取得できたらリスナーを停止            
        if self.start_and_stop_key:  
            return False        
        
    # もう少しいい仕組みにしたい
    def change_start_and_stop_key(self):
        self.start_and_stop_key = None

        with keyboard.Listener(on_press=self.on_press_change_start_key) as listener:
            listener.join()
        
        if self.start_and_stop_key:
            self.start_and_stop_key_label['text'] = self.start_and_stop_key        


