#test.py
import os
from pathlib import Path
from function.FormatManager import FormatManager
from function.FileConverter import FileConverter
from utils.log_manager import LogManager

def main():
    # 初始化 Logger
    logger = LogManager()
    logger.i('Test', 'Starting converter test...')

    # 初始化轉換器
    converter = FileConverter()
    
    # 測試檔案路徑
    file_path = '/Users/dylan/Documents/data/file/excel/0211_generating組/patinya/音樂後測_qa.csv'
    
    # 1. 分析檔案
    logger.i('Test', f'Analyzing file: {file_path}')
    analysis_result = converter.analyze_files(file_path)
    
    # 打印分析結果
    for result in analysis_result:
        if result.get('supported', False):
            logger.i('Test', f"File analysis result:")
            logger.i('Test', f"- Category: {result['category']}")
            logger.i('Test', f"- Subcategory: {result['subcategory']}")
            logger.i('Test', f"- Current format: {result['current_format']}")
            logger.i('Test', f"- Can convert to: {', '.join(result['convertible_formats'])}")
        else:
            logger.e('Test', f"File analysis failed: {result.get('error', 'Unknown error')}")
    
    # 2. 測試轉換
    if analysis_result[0].get('supported', False):
        # 創建輸出目錄（在當前執行目錄下）
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        output_dir = current_dir / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 選擇目標格式（根據分析結果中的可轉換格式）
        convertible_formats = analysis_result[0].get('convertible_formats', [])
        if convertible_formats:
            target_format = convertible_formats[0]  # 使用第一個可用的轉換格式
            
            logger.i('Test', f'Converting file to {target_format}')
            conversion_results = converter.convert_files(
                file_path,
                target_format=target_format,
                output_dir=str(output_dir)
            )
            
            # 打印轉換結果
            for result in conversion_results:
                if result['success']:
                    logger.i('Test', f"Conversion successful!")
                    logger.i('Test', f"Output file: {result['output_path']}")
                else:
                    logger.e('Test', f"Conversion failed: {result.get('error', 'Unknown error')}")
        else:
            logger.w('Test', 'No convertible formats available')
    else:
        logger.w('Test', 'File not supported for conversion')

if __name__ == '__main__':
    main()


# test_encoding_converter.py
import os
from pathlib import Path
from function.EncodingConverter import EncodingConverter
from utils.log_manager import LogManager

def main():
    # 初始化 Logger
    logger = LogManager()
    logger.i("Test", "Starting EncodingConverter test...")

    # 建立 EncodingConverter 實例
    converter = EncodingConverter()

    # 測試單一檔案轉換：
    # 1. 定義測試檔案路徑（如果檔案不存在，則建立一個測試檔案）
    test_file = Path("test_file.txt")
    if not test_file.exists():
        with test_file.open("w", encoding="utf-8") as f:
            f.write("這是一個測試檔案，用於驗證編碼轉換功能。")
        logger.i("Test", f"Created test file: {test_file}")

    # 2. 轉換該檔案的編碼（由 utf-8 轉換為 utf-8-sig）
    success = converter.convert_file(test_file, input_encoding="utf-8", output_encoding="utf-8-sig")
    if success:
        logger.i("Test", f"Successfully converted file encoding: {test_file}")
    else:
        logger.e("Test", f"Failed to convert file encoding: {test_file}")

    # 測試目錄批量轉換：
    # 1. 建立一個測試目錄與幾個測試檔案
    test_dir = Path("output")
    test_dir.mkdir(exist_ok=True)
    for i in range(3):
        file_path = test_dir / f"sample_{i}.txt"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f"這是第 {i+1} 個測試檔案。")
    logger.i("Test", f"Created {3} test files in directory: {test_dir}")

    # 2. 對目錄下所有 .txt 檔案進行編碼轉換（由 utf-8 轉為 utf-8-sig）
    results = converter.convert_directory(directory=test_dir, pattern="*.txt", input_encoding="utf-8", output_encoding="utf-8-sig")
    for res in results:
        status = "Success" if res['success'] else "Failed"
        logger.i("Test", f"File: {res['file_path']} conversion status: {status}")

if __name__ == '__main__':
    main()
