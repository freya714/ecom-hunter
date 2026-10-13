# 数据模型说明

ecom-hunter 的核心设计是**统一数据模型**：无论采集哪个平台，输出都是同一套 schema。

## Product（商品基础信息）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| platform | Platform | 来源平台 |
| product_id | str | 商品 ID |
| title | str | 商品标题 |
| price | float | 当前售价 |
| original_price | float | 原价 |
| shop_name | str | 店铺名称 |
| sales_count | int | 累计销量 |
| rating | float | 评分 |
| crawled_at | datetime | 采集时间 |

## ProductEffect（商品效果数据）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| effect_date | str | 数据日期 YYYY-MM-DD |
| impression | int | 曝光量 |
| click | int | 点击量 |
| ctr | float | 点击率 % |
| pay_amount | float | 成交金额 |
| conversion_rate | float | 转化率 % |
| refund_count | int | 退款单数 |

## CampaignData（推广数据）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| cost | float | 花费 |
| roi | float | 投产比 |
| gmv | float | 成交金额 |