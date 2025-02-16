# Speech Translation Tool

一個基於 PyQt6 開發的語音轉文字及翻譯工具，支援多種語言之間的轉換。

## 功能特點
![alt text](<CleanShot 2025-02-16 at 23.50.45@2x.png>)

- 支援拖放或選擇音訊檔案
- 使用 OpenAI Whisper 進行語音辨識
- 支援多種 Whisper 模型（tiny 到 large）
- 多語言翻譯支援（英文、中文、法文、西班牙文、德文）
- 支援簡繁體中文轉換
- 可調整字體大小
- 支援匯出語音辨識和翻譯結果

## 系統需求

- Python 3.8+
- CUDA 支援（可選，用於 GPU 加速）
- 足夠的磁碟空間（用於下載模型）

## 安裝步驟

1. 克隆專案：
```bash
git clone https://github.com/Dylan0624/python_tool.git
cd python_tool
```

2. 安裝相依套件：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 執行主程式：
```bash
python main.py
```

2. 在應用程序中：
   - 選擇或拖放音訊檔案
   - 選擇合適的 Whisper 模型
   - 選擇原始語言和目標翻譯語言
   - 點擊「語音辨識」進行語音轉文字
   - 點擊「翻譯」將辨識結果翻譯成目標語言

## 支援的音訊格式

- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)

## 注意事項

- 首次運行時會自動下載所需的模型文件
- 翻譯功能需要網路連接
- GPU 加速需要安裝 CUDA 相關套件

## 授權說明

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 貢獻指南

歡迎提交 Issue 和 Pull Request。請確保您的程式碼符合現有的程式碼風格。