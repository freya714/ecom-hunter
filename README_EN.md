# ecom-hunter 🛒

> Multi-platform e-commerce data collection and intelligent analysis framework — Collect data from 4 major platforms with one line of code.

<p align="center">
  <b>Pinduoduo</b> · <b>Taobao</b> · <b>JD.com</b> · <b>Douyin</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platforms-4-orange.svg" alt="Platforms">
</p>

## ✨ Features

- 🚀 **One-line Collection**: Unified `EcomHunter` entry, no need to understand platform differences
- 🛡️ **Built-in Anti-crawl**: Random UA, random delays, exponential backoff retry, proxy pool interface
- 📊 **Unified Data Format**: All platforms output the same `DataSchema`, downstream logic fully reusable
- 🧹 **Integrated Data Cleaning**: Deduplication, null handling, anomaly detection in one call
- 📈 **Built-in Data Analysis**: Trends, TOP rankings, conversion funnel, ROI analysis
- 📉 **One-click Visualization**: matplotlib static charts + Streamlit interactive dashboard

## 📦 Installation

```bash
# 1. Clone the project
git clone https://github.com/zhangwt121/ecom-hunter.git
cd ecom-hunter

# 2. Install dependencies
pip install -e .

# 3. Install browser driver (Playwright)
playwright install chromium
```

## 🚀 Quick Start

### Collect Product Data

```python
from ecom_hunter import EcomHunter

hunter = EcomHunter()

# Search products (JD.com/Taobao support public search)
data = hunter.collect("jd", keyword="wireless earbuds")
df = data.to_dataframe("products")
print(df[["title", "price", "shop_name"]].head())
```

### Collect Product Performance Data (Pinduoduo Merchant Backend)

```python
from ecom_hunter import EcomHunter

hunter = EcomHunter()

# First run will open browser for login, login state is automatically persisted
data = hunter.collect(
    "pinduoduo",
    data_date="2026-10-08",
    include_effect=True,
)
df = data.to_dataframe("effects")
```

### Clean → Analyze → Visualize

```python
from ecom_hunter.data.cleaner import clean
from ecom_hunter.data.analyzer import analyze
from ecom_hunter.data.visualizer import DataVisualizer

# Clean
clean_df = clean(df)

# Analyze
analyzer = analyze(clean_df)
top = analyzer.top_products(by="pay_amount", n=10)

# Visualize
DataVisualizer(clean_df).run_dashboard("My E-commerce Dashboard")
```

## 🏗️ Architecture

```
ecom_hunter/
├── core/              # Core framework
│   ├── collector.py   #   Unified entry EcomHunter (platform routing)
│   ├── engine.py      #   Engine base class BaseEngine
│   ├── models.py      #   Unified data models (Product / ProductEffect / CampaignData)
│   └── anti_crawl.py  #   Anti-crawl strategies
├── platforms/         # Platform engines
│   ├── pinduoduo.py   #   Pinduoduo (Playwright + persistent login state)
│   ├── taobao.py      #   Taobao
│   ├── jd.py          #   JD.com (public API + mobile)
│   └── douyin.py      #   Douyin
├── data/              # Data processing
│   ├── cleaner.py     #   Cleaning
│   ├── analyzer.py    #   Analysis
│   └── visualizer.py  #   Visualization
└── utils/             # Utilities
    ├── config.py      #   Configuration loading
    └── logger.py      #   Logging
```

## 🧩 Extending to New Platforms

Only three steps to integrate a new platform:

```python
# ecom_hunter/platforms/myplatform.py
from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.models import DataSchema, Platform, Product

class MyPlatformEngine(BaseEngine):
    platform = Platform.MYPLATFORM  # Add to Platform enum in models.py

    def collect(self, **kwargs):
        schema = self._make_schema()
        # ... implement collection logic ...
        schema.products = [...]
        return schema
```

Then register it in `_engine_registry` in `collector.py`.

## 📚 Documentation

- [Data Models](docs/models.md)
- [Configuration Guide](docs/config.md)

## ⚠️ Disclaimer

This project is for learning and research purposes only. Please comply with each platform's Terms of Service and relevant laws and regulations. Use data collection features **responsibly and moderately** — do not engage in high-frequency or malicious scraping. You are solely responsible for any consequences arising from the use of this project.

## 📄 License

[MIT License](LICENSE)

## 🤝 Contributing

Issues and Pull Requests are welcome!

- Found a bug → Open an Issue
- New platform support → Submit a PR
- Documentation improvements → Submit a PR directly
