# gui/image_magnifier.py
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt6.QtWidgets import QWidget

class ImageMagnifier(QWidget):

    max_zoom_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 基本設置
        self.setMouseTracking(True)
        self.setVisible(False)
        
        # 放大鏡參數
        self.zoom_factor = 2.0
        self.magnifier_size = 200
        self.border_width = 2
        
        # 追蹤滑鼠位置
        self.mouse_pos = QPoint()
        
        # 來源圖片
        self.source_pixmap = None

        # 防止超出視窗範圍
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
    def set_source_pixmap(self, pixmap):
        """設置需要放大的源圖片"""
        if pixmap and not pixmap.isNull():
            self.source_pixmap = pixmap
        
    def update_position(self, pos):
        """更新放大鏡位置"""
        try:
            if not self.source_pixmap or self.source_pixmap.isNull():
                return
                
            self.mouse_pos = pos
            
            # 計算放大鏡視窗的位置，確保在視窗範圍內
            parent = self.parentWidget()
            if parent:
                x = max(0, min(pos.x() - self.magnifier_size // 2,
                             parent.width() - self.magnifier_size))
                y = max(0, min(pos.y() - self.magnifier_size // 2,
                             parent.height() - self.magnifier_size))
                
                self.setGeometry(x, y, self.magnifier_size, self.magnifier_size)
                self.update()
        except Exception as e:
            print(f"更新放大鏡位置時發生錯誤: {str(e)}")
            self.hide()
        
    def paintEvent(self, event):
        """繪製放大鏡效果"""
        try:
            if not self.source_pixmap or self.source_pixmap.isNull():
                return
                
            painter = QPainter(self)
            
            # 獲取需要放大的區域
            source_rect = self.get_source_rect()
            target_rect = self.get_target_rect()
            
            # 繪製放大的圖像
            painter.drawPixmap(target_rect, self.source_pixmap, source_rect)
            
            # 繪製邊框
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(self.border_width)
            painter.setPen(pen)
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        except Exception as e:
            print(f"繪製放大鏡效果時發生錯誤: {str(e)}")
        
    def get_source_rect(self):
        """計算需要放大的源區域"""
        source_size = int(self.magnifier_size / self.zoom_factor)
        x = int(self.mouse_pos.x() - source_size / 2)
        y = int(self.mouse_pos.y() - source_size / 2)
        
        # 確保不會超出源圖片範圍
        if self.source_pixmap:
            x = max(0, min(x, self.source_pixmap.width() - source_size))
            y = max(0, min(y, self.source_pixmap.height() - source_size))
        
        return QRect(x, y, source_size, source_size)
        
    def get_target_rect(self):
        """計算放大後的目標區域"""
        return QRect(0, 0, self.magnifier_size, self.magnifier_size)