"""统一采集入口 —— EcomHunter。

这是用户唯一需要接触的顶层对象，负责：
1. 根据平台名路由到对应的采集引擎
2. 统一的错误处理与日志
3. 结果以 DataSchema 返回，保证跨平台结构一致
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from loguru import logger

from ecom_hunter.core.models import Platform, DataSchema
from ecom_hunter.core.engine import BaseEngine


class EcomHunter:
    """多平台电商数据采集器统一入口。

    Example:
        >>> hunter = EcomHunter()
        >>> data = hunter.collect("pinduoduo", product_id="123456")
        >>> df = data.to_dataframe("effects")
    """

    # 平台 -> 引擎类 的注册表（延迟导入避免循环依赖）
    _engine_registry: Dict[str, str] = {
        "pinduoduo": "ecom_hunter.platforms.pinduoduo.PinduoduoEngine",
        "taobao": "ecom_hunter.platforms.taobao.TaobaoEngine",
        "jd": "ecom_hunter.platforms.jd.JDEngine",
        "douyin": "ecom_hunter.platforms.douyin.DouyinEngine",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._engines: Dict[str, BaseEngine] = {}

    def _get_engine(self, platform: str) -> BaseEngine:
        """获取（并缓存）指定平台的采集引擎实例。"""
        if platform in self._engines:
            return self._engines[platform]

        module_path = self._engine_registry.get(platform)
        if module_path is None:
            raise ValueError(
                f"不支持的平台 '{platform}'，可用平台：{list(self._engine_registry)}"
            )

        module_name, class_name = module_path.rsplit(".", 1)
        try:
            import importlib

            module = importlib.import_module(module_name)
            engine_cls = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"加载平台引擎失败：{platform} —— {e}") from e

        engine = engine_cls(config=self.config.get(platform, {}))
        self._engines[platform] = engine
        return engine

    def collect(
        self,
        platform: str,
        product_id: Optional[str] = None,
        shop_id: Optional[str] = None,
        keyword: Optional[str] = None,
        data_date: Optional[str] = None,
        include_effect: bool = False,
        include_campaign: bool = False,
        **kwargs: Any,
    ) -> DataSchema:
        """采集指定平台的数据。

        Args:
            platform: 平台名（pinduoduo / taobao / jd / douyin）
            product_id: 商品 ID
            shop_id: 店铺 ID
            keyword: 搜索关键词
            data_date: 数据日期
            include_effect: 是否采集效果数据
            include_campaign: 是否采集推广数据
        """
        logger.info(f"开始采集 {platform}，条件: product_id={product_id}, keyword={keyword}")
        engine = self._get_engine(platform)
        result = engine.collect(
            product_id=product_id,
            shop_id=shop_id,
            keyword=keyword,
            data_date=data_date,
            include_effect=include_effect,
            include_campaign=include_campaign,
            **kwargs,
        )
        logger.info(f"采集完成，商品 {len(result.products)} 条，效果 {len(result.effects)} 条")
        return result

    def collect_effects(
        self,
        platform: str,
        data_date: str,
        product_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> DataSchema:
        """快捷方法：只采集商品效果数据。"""
        engine = self._get_engine(platform)
        return engine.collect_effects(data_date=data_date, product_ids=product_ids, **kwargs)

    def list_platforms(self) -> List[str]:
        """列出所有支持的平台。"""
        return list(self._engine_registry.keys())