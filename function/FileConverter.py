import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Union, Dict, Optional

from utils.log_manager import LogManager
from function.FormatManager import FormatManager


class FileConverter:
    """初始化 FileConverter"""

    def __init__(self):
        self.logger = LogManager()
        self.format_manager = FormatManager()

    def analyze_files(self, file_paths: Union[str, List[str]]) -> List[Dict]:
        """
        分析一個或多個檔案的類型和可用的轉換格式

        Args:
            file_paths: 單個檔案路徑或檔案路徑列表

        Returns:
            包含每個檔案分析結果的列表
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        results = []
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if not path.exists():
                    results.append({
                        'file_path': file_path,
                        'exists': False,
                        'error': 'File not found'
                    })
                    continue

                # 獲取檔案格式資訊
                format_info = self.format_manager.validate_format(file_path)
                if not format_info['valid']:
                    results.append({
                        'file_path': file_path,
                        'exists': True,
                        'supported': False,
                        'error': 'Unsupported format'
                    })
                    continue

                # 獲取可轉換的格式
                convertible_formats = self.get_convertible_formats(
                    format_info['category'],
                    format_info['subcategory']
                )

                results.append({
                    'file_path': file_path,
                    'exists': True,
                    'supported': True,
                    'category': format_info['category'],
                    'subcategory': format_info['subcategory'],
                    'current_format': format_info['current_format'],
                    'convertible_formats': convertible_formats
                })

            except Exception as e:
                self.logger.e(
                    'FileConverter',
                    f'Error analyzing file {file_path}: {str(e)}'
                )
                results.append({
                    'file_path': file_path,
                    'exists': True,
                    'error': str(e)
                })

        return results

    def get_convertible_formats(self, category: str, subcategory: str = None) -> List[str]:
        """
        獲取指定類別可轉換的格式列表

        Args:
            category: 檔案類別 (audio, video, image 等)
            subcategory: 子類別 (可選)

        Returns:
            可轉換的格式列表
        """
        try:
            formats = []
            if category and category in self.format_manager.formats:
                # 獲取所有該類別下的格式
                for subcat, extensions in self.format_manager.formats[category].items():
                    formats.extend(extensions)
                
                # 移除當前格式但保留同類型的其他格式
                if subcategory:
                    current_format = self.format_manager.formats[category].get(subcategory, [])
                    formats = [fmt for fmt in formats if fmt != current_format]

            return sorted(list(set(formats)))
        except Exception as e:
            self.logger.e('FileConverter', f'Error getting convertible formats: {str(e)}')
            return []

    def convert_files(
        self,
        file_paths: Union[str, List[str]],
        target_format: str,
        output_dir: Optional[str] = None,
        max_workers: int = 4
    ) -> List[Dict]:
        """
        轉換一個或多個檔案到指定格式

        Args:
            file_paths: 單個檔案路徑或檔案路徑列表
            target_format: 目標格式 (例如 '.mp3', '.jpg')
            output_dir: 輸出目錄 (可選，默認為源檔案目錄)
            max_workers: 最大同時轉換的檔案數

        Returns:
            轉換結果列表
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        # 驗證輸出目錄
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

        # 確保目標格式正確格式
        if not target_format.startswith('.'):
            target_format = f'.{target_format}'

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self._convert_single_file,
                    file_path,
                    target_format,
                    output_dir
                ): file_path
                for file_path in file_paths
            }

            for future in future_to_path:
                file_path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.e(
                        'FileConverter',
                        f'Error converting {file_path}: {str(e)}'
                    )
                    results.append({
                        'file_path': file_path,
                        'success': False,
                        'error': str(e)
                    })

        return results

    def _convert_single_file(
        self,
        file_path: str,
        target_format: str,
        output_dir: Optional[str] = None
    ) -> Dict:
        """
        轉換單個檔案（內部方法）

        Args:
            file_path: 檔案路徑
            target_format: 目標格式
            output_dir: 輸出目錄 (可選)

        Returns:
            轉換結果字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    'file_path': file_path,
                    'success': False,
                    'error': 'File not found'
                }

            # 驗證格式
            format_info = self.format_manager.validate_format(
                file_path, target_format
            )
            if not format_info['valid'] or not format_info['can_convert_to']:
                return {
                    'file_path': file_path,
                    'success': False,
                    'error': 'Unsupported conversion'
                }

            # 決定輸出路徑
            if output_dir:
                output_path = Path(output_dir) / f"{path.stem}{target_format}"
            else:
                output_path = path.with_suffix(target_format)

            # 根據檔案類型調用相應的轉換方法
            category = format_info['category']
            if category == 'image':
                success = self._convert_image(path, output_path)
            elif category == 'audio':
                success = self._convert_audio(path, output_path)
            elif category == 'video':
                success = self._convert_video(path, output_path)
            else:
                return {
                    'file_path': file_path,
                    'success': False,
                    'error': 'Unsupported file type'
                }

            return {
                'file_path': file_path,
                'success': success,
                'output_path': str(output_path) if success else None
            }

        except Exception as e:
            self.logger.e(
                'FileConverter',
                f'Error converting {file_path}: {str(e)}'
            )
            return {
                'file_path': file_path,
                'success': False,
                'error': str(e)
            }

    def _convert_image(self, input_path: Path, output_path: Path) -> bool:
        """
        轉換圖片檔案（需要實現具體轉換邏輯）
        """
        try:
            from PIL import Image

            image = Image.open(input_path)
            image.save(output_path)
            self.logger.i(
                'FileConverter',
                f'Successfully converted image: {input_path} -> {output_path}'
            )
            return True
        except Exception as e:
            self.logger.e(
                'FileConverter',
                f'Error converting image {input_path}: {str(e)}'
            )
            return False

    def _convert_audio(self, input_path: Path, output_path: Path) -> bool:
        """
        轉換音訊檔案（需要實現具體轉換邏輯）
        """
        try:
            import pydub

            audio = pydub.AudioSegment.from_file(str(input_path))
            fmt = output_path.suffix[1:]  # 移除點號
            audio.export(str(output_path), format=fmt)
            self.logger.i(
                'FileConverter',
                f'Successfully converted audio: {input_path} -> {output_path}'
            )
            return True
        except Exception as e:
            self.logger.e(
                'FileConverter',
                f'Error converting audio {input_path}: {str(e)}'
            )
            return False

    def _convert_video(self, input_path: Path, output_path: Path) -> bool:
        """
        轉換視訊檔案（需要實現具體轉換邏輯）
        """
        try:
            import ffmpeg

            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(stream, str(output_path))
            ffmpeg.run(stream)
            self.logger.i(
                'FileConverter',
                f'Successfully converted video: {input_path} -> {output_path}'
            )
            return True
        except Exception as e:
            self.logger.e(
                'FileConverter',
                f'Error converting video {input_path}: {str(e)}'
            )
            return False
