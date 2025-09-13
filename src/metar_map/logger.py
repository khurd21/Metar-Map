import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Any, Optional
from metar_map.config import load_config


class Logger:
    def __init__(self, config_path: Optional[str] = None):
        logger_config: dict[str, Any] = load_config(config_path=config_path).get(
            "logger", {}
        )
        log_file = Path(logger_config.get("log_file", "logs/metar_map.log"))
        log_file.parent.mkdir(parents=True, exist_ok=True)

        console_level = getattr(
            logging, logger_config.get("console_level", "INFO").upper(), logging.INFO
        )
        file_level = getattr(
            logging, logger_config.get("file_level", "DEBUG").upper(), logging.DEBUG
        )

        self.logger = logging.getLogger(f"MetarMap_{id(self)}")
        self.logger.setLevel(logging.DEBUG)

        # Remove any existing handlers to avoid duplicate logs
        self.logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(
            logging.Formatter(
                "[%(levelname)s] %(asctime)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        rotation_cfg = logger_config.get("rotation", {})
        rotation_type = rotation_cfg.get("type", "timed").lower()

        if rotation_type == "timed":
            file_handler = TimedRotatingFileHandler(
                log_file,
                when=rotation_cfg.get("when", "midnight"),
                interval=rotation_cfg.get("interval", 1),
                backupCount=rotation_cfg.get("backup_count", 7),
                encoding="utf-8",
            )
        else:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=rotation_cfg.get("max_bytes", 1_000_000),
                backupCount=rotation_cfg.get("backup_count", 5),
                encoding="utf-8",
            )

        file_handler.setLevel(file_level)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.critical(msg, *args, **kwargs)
