# gui\main_window.py
# Python 標準庫
import json
import os
import traceback
import shutil
from pathlib import Path

# 第三方庫
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QApplication
)

# 本地應用程式導入
from function import ImageReconstructor
from function.ImageReconstructor import FirstDirection, SecondDirection, StartCorner
from threads.reconstruction_thread import ReconstructionThread
from util.position_generator import PositionGenerator
from gui.zoom_preview_label import ZoomPreviewLabel

class MainWindow(QMainWindow):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.config = self.load_config()
        self.init_ui()
        self.reconstruction_thread = None
        self.setAcceptDrops(True)
        
    def load_config(self):
        """載入配置文件"""
        try:
            config_path = Path("config/reconstruction_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入配置文件失敗: {str(e)}")
            return None

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("圖像重構工具")
        
        # 創建主要的scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)
        
        # 主要容器widget
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 左側面板
        left_panel = QVBoxLayout()
        
        # 文件列表和參數設置組
        file_group = self.create_file_group()
        param_group, param_layout = self.create_param_group()  # 獲取 param_layout
        
        # 添加到左側面板
        left_panel.addWidget(file_group)
        left_panel.addWidget(param_group)
        
        # 建立主預覽區域和右側區域的容器
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        
        # 主預覽區域
        preview_group = QGroupBox("預覽")
        preview_layout = QVBoxLayout()
        
        # 建立預覽容器，使用 QWidget 作為容器
        preview_container = QWidget()
        preview_container_layout = QVBoxLayout(preview_container)
        preview_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 建立一個堆疊容器，用於管理預覽標籤和loading提示的層級關係
        stack_widget = QWidget()
        stack_widget.setLayout(QVBoxLayout())
        stack_widget.layout().setContentsMargins(0, 0, 0, 0)
        
        # 預覽標籤
        self.preview_label = ZoomPreviewLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stack_widget.layout().addWidget(self.preview_label)
        
        # Loading提示標籤
        self.loading_label = QLabel("正在生成預覽...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 20px 40px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 5px;
            }
        """)
        self.loading_label.hide()
        
        # 將 loading 標籤設置為浮動在預覽標籤上方
        self.loading_label.setParent(stack_widget)
        self.loading_label.setFixedSize(200, 60)
        
        # 更新 loading 標籤位置的方法
        def update_loading_position():
            if stack_widget.size().isValid():
                x = (stack_widget.width() - self.loading_label.width()) // 2
                y = (stack_widget.height() - self.loading_label.height()) // 2
                self.loading_label.move(x, y)
        
        # 當容器大小改變時更新 loading 標籤位置
        stack_widget.resizeEvent = lambda e: update_loading_position()

        # 不直接重寫事件，而是使用事件過濾器
        self.preview_label.installEventFilter(self)

        # # 在 preview_label 上添加鼠標追蹤
        # self.preview_label.setMouseTracking(True)
        # self.preview_label.mouseMoveEvent = self.on_preview_mouse_move
        # self.preview_label.leaveEvent = self.on_preview_mouse_leave
        
        # 將堆疊容器添加到預覽容器
        preview_container_layout.addWidget(stack_widget)
        preview_layout.addWidget(preview_container)
        preview_group.setLayout(preview_layout)
        
        # 右側區域容器
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        
        # 路徑預覽區域
        path_preview_group = QGroupBox("掃描路徑")
        path_preview_layout = QVBoxLayout()
        self.path_preview_label = QLabel()
        self.path_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path_preview_layout.addWidget(self.path_preview_label)
        path_preview_group.setLayout(path_preview_layout)
        
        # 資訊面板
        info_group = QGroupBox("圖片資訊")
        info_layout = QVBoxLayout()
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        
        # 將路徑預覽和資訊面板添加到右側容器
        right_layout.addWidget(path_preview_group, 2)
        right_layout.addWidget(info_group, 1)
        
        # 將主預覽和右側容器添加到內容容器
        content_layout.addWidget(preview_group, 2)
        content_layout.addWidget(right_container, 1)
        
        # 將左側面板和內容容器添加到主布局
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(content_container, 2)
        
        self.refresh_file_list()

    def create_file_group(self):
        """創建文件列表組"""
        file_group = QGroupBox("數據文件")
        file_layout = QVBoxLayout()
        
        # 檔案列表
        self.file_list = QListWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.itemSelectionChanged.connect(self.on_file_selected)
        
        # 檔案操作按鈕
        file_buttons_layout = QVBoxLayout()
        
        add_file_btn = QPushButton("新增檔案")
        add_file_btn.clicked.connect(self.add_files)
        file_buttons_layout.addWidget(add_file_btn)
        
        refresh_btn = QPushButton("刷新文件列表")
        refresh_btn.clicked.connect(self.refresh_file_list)
        file_buttons_layout.addWidget(refresh_btn)
        
        file_layout.addWidget(self.file_list)
        file_layout.addLayout(file_buttons_layout)
        file_group.setLayout(file_layout)
        
        return file_group

    def create_param_group(self):
        """創建參數設置組，返回 param_group 和 param_layout"""
        param_group = QGroupBox("重構參數")
        param_layout = QVBoxLayout()
        
        default_params = self.config["parameters"] if self.config else {}
        
        # 小圖數量設置
        image_count_layout = QHBoxLayout()
        image_count_layout.addWidget(QLabel("小圖數量:"))
        self.image_count_spin = QSpinBox()
        self.image_count_spin.setRange(1, 100)
        self.image_count_spin.setValue(default_params.get("num_images", 9))
        image_count_layout.addWidget(self.image_count_spin)
        param_layout.addLayout(image_count_layout)
        
        # 目標大小設置
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("寬度:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10)
        self.width_spin.setValue(default_params.get("target_width", 3))
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("高度:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10)
        self.height_spin.setValue(default_params.get("target_height", 3))
        size_layout.addWidget(self.height_spin)
        param_layout.addLayout(size_layout)
        
        # 起始角落選擇
        self.corner_combo = QComboBox()
        self.corner_combo.addItems(["左上", "右上", "左下", "右下"])
        if self.config:
            self.corner_combo.setCurrentIndex(default_params.get("start_corner", 0))
        param_layout.addWidget(QLabel("起始角落:"))
        param_layout.addWidget(self.corner_combo)
        
        # 移動方向選擇
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["向上", "向下", "向左", "向右"])
        if self.config:
            self.direction_combo.setCurrentIndex(default_params.get("first_direction", 3))
        param_layout.addWidget(QLabel("初始方向:"))
        param_layout.addWidget(self.direction_combo)
        
        # 網格顯示控制
        self.show_grid_checkbox = QCheckBox("顯示網格")
        self.show_grid_checkbox.setChecked(False)
        self.show_grid_checkbox.stateChanged.connect(self.preview_reconstruction)
        param_layout.addWidget(self.show_grid_checkbox)
        
        # 按鈕
        preview_btn = QPushButton("預覽")
        preview_btn.clicked.connect(self.preview_reconstruction)
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_reconstruction)
        
        param_layout.addWidget(preview_btn)
        param_layout.addWidget(save_btn)
        
        param_group.setLayout(param_layout)
        return param_group, param_layout

    def add_files(self):
            """開啟檔案對話框選擇檔案"""
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "選擇檔案",
                "",
                "文本文件 (*.txt)"
            )
            
            if files:
                self.import_files(files)

    def import_files(self, file_paths):
        """匯入檔案到data目錄"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        imported_files = []
        for file_path in file_paths:
            try:
                source_path = Path(file_path)
                target_path = data_dir / source_path.name
                
                # 檢查檔案是否已存在
                if target_path.exists():
                    reply = QMessageBox.question(
                        self,
                        "檔案已存在",
                        f"檔案 {source_path.name} 已存在。是否要覆蓋？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        continue
                
                # 複製檔案
                shutil.copy2(str(source_path), str(target_path))
                imported_files.append(source_path.name)
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "匯入失敗",
                    f"檔案 {source_path.name} 匯入失敗：{str(e)}"
                )
        
        if imported_files:
            self.refresh_file_list()
            QMessageBox.information(
                self,
                "匯入成功",
                f"成功匯入 {len(imported_files)} 個檔案"
            )

    def dragEnterEvent(self, event: QDragEnterEvent):
        """處理拖曳進入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """處理拖放事件"""
        file_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.txt'):
                file_paths.append(file_path)
        
        if file_paths:
            self.import_files(file_paths)
        else:
            QMessageBox.warning(
                self,
                "不支援的檔案類型",
                "只支援 .txt 檔案"
            )

    def refresh_file_list(self):
        """刷新文件列表"""
        self.file_list.clear()
        data_path = Path("data")
        if data_path.exists():
            for file in data_path.glob("*.txt"):
                self.file_list.addItem(file.name)

    def on_file_selected(self):
        """當選擇文件時觸發預覽"""
        self.preview_reconstruction()

    def get_current_parameters(self):
        """獲取當前參數設置"""
        from function.ImageReconstructor import StartCorner, FirstDirection, SecondDirection
        
        # 方向映射（從索引到枚舉值）
        direction_enums = [
            FirstDirection.UP,
            FirstDirection.DOWN,
            FirstDirection.LEFT,
            FirstDirection.RIGHT
        ]
        
        # 角落映射（從索引到枚舉值）
        corner_enums = [
            StartCorner.TOP_LEFT,
            StartCorner.TOP_RIGHT,
            StartCorner.BOTTOM_LEFT,
            StartCorner.BOTTOM_RIGHT
        ]
        
        # 從配置文件獲取第二方向
        second_direction_value = 3  # 預設為RIGHT (3)
        if self.config and "parameters" in self.config:
            second_direction_value = self.config["parameters"].get("second_direction", 3)
        
        return {
            "num_images": self.image_count_spin.value(),
            "target_width": self.width_spin.value(),
            "target_height": self.height_spin.value(),
            "start_corner": corner_enums[self.corner_combo.currentIndex()],
            "first_direction": direction_enums[self.direction_combo.currentIndex()],
            "second_direction": direction_enums[second_direction_value],
        }

    def preview_reconstruction(self):
        """預覽重構結果"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        # 顯示loading提示
        self.loading_label.show()
        self.preview_label.clear()  # 清空當前預覽
        self.path_preview_label.clear()  # 清空路徑預覽
        self.info_label.clear()  # 清空資訊標籤
        
        file_name = selected_items[0].text()
        input_file = str(Path("data") / file_name)
        
        from function.ImageReconstructor import ImageReconstructor
        reconstructor = ImageReconstructor(input_file, "output", self.logger)
        params = self.get_current_parameters()
        reconstructor.set_reconstruction_params(**params)
        
        self.reconstruction_thread = ReconstructionThread(reconstructor)
        self.reconstruction_thread.finished.connect(self.update_preview)
        self.reconstruction_thread.error.connect(self.show_error)
        self.reconstruction_thread.finished.connect(lambda _: self.loading_label.hide())  # 完成時隱藏loading提示
        self.reconstruction_thread.error.connect(lambda _: self.loading_label.hide())    # 發生錯誤時也隱藏loading提示
        self.reconstruction_thread.start()

    def show_error(self, error_message):
        """顯示錯誤訊息"""
        self.loading_label.hide()  # 確保發生錯誤時也隱藏loading提示
        QMessageBox.critical(self, "錯誤", error_message)

    def create_path_preview(self, positions, target_width, target_height):
        """創建路徑預覽圖像"""
        # 創建一個新的圖像用於顯示路徑
        cell_size = 80  # 每個格子的大小
        padding = 20    # 邊距
        img_width = target_width * cell_size + 2 * padding
        img_height = target_height * cell_size + 2 * padding
        
        # 創建白色背景的圖像
        path_img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(path_img)
        
        # 計算字體大小
        font_size = cell_size // 2
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # 繪製網格
        for i in range(target_width + 1):
            x = padding + i * cell_size
            draw.line([(x, padding), (x, img_height - padding)], fill='lightgray', width=1)
        
        for i in range(target_height + 1):
            y = padding + i * cell_size
            draw.line([(padding, y), (img_width - padding, y)], fill='lightgray', width=1)
        
        # 繪製數字和箭頭
        for idx, (x, y) in enumerate(positions):
            # 計算中心位置
            center_x = padding + x * cell_size + cell_size // 2
            center_y = padding + y * cell_size + cell_size // 2
            
            # 繪製數字
            text = str(idx + 1)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = center_x - text_width // 2
            text_y = center_y - text_height // 2
            draw.text((text_x, text_y), text, fill='black', font=font)
            
            # 繪製箭頭（如果不是最後一個位置）
            if idx < len(positions) - 1:
                next_x, next_y = positions[idx + 1]
                next_center_x = padding + next_x * cell_size + cell_size // 2
                next_center_y = padding + next_y * cell_size + cell_size // 2
                
                # 繪製箭頭線
                draw.line([(center_x, center_y), (next_center_x, next_center_y)], 
                        fill='blue', width=2)
        
        return path_img

    def update_preview(self, final_array):
        """更新預覽圖像，根據蛇形路徑添加編號標註，支持16位灰階圖像"""
        try:
            # 1. 驗證數組
            if final_array is None or final_array.size == 0:
                raise ValueError("無效的圖像數據")
            
            if not np.isfinite(final_array).all():
                raise ValueError("圖像數據包含無效值")
            
            # 更新圖片資訊
            height, width = final_array.shape
            params = self.get_current_parameters()
            target_width = params["target_width"]
            target_height = params["target_height"]
            num_images = params["num_images"]
            
            # 計算單個小圖的尺寸
            sub_height = height // target_height
            sub_width = width // target_width
            
            # 計算灰度統計信息
            gray_mean = np.mean(final_array)
            gray_median = np.median(final_array)
            gray_min = np.min(final_array)
            gray_max = np.max(final_array)
            gray_std = np.std(final_array)

            # 更新 info_text，增加灰度統計信息
            info_text = f"""
            <b>灰度統計：</b><br>
            - 平均值：{gray_mean:.2f}<br>
            - 中位數：{gray_median:.2f}<br>
            - 最小值：{gray_min:.2f}<br>
            - 最大值：{gray_max:.2f}<br>
            - 標準差：{gray_std:.2f}<br>
            <br>
            <b>大圖資訊：</b><br>
            - 整體尺寸：{width} x {height} pixels<br>
            - 網格配置：{target_width} x {target_height} 格<br>
            <br>
            <b>小圖資訊：</b><br>
            - 小圖數量：{num_images} 張<br>
            - 單張尺寸：{sub_width} x {sub_height} pixels<br>
            <br>
            <b>掃描配置：</b><br>
            - 起始角落：{self.corner_combo.currentText()}<br>
            - 初始方向：{self.direction_combo.currentText()}<br>
            """

            self.info_label.setText(info_text)

            # 2. 創建和處理圖像
            height, width = final_array.shape
            rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
            
            array_min = np.min(final_array)
            array_max = np.max(final_array)
            
            if array_max == array_min:
                normalized = np.zeros_like(final_array, dtype=np.uint8)
            else:
                normalized = ((final_array - array_min) / (array_max - array_min) * 255).astype(np.uint8)
            
            rgb_image[:,:,0] = normalized
            rgb_image[:,:,1] = normalized
            rgb_image[:,:,2] = normalized
            
            image = Image.fromarray(rgb_image, mode='RGB')
            
            # 3. 獲取參數
            params = self.get_current_parameters()
            target_width = params["target_width"]
            target_height = params["target_height"]
            
            # 4. 生成路徑
            generator = PositionGenerator(params)
            positions = generator.generate_path()
            
            # 5. 計算子圖尺寸
            sub_height = height // target_height
            sub_width = width // target_width
            
            # 6. 創建繪圖對象
            draw = ImageDraw.Draw(image)
            
            # 7. 繪製網格線 (只在勾選時繪製)
            if self.show_grid_checkbox.isChecked():
                for i in range(1, target_width):
                    x = i * sub_width
                    draw.line([(x, 0), (x, height)], fill=(255, 0, 0), width=1)

                for i in range(1, target_height):
                    y = i * sub_height
                    draw.line([(0, y), (image.width, y)], fill=(255, 0, 0), width=1)

            # 顯示主預覽圖像（不包含標籤）
            qimage = ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
                
            preview_size = self.preview_label.size()
            if not preview_size.isEmpty():
                scaled_pixmap = pixmap.scaled(
                    preview_size, 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation  # 改用 FastTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            else:
                self.preview_label.setPixmap(pixmap)
            
            
            # 8. 生成並顯示路徑預覽
            path_img = self.create_path_preview(positions, target_width, target_height)
            path_qimage = ImageQt(path_img)
            path_pixmap = QPixmap.fromImage(path_qimage)
            
            path_preview_size = self.path_preview_label.size()
            if not path_preview_size.isEmpty():
                scaled_path_pixmap = path_pixmap.scaled(
                    path_preview_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation  # 路徑預覽也使用 FastTransformation
                )
                self.path_preview_label.setPixmap(scaled_path_pixmap)
            else:
                self.path_preview_label.setPixmap(path_pixmap)
                
        except Exception as e:
            error_details = traceback.format_exc()
            error_message = f"預覽更新失敗: {str(e)}\n\n詳細錯誤信息:\n{error_details}"
            print(error_message)
            self.show_error(error_message)
            self.preview_label.clear()
            self.path_preview_label.clear()
            self.info_label.clear()


    def save_reconstruction(self):
        """保存當前重構結果"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        
        # 創建進度對話框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("保存中")
        progress_dialog.setText("正在保存文件...")  # 設置初始文字
        progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
        # 設置為模態對話框並移除關閉按鈕
        progress_dialog.setModal(True)
        progress_dialog.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )
        progress_dialog.setStyleSheet("""
            QMessageBox {
                font-size: 14px;
            }
            QLabel {
                min-width: 300px;
                min-height: 50px;
            }
        """)
        
        # 設置動畫計時器
        dots_count = [0]  # 使用list以便在lambda中修改
        def update_dots():
            dots = "." * ((dots_count[0] % 3) + 1)
            progress_dialog.setText(f"正在保存文件{dots}")
            progress_dialog.repaint()  # 強制重繪
            QApplication.processEvents()  # 處理其他事件
            dots_count[0] += 1
        
        # 創建並啟動計時器
        timer = QTimer(progress_dialog)
        timer.timeout.connect(update_dots)
        timer.start(300)  # 改為每300毫秒更新一次，使動畫更流暢
        
        file_name = selected_items[0].text()
        input_file = str(Path("data") / file_name)
        
        try:
            # 顯示進度對話框
            progress_dialog.show()
            QApplication.processEvents()
            
            # 執行保存操作
            from function.ImageReconstructor import ImageReconstructor
            reconstructor = ImageReconstructor(input_file, "output", self.logger)
            params = self.get_current_parameters()
            reconstructor.set_reconstruction_params(**params)
            
            tiff_path, txt_path = reconstructor.reconstruct_image()
            
            # 停止動畫並關閉對話框
            timer.stop()
            progress_dialog.done(0)
            
            # 創建結果訊息對話框
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("保存成功")
            success_msg.setText(f"文件已保存:\nTIFF: {tiff_path}\nTXT: {txt_path}")
            success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            success_msg.setModal(True)
            
            # 顯示成功訊息
            success_msg.exec()
            
        except Exception as e:
            # 停止動畫並關閉對話框
            timer.stop()
            progress_dialog.done(0)
            
            # 創建錯誤訊息對話框
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("保存失敗")
            error_msg.setText(f"保存過程中發生錯誤: {str(e)}")
            error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_msg.setModal(True)
            
            # 設置計時器在2秒後自動關閉
            QTimer.singleShot(2000, error_msg.close)
            
            # 顯示錯誤訊息
            error_msg.exec()
            """保存當前重構結果"""
            selected_items = self.file_list.selectedItems()
            if not selected_items:
                return
            
            # 創建進度對話框
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle("保存中")
            progress_dialog.setText("正在保存文件...")  # 設置初始文字
            progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
            # 設置為模態對話框並移除關閉按鈕
            progress_dialog.setModal(True)
            progress_dialog.setWindowFlags(
                Qt.WindowType.Window | 
                Qt.WindowType.CustomizeWindowHint | 
                Qt.WindowType.WindowTitleHint
            )
            progress_dialog.setStyleSheet("""
                QMessageBox {
                    font-size: 14px;
                }
                QLabel {
                    min-width: 300px;
                    min-height: 50px;
                }
            """)
            
            # 設置動畫計時器
            dots_count = [0]  # 使用list以便在lambda中修改
            def update_dots():
                dots = "." * ((dots_count[0] % 3) + 1)
                progress_dialog.setText(f"正在保存文件{dots}")
                dots_count[0] += 1
            
            # 創建並啟動計時器
            timer = QTimer(progress_dialog)
            timer.timeout.connect(update_dots)
            timer.start(500)  # 每500毫秒更新一次
            
            file_name = selected_items[0].text()
            input_file = str(Path("data") / file_name)
            
            try:
                # 顯示進度對話框
                progress_dialog.show()
                QApplication.processEvents()
                
                # 執行保存操作
                from function.ImageReconstructor import ImageReconstructor
                reconstructor = ImageReconstructor(input_file, "output", self.logger)
                params = self.get_current_parameters()
                reconstructor.set_reconstruction_params(**params)
                
                tiff_path, txt_path = reconstructor.reconstruct_image()
                
                # 停止動畫並關閉對話框
                timer.stop()
                progress_dialog.done(0)
                
                # 創建結果訊息對話框
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("保存成功")
                success_msg.setText(f"文件已保存:\nTIFF: {tiff_path}\nTXT: {txt_path}")
                success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_msg.setModal(True)
                
                # 設置計時器在2秒後自動關閉
                QTimer.singleShot(2000, success_msg.close)
                
                # 顯示成功訊息
                success_msg.exec()
                
            except Exception as e:
                # 停止動畫並關閉對話框
                timer.stop()
                progress_dialog.done(0)
                
                # 創建錯誤訊息對話框
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("保存失敗")
                error_msg.setText(f"保存過程中發生錯誤: {str(e)}")
                error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_msg.setModal(True)
                
                # 設置計時器在2秒後自動關閉
                QTimer.singleShot(2000, error_msg.close)
                
                # 顯示錯誤訊息
                error_msg.exec()