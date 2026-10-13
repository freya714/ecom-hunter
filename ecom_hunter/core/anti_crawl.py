"""反爬虫策略 —— 内置的对抗策略，作用是让采集更稳定。

当前实现的策略是「人性化 + 可配置」：
- 随机请求头（模拟不同浏览器/设备）
- 随机延迟（模拟人类操作节奏，避免匀速请求）
- 指数退避重试（遇到风控时自动放慢）
- 代理切换钩子（预留接口，接入代理池后自动轮换）
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

from loguru import logger


UA_POOL = [
    # Chrome / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


class AntiCrawlStrategy:
    """反爬虫策略配置与执行。"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        self.min_delay: float = config.get("min_delay", 0.5)  # 最小随机延迟（秒）
        self.max_delay: float = config.get("max_delay", 2.5)  # 最大随机延迟（秒）
        self.max_retries: int = config.get("max_retries", 3)
        self.proxy_getter = config.get("proxy_getter")  # 可注入的代理获取函数

    @property
    def headers(self) -> Dict[str, str]:
        """生成随机请求头。"""
        return {
            "User-Agent": random.choice(UA_POOL),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
        }

    def delay(self) -> None:
        """随机延迟，模拟人类节奏。"""
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def get_proxy(self) -> Optional[str]:
        """获取一个代理（如果配置了 proxy_getter）。"""
        if self.proxy_getter:
            try:
                return self.proxy_getter()
            except Exception as e:
                logger.warning(f"获取代理失败：{e}")
        return None

    def retry(self, fn, *args, **kwargs) -> Any:
        """带指数退避的重试执行。"""
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as e:  # noqa: BLE001
                last_exc = e
                wait = 2 ** attempt + random.uniform(0, 1)
                logger.warning(f"第 {attempt + 1} 次尝试失败（{e}），{wait:.1f}s 后重试")
                time.sleep(wait)
        raise last_exc  # type: ignore[misc]