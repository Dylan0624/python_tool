import os
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import time
from datetime import datetime, timedelta
import sys
from pathlib import Path


class LogManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """
        Initialize the LogManager instance, setting up loggers and handlers.
        """
        self.logger = logging.getLogger('AppLogger')
        self.logger.setLevel(logging.DEBUG)

        # 根據運行環境決定基礎目錄
        if getattr(sys, 'frozen', False):
            # 在打包環境中
            if sys.platform == 'win32':
                base_dir = Path(os.environ['APPDATA']) / 'RamanImage'
            else:
                base_dir = Path.home() / '.RamanImage'
        else:
            # 在開發環境中
            base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # 設置日誌和配置文件路徑
        self.log_dir = base_dir / 'logs'
        self.config_dir = base_dir / 'config'
        self.config_path = self.config_dir / 'log_config.json'

        # 確保目錄存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 如果配置文件不存在，創建默認配置
        if not self.config_path.exists():
            self.create_default_config()

        self.last_config_check = 0
        self.config_check_interval = 1

        self.setup_handlers()
        self.load_config()

    def create_default_config(self):
        """
        Create default logging configuration file.
        """
        default_config = {
            "display_levels": {
                "DEBUG": True,
                "INFO": True,
                "WARNING": True,
                "ERROR": True,
                "CRITICAL": True
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)

    def setup_handlers(self):
        """
        Set up log file handlers and console handlers.
        """
        log_file = self.log_dir / f'app_{time.strftime("%Y%m%d")}.log'
        self.file_handler = TimedRotatingFileHandler(
            str(log_file), 
            when='midnight', 
            interval=1, 
            backupCount=60
        )
        self.file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(tag)s - %(message)s')
        )
        self.logger.addHandler(self.file_handler)

        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(tag)s - %(message)s')
        )
        self.logger.addHandler(self.console_handler)

    def load_config(self):
        """
        Load logging configuration from JSON file.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.apply_log_levels(config['display_levels'])
            print(f"Loaded config from: {self.config_path}")
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            print(f"Attempted to load config from: {self.config_path}")
            # 如果載入失敗，創建新的默認配置
            self.create_default_config()

    def apply_log_levels(self, levels):
        """
        Apply log levels from the configuration.

        Args:
            levels (dict): Dictionary containing log levels for handlers.
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        min_level = logging.CRITICAL
        for level, enabled in levels.items():
            if enabled and level_map[level] < min_level:
                min_level = level_map[level]

        self.console_handler.setLevel(min_level)
        self.file_handler.setLevel(min_level)
        print(f"Set log level to: {logging.getLevelName(min_level)}")

    def check_config(self):
        """
        Check if the logging configuration file has been updated and reload if necessary.
        """
        current_time = time.time()
        if current_time - self.last_config_check > self.config_check_interval:
            self.last_config_check = current_time
            if self.config_path.exists():
                config_mtime = os.path.getmtime(self.config_path)
                if config_mtime > self.last_config_check:
                    self.load_config()

    def log(self, level, tag, message):
        """
        Log a message with a specified level and tag.

        Args:
            level (int): The logging level (e.g., logging.INFO).
            tag (str): A tag to indicate the source of the log message.
            message (str): The log message.
        """
        self.check_config()
        if self.logger.isEnabledFor(level):
            self.logger.log(level, message, extra={'tag': tag})

    def d(self, tag, message):
        """Log a debug message."""
        self.log(logging.DEBUG, tag, message)

    def i(self, tag, message):
        """Log an info message."""
        self.log(logging.INFO, tag, message)

    def w(self, tag, message):
        """Log a warning message."""
        self.log(logging.WARNING, tag, message)

    def e(self, tag, message):
        """Log an error message."""
        self.log(logging.ERROR, tag, message)

    def c(self, tag, message):
        """Log a critical message."""
        self.log(logging.CRITICAL, tag, message)

    def reload_config(self):
        """Reload the logging configuration."""
        self.load_config()