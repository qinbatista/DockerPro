"""
logging配置
"""
import os
import logging.config
from config.LogConfig import LOGGING_CONFIG


class Log:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            if not hasattr(cls, "logger"):
                cls.load_logging()
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load_logging(cls):
        logging.config.dictConfig(LOGGING_CONFIG)
        cls.logger = logging.getLogger("service")
