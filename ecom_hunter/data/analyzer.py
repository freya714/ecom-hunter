"""数据分析器 —— 从干净数据中提炼洞见。

内置电商常用指标计算：
- 趋势分析（环比、同比）
- TOP 商品排行
- 转化漏斗
- ROI 分析
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
from loguru import logger


class DataAnalyzer:
    """电商数据分析器。"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def top_products(self, by: str = "pay_amount", n: int = 10) -> pd.DataFrame:
        """按指标取 TOP 商品。"""
        if by not in self.df.columns:
            raise ValueError(f"指标列 '{by}' 不存在，可用列：{list(self.df.columns)}")
        return self.df.nlargest(n, by)

    def trend(self, date_col: str, metric_cols: List[str]) -> pd.DataFrame:
        """按日期聚合趋势。"""
        return self.df.groupby(date_col)[metric_cols].sum().reset_index()

    def add_growth_rates(self, df: pd.DataFrame, date_col: str, metric_col: str) -> pd.DataFrame:
        """计算环比增长率（相对上一周期）。"""
        df = df.sort_values(date_col)
        df[f"{metric_col}_环比"] = df[metric_col].pct_change() * 100
        return df

    def conversion_funnel(self) -> Dict[str, float]:
        """计算转化漏斗（点击 -> 访客 -> 下单 -> 成交）。"""
        funnel = {}
        mapping = {
            "click": "曝光->点击率",
            "visit": "点击->访客率",
            "order_count": "访客->下单率",
            "pay_count": "下单->成交率",
        }
        for col, label in mapping.items():
            if col in self.df.columns:
                funnel[label] = float(self.df[col].sum())
        return funnel

    def roi_analysis(self, cost_col: str = "cost", gmv_col: str = "gmv") -> pd.DataFrame:
        """ROI 分析。"""
        if cost_col not in self.df.columns or gmv_col not in self.df.columns:
            raise ValueError("需要 cost 和 gmv 列")
        result = self.df.copy()
        result["roi"] = result[gmv_col] / result[cost_col].replace(0, float("nan"))
        return result

    def summary(self) -> Dict[str, float]:
        """数值列汇总统计。"""
        return {
            col: float(self.df[col].sum())
            for col in self.df.select_dtypes(include=["number"]).columns
        }


def analyze(df: pd.DataFrame) -> DataAnalyzer:
    """快捷函数：创建分析器。"""
    return DataAnalyzer(df)