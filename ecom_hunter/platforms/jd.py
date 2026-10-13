"""京东平台采集引擎。

京东公开数据相对友好，且商品详情页有两种形态：
- item.jd.com 主站
- item.m.jd.com 移动端（结构更简单，适合采集）
本引擎默认走移动端，降低反爬对抗成本。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import re

from loguru import logger

from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.models import DataSchema, Platform, Product


SEARCH_URL = "https://search.jd.com/Search?keyword={keyword}&enc=utf-8"


class JDEngine(BaseEngine):
    """京东采集引擎。"""

    platform = Platform.JD

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._session_headers = None

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
        products: List[Product] = []

        if keyword:
            products = self._search_products(keyword)
        elif product_id:
            products = [self._get_product_detail(product_id)]

        schema.products = products
        return schema

    def _search_products(self, keyword: str, limit: int = 20) -> List[Product]:
        """京东搜索（移动端接口，返回 JSON，更稳定）。"""
        import requests

        url = (
            "https://api.m.jd.com/client.action?functionId=searchWare"
            f"&keyword={keyword}&page=1&pageSize={limit}"
        )
        headers = self.anti_crawl.headers
        headers["Referer"] = "https://so.m.jd.com/"
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()

        products = []
        goods_list = data.get("data", {}).get("goods_list", [])
        for g in goods_list:
            products.append(
                Product(
                    platform=self.platform,
                    product_id=str(g.get("wareId", "")),
                    title=g.get("wname", ""),
                    price=float(g.get("jdPrice", 0)) if g.get("jdPrice") else None,
                    shop_name=g.get("shopName"),
                    image_url=g.get("imageurl"),
                    detail_url=f"https://item.jd.com/{g.get('wareId')}.html",
                )
            )
        return products

    def _get_product_detail(self, product_id: str) -> Product:
        """通过移动端页面抓取商品详情。"""
        import requests
        from bs4 import BeautifulSoup

        url = f"https://item.m.jd.com/product/{product_id}.html"
        resp = requests.get(url, headers=self.anti_crawl.headers, timeout=15)
        soup = BeautifulSoup(resp.text, "lxml")

        title = soup.find("div", class_="item-name") or soup.find("title")
        title_text = title.get_text(strip=True) if title else ""

        price_el = soup.find("span", class_="p-price") or soup.find("price")
        price_text = price_el.get_text() if price_el else ""
        price = self._parse_price(price_text)

        return Product(
            platform=self.platform,
            product_id=product_id,
            title=title_text,
            price=price,
            detail_url=url,
        )

    @staticmethod
    def _parse_price(text: str) -> Optional[float]:
        m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
        return float(m.group(1)) if m else None