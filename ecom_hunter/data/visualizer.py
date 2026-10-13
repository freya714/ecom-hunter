"""数据可视化器 —— 快速生成图表和一个交互式 Dashboard。

两种使用方式：
1. render_charts()：生成 matplotlib 静态图，保存为 PNG
2. run_dashboard()：启动 Streamlit 交互式看板
"""

from __future__ import annotations

import os
from typing import List, Optional

import pandas as pd


class DataVisualizer:
    """电商数据可视化器。"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def trend_chart(
        self, date_col: str, metric_cols: List[str], save_path: Optional[str] = None
    ) -> str:
        """生成趋势折线图。"""
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        agg = self.df.groupby(date_col)[metric_cols].sum()
        ax = agg.plot(figsize=(12, 6), marker="o")
        ax.set_title("趋势分析")
        ax.set_xlabel(date_col)
        ax.set_ylabel("数值")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")

        save_path = save_path or "trend.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        return save_path

    def top_chart(
        self, name_col: str, value_col: str, top_n: int = 10, save_path: Optional[str] = None
    ) -> str:
        """生成 TOP 商品横向条形图。"""
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        top = self.df.nlargest(top_n, value_col)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top[name_col], top[value_col])
        ax.invert_yaxis()
        ax.set_title(f"TOP {top_n} 商品（按 {value_col}）")
        ax.set_xlabel(value_col)

        save_path = save_path or "top.png"
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        return save_path

    def run_dashboard(self, title: str = "电商数据分析看板"):
        """启动 Streamlit 交互式看板（阻塞式，CLI 场景使用）。"""
        try:
            import streamlit as st
        except ImportError:
            raise ImportError("请安装 streamlit：pip install streamlit")

        st.set_page_config(page_title=title, layout="wide")
        st.title(title)

        st.subheader("数据概览")
        st.dataframe(self.df, use_container_width=True)

        st.subheader("数值统计")
        numeric_cols = self.df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            st.dataframe(self.df[numeric_cols].describe(), use_container_width=True)

        # 日期列趋势
        date_cols = [
            c
            for c in self.df.columns
            if "date" in c.lower() or "日期" in c or "时间" in c
        ]
        if date_cols and numeric_cols:
            st.subheader("趋势图")
            date_col = st.selectbox("选择日期列", date_cols)
            metric_cols = st.multiselect("选择指标", numeric_cols, default=numeric_cols[:1])
            if metric_cols:
                agg = self.df.groupby(date_col)[metric_cols].sum()
                st.line_chart(agg)

        st.subheader("TOP 商品")
        if numeric_cols:
            value_col = st.selectbox("排序指标", numeric_cols)
            name_col = st.selectbox("名称列", self.df.columns.tolist())
            st.bar_chart(self.df.nlargest(10, value_col).set_index(name_col)[value_col])


def dashboard(df: pd.DataFrame, title: str = "电商数据分析看板"):
    """快捷函数：启动看板。"""
    DataVisualizer(df).run_dashboard(title)