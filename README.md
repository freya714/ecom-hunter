# ecom-hunter 🛒

> 多平台电商数据采集与智能分析框架 —— 一行代码，采集四大平台数据。

<p align="center">
  <b>拼多多</b> · <b>淘宝</b> · <b>京东</b> · <b>抖音</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platforms-4-orange.svg" alt="Platforms">
</p>

## ✨ 特性

- 🚀 **一行代码采集**：统一的 `EcomHunter` 入口，无需了解各平台差异
- 🛡️ **内置反爬策略**：随机 UA、随机延迟、指数退避重试、代理池接口
- 📊 **统一数据格式**：所有平台输出同一套 `DataSchema`，下游逻辑完全复用
- 🧹 **集成数据清洗**：去重、空值处理、异常标记，一行调用
- 📈 **内置数据分析**：趋势、TOP 排行、转化漏斗、ROI 分析
- 📉 **一键可视化**：matplotlib 静态图 + Streamlit 交互式看板

## 📦 安装

```bash
# 1. 克隆项目
git clone https://github.com/zhangwt121/ecom-hunter.git
cd ecom-hunter

# 2. 安装依赖
pip install -e .

# 3. 安装浏览器驱动（Playwright）
playwright install chromium
```

## 🚀 快速开始

### 采集商品数据

```python
from ecom_hunter import EcomHunter

hunter = EcomHunter()

# 搜索商品（京东/淘宝支持公开搜索）
data = hunter.collect("jd", keyword="蓝牙耳机")
df = data.to_dataframe("products")
print(df[["title", "price", "shop_name"]].head())
```

### 采集商品效果数据（拼多多商家后台）

```python
from ecom_hunter import EcomHunter

hunter = EcomHunter()

# 首次运行会打开浏览器登录，登录态自动持久化，之后无需重复登录
data = hunter.collect(
    "pinduoduo",
    data_date="2026-10-08",
    include_effect=True,
)
df = data.to_dataframe("effects")
```

### 清洗 → 分析 → 可视化

```python
from ecom_hunter.data.cleaner import clean
from ecom_hunter.data.analyzer import analyze
from ecom_hunter.data.visualizer import DataVisualizer

# 清洗
clean_df = clean(df)

# 分析
analyzer = analyze(clean_df)
top = analyzer.top_products(by="pay_amount", n=10)

# 可视化
DataVisualizer(clean_df).run_dashboard("我的电商看板")
```

## 🏗️ 架构

```
ecom_hunter/
├── core/              # 核心框架
│   ├── collector.py   #   统一入口 EcomHunter（平台路由）
│   ├── engine.py      #   引擎基类 BaseEngine
│   ├── models.py      #   统一数据模型（Product / ProductEffect / CampaignData）
│   └── anti_crawl.py  #   反爬策略
├── platforms/         # 平台引擎
│   ├── pinduoduo.py   #   拼多多（Playwright + 登录态持久化）
│   ├── taobao.py      #   淘宝
│   ├── jd.py          #   京东（公开 API + 移动端）
│   └── douyin.py      #   抖音
├── data/              # 数据处理
│   ├── cleaner.py     #   清洗
│   ├── analyzer.py    #   分析
│   └── visualizer.py  #   可视化
└── utils/             # 工具
    ├── config.py      #   配置加载
    └── logger.py      #   日志
```

## 🧩 扩展新平台

只需三步即可接入新平台：

```python
# ecom_hunter/platforms/myplatform.py
from ecom_hunter.core.engine import BaseEngine
from ecom_hunter.core.models import DataSchema, Platform, Product

class MyPlatformEngine(BaseEngine):
    platform = Platform.MYPLATFORM  # 在 models.py 的 Platform 枚举中新增

    def collect(self, **kwargs):
        schema = self._make_schema()
        # ... 实现采集逻辑 ...
        schema.products = [...]
        return schema
```

然后在 `collector.py` 的 `_engine_registry` 中注册即可。

## 📚 详细文档

- [数据模型说明](docs/models.md)
- [配置说明](docs/config.md)

## ⚠️ 免责声明

本项目仅供学习交流使用。请遵守各平台的《服务协议》与相关法律法规，
**合理、克制地**使用数据采集功能，不要进行高频、恶意抓取。因使用本项目造成的任何后果由使用者自行承担。

## 📄 License

[MIT License](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- 发现 bug → 提 Issue
- 新平台支持 → 提交 PR
- 文档改进 → 直接提 PR