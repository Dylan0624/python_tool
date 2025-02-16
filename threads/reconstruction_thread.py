# threads/reconstruction_thread.py
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np

class ReconstructionThread(QThread):
    """負責圖像重構的線程"""
    finished = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)
    
    def __init__(self, reconstructor, parent=None):
        super().__init__(parent)
        self.reconstructor = reconstructor
        
    def run(self):
        try:
            final_array = self.reconstructor.preview_reconstruction()
            
            # Validate array before emitting
            if final_array is None or final_array.size == 0:
                self.error.emit("重構產生了空的數組")
                return
                
            self.finished.emit(final_array)
        except Exception as e:
            self.error.emit(f"重構失敗: {str(e)}")