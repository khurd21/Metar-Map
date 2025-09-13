from pathlib import Path
import threading
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

import pytest

from metar_map.logger import Logger


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True)
    return log_dir


@pytest.fixture
def sample_config_file(temp_log_dir: Path, tmp_path: Path) -> Path:  # type: ignore
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
logger:
  log_file: "{temp_log_dir / 'test.log'}"
console_level: "INFO"
file_level: "DEBUG"
rotation:
  type: "timed"
  when: "S"
  interval: 1
  backup_count: 1
"""
    )
    return config_path


def test_logger_creates_file(sample_config_file: Path) -> None:
    logger = Logger(config_path=str(sample_config_file))
    logger.info("This is a test log")
    file_handler = next(h for h in logger.logger.handlers if hasattr(h, "baseFilename"))
    log_file = Path(file_handler.baseFilename)  # type: ignore
    assert log_file.exists()
    contents = log_file.read_text()
    assert "This is a test log" in contents


def test_logger_has_console_and_file_handlers(sample_config_file: Path) -> None:
    logger = Logger(config_path=str(sample_config_file))
    handler_types = {type(h) for h in logger.logger.handlers}
    assert any("StreamHandler" in h.__name__ for h in handler_types)
    assert any("FileHandler" in h.__name__ for h in handler_types)


def test_logger_rotation_type_switch(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
logger:
  log_file: "{tmp_path / 'rotate.log'}"
  rotation:
    type: "size"
    max_bytes: 200
    backup_count: 1
"""
    )
    logger = Logger(config_path=str(config_path))
    file_handlers = [
        h
        for h in logger.logger.handlers
        if isinstance(h, RotatingFileHandler)
        and not isinstance(h, TimedRotatingFileHandler)
    ]
    assert file_handlers, "No RotatingFileHandler found"


def test_logging_levels_write_to_file(sample_config_file: Path) -> None:
    logger = Logger(config_path=str(sample_config_file))
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    file_handler = next(h for h in logger.logger.handlers if hasattr(h, "baseFilename"))
    log_file = Path(file_handler.baseFilename)  # type: ignore
    contents = log_file.read_text(encoding="utf-8")
    assert "debug message" in contents
    assert "info message" in contents
    assert "warning message" in contents
    assert "error message" in contents
    assert "critical message" in contents


def test_logger_thread_safety(sample_config_file: Path) -> None:

    logger = Logger(config_path=str(sample_config_file))
    results: list[int] = []

    def log_in_thread(idx: int):
        logger.info(f"Thread {idx} logging")
        results.append(idx)

    threads = [threading.Thread(target=log_in_thread, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    file_handler = next(h for h in logger.logger.handlers if hasattr(h, "baseFilename"))
    log_file = Path(file_handler.baseFilename)  # type: ignore
    contents = log_file.read_text(encoding="utf-8")
    for i in range(5):
        assert f"Thread {i} logging" in contents


def test_logger_levels_configurable(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
logger:
  log_file: "{tmp_path / 'level.log'}"
  console_level: "ERROR"
  file_level: "ERROR"
  rotation:
    type: "timed"
    when: "S"
    interval: 1
    backup_count: 1
"""
    )
    logger = Logger(config_path=str(config_path))
    logger.info("info message should not appear")
    logger.error("error message should appear")
    file_handler = next(h for h in logger.logger.handlers if hasattr(h, "baseFilename"))
    log_file = Path(file_handler.baseFilename)  # type: ignore
    contents = log_file.read_text(encoding="utf-8")
    assert "error message should appear" in contents
    assert "info message should not appear" not in contents
