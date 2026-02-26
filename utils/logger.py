import os
import time
import logging
import colorlog
from root import ROOT_PATH
from logging.handlers import RotatingFileHandler


logfile_name = os.path.join(
    ROOT_PATH, "logs", r"\\test.{}.log".format(time.strftime("%Y%M%d"))
)


class Logger:
    """日志处理模块"""

    @classmethod
    def set_log_color(cls):
        _config = {
            "DEBUG": "cyan",
            "INFO": "green",
            "ERROR": "red",
            "WARNING": "yellow",
            "CRITICAL": "red",
        }

        formatter = colorlog.ColoredFormatter(
            "%(log_color)s %(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - "
            "%(message)s",
            log_colors=_config,
        )

        return formatter

    @classmethod
    def logger(cls):
        _logger = logging.getLogger(__name__)
        stream_format = cls.set_log_color()

        if not _logger.handlers:
            _logger.setLevel(logging.DEBUG)
            log_format = logging.Formatter(
                "%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - %(message)s"
            )

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(stream_format)
            _logger.addHandler(stream_handler)

            file_handler = RotatingFileHandler(
                filename=logfile_name,
                mode="a",
                maxBytes=5242880,
                backupCount=7,
                encoding="utf-8",
            )

            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(log_format)
            _logger.addHandler(file_handler)
        return _logger


logger = Logger()
log = logger.logger()
