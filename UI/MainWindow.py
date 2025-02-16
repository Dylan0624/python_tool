# UI/MainWindow.py (PyQt6 版本)
import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
    QTextEdit,
    QApplication,
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from function.SpeechTranslator import SpeechTranslator
from PyQt6.QtWidgets import QFileDialog
import os
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

class Worker(QThread):
    """
    Worker 執行緒，可用來執行耗時工作，並利用 finished 與 error 訊號回傳結果。
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self, fn, *args, **kwargs):
        """
        初始化 Worker
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


class DragDropLabel(QLabel):
    """可拖曳檔案進來的 Label"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("拖曳音訊檔案到此區域")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("QLabel { border: 2px dashed #aaa; }")
        self.setAcceptDrops(True)
        self.file_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            # 只取第一個檔案
            self.file_path = urls[0].toLocalFile()
            self.setText(self.file_path)
            event.acceptProposedAction()


class MainWindow(QMainWindow):
    """
    主視窗：可以選取或拖曳音訊檔案、選擇語音辨識模型，
    並可指定翻譯的原文語言與目標語言，分別顯示語音辨識及翻譯結果。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("語音轉換及翻譯工具")
        self.setGeometry(100, 100, 800, 600)
        self.speech_translator = None  # 後續初始化
        self.lang_mapping = {
            "英文": "en",
            "中文": "zh",
            "法文": "fr",
            "西班牙文": "es",
            "德文": "de",
        }
        # 以百分比調整字體大小，初始倍率為 0.6（可依需求調整）
        self.font_scale = 1
        self.base_font_size = self.height() // 50  # 基於視窗高度計算
        self.current_font_size = int(self.base_font_size * self.font_scale)
        # 根據作業系統決定字體族群
        if sys.platform.startswith("win"):
            self.font_family = "Microsoft JhengHei"
        elif sys.platform == "darwin":
            self.font_family = "Helvetica Neue"
        else:
            self.font_family = "Arial"

        self.init_ui()
        self.create_menu_bar()
        self.update_font_size(self.current_font_size)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # 檔案拖曳區與選取檔案按鈕
        file_layout = QHBoxLayout()
        self.drag_drop_label = DragDropLabel()
        self.drag_drop_label.setMinimumHeight(50)
        file_layout.addWidget(self.drag_drop_label)

        self.select_file_button = QPushButton("選取檔案")
        self.select_file_button.clicked.connect(self.open_file_dialog)
        file_layout.addWidget(self.select_file_button)
        self.main_layout.addLayout(file_layout)

        # 語音辨識模型選擇
        model_layout = QHBoxLayout()
        self.model_label = QLabel("選擇語音辨識模型:")
        model_layout.addWidget(self.model_label)

        self.model_combo = QComboBox()
        models = [
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "medium",
            "medium.en",
            "large",
        ]
        self.model_combo.addItems(models)
        model_layout.addWidget(self.model_combo)
        self.main_layout.addLayout(model_layout)

        # 翻譯語言選擇
        translation_lang_layout = QHBoxLayout()
        self.source_lang_label = QLabel("原文語言:")
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems(["英文", "中文", "法文", "西班牙文", "德文"])
        translation_lang_layout.addWidget(self.source_lang_label)
        translation_lang_layout.addWidget(self.source_lang_combo)

        self.target_lang_label = QLabel("翻譯目標語言:")
        self.target_lang_combo = QComboBox()
        # 若選擇中文，提供「中文(繁體)」與「中文」兩種選項
        self.target_lang_combo.addItems(
            ["中文(繁體)", "英文", "中文", "法文", "西班牙文", "德文"]
        )
        translation_lang_layout.addWidget(self.target_lang_label)
        translation_lang_layout.addWidget(self.target_lang_combo)
        self.main_layout.addLayout(translation_lang_layout)

        # 語音辨識按鈕
        self.transcribe_button = QPushButton("語音辨識")
        self.transcribe_button.clicked.connect(self.perform_transcription)
        self.main_layout.addWidget(self.transcribe_button)

        # 語音辨識結果 (原文) 顯示區
        self.transcription_text_edit = QTextEdit()
        self.transcription_text_edit.setPlaceholderText("語音辨識結果 (原文) 將顯示於此...")
        self.main_layout.addWidget(self.transcription_text_edit)

        # 翻譯按鈕
        self.translate_button = QPushButton("翻譯")
        self.translate_button.clicked.connect(self.perform_translation)
        self.main_layout.addWidget(self.translate_button)

        # 翻譯結果顯示區
        self.translation_text_edit = QTextEdit()
        self.translation_text_edit.setPlaceholderText("翻譯結果將顯示於此...")
        self.main_layout.addWidget(self.translation_text_edit)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File 選單
        file_menu = menu_bar.addMenu("File")
        save_transcript_action = QAction("存檔(語音辨識結果)", self)
        save_transcript_action.triggered.connect(self.save_transcript)
        file_menu.addAction(save_transcript_action)

        save_translation_action = QAction("存檔(翻譯結果)", self)
        save_translation_action.triggered.connect(self.save_translation)
        file_menu.addAction(save_translation_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View 選單
        view_menu = menu_bar.addMenu("View")
        increase_font_action = QAction("放大字體 (110%)", self)
        increase_font_action.triggered.connect(self.increase_font)
        view_menu.addAction(increase_font_action)

        decrease_font_action = QAction("縮小字體 (90%)", self)
        decrease_font_action.triggered.connect(self.decrease_font)
        view_menu.addAction(decrease_font_action)

        reset_font_action = QAction("重設字體", self)
        reset_font_action.triggered.connect(self.reset_font)
        view_menu.addAction(reset_font_action)

    def save_transcript(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "存檔語音辨識結果", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.transcription_text_edit.toPlainText())

    def save_translation(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "存檔翻譯結果", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.translation_text_edit.toPlainText())

    def increase_font(self):
        self.font_scale *= 1.1
        new_size = int(self.base_font_size * self.font_scale)
        self.update_font_size(new_size)

    def decrease_font(self):
        self.font_scale *= 0.9
        new_size = int(self.base_font_size * self.font_scale)
        self.update_font_size(new_size)

    def reset_font(self):
        self.font_scale = 1.0
        new_size = int(self.base_font_size * self.font_scale)
        self.update_font_size(new_size)

    def update_font_size(self, new_size):
        self.current_font_size = new_size
        font = QFont(self.font_family, self.current_font_size)
        # 更新所有文字元件
        self.transcription_text_edit.setFont(font)
        self.translation_text_edit.setFont(font)
        self.drag_drop_label.setFont(font)
        self.select_file_button.setFont(font)
        self.transcribe_button.setFont(font)
        self.translate_button.setFont(font)
        self.model_combo.setFont(font)
        self.source_lang_combo.setFont(font)
        self.target_lang_combo.setFont(font)
        # 更新所有 QLabel
        self.model_label.setFont(font)
        self.source_lang_label.setFont(font)
        self.target_lang_label.setFont(font)

    def resizeEvent(self, event):
        self.base_font_size = self.height() // 50
        new_size = int(self.base_font_size * self.font_scale)
        self.update_font_size(new_size)
        super().resizeEvent(event)

    def open_file_dialog(self):
        # 取得當前檔案所在資料夾的父資料夾
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        options = QFileDialog.Option.DontUseNativeDialog  # 使用 Qt 內建對話框
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "選擇音訊檔案",
            parent_dir,  # 以父資料夾作為初始目錄
            "Audio Files (*.m4a *.mp3 *.wav);;All Files (*)",
            options=options
        )
        if file_name:
            self.drag_drop_label.file_path = file_name
            self.drag_drop_label.setText(file_name)

    def perform_transcription(self):
        file_path = self.drag_drop_label.file_path
        if not file_path:
            self.transcription_text_edit.setPlainText("請先選擇或拖曳一個音訊檔案。")
            return

        model_name = self.model_combo.currentText()
        self.transcription_text_edit.setPlainText("正在進行語音辨識...")
        QApplication.processEvents()

        try:
            # 建立 SpeechTranslator 實例；翻譯參數將於翻譯前更新
            self.speech_translator = SpeechTranslator(whisper_model_name=model_name)
            # 使用 Worker 執行緒進行語音辨識（避免阻塞 UI）
            self.worker = Worker(self.speech_translator.speech_to_text, file_path)
            self.worker.finished.connect(self.on_transcription_finished)
            self.worker.error.connect(self.on_transcription_error)
            self.worker.start()
        except Exception as e:
            self.transcription_text_edit.setPlainText(f"語音辨識發生錯誤: {str(e)}")

    def on_transcription_finished(self, result):
        self.transcription_text_edit.setPlainText(result)
        self.translation_text_edit.clear()

    def on_transcription_error(self, error):
        self.transcription_text_edit.setPlainText(f"語音辨識發生錯誤: {str(error)}")

    def perform_translation(self):
        if not self.speech_translator:
            self.translation_text_edit.setPlainText("請先進行語音辨識。")
            return

        original_text = self.transcription_text_edit.toPlainText()
        if not original_text.strip():
            self.translation_text_edit.setPlainText("沒有可翻譯的文字。")
            return

        # 取得語言選擇
        source_lang_text = self.source_lang_combo.currentText()
        target_lang_text = self.target_lang_combo.currentText()
        source_lang_code = self.lang_mapping.get(source_lang_text, "en")
        if target_lang_text == "中文(繁體)":
            target_lang_code = "zh"
            target_traditional = True
        elif target_lang_text == "中文":
            target_lang_code = "zh"
            target_traditional = False
        else:
            target_lang_code = self.lang_mapping.get(target_lang_text, "en")
            target_traditional = False

        # 更新翻譯參數
        self.speech_translator.set_translation_params(
            source_lang=source_lang_code,
            target_lang=target_lang_code,
            target_traditional=target_traditional,
        )

        self.translation_text_edit.setPlainText("正在翻譯...")
        QApplication.processEvents()

        # 使用 Worker 執行緒進行翻譯
        self.worker = Worker(self.speech_translator.translate_text, original_text)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.start()

    def on_translation_finished(self, result):
        if result:
            self.translation_text_edit.setPlainText(result)
        else:
            self.translation_text_edit.setPlainText("翻譯失敗。")

    def on_translation_error(self, error):
        self.translation_text_edit.setPlainText(f"翻譯發生錯誤: {str(error)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
