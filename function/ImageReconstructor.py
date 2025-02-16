# function/ImageReconstructor
import time
import numpy as np
import json
from pathlib import Path
from PIL import Image
import os
from enum import Enum
from util.log_manager import LogManager

class StartCorner(Enum):
    """起始角落的枚舉"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

class FirstDirection(Enum):
    """第一個移動方向的枚舉"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class SecondDirection(Enum):
    """第二個移動方向的枚舉"""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

class ImageReconstructor:
    def __init__(self, input_data_path, output_path, logger):
        """
        初始化圖像重構器
        
        Parameters:
        input_data_path: str, 輸入數據的路徑
        output_path: str, 輸出圖像的路徑
        logger: LogManager instance
        """
        self.input_path = input_data_path
        self.output_path = output_path
        self.logger = logger
        self.raw_data = None
        
        # 基本參數
        self.num_images = None  # 小圖數量
        self.target_width = None  # 目標寬度
        self.target_height = None  # 目標高度
        
        # 路徑相關參數
        self.start_corner = None
        self.first_direction = None
        self.second_direction = None
        
        # 確保輸出目錄存在
        os.makedirs(output_path, exist_ok=True)
        
        self.logger.i("ImageReconstructor", f"初始化完成，輸入路徑: {input_data_path}")

    def load_data(self):
        """
        載入原始數據，自動偵測和適應數據維度
        """
        try:
            self.logger.d("ImageReconstructor", f"開始載入數據: {self.input_path}")
            with open(self.input_path, 'r') as file:
                lines = file.readlines()
                
            # 通過分析數據結構來確定維度
            processed_lines = []
            for line in lines:
                # 移除空白並分割數字
                numbers = [float(x) for x in line.strip().split()]
                if numbers:  # 確保不是空行
                    processed_lines.append(numbers)
            
            # 轉換為numpy數組
            self.raw_data = np.array(processed_lines)
            self.logger.i("ImageReconstructor", f"成功載入數據，形狀: {self.raw_data.shape}")
        except Exception as e:
            self.logger.e("ImageReconstructor", f"載入數據失敗: {str(e)}")
            raise

    def load_reconstruction_params(self, config_path):
        """
        從配置文件讀取重構參數
        
        Parameters:
        config_path: str, 配置文件的路徑（JSON格式）
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
            
            # 數字到枚舉的映射
            corner_map = {
                0: StartCorner.TOP_LEFT,
                1: StartCorner.TOP_RIGHT,
                2: StartCorner.BOTTOM_LEFT,
                3: StartCorner.BOTTOM_RIGHT
            }
            
            direction_map = {
                0: FirstDirection.UP,
                1: FirstDirection.DOWN,
                2: FirstDirection.LEFT,
                3: FirstDirection.RIGHT
            }
            
            # 從配置中獲取參數
            params = config['parameters']
            
            # 設置參數
            self.set_reconstruction_params(
                num_images=params['num_images'],
                target_width=params['target_width'],
                target_height=params['target_height'],
                start_corner=corner_map[params['start_corner']],
                first_direction=direction_map[params['first_direction']],
                second_direction=direction_map[params['second_direction']]
            )
            
            self.logger.i("ImageReconstructor", f"已從配置文件 {config_path} 載入參數")
            
        except Exception as e:
            self.logger.e("ImageReconstructor", f"載入配置文件失敗: {str(e)}")
            raise

    def set_reconstruction_params(self, num_images, target_width, target_height,
                            start_corner=StartCorner.BOTTOM_RIGHT,
                            first_direction=FirstDirection.RIGHT,
                            second_direction=SecondDirection.LEFT):
        """
        設置重構參數
        
        Parameters:
        num_images: int, 拍攝的小圖數量
        target_width: int, 目標拼接寬度
        target_height: int, 目標拼接高度
        start_corner: StartCorner, 起始角落
        first_direction: FirstDirection, 第一個移動方向
        second_direction: SecondDirection, 第二個移動方向
        """
        self.num_images = num_images
        self.target_width = target_width
        self.target_height = target_height
        self.start_corner = start_corner
        self.first_direction = first_direction
        self.second_direction = second_direction
        
        # 使用枚舉的名稱而不是值來記錄日誌
        self.logger.i("ImageReconstructor", 
                    f"設置參數: 小圖數量={num_images}, "
                    f"目標大小={target_width}x{target_height}, "
                    f"起始位置={start_corner.name}, "
                    f"主要方向={first_direction.name}, "
                    f"次要方向={second_direction.name}")
    def generate_snake_path(self):
        """
        根據起點和第一個移動方向智能生成蛇形路徑
        自動調整方向以確保能夠覆蓋所有位置
        """
        positions = []
        
        # 根據起始角落決定起點位置
        if self.start_corner == StartCorner.TOP_LEFT:
            current_x, current_y = 0, 0
            can_move_right = True
            can_move_down = True
        elif self.start_corner == StartCorner.TOP_RIGHT:
            current_x, current_y = self.target_width - 1, 0
            can_move_right = False
            can_move_down = True
        elif self.start_corner == StartCorner.BOTTOM_LEFT:
            current_x, current_y = 0, self.target_height - 1
            can_move_right = True
            can_move_down = False
        else:  # BOTTOM_RIGHT
            current_x, current_y = self.target_width - 1, self.target_height - 1
            can_move_right = False
            can_move_down = False
        
        # 初始化方向標誌
        moving_horizontally = self.first_direction in [FirstDirection.LEFT, FirstDirection.RIGHT]
        
        # 根據起始位置和首選方向決定實際的移動方向
        if moving_horizontally:
            if self.first_direction == FirstDirection.RIGHT and not can_move_right:
                dx = -1  # 強制向左
            elif self.first_direction == FirstDirection.LEFT and can_move_right:
                dx = 1   # 強制向右
            else:
                dx = 1 if self.first_direction == FirstDirection.RIGHT else -1
            dy = 0
        else:
            if self.first_direction == FirstDirection.DOWN and not can_move_down:
                dy = -1  # 強制向上
            elif self.first_direction == FirstDirection.UP and can_move_down:
                dy = 1   # 強制向下
            else:
                dy = 1 if self.first_direction == FirstDirection.DOWN else -1
            dx = 0
        
        # 生成路徑
        total_positions = self.target_width * self.target_height
        while len(positions) < total_positions:
            positions.append((current_x, current_y))
            
            # 計算下一個位置
            next_x = current_x + dx
            next_y = current_y + dy
            
            # 處理方向改變
            if moving_horizontally:
                # 水平移動時碰到邊界或已訪問的位置
                if next_x < 0 or next_x >= self.target_width or (next_x, next_y) in positions:
                    # 決定是向上還是向下移動
                    if can_move_down:
                        next_y = current_y + 1
                        if next_y >= self.target_height:
                            can_move_down = False
                            next_y = current_y - 1
                    else:
                        next_y = current_y - 1
                        if next_y < 0:
                            can_move_down = True
                            next_y = current_y + 1
                    
                    # 檢查新的垂直位置是否有效
                    if 0 <= next_y < self.target_height and (current_x, next_y) not in positions:
                        current_y = next_y
                        dx = -dx  # 反轉水平方向
                    else:
                        break
                else:
                    current_x = next_x
            else:
                # 垂直移動時碰到邊界或已訪問的位置
                if next_y < 0 or next_y >= self.target_height or (next_x, next_y) in positions:
                    # 決定是向左還是向右移動
                    if can_move_right:
                        next_x = current_x + 1
                        if next_x >= self.target_width:
                            can_move_right = False
                            next_x = current_x - 1
                    else:
                        next_x = current_x - 1
                        if next_x < 0:
                            can_move_right = True
                            next_x = current_x + 1
                    
                    # 檢查新的水平位置是否有效
                    if 0 <= next_x < self.target_width and (next_x, current_y) not in positions:
                        current_x = next_x
                        dy = -dy  # 反轉垂直方向
                    else:
                        break
                else:
                    current_y = next_y
        
        return positions

    def save_outputs(self, final_image_array):
        """
        保存不同格式的輸出文件，保持數據原始格式
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_filename = f'reconstructed_image_{timestamp}'
            
            # 在文件名中添加尺寸信息
            height, width = final_image_array.shape
            size_info = f'_{height}x{width}'
            base_filename += size_info
            
            # 直接將數據轉換為16位整數，不做正規化
            tiff_path = os.path.join(self.output_path, f'{base_filename}.tiff')
            image_16bit = final_image_array.astype(np.uint16)
            tiff_image = Image.fromarray(image_16bit)
            tiff_image.save(tiff_path, format='TIFF')
            self.logger.i("ImageReconstructor", f"已保存TIFF文件: {tiff_path}")
            
            # 保存原始數據為整數格式的txt
            txt_path = os.path.join(self.output_path, f'{base_filename}.txt')
            np.savetxt(txt_path, final_image_array, fmt='%d')  # 使用 %d 格式保存為整數
            self.logger.i("ImageReconstructor", f"已保存TXT文件: {txt_path}")
            
            return tiff_path, txt_path
            
        except Exception as e:
            self.logger.e("ImageReconstructor", f"保存輸出文件失敗: {str(e)}")
            raise

    def reconstruct_image(self):
        """
        重構圖像
        """
        try:
            if self.raw_data is None:
                self.load_data()

            # Get the actual dimensions of input data
            input_height, total_width = self.raw_data.shape
            
            # Calculate single image width
            single_width = total_width // self.num_images
            
            # Cut data into slices
            slices_raw = []
            for i in range(self.num_images):
                start_idx = i * single_width
                end_idx = start_idx + single_width
                image_data = self.raw_data[:, start_idx:end_idx]
                slices_raw.append(image_data)

            if len(slices_raw) < self.target_width * self.target_height:
                raise ValueError(f"小圖數量不足，只有 {len(slices_raw)} 張，需要 {self.target_width * self.target_height} 張")

            # Get snake path
            positions = self.generate_snake_path()

            # Create final image array with correct dimensions
            final_width = self.target_width * single_width
            final_height = self.target_height * input_height  # Use actual input height
            final_array = np.zeros((final_height, final_width))

            # Place images according to snake path
            for i, pos in enumerate(positions):
                if i >= len(slices_raw):
                    break
                    
                x, y = pos
                paste_x = x * single_width
                paste_y = y * input_height
                
                # Use actual input height instead of hard-coded value
                final_array[paste_y:paste_y+input_height, 
                        paste_x:paste_x+single_width] = slices_raw[i]

            # Save outputs
            tiff_path, txt_path = self.save_outputs(final_array)
            
            self.logger.i("ImageReconstructor", "圖像重構完成")
            return tiff_path, txt_path

        except Exception as e:
            self.logger.e("ImageReconstructor", f"重構圖像失敗: {str(e)}")
            raise

    def preview_reconstruction(self):
        """
        執行重構但不保存文件，適應不同大小的輸入數據
        """
        if self.raw_data is None:
            self.load_data()

        rows, cols = self.raw_data.shape
        # 計算每個小圖的尺寸
        single_width = cols // self.num_images

        # 切分數據為小圖
        slices_raw = []
        for i in range(self.num_images):
            start_idx = i * single_width
            end_idx = start_idx + single_width
            
            # 取出對應區域的數據
            image_data = self.raw_data[:, start_idx:end_idx]
            slices_raw.append(image_data)

        # 驗證小圖數量
        if len(slices_raw) < self.target_width * self.target_height:
            raise ValueError(f"小圖數量不足，只有 {len(slices_raw)} 張，需要 {self.target_width * self.target_height} 張")

        # 獲取蛇形路徑
        positions = self.generate_snake_path()

        # 計算最終圖像尺寸
        final_row_size = rows * self.target_height
        final_col_size = single_width * self.target_width
        final_array = np.zeros((final_row_size, final_col_size))

        # 按照蛇形路徑放置圖片
        for i, pos in enumerate(positions):
            if i >= len(slices_raw):
                break
                
            x, y = pos
            paste_x = x * single_width
            paste_y = y * rows
            
            # 貼上小圖，確保維度正確
            final_array[paste_y:paste_y + rows, 
                    paste_x:paste_x + single_width] = slices_raw[i]

        return final_array