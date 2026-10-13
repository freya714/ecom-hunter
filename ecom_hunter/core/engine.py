"""采集引擎基类 —— 所有平台引擎的抽象接口。

每个平台引擎必须继承 BaseEngine 并实现 collect 方法。
基类统一处理：配置解析、登录态管理、重试、以及 DataSchema 的组装。
"""

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional

from loguru import logger

from ecom_hunter.core.models import DataSchema, Platform
from ecom_hunter.core.anti_crawl import AntiCrawlStrategy


class BaseEngine(abc.ABC):
    """平台采集引擎抽象基类。"""

    platform: Platform

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.anti_crawl = AntiCrawlStrategy(self.config.get("anti_crawl", {}))
        self.session = None  # 登录态由子类维护

    @abc.abstractmethod
    def collect(
        self,
        product_id: Optional[str] = None,
        shop_id: Optional[str] = None,
        keyword: Optional[str] = None,
        data_date: Optional[str] = None,
        include_effect: bool = False,
        include_campaign: bool = False,
        **kwargs: Any,
    ) -> DataSchema:
        """采集数据，返回统一的 DataSchema。"""

    def collect_effects(
        self, data_date: str, product_ids: Optional[List[str]] = None, **kwargs: Any
    ) -> DataSchema:
        """默认实现：采集效果数据。子类可覆写。"""
        raise NotImplementedError(f"{self.platform.value} 暂不支持效果数据采集")

    def _make_schema(self) -> DataSchema:
        """创建一个空的 schema 容器。"""
        return DataSchema(platform=self.platform)

    def _handle_error(self, exc: Exception, context: str) -> None:
        """统一的错误日志。"""
        logger.error(f"[{self.platform.value}] {context} 失败：{exc}")