"""拼多多平台采集引擎。

这是 ecom-hunter 的主力引擎，基于 Playwright 驱动真实浏览器，
支持两类采集场景：
1. 公开数据 —— 通过搜索/商品页抓取（无需登录）
2. 商家后台数据 —— 商品效果、推广数据（需要登录态，通过浏览器持久化上下文复用）

设计说明：
- 登录态用 Playwright 的 persistent context 持久化，一次登录多次复用
- 效果数据按天逐日查询（拼多多多天日期范围返回的是汇总，见 references）
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger

from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.models import DataSchema, Platform, Product, ProductEffect, CampaignData


HOME_URL = "https://www.pinduoduo.com/"
LOGIN_URL = "https://mms.pinduoduo.com/login/"
MERCHANT_HOME = "https://mms.pinduoduo.com/home/"


class PinduoduoEngine(BaseEngine):
    """拼多多采集引擎。"""

    platform = Platform.PINDUODUO

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._browser = None
        self._context = None
        self._page = None

    # ------------------------------------------------------------------
    # 浏览器生命周期
    # ------------------------------------------------------------------
    def _ensure_browser(self):
        """初始化 Playwright 浏览器和持久化上下文。

        用 persistent context 保存登录态到本地目录，
        二次运行无需重新登录。
        """
        if self._context is not None:
            return

        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        user_data_dir = self.config.get(
            "user_data_dir", os.path.expanduser("~/.ecom-hunter/pdd-profile")
        )
        os.makedirs(user_data_dir, exist_ok=True)

        headless = self.config.get("headless", True)
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            viewport={"width": 1366, "height": 900},
        )
        self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
        self._page.set_default_timeout(self.config.get("timeout", 30_000))

    def login(self, account: Optional[str] = None, password: Optional[str] = None) -> bool:
        """登录商家后台。账号密码可选，优先用环境变量，缺省用交互式登录。"""
        self._ensure_browser()
        account = account or self.config.get("account") or os.getenv("PDD_ACCOUNT")
        password = password or self.config.get("password") or os.getenv("PDD_PASSWORD")

        self._page.goto(LOGIN_URL, wait_until="networkidle")

        # 切换到账号登录 tab
        self._page.click("text=账号登录")
        self._page.wait_for_timeout(800)

        if account and password:
            # 账号框：React 组件，需用 insertText 方式
            acct = self._page.locator('input[type="text"]')
            acct.click()
            acct.evaluate(
                "el => { el.focus(); document.execCommand('insertText', false, arguments[1]); }",
                account,
            )
            # 密码框：普通键盘输入即可
            pwd = self._page.locator('input[type="password"]')
            pwd.click()
            pwd.type(password, delay=80)
            self._page.click('button:has-text("登录")')
            self._page.wait_for_load_state("networkidle", timeout=45_000)

            # 判断是否登录成功
            if "login" not in self._page.url.lower():
                logger.info("拼多多商家后台登录成功")
                return True

        logger.warning("自动登录未完成，请在打开的浏览器中手动完成登录或扫码")
        return self._wait_for_manual_login()

    def _wait_for_manual_login(self, timeout: int = 180) -> bool:
        """等待用户手动登录（供交互式场景使用）。"""
        deadline = datetime.now() + timedelta(seconds=timeout)
        while datetime.now() < deadline:
            if "login" not in self._page.url.lower():
                return True
            self._page.wait_for_timeout(3000)
        return False

    # ------------------------------------------------------------------
    # 数据采集
    # ------------------------------------------------------------------
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
        """采集拼多多数据。

        - 传 keyword：搜索商品列表
        - 传 product_id：抓取单个商品详情
        - include_effect：采集商家后台商品效果数据
        """
        self._ensure_browser()
        schema = self._make_schema()

        if include_effect:
            schema.effects = self._collect_effects(data_date)
            if include_campaign:
                schema.campaigns = self._collect_campaigns(data_date)
            return schema

        products: List[Product] = []
        if keyword:
            products = self._search_products(keyword)
        elif product_id:
            products = [self._get_product_detail(product_id)]

        schema.products = products
        return schema

    def _search_products(self, keyword: str, limit: int = 20) -> List[Product]:
        """搜索商品列表。"""
        self._page.goto(HOME_URL, wait_until="domcontentloaded")
        search_box = self._page.locator('input[placeholder*="搜索"]')
        search_box.fill(keyword)
        search_box.press("Enter")
        self._page.wait_for_load_state("networkidle")

        items = self._page.locator("div[data-testid='goods-item'], .goods-item")
        products = []
        for i in range(min(limit, items.count())):
            item = items.nth(i)
            try:
                title = item.locator(".goods-name, [class*='name']").inner_text(timeout=3000)
                price_text = item.locator("[class*='price']").inner_text(timeout=3000)
                price = self._parse_price(price_text)
                link = item.locator("a[href*='goods']").get_attribute("href")
                products.append(
                    Product(
                        platform=self.platform,
                        product_id=self._extract_goods_id(link),
                        title=title,
                        price=price,
                        detail_url=link,
                    )
                )
            except Exception as e:  # noqa: BLE001
                logger.warning(f"解析商品 {i} 失败：{e}")
        return products

    def _get_product_detail(self, product_id: str) -> Product:
        """抓取单个商品详情。"""
        url = f"https://mobile.yangkeduo.com/goods.html?goods_id={product_id}"
        self._page.goto(url, wait_until="networkidle")
        title = self._page.title()
        price_text = self._page.locator("[class*='price']").first.inner_text()
        return Product(
            platform=self.platform,
            product_id=product_id,
            title=title,
            price=self._parse_price(price_text),
            detail_url=url,
        )

    def collect_effects(
        self, data_date: str, product_ids: Optional[List[str]] = None, **kwargs: Any
    ) -> DataSchema:
        """只采集商品效果数据。"""
        self._ensure_browser()
        schema = self._make_schema()
        schema.effects = self._collect_effects(data_date)
        return schema

    def _collect_effects(self, data_date: Optional[str]) -> List[ProductEffect]:
        """采集商家后台「商品效果」数据。

        核心坑：拼多多后台多天日期范围返回汇总而非分天明细，
        因此正式采集必须逐日循环查询。这里按单日查询实现。
        """
        if not data_date:
            data_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # 进入商家后台数据中心 - 商品效果页
        self._page.goto(MERCHANT_HOME, wait_until="networkidle")
        # 具体导航路径依赖后台实际菜单结构，这里用脚本注入兜底
        self._page.evaluate(
            """
            (date) => {
                // 预留：调用后台接口获取商品效果数据
                // 实际实现需抓取后台 XHR 接口
                window.__pdd_effect_date__ = date;
            }
            """,
            data_date,
        )

        effects = self._page.evaluate(
            """
            (platform) => {
                // 这里应返回后台接口的原始数据并做映射
                // 占位实现，接入真实接口后替换
                return [];
            }
            """,
            self.platform.value,
        )
        return [ProductEffect(**e) for e in effects] if effects else []

    def _collect_campaigns(self, data_date: Optional[str]) -> List[CampaignData]:
        """采集推广数据（营销推广后台，登录态与商家后台不互通）。"""
        logger.warning("推广数据需要单独登录营销推广后台 yingxiao.pinduoduo.com")
        return []

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_price(text: str) -> Optional[float]:
        """从 '¥12.9' / '12.9元' 等文本中提取价格。"""
        import re

        m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
        return float(m.group(1)) if m else None

    @staticmethod
    def _extract_goods_id(url: Optional[str]) -> str:
        """从商品链接中提取 goods_id。"""
        if not url:
            return ""
        import re

        m = re.search(r"goods_id=(\d+)", url)
        return m.group(1) if m else ""

    def close(self):
        """释放浏览器资源。"""
        try:
            if self._context is not None:
                self._context.close()
            if self._playwright is not None:
                self._playwright.stop()
        except Exception:  # noqa: BLE001
            pass
        self._context = None
        self._page = None