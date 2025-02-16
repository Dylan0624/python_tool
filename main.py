import os
import sys
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
# 手動設置 Qt plugin 路徑
conda_prefix = os.environ.get('CONDA_PREFIX', '')
if conda_prefix:
    qt_plugin_path = os.path.join(conda_prefix, 'lib', 'qt6', 'plugins')
    os.environ['QT_PLUGIN_PATH'] = qt_plugin_path

import shutil
from PyQt6.QtWidgets import QApplication
from UI.MainWindow import MainWindow

def remove_pycache_dirs(path):
    """
    遞迴刪除指定路徑下所有 __pycache__ 資料夾
    """
    for root, dirs, files in os.walk(path):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"已刪除: {pycache_path}")
            except Exception as e:
                print(f"刪除 {pycache_path} 時發生錯誤: {e}")

def main():
    # 取得 main.py 所在的目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 刪除所有子資料夾中的 __pycache__
    remove_pycache_dirs(base_dir)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()