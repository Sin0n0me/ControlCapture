import threading
import os
import subprocess
import time
from tkinter import Tk, messagebox
from tkinter import ttk
from .abstract_widget import *
from capture_device.abstract_capture_device import AbstractCaptureDevice

EXECUTE_EXTENDS =[
    # Windows
    '.exe',
    '.bat',
    '.cmd',
    '.ps1',
    '.vbs',
    
    # Linux
    '', # 拡張子なしは実行可能バイナリ
    '.sh',
    '.py',
    
]

class StartProcess(AbstractWidget):
    
    def __init__(self, root: Tk):
        super().__init__(root)

        self.run_thread:threading.Thread = None
        self.search_thread:threading.Thread = None
        self.tkinter_update_lock = threading.Lock()

        # 情報用ラベル
        search_label = tkinter.Label(self.root, text='リストからキャプチャ対象を選択してください。\n別ディレクトリの場合はパスを入力してください(Enterで検索開始します)') 
        search_label.pack(fill='both', expand=True)
        self.target_info_label = tkinter.Label(self.root, text='キャプチャ対象を選択してください')
        self.target_info_label.pack(fill='both', expand=True)

        # Entryウィジェット（テキスト入力ボックス）
        self.string_var = tkinter.StringVar()
        self.string_var.set(os.curdir)
        self.search_entry = tkinter.Entry(self.root, textvariable=self.string_var, font=('', 16, 'bold'))
        self.search_entry.bind('<Return>', self.on_enter_search_box)
        self.search_entry.pack(fill='both', expand=True)

        # プロセス名の選択用プルダウンメニュー
        self.process_var = tkinter.StringVar()
        self.process_var.trace_add('write',  lambda name, index, mode: self.on_select_process_list())
        self.process_list = ttk.Combobox(self.root, state='readonly', textvariable=self.process_var, font=('', 16))
        self.process_list.pack(fill='both', expand=True)
        
        # 先に検索しておく
        self.on_enter_search_box(None)

    def on_close(self):
        if self.run_thread:
            if self.run_thread.is_alive():
                self.run_thread.join()
        
        if self.search_thread:
            if self.search_thread.is_alive():
                self.search_thread.join()        

    def on_change_capture_flag(self, flag:bool):
        if flag:
            self.search_entry.config(state='readonly')            
        else:
            self.search_entry.config(state='normal')

    def on_change_process_start(self, flag:bool):
        if not flag:
            if self.run_thread:
                if self.run_thread.is_alive():
                    self.run_thread.join()
            
            return
        
        # そもそも存在しなければ何もしない
        file_path = self.process_var.get()
        print(file_path)
        if not os.path.exists(file_path):
            self.notify_process_start(False)
            messagebox.showerror('エラー', 'キャプチャする対象を選択してください')
            return
        
        # ディレクトリであれば何もしない
        if os.path.isdir(file_path):
            self.notify_process_start(False)
            messagebox.showerror('エラー', 'キャプチャする対象を選択してください')            
            return
        
        # 実行可能でなければ何もしない
        if not os.access(file_path, os.X_OK):
            self.notify_process_start(False)
            messagebox.showerror('エラー', 'キャプチャする対象を選択してください')
            return
        
        # キャプチャ対象の実行
        self.run_thread = threading.Thread(target=self.run_file,args=(file_path,))
        self.run_thread.start()
        
    def run_file(self, file_path:str):        
        if not self.is_executable_file(file_path):
            return
        
        root, extends = os.path.splitext(file_path)
        command = []
        target_exit = False
        try:
            if extends == '.py':
                command.append('python')                
            
            # 実行&終了まで待機
            # 終了時にキャプチャフラグを折る
            command.append(file_path)
            process = subprocess.Popen(command)
            
            # キャプチャスレッドが開始するまで待機
            while not AbstractCaptureDevice.capturing:
                if process.poll() is not None:
                    target_exit = True
                    break
                
                time.sleep(0.00001)
            
            # キャプチャが終了するかキャプチャ対象が終了するまでループ
            while AbstractWidget.capture_flag and AbstractCaptureDevice.capturing:
                if process.poll() is not None:
                    target_exit = True
                    break
                time.sleep(0.00001)
            
            # コンフィグから終了時にキャプチャ対象を落とすか選択させてもよさそう?
            # process.kill()
        except Exception as e:
            print(e)
            messagebox.showerror('エラー', 'キャプチャ対象の実行に失敗しました')
        else:
            if target_exit:
                AbstractCaptureDevice.capturing = False
                messagebox.showinfo('情報', 'キャプチャ対象が終了しました')
            else:
                messagebox.showinfo('情報', 'キャプチャを終了しました')
                
        finally:
            AbstractWidget.capture_flag = False
            AbstractWidget.process_start = False


    def on_enter_search_box(self, event):
        if not self.search_thread:
            self.search_thread = threading.Thread(target=self.search_executable_file)
        else:
            if self.search_thread.is_alive():
                self.search_thread.join()
            self.search_thread = threading.Thread(target=self.search_executable_file)

        self.search_thread.start()
        with self.tkinter_update_lock:
            self.target_info_label['text'] = '実行可能ファイル検索中...'

    def search_executable_file(self):
        executable_file_path = self.string_var.get()
        files_list = [] 
        for file in os.listdir(executable_file_path):
            file_path = os.path.join(executable_file_path, file)

            # 実行可能な拡張子でなければ追加しない
            if not self.is_executable_file(file_path):
                continue

            # 実行可能でなければ追加しない
            if not os.access(file_path, os.X_OK):
                continue
            
            # 実行可能でなければ追加しない
            if not os.path.isfile(file_path):
                continue
            
            files_list.append(file_path)
            
        self.process_list['values'] = files_list 
        with self.tkinter_update_lock:
            self.target_info_label['text'] = f'検索が完了しました({len(files_list)}件ヒットしました)'            

    def on_select_process_list(self):
        if not self.search_thread:
            return
                
        if self.search_thread.is_alive():
            self.search_thread.join()

    @staticmethod
    def is_executable_file(file_path):
        # ファイル名と拡張子を分割
        root, extends = os.path.splitext(file_path)
        return extends in EXECUTE_EXTENDS
