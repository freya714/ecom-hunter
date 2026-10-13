"""核心包。"""

from ecom_hunter.core.models import (
    CampaignData,
    DataSchema,
    Platform,
    Product,
    ProductEffect,
)
from ecom_hunter.core.collector import EcomHunter
from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.anti_crawl import AntiCrawlStrategy

__all__ = [
    "EcomHunter",
    "BaseEngine",
    "AntiCrawlStrategy",
    "Platform",
    "Product",
    "ProductEffect",
    "CampaignData",
    "DataSchema",
]