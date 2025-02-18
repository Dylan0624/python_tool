# File Format Converter

一個跨平台的檔案格式轉換工具，支援音訊、視訊和圖片格式的批量轉換。

## 功能特點

- 支援多種檔案格式的轉換：
  - 音訊：WAV, FLAC, MP3, M4A 等
  - 視訊：MP4, AVI, MKV 等
  - 圖片：JPG, PNG, BMP, SVG 等
- 批量轉換功能
- 可自定義添加/移除支援的格式
- 自動記錄轉換過程日誌

## 系統需求

- Python 3.8 或以上
- 相關依賴套件（見 requirements.txt）
- FFmpeg（用於音訊和視訊轉換）

## 安裝步驟

1. 安裝 Python 依賴：
```bash
pip install -r requirements.txt
```

2. 安裝 FFmpeg：
   - Windows：下載 FFmpeg 並添加到系統環境變數
   - macOS：使用 Homebrew 安裝：`brew install ffmpeg`
   - Linux：使用套件管理器安裝：`sudo apt-get install ffmpeg`

## 使用方法

1. 基本使用：
```python
from function.FileConverter import FileConverter

# 初始化轉換器
converter = FileConverter()

# 分析檔案
results = converter.analyze_files('path/to/your/file.mp3')

# 轉換檔案
converter.convert_files('path/to/your/file.mp3', 'wav', output_dir='output')
```

2. 批量轉換：
```python
# 轉換多個檔案
files = ['file1.mp3', 'file2.mp3']
converter.convert_files(files, 'wav', output_dir='output')
```

3. 管理支援的格式：
```python
from function.FormatManager import FormatManager

format_manager = FormatManager()

# 添加新格式
format_manager.add_format('audio', 'lossless', '.aiff')

# 移除格式
format_manager.remove_format('audio', 'lossless', '.aiff')
```

## 專案結構

```
Converter/
├── config/
│   └── file_formats.json    # 格式配置文件
├── function/
│   ├── FileConverter.py     # 檔案轉換類
│   └── FormatManager.py     # 格式管理類
├── utils/
│   └── log_manager.py       # 日誌管理類
├── output/                  # 輸出目錄
├── requirements.txt         # 依賴套件
└── README.md               # 說明文件
```

## 注意事項

1. 確保已正確安裝 FFmpeg 並可在命令行中使用
2. 輸出目錄會自動創建在執行目錄下的 `output` 資料夾
3. 轉換大檔案時請注意磁碟空間

## License

MIT

## 貢獻指南

1. Fork 本專案
2. 創建特性分支
3. 提交變更
4. 發起 Pull Request

## 常見問題

Q: 為什麼某些格式無法轉換？  
A: 請確認已安裝 FFmpeg 且版本正確。

Q: 如何添加新的轉換格式？  
A: 使用 FormatManager 的 add_format 方法，或直接修改 config/file_formats.json。