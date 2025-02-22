# File Format Converter
一個跨平台的檔案格式轉換工具，支援音訊、視訊、圖片和文字檔案的批量轉換，具備直觀的 GUI 介面。

## 功能特點
- **多種檔案格式轉換**：
  - 音訊：WAV、FLAC、MP3、M4A 等
  - 視訊：MP4、AVI、MKV 等
  - 圖片：JPG、PNG、BMP、SVG 等
  - 文字：CSV、TSV、TXT 等
- **批量轉換**：支援多檔案同時處理
- **自訂格式**：可添加或移除支援的檔案格式
- **日誌記錄**：自動記錄轉換過程至日誌檔案
- **文字檔案專屬功能**：
  - CSV 轉 TSV（Tab 分隔）
  - 一般文字檔案格式轉換
  - 編碼轉換（預設 UTF-8，支援 UTF-8-SIG 等）
- **GUI 介面**：支援拖曳檔案/資料夾、檔案分析與轉換

## 系統需求
- Python 3.8 或以上
- 依賴套件（見 `requirements.txt`）
- FFmpeg（音訊/視訊轉換）
- Pandas（文字檔案處理）

## 安裝步驟
1. **安裝 Python 依賴**：
   ```bash
   pip install -r requirements.txt
   ```
2. **安裝 FFmpeg**：
   - Windows：下載 FFmpeg 並加入系統環境變數
   - macOS：`brew install ffmpeg`
   - Linux：`sudo apt-get install ffmpeg`

## 使用方法
### GUI 使用
1. 啟動程式：
   ```bash
   python main.py
   ```
2. 操作步驟：
   - **選擇檔案/資料夾**：點擊「選擇檔案」或「選擇目錄」，或直接拖曳檔案/資料夾至虛線框區域。
   - **分析檔案**：點擊「分析檔案」查看當前格式與可轉換格式。
   - **編碼轉換**：選擇輸入/輸出編碼，點擊「轉換編碼」。
   - **格式轉換**：選擇目標格式，點擊「轉換格式」。
   - **查看日誌**：轉換結果顯示於下方日誌區域。

### 程式碼使用
1. **基本轉換**：
   ```python
   from function.FileConverter import FileConverter
   converter = FileConverter()
   results = converter.analyze_files("path/to/file.mp3")
   converter.convert_files("path/to/file.mp3", "wav", output_dir="output")
   ```
2. **批量轉換**：
   ```python
   files = ["file1.mp3", "file2.mp3"]
   converter.convert_files(files, "wav", output_dir="output")
   ```
3. **文字檔案轉換**：
   ```python
   # CSV 轉 TSV
   converter.convert_files("data.csv", "tsv", output_dir="output")
   # 編碼轉換
   from function.EncodingConverter import EncodingConverter
   encoder = EncodingConverter()
   encoder.convert_file("file.txt", input_encoding="utf-8", output_encoding="utf-8-sig")
   ```
4. **管理格式**：
   ```python
   from function.FormatManager import FormatManager
   fm = FormatManager()
   fm.add_format("text", "document", ".tsv")
   fm.remove_format("text", "document", ".tsv")
   ```

## 專案結構
```
Converter/
├── GUI/
│   └── MainUI.py            # GUI 介面實現
├── config/
│   ├── file_formats.json    # 格式配置文件
│   └── log_config.json      # 日誌配置文件
├── function/
│   ├── EncodingConverter.py # 編碼轉換類
│   ├── FileConverter.py     # 檔案轉換類
│   ├── FormatManager.py     # 格式管理類
│   └── __init__.py
├── logs/                    # 日誌存放目錄
├── output/                  # 轉換輸出目錄
├── utils/
│   ├── log_manager.py       # 日誌管理類
│   └── __init__.py
├── main.py                  # 程式入口
├── requirements.txt         # 依賴套件
├── test.py                  # 測試腳本
└── README.md                # 說明文件
```

## 文字檔案轉換說明
- **支援轉換**：
  - CSV 轉 TSV：逗號分隔轉為 Tab 分隔
  - 一般文字：保留內容，變更副檔名
  - 編碼轉換：支援 UTF-8、UTF-8-SIG、UTF-16 等
- **注意事項**：
  - CSV 轉換移除索引欄位
  - 預設使用 UTF-8 編碼
  - 原始檔案保持不變
  - 日誌記錄詳細轉換資訊

## 注意事項
- 確保 FFmpeg 已加入系統路徑
- 輸出預設存於 `output/` 目錄
- 大檔案轉換前檢查磁碟空間
- 文字轉換建議先測試小檔案

## License
MIT

## 貢獻指南
1. Fork 專案
2. 創建特性分支（`git checkout -b feature/new-feature`）
3. 提交變更（`git commit -m "Add new feature"`)
4. 推送到遠端（`git push origin feature/new-feature`）
5. 發起 Pull Request

## 常見問題
- **Q：為何某些格式無法轉換？**  
  A：檢查 FFmpeg 是否正確安裝並可執行。
- **Q：如何新增格式？**  
  A：使用 `FormatManager.add_format()` 或編輯 `file_formats.json`。
- **Q：CSV 轉換亂碼？**  
  A：確認原始檔案編碼，必要時指定正確編碼。
- **Q：如何處理大檔案？**  
  A：先測試小檔案，確保穩定後再處理