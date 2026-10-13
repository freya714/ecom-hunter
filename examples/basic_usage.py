"""ecom-hunter 使用示例。

运行前请先安装依赖：
    pip install -e .
    playwright install chromium
"""

from ecom_hunter import EcomHunter
from ecom_hunter.data.cleaner import clean
from ecom_hunter.data.analyzer import analyze
from ecom_hunter.data.visualizer import DataVisualizer


def demo_search():
    """示例 1：搜索商品（京东公开数据，无需登录）。"""
    hunter = EcomHunter()
    data = hunter.collect("jd", keyword="蓝牙耳机")

    df = data.to_dataframe("products")
    print("采集到商品数：", len(df))
    print(df[["title", "price", "shop_name"]].head(10))


def demo_clean_and_analyze():
    """示例 2：清洗 + 分析流水线。"""
    import pandas as pd

    # 模拟一份采集到的效果数据
    df = pd.DataFrame(
        {
            "product_id": ["A", "A", "B", "B", "C"],
            "effect_date": ["2026-10-01", "2026-10-02", "2026-10-01", "2026-10-02", "2026-10-01"],
            "impression": [1000, 1200, 800, 850, 500],
            "pay_amount": [100.5, 150.0, 80.0, 90.0, 60.0],
            "cost": [20.0, 25.0, 15.0, 15.0, 10.0],
        }
    )

    # 清洗
    clean_df = clean(df)
    print("清洗后：")
    print(clean_df)

    # 分析
    analyzer = analyze(clean_df)
    print("\nTOP 商品：")
    print(analyzer.top_products(by="pay_amount", n=3))


def demo_visualize():
    """示例 3：可视化。"""
    import pandas as pd

    df = pd.DataFrame(
        {
            "effect_date": ["2026-10-01", "2026-10-02", "2026-10-03"],
            "pay_amount": [100, 150, 130],
            "cost": [20, 25, 22],
        }
    )
    viz = DataVisualizer(df)
    path = viz.trend_chart("effect_date", ["pay_amount", "cost"], save_path="trend.png")
    print(f"趋势图已保存到 {path}")


if __name__ == "__main__":
    import sys

    demo = sys.argv[1] if len(sys.argv) > 1 else "clean"
    {
        "search": demo_search,
        "clean": demo_clean_and_analyze,
        "viz": demo_visualize,
    }[demo]()