import pygame
import threading
import time
from datetime import timedelta
from .command_separator import CommandSeparater
from .abstract_capture_device import *

DEFAULT_DEAD_ZONE = 0.1
MAX_BUFFER_SIZE = 1024

class CaptureGamePad(AbstractCaptureDevice):
    dead_zone = DEFAULT_DEAD_ZONE
    
    def __init__(self, file_name) -> None:
        super().__init__(file_name)
        self.update_index_flag = False
        self.index_joistick_buffer = 0
        self.button_time_dict = {}
        self.button_flag_dict = {}
        self.joistick_pos_dict = {}
        self.joistick_buffer = [{},{}]
        self.write_thread:threading.Thread = threading.Thread(target=self.write)
        
        # ライブラリとジョイスティックの初期化
        pygame.init()
        pygame.joystick.init()

    def write(self):
        pre_index = self.index_joistick_buffer
        self.index_joistick_buffer = 1 if self.index_joistick_buffer == 0 else 0  # indexの切り替え
       
        # ファイルに書き出し
        command_list = self.joistick_buffer[pre_index].values()
        for command_text in command_list:
            self.logger.write_command(command_text, True)
            
        self.joistick_buffer[pre_index].clear()        
    
    def swap_buffer(self):
        if self.write_thread.is_alive():
            self.write_thread.join()
        
        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.start()
        self.update_index_flag = False

    def capture_gamepad(self): 
        # 最初に接続されているジョイスティックを選択
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            
            for i in range(joystick.get_numaxes()):
                self.joistick_pos_dict[i] = 0.0
            
        else:
            print('ゲームパッドが接続されていません')
            self.logger.write_command('# ゲームパッドが接続されていません', True)
            return

        self.logger.start_log()        
        while AbstractCaptureDevice.capturing:
            if self.update_index_flag:
                self.swap_buffer()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

                # ゲームパッドのボタンが押されたとき
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.on_press_button(event.button)

                # ゲームパッドのボタンが離されたとき
                elif event.type == pygame.JOYBUTTONUP:
                    self.on_release_button(event.button)

                # ジョイスティックの軸が動いたとき
                elif event.type == pygame.JOYAXISMOTION:
                    # デッドゾーンの範囲内であれば何もしない
                    if self.dead_zone > abs(event.value):
                        continue
                    
                    self.on_move_joystick(event.axis, event.value)

                # ジョイスティックのハットスイッチが動いたとき
                elif event.type == pygame.JOYHATMOTION:
                    print(f"Joystick Hat {event.hat} moved to {event.value}")
                    
            time.sleep(SLEEP_TIME)
        
        print('ゲームパッドのキャプチャを終了')

        # 書き込み用スレッドのjoin
        if self.write_thread.is_alive():
            self.write_thread.join()

        # バッファ内のログを全て書き出し
        for temp_dict in self.joistick_buffer:
            for command_text in temp_dict.values():
                self.logger.write_command(command_text, True)
        
        self.logger.sort_and_fix_command_file()
        
    def on_press_button(self, button):
        if not AbstractCaptureDevice.capturing:
            return AbstractCaptureDevice.capturing
        
        # 既に押下中の場合は何もしない
        if button in self.button_flag_dict:
            if self.button_flag_dict[button]:
                return

        self.button_flag_dict[button] = True
        self.button_time_dict[button] = self.logger.get_elapsed_time()

        return AbstractCaptureDevice.capturing

    def on_release_button(self, button):
        if not AbstractCaptureDevice.capturing:
            return AbstractCaptureDevice.capturing

        elapsed_time = self.logger.get_elapsed_time()
                
        self.button_flag_dict[button] = False
        key_push_time:timedelta = elapsed_time - self.button_time_dict[button]        
        milli_second = int(key_push_time.total_seconds() * 1000)
        time_difference = elapsed_time - key_push_time
        command_text = CommandSeparater.format_command_gamepad_button(time_difference, button, milli_second)

        self.logger.write_command(command_text, True)
        AbstractCaptureDevice.add_capture_view(command_text)
        
        return AbstractCaptureDevice.capturing 
    
    
    def on_move_joystick(self, axis, value):
        self.joistick_pos_dict[axis] = value
        # 2で割った値がスティック番号になる
        stick_number = int(axis / 2)

        elapsed_time = self.logger.get_elapsed_time()
        command_text = CommandSeparater.format_command_gamepad_joystick(
            elapsed_time,
            stick_number,
            self.joistick_pos_dict[stick_number * 2],
            self.joistick_pos_dict[stick_number * 2 + 1]
            )

        # サイズ肥大化を防ぐために特定サイズ以上になった場合はインデックスの切り替え
        if len(self.joistick_buffer[self.index_joistick_buffer]) > MAX_BUFFER_SIZE:
            self.update_index_flag = True

        # 大量に記録されるので一回一回ファイルに書き込まずに時間をキーとした辞書に追加
        self.joistick_buffer[self.index_joistick_buffer][CommandSeparater.format_time(elapsed_time)] = command_text
        
        #self.logger.write_command(command_text, True)
        #self.add_capture_view(command_text)

