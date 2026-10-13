"""ecom-hunter — 多平台电商数据采集与智能分析框架。

统一的采集接口，覆盖拼多多、淘宝、京东、抖音四大平台，
内置数据清洗、分析与可视化能力，让你几行代码就能拿到干净、可用的电商数据。
"""

__version__ = "0.1.0"
__author__ = "zhangwt121"

from ecom_hunter.core.models import (
    Product,
    ProductEffect,
    CampaignData,
    DataSchema,
    Platform,
)
from ecom_hunter.core.collector import EcomHunter

__all__ = [
    "EcomHunter",
    "Product",
    "ProductEffect",
    "CampaignData",
    "DataSchema",
    "Platform",
    "__version__",
]