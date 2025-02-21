#function/EncodingConverter.py
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Union

from utils.log_manager import LogManager  # 假設你已有這個模組來管理日誌

class EncodingConverter:
    """
    用於轉換文字檔案編碼的類別，可以單檔或批量轉換檔案編碼
    """
    def __init__(self):
        self.logger = LogManager()

    def convert_file(self, file_path: Union[str, Path],
                     input_encoding: str = 'utf-8',
                     output_encoding: str = 'utf-8-sig') -> bool:
        """
        將單一檔案從指定的輸入編碼轉換為指定的輸出編碼

        參數:
            file_path: 檔案路徑
            input_encoding: 輸入檔案的編碼（預設：utf-8）
            output_encoding: 輸出檔案的編碼（預設：utf-8-sig，含 BOM）

        回傳:
            轉換成功回傳 True，否則回傳 False
        """
        file_path = Path(file_path)
        try:
            with file_path.open('r', encoding=input_encoding) as f:
                content = f.read()

            with file_path.open('w', encoding=output_encoding) as f:
                f.write(content)

            self.logger.i("EncodingConverter", f"成功轉換檔案: {file_path}")
            return True

        except Exception as e:
            self.logger.e("EncodingConverter", f"轉換檔案失敗 {file_path}: {str(e)}")
            return False

    def convert_files(self,
                      file_paths: Union[str, List[Union[str, Path]]],
                      input_encoding: str = 'utf-8',
                      output_encoding: str = 'utf-8-sig',
                      max_workers: int = 4) -> List[Dict]:
        """
        批量轉換多個檔案的編碼，支援多線程並行處理

        參數:
            file_paths: 單一檔案路徑或檔案路徑列表
            input_encoding: 輸入編碼
            output_encoding: 輸出編碼
            max_workers: 最大同時處理的線程數

        回傳:
            每個檔案轉換結果的列表，每個元素為一個包含檔案路徑與轉換狀態的字典
        """
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.convert_file, file, input_encoding, output_encoding): file
                for file in file_paths
            }
            for future in future_to_file:
                file = future_to_file[future]
                try:
                    success = future.result()
                    results.append({
                        'file_path': str(file),
                        'success': success
                    })
                except Exception as e:
                    results.append({
                        'file_path': str(file),
                        'success': False,
                        'error': str(e)
                    })
        return results

    def convert_directory(self,
                          directory: Union[str, Path] = ".",
                          input_encoding: str = 'utf-8',
                          output_encoding: str = 'utf-8-sig',
                          pattern: str = "*.csv",
                          max_workers: int = 4) -> List[Dict]:
        """
        遞迴處理指定目錄及其所有子目錄中符合模式的檔案，轉換其編碼

        參數:
            directory: 起始目錄（預設：當前目錄）
            input_encoding: 輸入編碼
            output_encoding: 輸出編碼
            pattern: 檔案搜尋模式（例如： "*.csv", "*.txt"）
            max_workers: 最大同時處理的線程數

        回傳:
            每個檔案轉換結果的列表
        """
        directory = Path(directory)
        files = list(directory.rglob(pattern))
        self.logger.i("EncodingConverter", f"在 {directory} 中找到 {len(files)} 個檔案符合模式 {pattern}")
        return self.convert_files(files, input_encoding, output_encoding, max_workers)
