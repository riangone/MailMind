import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Log rotation: 10 MB per file, keep 5 backups
LOG_MAX_BYTES = int(os.environ.get("LOG_MAX_BYTES", 10 * 1024 * 1024))
LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT", 5))

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)

def setup_logger(name="mailmind", level=logging.INFO, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    # Console handler with simple format for CLI users
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Rotating file handler with JSON format for machine parsing
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, encoding="utf-8",
            maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger

log = setup_logger(log_file="daemon.log")
