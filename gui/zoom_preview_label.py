from PyQt6.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal, QRect
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QLabel

class ScalingThread(QThread):
    finished = pyqtSignal(QPixmap)

    def __init__(self, pixmap, new_size):
        super().__init__()
        self.pixmap = pixmap
        self.new_size = new_size

    def run(self):
        scaled = self.pixmap.scaled(
            self.new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.finished.emit(scaled)


class ZoomPreviewLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scale = 1.0
        self.min_scale = 0.1
        self.max_scale = 10.0
        self.zoom_step = 1.1
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_pixmap = None
        self.offset = QPoint(0, 0)
        self.scaling_thread = None
        self.zoom_timer = QTimer()
        self.zoom_timer.timeout.connect(self.process_zoom)
        self.zoom_timer.setInterval(16)
        self.pending_zoom = None
        self.zoom_pos = None
        self.last_mouse_pos = None
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        if not self.original_pixmap:
            return
        self.pending_zoom = event.angleDelta().y()
        self.zoom_pos = event.position()
        if not self.zoom_timer.isActive():
            self.zoom_timer.start()
            self.process_zoom()

    def process_zoom(self):
        if self.pending_zoom is None or not self.original_pixmap:
            self.zoom_timer.stop()
            return

        delta = self.pending_zoom
        pos = self.zoom_pos
        self.pending_zoom = None
        self.zoom_pos = None

        old_scale = self.scale
        if delta > 0:
            new_scale = min(self.scale * self.zoom_step, self.max_scale)
        else:
            new_scale = max(self.scale / self.zoom_step, self.min_scale)

        if new_scale != old_scale:
            view_rect = self.get_view_rect()
            rel_x = (pos.x() - view_rect.x()) / view_rect.width()
            rel_y = (pos.y() - view_rect.y()) / view_rect.height()

            self.scale = new_scale
            new_size = self.original_pixmap.size() * new_scale
            new_rect = self.get_centered_rect(new_size)

            self.offset += QPoint(
                int((view_rect.width() - new_rect.width()) * rel_x),
                int((view_rect.height() - new_rect.height()) * rel_y)
            )
            self.clamp_offset(new_rect)

            if self.scaling_thread and self.scaling_thread.isRunning():
                self.scaling_thread.quit()
                self.scaling_thread.wait()

            self.scaling_thread = ScalingThread(self.original_pixmap, new_size)
            self.scaling_thread.finished.connect(self.update_pixmap)
            self.scaling_thread.start()

    def get_centered_rect(self, size):
        return QRect(
            max((self.width() - size.width()) // 2, 0),
            max((self.height() - size.height()) // 2, 0),
            min(size.width(), self.width()),
            min(size.height(), self.height())
        )

    def get_view_rect(self):
        if not self.original_pixmap:
            return QRect()
        scaled_size = self.original_pixmap.size() * self.scale
        return self.get_centered_rect(scaled_size).translated(self.offset)

    def clamp_offset(self, new_rect):
        max_x = max(0, new_rect.width() - self.width())
        max_y = max(0, new_rect.height() - self.height())
        self.offset.setX(max(min(self.offset.x(), max_x), -max_x))
        self.offset.setY(max(min(self.offset.y(), max_y), -max_y))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.pos()
            self.clamp_offset(self.get_view_rect())
            self.update()

    def paintEvent(self, event):
        if not self.pixmap():
            return super().paintEvent(event)
        painter = QPainter(self)
        view_rect = self.get_view_rect()
        painter.drawPixmap(view_rect, self.pixmap())

    def update_pixmap(self, scaled_pixmap):
        super().setPixmap(scaled_pixmap)

    def setPixmap(self, pixmap: QPixmap):
        self.scale = 1.0
        self.offset = QPoint(0, 0)
        self.original_pixmap = pixmap
        super().setPixmap(pixmap)
