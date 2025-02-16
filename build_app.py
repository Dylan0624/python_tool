# build_app.py
import PyInstaller.__main__
import os

# 設定項目根目錄
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=ImageReconstructor',
    '--windowed',  # 不顯示控制台窗口
    '--onedir',    # 創建單一目錄
    '--add-data=gui;gui',  # 添加額外資料夾
    '--add-data=util;util',
    '--add-data=config;config',  # 添加配置目錄
    '--add-data=data;data',      # 添加數據目錄
    '--add-data=output;output',  # 添加輸出目錄
    '--hidden-import=PyQt6',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtWidgets',
    '--hidden-import=PIL',
    '--clean',
    '--noconfirm',
])