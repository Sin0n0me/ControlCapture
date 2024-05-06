import threading
from datetime import datetime, timedelta
from .command_separator import CommandSeparater

COMMAND_FILE_NAME = 'command_list.txt'

# 各行を時間でソートするために(秒数, 元の行)のタプルのリストを作る
def line_to_seconds(line):
    try:
        time_part, text_part = line.strip().split(';')
    except Exception as e:
        print(f'error:{e}\nline:{line}')
        
    hour ,minutes, seconds = map(float, time_part.split(':'))
    total_seconds = hour * 3600 + minutes * 60 + seconds
    return total_seconds, line.strip()

class CommandLogger():
    
    def __init__(self, file_name:str) -> None:        
        self.lock = threading.Lock()
        self.is_write_command = True
        self.file_name = file_name
            
    def start_log(self):
        with open(self.file_name, 'w'):
            pass
        
        # キー押下時間取得用
        self.program_start_time = datetime.now()        
           
    def write_command(self, capture_data, capture_data_include_time=False) -> str:        
        if capture_data_include_time:
            start_time = ''
        else:
            start_time = CommandSeparater.format_time(self.get_elapsed_time()) + ';'
        
        log = start_time + capture_data + '\n'
        
        # 
        if self.is_write_command:
            with self.lock:
                with open(self.file_name, 'a') as file:
                    file.write(log) 
        
        return log 
    
    def get_elapsed_time(self) -> timedelta:
        return datetime.now() - self.program_start_time          

    def sort_and_fix_command_file(self):
        # ファイルを読み込んで処理
        with open(self.file_name, 'r') as file:
            lines = file.readlines()
            
        # 各行を秒数に変換し、ソートする
        sorted_lines = sorted(lines, key=line_to_seconds)
                
        # ソートされた内容を新しいファイルに書き出す
        with open(self.file_name, 'w') as file:
            for line in sorted_lines:
                if not line.endswith('\n'):
                    line += '\n'
                file.write(line)
        
    @staticmethod
    def merge_command_files(files:list[str]):
        command_list = []
        for file_name in files:
            with open(file_name, mode='r') as f:
                command_list.extend(f.readlines())
        
        # ソート
        sorted_command_list = sorted(command_list, key=line_to_seconds)
        
        with open(COMMAND_FILE_NAME,mode='w') as file:
            for command in sorted_command_list:                
                file.write(command)
         
