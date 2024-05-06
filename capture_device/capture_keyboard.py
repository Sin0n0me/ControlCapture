import pynput
import time
from datetime import datetime, timedelta
from .abstract_capture_device import *

DEFAULT_CAPTURE_START_AND_STOP_KEY = 'f4'

# スレッド外でインスタンスを作成され、キャプチャ用メソッドを別スレッドで実行されることを想定
class CaptureKeyboard(AbstractCaptureDevice):
    
    start_and_stop_key = DEFAULT_CAPTURE_START_AND_STOP_KEY
    
    def __init__(self, file_name) -> None:
        super().__init__(file_name)
        self.key_down_time_dict = {}
        self.key_down_flag_dict = {}

    def capture_keyboard(self): 
        # キーボードイベントを取得
        listener =  pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        self.logger.start_log()
        while AbstractCaptureDevice.capturing:                              
            time.sleep(SLEEP_TIME)
        
        listener.join()
        
        print('キーボードのキャプチャを終了')
        
    def on_press(self, key):
        if not AbstractCaptureDevice.capturing:
            return AbstractCaptureDevice.capturing
        
        key_name = CaptureKeyboard.get_key_name(key)

        # 既に押下中の場合は何もしない
        if key_name in self.key_down_flag_dict:
            if self.key_down_flag_dict[key_name]:
                return

        self.key_down_flag_dict[key_name] = True
        self.key_down_time_dict[key_name] = self.logger.get_elapsed_time()

        return AbstractCaptureDevice.capturing

    def on_release(self, key):
        if not AbstractCaptureDevice.capturing:
            return False
        elapsed_time = self.logger.get_elapsed_time()
        key_name = CaptureKeyboard.get_key_name(key)

        if self.start_and_stop_key == key_name:
            AbstractCaptureDevice.capturing = False
            return False

        # int型の場合はキーコード(Winキーなどはキーコードとして取得される)
        if isinstance(key_name, int):
            command_text = CommandSeparater.format_command_key_down(elapsed_time, key)            
            self.logger.write_command(command_text, True)
            return
                
        self.key_down_flag_dict[key_name] = False
        key_push_time:timedelta = elapsed_time - self.key_down_time_dict[key_name]        
        milli_second = int(key_push_time.total_seconds() * 1000)
        time_difference = elapsed_time - key_push_time
        command_text = CommandSeparater.format_command_key_down(time_difference, key, milli_second)

        self.logger.write_command(command_text, True)
        AbstractCaptureDevice.add_capture_view(command_text)
        
        return AbstractCaptureDevice.capturing    
    
    def get_key_down_time_dict(self):
        return self.key_down_time_dict
    
    @staticmethod
    def get_key_name(key):
        key_name = None
                
        if isinstance(key, pynput.keyboard.Key):
            try:
                key_name = key.name
            except Exception as e:
                print(e)
                return None
        elif isinstance(key, pynput.keyboard.KeyCode):
            key_name = key.char
            
            # キーコードにする
            if not key_name:
                key_name = key.vk
            
        return key_name

    @staticmethod
    def is_pynput_key(key_str):
        if hasattr(pynput.keyboard.Key, key_str):
            return True

        try:
            pynput.keyboard.KeyCode.from_char(key_str)
            return True
        except ValueError:
            return False
