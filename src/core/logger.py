import sys
from pathlib import Path
from loguru import logger

from src.core.config import BASE_DIR


LOG_DIR: Path = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "req_id={extra[request_id]} | "
    "user_id={extra[user_id]} | "
    "{extra[method]} {extra[path]} | "
    "status={extra[status_code]} | "
    "time={extra[execution_time_ms]}ms | "
    "ip={extra[client_ip]} | "
    "{name}:{function}:{line} - "
    "{message}"
)

JSON_FORMAT = (
    "{{"
    "\"time\": \"{time:YYYY-MM-DD HH:mm:ss.SSS}\", "
    "\"level\": \"{level}\", "
    "\"request_id\": \"{extra[request_id]}\", "
    "\"user_id\": \"{extra[user_id]}\", "
    "\"method\": \"{extra[method]}\", "
    "\"path\": \"{extra[path]}\", "
    "\"status_code\": \"{extra[status_code]}\", "
    "\"execution_time_ms\": \"{extra[execution_time_ms]}\", "
    "\"client_ip\": \"{extra[client_ip]}\", "
    "\"module\": \"{name}\", "
    "\"function\": \"{function}\", "
    "\"line\": {line}, "
    "\"message\": \"{message}\""
    "}}"
)


def only_level(level_name: str):
    def _filter(record):
        return record["level"].name == level_name
    return _filter


def error_filter(record):
    return record["level"].name in ("ERROR", "CRITICAL")


def setup_logging() -> None:

    logger.remove()

    # default values чтобы не было KeyError вне request context
    logger.configure(
        extra={
            "request_id": "-",
            "user_id": "-",
            "method": "-",
            "path": "-",
            "status_code": "-",
            "execution_time_ms": "-",
            "client_ip": "-"
        }
    )

    # Console
    logger.add(
        sys.stdout,
        level="INFO",
        format=LOG_FORMAT,
        colorize=True,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    # INFO
    logger.add(
        LOG_DIR / "info.log",
        level="INFO",
        filter=only_level("INFO"),
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8",
        format=LOG_FORMAT,
    )

    # WARNING
    logger.add(
        LOG_DIR / "warning.log",
        level="WARNING",
        filter=only_level("WARNING"),
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8",
        format=LOG_FORMAT,
    )

    # ERROR
    logger.add(
        LOG_DIR / "error.log",
        level="ERROR",
        filter=error_filter,
        rotation="10 MB",
        retention="60 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8",
        format=LOG_FORMAT,
        backtrace=True,
        diagnose=False,
    )

    # JSON structured logs
    logger.add(
        LOG_DIR / "app.json.log",
        level="INFO",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        encoding="utf-8",
        format=JSON_FORMAT,
    )
