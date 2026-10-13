"""抖音平台采集引擎。

抖音电商数据主要来自抖音小店（抖店）后台和精选联盟，
公开可采集的数据有限，主要依赖抖音开放平台 API。
本引擎提供基于 Playwright 的兜底实现，用于采集商品橱窗等公开数据。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from loguru import logger

from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.models import DataSchema, Platform, Product


class DouyinEngine(BaseEngine):
    """抖音采集引擎。"""

    platform = Platform.DOUYIN

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._browser = None
        self._context = None
        self._page = None

    def _ensure_browser(self):
        import os

        if self._context is not None:
            return
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        user_data_dir = self.config.get(
            "user_data_dir", os.path.expanduser("~/.ecom-hunter/dy-profile")
        )
        os.makedirs(user_data_dir, exist_ok=True)
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=self.config.get("headless", True),
        )
        self._page = self._context.pages[0] if self._context.pages else self._context.new_page()

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
        schema = self._make_schema()
        # 抖音公开商品数据有限，这里返回空 schema 并提示
        logger.warning(
            "抖音公开数据采集能力有限，建议接入抖音开放平台 API（商品/订单/售后）。"
            "本引擎暂返回空结果。"
        )
        return schema

    def close(self):
        try:
            if self._context is not None:
                self._context.close()
            if self._playwright is not None:
                self._playwright.stop()
        except Exception:  # noqa: BLE001
            pass