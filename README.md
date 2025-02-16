# 拉曼光譜圖像重構工具

一個基於 Python 的 GUI 應用程序，用於重構和分析拉曼光譜圖像數據。這個工具提供了直觀的用戶界面，支持數據載入、處理和可視化。

## 功能特點

- 互動式圖形界面
  - 即時預覽重構結果
  - 支持拖放文件導入
  - 圖像放大查看功能
- 靈活的重構參數設置
  - 可配置小圖數量
  - 自定義目標尺寸
  - 多種掃描路徑選項
- 掃描路徑可視化
  - 實時顯示重構路徑
  - 網格線顯示選項
- 多格式輸出支持
  - TIFF 圖像格式
  - 文本數據格式
- 完整的日誌系統
  - 自動記錄操作過程
  - 錯誤追踪功能

## 系統要求

- Python 3.8 或更高版本
- 操作系統支持：
  - Windows 10/11
  - macOS
  - Linux

## 安裝步驟

1. 下載或克隆專案：
```bash
git clone [repository-url]
cd raman-image-tool
```

2. 創建虛擬環境：
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. 安裝依賴：
```bash
pip install -r requirements.txt
```

## 目錄結構
```
raman-image-tool/
├── config/                 # 配置文件目錄
│   ├── log_config.json    # 日誌配置
│   └── reconstruction_config.json  # 重構參數配置
├── data/                  # 數據文件目錄
├── gui/                   # GUI 組件
├── function/             # 核心功能模塊
├── util/                 # 工具類
├── output/               # 輸出文件目錄
├── logs/                 # 日誌文件目錄
└── main.py              # 程序入口
```

## 使用說明

1. 啟動程序：
```bash
python main.py
```

2. 數據導入：
   - 點擊"新增檔案"按鈕選擇文件
   - 或直接拖放文件到程序窗口

3. 設置重構參數：
   - 小圖數量：設置原始數據中的圖片數量
   - 目標尺寸：設置重構後的網格大小
   - 起始位置：選擇掃描起點
   - 掃描方向：選擇主要掃描方向

4. 預覽和保存：
   - 使用預覽功能檢查重構效果
   - 確認無誤後點擊保存

## 輸出文件

程序生成兩種格式的輸出文件：
- TIFF 格式：重構後的圖像文件
- TXT 格式：原始數據文件

文件命名格式：`reconstructed_image_[timestamp]_[dimensions].[extension]`

## 日誌系統

- 日誌文件位置：`logs/` 目錄
- 日誌級別：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 每日自動輪換
- 支持通過 `log_config.json` 配置

## 故障排除

常見問題：
1. 程序無法啟動
   - 檢查 Python 版本
   - 確認依賴包安裝完整
   
2. 無法載入文件
   - 確認文件格式正確
   - 檢查文件權限

3. 預覽顯示異常
   - 檢查參數設置
   - 確認數據格式

## 開發相關

歡迎貢獻代碼，請遵循以下步驟：
1. Fork 專案
2. 創建功能分支
3. 提交更改
4. 發起 Pull Request

## 許可證

MIT License

## 聯繫方式

如有問題或建議，請通過以下方式聯繫：
- Issue Tracker: [project-issues-url]
- Email: [contact-email]