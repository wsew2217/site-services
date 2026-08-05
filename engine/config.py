from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent
DEFAULTS_PATH = ROOT / "defaults" / "parameters.json"
OPS_KPI_PATH = ROOT / "defaults" / "ops_kpis.json"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def default_settings() -> Dict[str, Any]:
    return load_json(DEFAULTS_PATH)


def default_ops_kpis() -> Dict[str, Any]:
    return load_json(OPS_KPI_PATH)


def merge_settings(overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    base = default_settings()
    if overrides:
        for k, v in overrides.items():
            if v is not None and str(v).strip() != "":
                base[k] = v
    return base


def num(settings: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(settings.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def as_bool(val: Any) -> bool:
    if val is True or val is False:
        return bool(val)
    s = str(val or "").strip().upper()
    return s.startswith("Y") or s in {"1", "TRUE", "T", "YES"}
