import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Union

from utils.log_manager import LogManager


class FormatManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FormatManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """初始化 FormatManager 實例"""
        self.logger = LogManager()

        # 根據執行環境設定基礎目錄
        if getattr(sys, 'frozen', False):
            if sys.platform == 'win32':
                base_dir = Path(os.environ['APPDATA']) / 'Converter'
            else:
                base_dir = Path.home() / '.Converter'
        else:
            base_dir = Path(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))

        # 設定配置目錄及檔案路徑
        self.config_dir = base_dir / 'config'
        self.formats_path = self.config_dir / 'file_formats.json'

        # 確保配置目錄存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 載入格式配置
        self.formats = self.load_formats()

    def load_formats(self) -> Dict:
        """從 JSON 檔案載入格式配置"""
        try:
            if self.formats_path.exists():
                with open(self.formats_path, 'r', encoding='utf-8') as f:
                    formats = json.load(f)

                # 過濾掉 `encoding_formats`，確保遍歷的都是檔案格式
                formats = {k: v for k, v in formats.items() if isinstance(v, dict) and k != "encoding_formats"}

                self.logger.i(
                    'FormatManager',
                    f'已從 {self.formats_path} 載入格式配置'
                )
                return formats
            else:
                self.logger.w(
                    'FormatManager',
                    '找不到格式配置檔案，將建立預設配置'
                )
                return self.create_default_formats()
        except Exception as e:
            self.logger.e(
                'FormatManager',
                f'載入格式配置時出錯: {str(e)}'
            )
            return self.create_default_formats()

    def save_formats(self) -> bool:
        """儲存目前的格式配置到 JSON 檔案"""
        try:
            with open(self.formats_path, 'w', encoding='utf-8') as f:
                json.dump(self.formats, f, indent=2, ensure_ascii=False)
            self.logger.i('FormatManager', '格式配置儲存成功')
            return True
        except Exception as e:
            self.logger.e(
                'FormatManager',
                f'儲存格式配置時出錯: {str(e)}'
            )
            return False

    def create_default_formats(self) -> Dict:
        """建立並儲存預設格式配置"""
        default_formats = {
            "audio": {
                "lossless": [".wav", ".flac"],
                "lossy": [".mp3", ".m4a"]
            },
            "video": {
                "common": [".mp4", ".avi", ".mkv"]
            },
            "image": {
                "raster": [".jpg", ".png", ".bmp"],
                "vector": [".svg"]
            }
        }
        self.formats = default_formats
        self.save_formats()
        return default_formats

    def add_format(self, category: str, subcategory: str, extension: str) -> bool:
        """
        新增格式副檔名到指定的類別和子類別中

        Args:
            category: 主類別（例如：'audio'、'video'、'image'）
            subcategory: 子類別（例如：'lossless'、'lossy'、'raster'）
            extension: 要新增的檔案副檔名（例如：'.mp3'、'.jpg'）

        Returns:
            新增成功回傳 True，否則回傳 False
        """
        try:
            if not extension.startswith('.'):
                extension = f'.{extension}'

            if category not in self.formats:
                self.formats[category] = {}

            if subcategory not in self.formats[category]:
                self.formats[category][subcategory] = []

            if extension not in self.formats[category][subcategory]:
                self.formats[category][subcategory].append(extension)
                self.save_formats()
                self.logger.i(
                    'FormatManager',
                    f'已新增格式: {extension} 至 {category}/{subcategory}'
                )
                return True

            return False
        except Exception as e:
            self.logger.e(
                'FormatManager',
                f'新增格式時出錯: {str(e)}'
            )
            return False

    def remove_format(
        self, category: str, subcategory: str, extension: str
    ) -> bool:
        """
        從指定的類別和子類別中移除格式副檔名

        Args:
            category: 主類別（例如：'audio'、'video'、'image'）
            subcategory: 子類別（例如：'lossless'、'lossy'、'raster'）
            extension: 要移除的檔案副檔名（例如：'.mp3'、'.jpg'）

        Returns:
            移除成功回傳 True，否則回傳 False
        """
        try:
            if not extension.startswith('.'):
                extension = f'.{extension}'

            if (
                category in self.formats and
                subcategory in self.formats[category] and
                extension in self.formats[category][subcategory]
            ):
                self.formats[category][subcategory].remove(extension)
                self.save_formats()
                self.logger.i(
                    'FormatManager',
                    f'已從 {category}/{subcategory} 移除格式: {extension}'
                )
                return True

            return False
        except Exception as e:
            self.logger.e(
                'FormatManager',
                f'移除格式時出錯: {str(e)}'
            )
            return False

    def get_supported_formats(
        self, category: str = None, subcategory: str = None
    ) -> List[str]:
        """
        取得支援的格式列表，可依類別或子類別進行篩選

        Args:
            category: 選擇性主類別篩選
            subcategory: 選擇性子類別篩選

        Returns:
            經排序後的支援格式列表
        """
        try:
            formats = []
            if category and category in self.formats:
                if subcategory and subcategory in self.formats[category]:
                    formats.extend(self.formats[category][subcategory])
                elif not subcategory:
                    for subcat in self.formats[category].values():
                        formats.extend(subcat)
            elif not category:
                for cat in self.formats.values():
                    for subcat in cat.values():
                        formats.extend(subcat)
            return sorted(list(set(formats)))
        except Exception as e:
            self.logger.e(
                'FormatManager',
                f'取得支援格式列表時出錯: {str(e)}'
            )
            return []

    def validate_format(
        self, file_path: Union[str, Path], target_format: str = None
    ) -> Dict:
        """
        驗證檔案格式是否支援，並確定其所屬的類別與子類別

        Args:
            file_path: 要驗證的檔案路徑
            target_format: 選擇性目標格式，用於檢查是否可轉換

        Returns:
            包含驗證結果的字典
        """
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            result = {
                "valid": False,
                "category": None,
                "subcategory": None,
                "current_format": extension,
                "can_convert_to": target_format is None,
            }

            # 根據檔案副檔名找出對應的類別與子類別
            for category, subcats in self.formats.items():
                for subcat, extensions in subcats.items():
                    if extension in extensions:
                        result.update({
                            "valid": True,
                            "category": category,
                            "subcategory": subcat,
                        })

                        # 若指定目標格式則檢查是否可轉換
                        if target_format:
                            if not target_format.startswith('.'):
                                target_format = f'.{target_format}'
                            result["can_convert_to"] = any(
                                target_format in exts
                                for exts in self.formats[category].values()
                            )

                        return result

            return result
        except Exception as e:
            self.logger.e(
                'FormatManager',
                f'驗證格式時出錯: {str(e)}'
            )
            return {"valid": False, "error": str(e)}
