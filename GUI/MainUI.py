"""Main UI for the Converter application using PyQt6."""
# GUI/MainUI.py
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPushButton,
    QListWidget,
    QLabel,
    QComboBox,
    QTextEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDropEvent, QDragEnterEvent
from pathlib import Path
import sys

from function.EncodingConverter import EncodingConverter
from function.FileConverter import FileConverter
from utils.log_manager import LogManager


class MainUI(QMainWindow):
    """Main window for the Converter application."""

    def __init__(self):
        """Initialize the MainUI."""
        super().__init__()
        self.setWindowTitle("檔案轉換工具")
        self.resize(800, 500)

        # Initialize converters and logger
        self.encoding_converter = EncodingConverter()
        self.file_converter = FileConverter()
        self.logger = LogManager()

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # File selection section
        file_section = self._create_file_section()
        main_layout.addWidget(file_section)

        # Conversion sections
        conversion_layout = QHBoxLayout()
        encoding_section = self._create_encoding_section()
        format_section = self._create_format_section()
        conversion_layout.addWidget(encoding_section)
        conversion_layout.addWidget(format_section)
        main_layout.addLayout(conversion_layout)

        # Log section
        log_section = self._create_log_section()
        main_layout.addWidget(log_section)

    def _create_file_section(self):
        """Create the file selection section."""
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Buttons
        button_layout = QHBoxLayout()
        select_file_btn = QPushButton("選擇檔案")
        select_file_btn.clicked.connect(self._select_file)
        select_dir_btn = QPushButton("選擇目錄")
        select_dir_btn.clicked.connect(self._select_directory)
        button_layout.addWidget(select_file_btn)
        button_layout.addWidget(select_dir_btn)
        file_layout.addLayout(button_layout)

        # File list with dashed border and drop support
        self.file_list = DragDropListWidget()
        self.file_list.setStyleSheet("border: 2px dashed gray;")
        file_layout.addWidget(self.file_list)

        return file_widget

    def _create_encoding_section(self):
        """Create the encoding conversion section."""
        encoding_widget = QWidget()
        encoding_layout = QVBoxLayout(encoding_widget)
        encoding_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Input encoding
        encoding_layout.addWidget(QLabel("輸入編碼:"))
        self.input_encoding = QComboBox()
        self.input_encoding.addItems(["utf-8", "utf-16", "ascii"])
        self.input_encoding.setCurrentText("utf-8")
        encoding_layout.addWidget(self.input_encoding)

        # Output encoding
        encoding_layout.addWidget(QLabel("輸出編碼:"))
        self.output_encoding = QComboBox()
        self.output_encoding.addItems(["utf-8-sig", "utf-8", "utf-16"])
        self.output_encoding.setCurrentText("utf-8-sig")
        encoding_layout.addWidget(self.output_encoding)

        # Convert button
        convert_btn = QPushButton("轉換編碼")
        convert_btn.clicked.connect(self._convert_encoding)
        encoding_layout.addWidget(convert_btn)

        return encoding_widget

    def _create_format_section(self):
        """Create the format conversion section."""
        format_widget = QWidget()
        format_layout = QVBoxLayout(format_widget)
        format_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Current format
        format_layout.addWidget(QLabel("當前格式:"))
        self.current_format = QLabel("N/A")
        format_layout.addWidget(self.current_format)

        # Target format
        format_layout.addWidget(QLabel("目標格式:"))
        self.target_format = QComboBox()
        format_layout.addWidget(self.target_format)

        # Buttons
        button_layout = QHBoxLayout()
        analyze_btn = QPushButton("分析檔案")
        analyze_btn.clicked.connect(self._analyze_file)
        convert_btn = QPushButton("轉換格式")
        convert_btn.clicked.connect(self._convert_format)
        button_layout.addWidget(analyze_btn)
        button_layout.addWidget(convert_btn)
        format_layout.addLayout(button_layout)

        return format_widget

    def _create_log_section(self):
        """Create the log display section."""
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("日誌:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        return log_widget

    def _select_file(self):
        """Handle file selection."""
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇檔案", "", "All Files (*.*)")
        if file_path:
            self.file_list.clear()
            self.file_list.addItem(file_path)
            self._analyze_file()

    def _select_directory(self):
        """Handle directory selection."""
        dir_path = QFileDialog.getExistingDirectory(self, "選擇目錄")
        if dir_path:
            self.file_list.clear()
            files = [str(f) for f in Path(dir_path).rglob("*.*")]
            self.file_list.addItems(files)

    def _analyze_file(self):
        """Analyze the selected file."""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "請先選擇檔案！")
            return

        file_path = self.file_list.item(0).text()
        analysis = self.file_converter.analyze_files(file_path)
        if analysis and analysis[0].get("supported", False):
            self.current_format.setText(analysis[0]["current_format"])
            self.target_format.clear()
            self.target_format.addItems(analysis[0]["convertible_formats"])
            self.target_format.setCurrentIndex(0)
            self.log_text.append(f"分析完成: {file_path}")
        else:
            self.current_format.setText("N/A")
            self.target_format.clear()
            self.log_text.append(f"分析失敗: {analysis[0].get('error', 'Unknown error')}")

    def _convert_encoding(self):
        """Perform encoding conversion."""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "請先選擇檔案或目錄！")
            return

        input_enc = self.input_encoding.currentText()
        output_enc = self.output_encoding.currentText()
        self.log_text.clear()
        self.log_text.append("開始編碼轉換...")

        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if len(files) == 1:
            success = self.encoding_converter.convert_file(files[0], input_enc, output_enc)
            self.log_text.append(f"轉換 {files[0]} {'成功' if success else '失敗'}")
        else:
            results = self.encoding_converter.convert_directory(
                files[0], input_enc, output_enc, pattern="*.*"
            )
            for res in results:
                self.log_text.append(f"檔案: {res['file_path']} {'成功' if res['success'] else '失敗'}")

    def _convert_format(self):
        """Perform format conversion."""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "請先選擇檔案！")
            return

        target = self.target_format.currentText()
        if not target:
            QMessageBox.warning(self, "警告", "請選擇目標格式！")
            return

        self.log_text.clear()
        self.log_text.append(f"開始格式轉換到 {target}...")
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        results = self.file_converter.convert_files(files, target, output_dir="output")
        for res in results:
            if res["success"]:
                self.log_text.append(f"轉換成功: {res['output_path']}")
            else:
                self.log_text.append(f"轉換失敗: {res.get('error', 'Unknown error')}")


class DragDropListWidget(QListWidget):
    """Custom QListWidget with drag-and-drop support for files and directories."""

    def __init__(self, parent=None):
        """Initialize the DragDropListWidget."""
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event for files and directories."""
        if event.mimeData().hasUrls():
            self.clear()
            for url in event.mimeData().urls():
                path = Path(url.toLocalFile())
                if path.is_file():
                    self.addItem(str(path))
                elif path.is_dir():
                    files = [str(f) for f in path.rglob("*.*")]
                    self.addItems(files)
            event.acceptProposedAction()
            # Trigger analysis for the first dropped item if any
            if self.count() > 0:
                window = self.window()
                if isinstance(window, MainUI):
                    window._analyze_file()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())