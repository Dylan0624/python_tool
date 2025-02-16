# main.py
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from util.log_manager import LogManager
import sys
import os
import shutil

def clean_pycache():
    """
    遞迴删除當前目錄下所有的 __pycache__ 文件夾
    """
    current_dir = os.getcwd()
    deleted_count = 0
    
    for root, dirs, files in os.walk(current_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                deleted_count += 1
                print(f"已删除: {pycache_path}")
            except Exception as e:
                print(f"删除失敗 {pycache_path}: {str(e)}")
                
    print(f"清理完成! 共删除 {deleted_count} 個 __pycache__ 目錄")

def main():
    # 啟動程式前先清理 __pycache__
    clean_pycache()
    
    app = QApplication(sys.argv)
    logger = LogManager()
    window = MainWindow(logger)
    window.showMaximized() 
    sys.exit(app.exec())

if __name__ == "__main__":    
    main()