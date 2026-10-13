"""ecom-hunter 单元测试。"""

import pandas as pd
import pytest

from ecom_hunter.core.models import Platform, Product, ProductEffect
from ecom_hunter.data.cleaner import DataCleaner, clean
from ecom_hunter.data.analyzer import DataAnalyzer


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
def test_product_model():
    p = Product(platform=Platform.JD, product_id="123", title="测试商品", price=9.9)
    assert p.price == 9.9
    assert p.platform == Platform.JD


def test_effect_percent_strip():
    e = ProductEffect(
        platform=Platform.PINDUODUO,
        product_id="1",
        effect_date="2026-10-01",
        ctr="3.5%",
        conversion_rate="2.1%",
    )
    assert e.ctr == 3.5
    assert e.conversion_rate == 2.1


# ---------------------------------------------------------------------------
# 数据清洗
# ---------------------------------------------------------------------------
def test_clean_drop_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [10, 10, 20]})
    result = DataCleaner(df).drop_duplicates().result()
    assert len(result) == 2


def test_clean_fill_missing():
    df = pd.DataFrame({"num": [1.0, None], "text": ["x", None]})
    result = DataCleaner(df).fill_missing().result()
    assert result["num"].iloc[1] == 0
    assert result["text"].iloc[1] == ""


def test_clean_pipeline():
    df = pd.DataFrame({"a": [1, 1, 2, None], "b": ["x", "x", "y", None]})
    result = clean(df)
    assert result["a"].isna().sum() == 0


def test_flag_anomalies():
    df = pd.DataFrame({"price": [10, 20, 99999]})
    result = DataCleaner(df).flag_anomalies("price", upper=1000).result()
    assert result["price_is_anomaly"].sum() == 1


# ---------------------------------------------------------------------------
# 数据分析
# ---------------------------------------------------------------------------
def test_top_products():
    df = pd.DataFrame({"name": ["a", "b", "c"], "pay_amount": [100, 300, 200]})
    top = DataAnalyzer(df).top_products(by="pay_amount", n=2)
    assert list(top["name"]) == ["b", "c"]


def test_growth_rate():
    df = pd.DataFrame({"date": ["2026-10-01", "2026-10-02"], "pay": [100, 150]})
    result = DataAnalyzer(df).add_growth_rates(df, "date", "pay")
    assert result["pay_环比"].iloc[1] == 50.0


def test_roi():
    df = pd.DataFrame({"cost": [100, 50], "gmv": [300, 100]})
    result = DataAnalyzer(df).roi_analysis()
    assert result["roi"].iloc[0] == 3.0
    assert result["roi"].iloc[1] == 2.0