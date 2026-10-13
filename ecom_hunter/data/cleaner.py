"""数据清洗器 —— 把采集到的原始 DataFrame 变成干净、可分析的数据。

内置常见电商数据的清洗规则：
- 去重（按主键）
- 空值处理（数值列填 0 / 文本列填空串）
- 异常值识别（负值、极端值标记）
- 数据格式化（价格保留 2 位小数、日期统一格式）
"""

from __future__ import annotations

from typing import List, Optional

import pandas as pd
from loguru import logger


class DataCleaner:
    """电商数据清洗器。"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def drop_duplicates(self, subset: Optional[List[str]] = None) -> "DataCleaner":
        """按指定列去重（默认按全部列）。"""
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset)
        removed = before - len(self.df)
        if removed:
            logger.info(f"去重：删除 {removed} 条重复记录")
        return self

    def fill_missing(self, numeric_zero: bool = True) -> "DataCleaner":
        """处理缺失值：数值列填 0，文本列填空字符串。"""
        for col in self.df.columns:
            if pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(0 if numeric_zero else None)
            else:
                self.df[col] = self.df[col].fillna("")
        return self

    def round_numeric(self, decimals: int = 2) -> "DataCleaner":
        """数值列统一保留小数位（仅对 float 列）。"""
        for col in self.df.select_dtypes(include=["float"]).columns:
            self.df[col] = self.df[col].round(decimals)
        return self

    def flag_anomalies(
        self, column: str, lower: Optional[float] = None, upper: Optional[float] = None
    ) -> "DataCleaner":
        """标记异常值，新增一列 `<column>_is_anomaly`。"""
        flag_col = f"{column}_is_anomaly"
        self.df[flag_col] = False
        if lower is not None:
            self.df.loc[self.df[column] < lower, flag_col] = True
        if upper is not None:
            self.df.loc[self.df[column] > upper, flag_col] = True
        n = int(self.df[flag_col].sum())
        if n:
            logger.warning(f"{column} 列发现 {n} 条异常值")
        return self

    def normalize_date(self, column: str, fmt: str = "%Y-%m-%d") -> "DataCleaner":
        """统一日期格式。"""
        if column in self.df.columns:
            self.df[column] = pd.to_datetime(self.df[column], errors="coerce").dt.strftime(fmt)
        return self

    def result(self) -> pd.DataFrame:
        """返回清洗后的 DataFrame。"""
        return self.df


def clean(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """快捷函数：一行完成基础清洗。"""
    cleaner = (
        DataCleaner(df)
        .drop_duplicates()
        .fill_missing()
        .round_numeric()
    )
    return cleaner.result()