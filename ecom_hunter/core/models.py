"""数据模型定义 —— 所有平台统一的数据结构。

这是 ecom-hunter 的核心设计：无论采集哪个平台，输出都是同一套 schema，
这样下游的清洗、分析、可视化逻辑可以完全复用。
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Platform(str, Enum):
    """支持的电商平台。"""

    PINDUODUO = "pinduoduo"
    TAOBAO = "taobao"
    JD = "jd"
    DOUYIN = "douyin"

    @property
    def display_name(self) -> str:
        names = {
            "pinduoduo": "拼多多",
            "taobao": "淘宝",
            "jd": "京东",
            "douyin": "抖音",
        }
        return names[self.value]


class Product(BaseModel):
    """商品基础信息。"""

    platform: Platform
    product_id: str = Field(..., description="商品 ID（平台内唯一）")
    title: str = Field(..., description="商品标题")
    price: Optional[float] = Field(None, description="当前售价（元）")
    original_price: Optional[float] = Field(None, description="原价/划线价")
    shop_id: Optional[str] = Field(None, description="店铺 ID")
    shop_name: Optional[str] = Field(None, description="店铺名称")
    category: Optional[str] = Field(None, description="商品类目")
    image_url: Optional[str] = Field(None, description="主图链接")
    detail_url: Optional[str] = Field(None, description="商品详情页链接")
    sales_count: Optional[int] = Field(None, description="累计销量")
    comment_count: Optional[int] = Field(None, description="累计评价数")
    rating: Optional[float] = Field(None, description="评分（满分5）")
    sku_list: List[Dict[str, Any]] = Field(default_factory=list, description="SKU 列表")
    crawled_at: datetime = Field(default_factory=datetime.now, description="采集时间")


class ProductEffect(BaseModel):
    """商品效果数据（流量/转化/交易等运营指标）。"""

    platform: Platform
    product_id: str
    effect_date: str = Field(..., description="数据日期 YYYY-MM-DD")
    impression: Optional[int] = Field(None, description="曝光量/展现量")
    click: Optional[int] = Field(None, description="点击量")
    ctr: Optional[float] = Field(None, description="点击率（%）")
    visit: Optional[int] = Field(None, description="访客数")
    order_count: Optional[int] = Field(None, description="下单数")
    pay_count: Optional[int] = Field(None, description="成交/支付件数")
    pay_amount: Optional[float] = Field(None, description="成交金额（元）")
    conversion_rate: Optional[float] = Field(None, description="转化率（%）")
    refund_count: Optional[int] = Field(None, description="退款单数")
    crawled_at: datetime = Field(default_factory=datetime.now)

    @field_validator("ctr", "conversion_rate", mode="before")
    @classmethod
    def _strip_percent(cls, v):
        """兼容 "3.5%" 这类带百分号的字符串。"""
        if isinstance(v, str):
            return float(v.replace("%", "").strip())
        return v


class CampaignData(BaseModel):
    """推广/营销数据。"""

    platform: Platform
    campaign_id: Optional[str] = None
    campaign_name: Optional[str] = None
    data_date: str = Field(..., description="数据日期 YYYY-MM-DD")
    cost: Optional[float] = Field(None, description="花费（元）")
    impression: Optional[int] = Field(None, description="展现量")
    click: Optional[int] = Field(None, description="点击量")
    cpc: Optional[float] = Field(None, description="平均点击成本（元）")
    order_count: Optional[int] = Field(None, description="成交单数")
    gmv: Optional[float] = Field(None, description="成交金额（元）")
    roi: Optional[float] = Field(None, description="投产比 ROI")
    crawled_at: datetime = Field(default_factory=datetime.now)


class DataSchema(BaseModel):
    """一次采集任务的完整结果包。"""

    platform: Platform
    products: List[Product] = Field(default_factory=list)
    effects: List[ProductEffect] = Field(default_factory=list)
    campaigns: List[CampaignData] = Field(default_factory=list)
    raw: Dict[str, Any] = Field(default_factory=dict, description="平台原始响应，便于调试")
    collected_at: datetime = Field(default_factory=datetime.now)

    def to_dataframe(self, kind: str = "effects"):
        """把某一类数据转成 pandas DataFrame（pandas 懒加载）。"""
        import pandas as pd

        data = getattr(self, kind)
        if not data:
            return pd.DataFrame()
        return pd.DataFrame([item.dict() for item in data])