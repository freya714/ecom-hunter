"""淘宝平台采集引擎。

淘宝反爬较严，主站搜索需要登录 + 滑块验证，因此这里采用
「公开数据 + 可选登录态」两种模式。建议优先使用淘宝开放平台官方 API，
本引擎提供 Playwright 兜底实现。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from loguru import logger

from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.models import DataSchema, Platform, Product


HOME_URL = "https://www.taobao.com/"
SEARCH_URL = "https://s.taobao.com/search?q={keyword}"


class TaobaoEngine(BaseEngine):
    """淘宝采集引擎。"""

    platform = Platform.TAOBAO

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
            "user_data_dir", os.path.expanduser("~/.ecom-hunter/tb-profile")
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
        self._ensure_browser()
        schema = self._make_schema()

        products: List[Product] = []
        if keyword:
            products = self._search_products(keyword)
        elif product_id:
            products = [self._get_product_detail(product_id)]

        schema.products = products
        return schema

    def _search_products(self, keyword: str, limit: int = 20) -> List[Product]:
        self._page.goto(SEARCH_URL.format(keyword=keyword), wait_until="networkidle")
        self._page.wait_for_timeout(1500)
        products = []
        items = self._page.locator(".items .item, [class*='Card--doubleCard']")
        for i in range(min(limit, items.count())):
            item = items.nth(i)
            try:
                title = item.locator("[class*='title']").inner_text(timeout=3000)
                price_text = item.locator("[class*='price']").inner_text(timeout=3000)
                link = item.locator("a").first.get_attribute("href")
                products.append(
                    Product(
                        platform=self.platform,
                        product_id=link or "",
                        title=title,
                        price=self._parse_price(price_text),
                        detail_url=link,
                    )
                )
            except Exception as e:  # noqa: BLE001
                logger.warning(f"解析商品 {i} 失败：{e}")
        return products

    def _get_product_detail(self, product_id: str) -> Product:
        url = f"https://item.taobao.com/item.htm?id={product_id}"
        self._page.goto(url, wait_until="networkidle")
        return Product(
            platform=self.platform,
            product_id=product_id,
            title=self._page.title(),
            detail_url=url,
        )

    @staticmethod
    def _parse_price(text: str) -> Optional[float]:
        import re

        m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
        return float(m.group(1)) if m else None

    def close(self):
        try:
            if self._context is not None:
                self._context.close()
            if self._playwright is not None:
                self._playwright.stop()
        except Exception:  # noqa: BLE001
            pass