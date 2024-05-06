import psutil
import re

class ProcessView():
    def __init__(self) -> None:
        self.process_path_dict = {}
        self.process_pid_dict = {}
    
    # プロセスリストの取得
    def get_processes(self, mach_text:str):
        # 現在実行中の全プロセスのPIDと名前を取得
        # 初期化する
        process_name_list = []
        self.process_path_dict = {} 
        self.process_pid_dict = {}
        re_compile = re.compile(mach_text.lower())
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status']):
            try:                
                # プロセスのPID, 名前, パス, ステータスを取得
                pid = proc.info['pid']
                name = proc.info['name']
                exe = proc.info['exe']
                status = proc.info['status']
                
                # 名前の条件にマッチしなければ弾く
                if not re_compile.search(name.lower()):
                    continue
                        
                # username == current_user and
                if status == psutil.STATUS_RUNNING:
                    if name in self.process_pid_dict:
                        self.process_pid_dict[name].append(pid)
                    else:
                        self.process_pid_dict[name] = [pid]
                    self.process_path_dict[name] = exe
                    
                    process_name_list.append(name) 
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # アクセスできないプロセスは無視
        
        process_name_list = list(set(process_name_list))
        process_name_list = sorted(process_name_list)
        
        return process_name_list
    
    # プロセスが生きているか確認する
    def check_pid(self, name):        
        # 辞書に存在しなければ生きていないと判断    
        if name not in self.process_pid_dict:
            print(f'{name}が存在しません')
            return False
        
        # マルチスレッドなどで複数のPIDが生成されるので1つでも生きていたら生きていると判定する
        pid_list = self.process_pid_dict[name]
        for pid in pid_list:
            try:
                process = psutil.Process(pid)
                if process.is_running():                    
                    return True
            except psutil.NoSuchProcess:
                self.process_pid_dict[name].remove(pid) # 見つからなければ削除

        print(f'実行中のPIDが存在しません')
        return False
