"""日志配置 —— 基于 loguru 的统一日志。"""

from __future__ import annotations

import sys
from typing import Optional

from loguru import logger


def setup_logger(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """配置全局日志。

    Args:
        level: 日志级别 DEBUG / INFO / WARNING / ERROR
        log_file: 可选，写入日志文件路径
    """
    logger.remove()  # 移除默认 handler
    logger.add(sys.stderr, level=level, enqueue=True)

    if log_file:
        logger.add(
            log_file,
            level=level,
            rotation="10 MB",
            retention="7 days",
            enqueue=True,
        )

    return logger