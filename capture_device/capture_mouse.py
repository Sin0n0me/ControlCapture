import pynput
import time
import threading
from .abstract_capture_device import *

MAX_BUFFER_SIZE = 1024 # バッファサイズが小さすぎると動作が不安定になる

class CaptureMouse(AbstractCaptureDevice):
    record_move_mouse_flag = True
        
    def __init__(self, file_name) -> None:
        super().__init__(file_name)
        self.update_index_flag = False
        self.index_buffer = 0
        self.mouse_click_time_dict = {}
        self.mouse_click_flag_dict = {}
        self.mouse_buffer = [{},{}]        

        self.write_thread:threading.Thread = threading.Thread(target=self.write)

    def write(self):
        pre_index = self.index_buffer
        self.index_buffer = 1 if self.index_buffer == 0 else 0  # indexの切り替え
       
        # ファイルに書き出し
        command_list = self.mouse_buffer[pre_index].values()
        for command_text in command_list:
            self.logger.write_command(command_text, True)
            
        self.mouse_buffer[pre_index].clear()        
    
    def swap_buffer(self):
        if self.write_thread.is_alive():
            self.write_thread.join()
        
        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.start()
        self.update_index_flag = False
    
    def capture_mouse(self):
        # マウスイベントを取得
        listener = pynput.mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        listener.start()
                
        self.logger.start_log()
        while AbstractCaptureDevice.capturing:            
            # バッファが満タンの場合ファイルに書き込んで削除
            if self.update_index_flag:
                self.swap_buffer()
            time.sleep(SLEEP_TIME)
                    
        try:
            listener.join()
        finally:
            listener.stop()
            
        print('マウスのキャプチャを終了')

        # 書き込み用スレッドのjoin
        if self.write_thread.is_alive():
            self.write_thread.join()

        # バッファ内のログを全て書き出し
        for temp_dict in self.mouse_buffer:
            for command_text in temp_dict.values():
                self.logger.write_command(command_text, True)

        # ソート
        self.logger.sort_and_fix_command_file()
    
        
    # 頻繁に呼び出されるのでメモリ上に保管
    def on_move(self, x, y):
        if not self.record_move_mouse_flag:
            return AbstractCaptureDevice.capturing
        
        elapsed_time = self.logger.get_elapsed_time()

        # サイズ肥大化を防ぐために特定サイズ以上になった場合はインデックスの切り替え
        if len(self.mouse_buffer[self.index_buffer]) > MAX_BUFFER_SIZE:
            self.update_index_flag = True
        
        command_text = CommandSeparater.format_command_mouse_move(elapsed_time, 'Move', x, y)        
        self.mouse_buffer[self.index_buffer][CommandSeparater.format_time(elapsed_time)] = command_text
        
        return AbstractCaptureDevice.capturing

    def on_click(self, x, y, button, pressed):
        if pressed:
            command_text = CommandSeparater.format_command_mouse_click(self.logger.get_elapsed_time(), button.name, x, y)
            log = self.logger.write_command(command_text, True)
        else:
            pass
            #print(f'Mouse released at ({x}, {y}) with {button.name}')
            
        return AbstractCaptureDevice.capturing

    def on_scroll(self, x, y, dx, dy):
        #log = self.logger.write_command(f'{CommandSeparater.COMMAND_MOUSE_SCROLL}:{dx} {dy}')
        #self.add_capture_view(log)
        return AbstractCaptureDevice.capturing    
    