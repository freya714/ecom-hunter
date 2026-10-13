"""配置加载 —— 从 YAML / JSON 文件或字典加载配置。"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件。

    支持 YAML（需要 PyYAML）和 JSON。若 path 为空，返回空字典。
    """
    if path is None:
        return {}

    if not os.path.exists(path):
        raise FileNotFoundError(f"配置文件不存在：{path}")

    ext = os.path.splitext(path)[1].lower()
    with open(path, encoding="utf-8") as f:
        if ext in (".yaml", ".yml"):
            try:
                import yaml

                return yaml.safe_load(f) or {}
            except ImportError:
                raise ImportError("请安装 PyYAML：pip install pyyaml")
        elif ext == ".json":
            return json.load(f)
        else:
            raise ValueError(f"不支持的配置格式：{ext}，请使用 .yaml / .yml / .json")


def merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """浅层合并配置，override 覆盖 base。"""
    merged = base.copy()
    merged.update(override)
    return merged