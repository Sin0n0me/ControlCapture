import threading
from capture_device import *

GAMEPAD_CAPTURE_LOG_FILE_NAME = 'gamepad_log.txt'
KEYBOARD_CAPTURE_LOG_FILE_NAME = 'keyboard_log.txt'
MOUSE_CAPTURE_LOG_FILE_NAME = 'mouse_log.txt'

class ControlCaptureThread:  
    
    thread_pool:list[threading.Thread] = []
    capturing = False
    
    def __init__(self) -> None:                
        self.record_keyboard = CaptureKeyboard(KEYBOARD_CAPTURE_LOG_FILE_NAME)
        self.record_mouse = CaptureMouse(MOUSE_CAPTURE_LOG_FILE_NAME)
        self.record_gamepad = CaptureGamePad(GAMEPAD_CAPTURE_LOG_FILE_NAME)

    def add_thread(self, thread:threading.Thread):
        self.thread_pool.append(thread)
        self.thread_pool[-1].start()

    def start_capture(self):
        if self.capturing:
           return
        
        ControlCaptureThread.capturing = True
        AbstractCaptureDevice.capturing = True
        self.add_thread(threading.Thread(target=self.record_gamepad.capture_gamepad))
        self.add_thread(threading.Thread(target=self.record_keyboard.capture_keyboard))
        self.add_thread(threading.Thread(target=self.record_mouse.capture_mouse))

    def stop_capture(self):
        if not ControlCaptureThread.capturing:
            return
        
        ControlCaptureThread.capturing = False        
        AbstractCaptureDevice.capturing = False

        for thread in ControlCaptureThread.thread_pool:
            if thread.is_alive():
                thread.join()
        
        ControlCaptureThread.thread_pool.clear()
        
        # 各ファイルに書き出したコマンドの結合
        CommandLogger.merge_command_files([
            GAMEPAD_CAPTURE_LOG_FILE_NAME,
            KEYBOARD_CAPTURE_LOG_FILE_NAME,
            MOUSE_CAPTURE_LOG_FILE_NAME
        ])

    @staticmethod
    def update():
        # キャプチャスレッドが全て停止しているかつスレッド生成クラスのキャプチャフラグが立っている場合は
        # 終了キー押下での終了なのでファイルに書き出して終了する
        if not AbstractCaptureDevice.capturing and ControlCaptureThread.capturing:
            ControlCaptureThread.capturing = False
            AbstractCaptureDevice.capturing = False

            # 各ファイルに書き出したコマンドの結合
            CommandLogger.merge_command_files([
                GAMEPAD_CAPTURE_LOG_FILE_NAME,
                KEYBOARD_CAPTURE_LOG_FILE_NAME,
                MOUSE_CAPTURE_LOG_FILE_NAME
            ])            
        
        
        
        
