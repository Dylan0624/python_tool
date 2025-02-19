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
            target_format = convertible_formats[-6]  # 使用第一個可用的轉換格式
            
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
