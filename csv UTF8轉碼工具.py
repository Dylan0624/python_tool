import pandas as pd
import os
from pathlib import Path

def convert_csv_encoding(file_path, input_encoding='utf-8', output_encoding='utf-8-sig'):
    """
    轉換 CSV 檔案的編碼，並添加 BOM 標記
    
    參數:
        file_path: CSV 檔案路徑
        input_encoding: 輸入檔案的編碼（預設 utf-8）
        output_encoding: 輸出檔案的編碼（預設 utf-8-sig，會包含 BOM）
    """
    try:
        # 讀取 CSV 檔案
        df = pd.read_csv(file_path, encoding=input_encoding)
        
        # 直接覆蓋原檔案，使用 utf-8-sig 編碼（包含 BOM）
        df.to_csv(file_path, encoding=output_encoding, index=False)
        print(f"✓ 成功處理: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ 處理失敗 {file_path}: {str(e)}")
        return False

def process_all_directories(start_path="."):
    """
    遞迴處理指定目錄及其所有子目錄下的 CSV 檔案
    
    參數:
        start_path: 起始目錄路徑（預設為當前目錄）
    """
    # 轉換為 Path 物件
    start_dir = Path(start_path)
    
    # 計數器
    total_files = 0
    success_files = 0
    
    # 遞迴搜尋所有 CSV 檔案
    for csv_file in start_dir.rglob("*.csv"):
        total_files += 1
        if convert_csv_encoding(str(csv_file)):
            success_files += 1
    
    # 輸出處理結果統計
    print("\n處理完成!")
    print(f"總計處理檔案數: {total_files}")
    print(f"成功處理檔案數: {success_files}")
    print(f"失敗處理檔案數: {total_files - success_files}")

if __name__ == "__main__":
    # 從當前目錄開始處理
    print("開始處理所有 CSV 檔案...\n")
    process_all_directories()