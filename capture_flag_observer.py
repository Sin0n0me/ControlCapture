import threading

class CaptureFlagObserver():

    lock = threading.Lock()
    is_capture_start:bool = False
    is_target_start:bool = False
    
    capture_start_flag_callback_func = [()]
    capture_target_start_flag_callback_func = [()]
    
    @staticmethod
    def set_capture_flag(flag:bool):
        with CaptureFlagObserver.lock:
            CaptureFlagObserver.is_capture_start = flag        
        
        for func in CaptureFlagObserver.capture_start_flag_callback_func:
            func[0](*func[1])

    @staticmethod
    def get_capture_flag(flag:bool):
        return CaptureFlagObserver.is_capture_start
        
    @staticmethod
    def register_callback_on_changed_capture_start_flag(call_back:function, args:tuple):
        CaptureFlagObserver.capture_start_flag_callback_func.append((call_back, args))

    @staticmethod
    def set_capture_target_start_flag(flag:bool):
        with CaptureFlagObserver.lock:
            CaptureFlagObserver.is_capture_start = flag        
        
        for func in CaptureFlagObserver.capture_start_flag_callback_func:
            func[0](*func[1])

    @staticmethod
    def get_capture_target_start_flag(flag:bool):
        return CaptureFlagObserver.is_capture_start
        
    @staticmethod
    def register_callback_on_changed_capture_target_start_flag(call_back:function, args:tuple):
        CaptureFlagObserver.capture_start_flag_callback_func.append((call_back, args))
    

