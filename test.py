# #test.py
# import os
# from pathlib import Path
# from function.FormatManager import FormatManager
# from function.FileConverter import FileConverter
# from utils.log_manager import LogManager

# def main():
#     # 初始化 Logger
#     logger = LogManager()
#     logger.i('Test', 'Starting converter test...')

#     # 初始化轉換器
#     converter = FileConverter()
    
#     # 測試檔案路徑
#     file_path = '/Users/dylan/Documents/data/file/excel/0211_generating組/patinya/音樂後測_qa.csv'
    
#     # 1. 分析檔案
#     logger.i('Test', f'Analyzing file: {file_path}')
#     analysis_result = converter.analyze_files(file_path)
    
#     # 打印分析結果
#     for result in analysis_result:
#         if result.get('supported', False):
#             logger.i('Test', f"File analysis result:")
#             logger.i('Test', f"- Category: {result['category']}")
#             logger.i('Test', f"- Subcategory: {result['subcategory']}")
#             logger.i('Test', f"- Current format: {result['current_format']}")
#             logger.i('Test', f"- Can convert to: {', '.join(result['convertible_formats'])}")
#         else:
#             logger.e('Test', f"File analysis failed: {result.get('error', 'Unknown error')}")
    
#     # 2. 測試轉換
#     if analysis_result[0].get('supported', False):
#         # 創建輸出目錄（在當前執行目錄下）
#         current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
#         output_dir = current_dir / 'output'
#         output_dir.mkdir(parents=True, exist_ok=True)
        
#         # 選擇目標格式（根據分析結果中的可轉換格式）
#         convertible_formats = analysis_result[0].get('convertible_formats', [])
#         if convertible_formats:
#             target_format = convertible_formats[0]  # 使用第一個可用的轉換格式
            
#             logger.i('Test', f'Converting file to {target_format}')
#             conversion_results = converter.convert_files(
#                 file_path,
#                 target_format=target_format,
#                 output_dir=str(output_dir)
#             )
            
#             # 打印轉換結果
#             for result in conversion_results:
#                 if result['success']:
#                     logger.i('Test', f"Conversion successful!")
#                     logger.i('Test', f"Output file: {result['output_path']}")
#                 else:
#                     logger.e('Test', f"Conversion failed: {result.get('error', 'Unknown error')}")
#         else:
#             logger.w('Test', 'No convertible formats available')
#     else:
#         logger.w('Test', 'File not supported for conversion')

# if __name__ == '__main__':
#     main()


# # test_encoding_converter.py
# import os
# from pathlib import Path
# from function.EncodingConverter import EncodingConverter
# from utils.log_manager import LogManager

# def main():
#     # 初始化 Logger
#     logger = LogManager()
#     logger.i("Test", "Starting EncodingConverter test...")

#     # 建立 EncodingConverter 實例
#     converter = EncodingConverter()

#     # 測試單一檔案轉換：
#     # 1. 定義測試檔案路徑（如果檔案不存在，則建立一個測試檔案）
#     test_file = Path("test_file.txt")
#     if not test_file.exists():
#         with test_file.open("w", encoding="utf-8") as f:
#             f.write("這是一個測試檔案，用於驗證編碼轉換功能。")
#         logger.i("Test", f"Created test file: {test_file}")

#     # 2. 轉換該檔案的編碼（由 utf-8 轉換為 utf-8-sig）
#     success = converter.convert_file(test_file, input_encoding="utf-8", output_encoding="utf-8-sig")
#     if success:
#         logger.i("Test", f"Successfully converted file encoding: {test_file}")
#     else:
#         logger.e("Test", f"Failed to convert file encoding: {test_file}")

#     # 測試目錄批量轉換：
#     # 1. 建立一個測試目錄與幾個測試檔案
#     test_dir = Path("output")
#     test_dir.mkdir(exist_ok=True)
#     for i in range(3):
#         file_path = test_dir / f"sample_{i}.txt"
#         with file_path.open("w", encoding="utf-8") as f:
#             f.write(f"這是第 {i+1} 個測試檔案。")
#     logger.i("Test", f"Created {3} test files in directory: {test_dir}")

#     # 2. 對目錄下所有 .txt 檔案進行編碼轉換（由 utf-8 轉為 utf-8-sig）
#     results = converter.convert_directory(directory=test_dir, pattern="*.txt", input_encoding="utf-8", output_encoding="utf-8-sig")
#     for res in results:
#         status = "Success" if res['success'] else "Failed"
#         logger.i("Test", f"File: {res['file_path']} conversion status: {status}")

# if __name__ == '__main__':
#     main()

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path
from function.EncodingConverter import EncodingConverter
from function.FileConverter import FileConverter
from utils.log_manager import LogManager

class ConverterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("檔案轉換工具")
        self.root.geometry("800x500")
        
        self.encoding_converter = EncodingConverter()
        self.file_converter = FileConverter()
        self.logger = LogManager()
        
        self.setup_ui()
    
    def setup_ui(self):
        # 檔案選擇區域
        self.file_frame = ttk.LabelFrame(self.root, text="檔案選擇", padding=10)
        self.file_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(self.file_frame, text="選擇檔案", command=self.select_file).pack(side="left")
        ttk.Button(self.file_frame, text="選擇目錄", command=self.select_directory).pack(side="left", padx=5)
        
        self.file_listbox = tk.Listbox(self.file_frame, height=5)
        self.file_listbox.pack(fill="x", pady=5)
        
        # 編碼轉換區域
        self.encoding_frame = ttk.LabelFrame(self.root, text="編碼轉換", padding=10)
        self.encoding_frame.pack(side="left", fill="y", padx=10, pady=5)
        
        ttk.Label(self.encoding_frame, text="輸入編碼:").grid(row=0, column=0, padx=5, pady=5)
        self.input_encoding = ttk.Combobox(self.encoding_frame, values=["utf-8", "utf-16", "ascii"])
        self.input_encoding.set("utf-8")
        self.input_encoding.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.encoding_frame, text="輸出編碼:").grid(row=1, column=0, padx=5, pady=5)
        self.output_encoding = ttk.Combobox(self.encoding_frame, values=["utf-8-sig", "utf-8", "utf-16"])
        self.output_encoding.set("utf-8-sig")
        self.output_encoding.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.encoding_frame, text="轉換編碼", command=self.convert_encoding).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 格式轉換區域
        self.format_frame = ttk.LabelFrame(self.root, text="格式轉換", padding=10)
        self.format_frame.pack(side="left", fill="y", padx=10, pady=5)
        
        ttk.Label(self.format_frame, text="當前格式:").grid(row=0, column=0, padx=5, pady=5)
        self.current_format = ttk.Label(self.format_frame, text="N/A")
        self.current_format.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.format_frame, text="目標格式:").grid(row=1, column=0, padx=5, pady=5)
        self.target_format = ttk.Combobox(self.format_frame)
        self.target_format.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.format_frame, text="分析檔案", command=self.analyze_file).grid(row=2, column=0, pady=10)
        ttk.Button(self.format_frame, text="轉換格式", command=self.convert_format).grid(row=2, column=1, pady=10)
        
        # 日誌區域
        self.log_frame = ttk.LabelFrame(self.root, text="日誌", padding=10)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(self.log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if file_path:
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(tk.END, file_path)
            self.analyze_file()
    
    def select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.file_listbox.delete(0, tk.END)
            files = list(Path(dir_path).rglob("*.*"))
            for f in files:
                self.file_listbox.insert(tk.END, str(f))
    
    def analyze_file(self):
        files = self.file_listbox.get(0, tk.END)
        if not files:
            messagebox.showwarning("警告", "請先選擇檔案！")
            return
        
        analysis = self.file_converter.analyze_files(files[0])
        if analysis and analysis[0].get("supported", False):
            self.current_format.config(text=analysis[0]["current_format"])
            self.target_format["values"] = analysis[0]["convertible_formats"]
            self.target_format.set(analysis[0]["convertible_formats"][0] if analysis[0]["convertible_formats"] else "")
            self.log_text.insert(tk.END, f"分析完成: {files[0]}\n")
        else:
            self.current_format.config(text="N/A")
            self.target_format["values"] = []
            self.log_text.insert(tk.END, f"分析失敗: {analysis[0].get('error', 'Unknown error')}\n")
    
    def convert_encoding(self):
        files = self.file_listbox.get(0, tk.END)
        if not files:
            messagebox.showwarning("警告", "請先選擇檔案或目錄！")
            return
        
        input_enc = self.input_encoding.get()
        output_enc = self.output_encoding.get()
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "開始編碼轉換...\n")
        
        if len(files) == 1:
            success = self.encoding_converter.convert_file(files[0], input_enc, output_enc)
            self.log_text.insert(tk.END, f"轉換 {files[0]} {'成功' if success else '失敗'}\n")
        else:
            results = self.encoding_converter.convert_directory(files[0], input_enc, output_enc, pattern="*.*")
            for res in results:
                self.log_text.insert(tk.END, f"檔案: {res['file_path']} {'成功' if res['success'] else '失敗'}\n")
    
    def convert_format(self):
        files = self.file_listbox.get(0, tk.END)
        if not files:
            messagebox.showwarning("警告", "請先選擇檔案！")
            return
        
        target = self.target_format.get()
        if not target:
            messagebox.showwarning("警告", "請選擇目標格式！")
            return
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"開始格式轉換到 {target}...\n")
        
        results = self.file_converter.convert_files(files, target, output_dir="output")
        for res in results:
            if res["success"]:
                self.log_text.insert(tk.END, f"轉換成功: {res['output_path']}\n")
            else:
                self.log_text.insert(tk.END, f"轉換失敗: {res.get('error', 'Unknown error')}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterUI(root)
    root.mainloop()