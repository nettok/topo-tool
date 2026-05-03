from __future__ import annotations

from pathlib import Path
from typing import cast

import yaml

from topo_tool.models import Document, Feature, Projection, ShapeType

_VALID_TYPES: set[ShapeType] = {"point", "polygon", "line"}


def load_document(path: Path) -> Document:
    """Parse a YAML file and return a validated Document."""
    raw = _read_yaml(path)
    projections = _parse_projections(raw.get("projections", {}))
    features_data = raw.get("features", [])
    if not isinstance(features_data, list):
        raise ValueError("'features' must be a list")
    features = tuple(_parse_feature(fd) for fd in features_data)
    return Document(projections=projections, features=features)


def _read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return data


def _parse_projections(data: object) -> tuple[Projection, ...]:
    if not isinstance(data, dict):
        raise ValueError("'projections' must be a mapping of name → definition")
    result = []
    for name, definition in data.items():
        if not isinstance(definition, str) or not definition.strip():
            raise ValueError(
                f"Projection '{name}': definition must be a non-empty string"
            )
        result.append(Projection(name=str(name).strip(), definition=definition.strip()))
    return tuple(result)


def _parse_feature(data: object) -> Feature:
    if not isinstance(data, dict):
        raise ValueError(f"Each feature must be a mapping, got {type(data).__name__}")

    name = _require_str(data, "name")
    ftype = _require_str(data, "type")
    crs = _require_str(data, "crs")
    coords_raw = data.get("coords")
    description = data.get("description")

    if ftype not in _VALID_TYPES:
        raise ValueError(
            f"Feature '{name}': invalid type '{ftype}', must be one of {_VALID_TYPES}"
        )

    coords = _normalize_coords(ftype, coords_raw, name)

    if description is not None and not isinstance(description, str):
        raise ValueError(
            f"Feature '{name}': 'description' must be a string, got {type(description).__name__}"
        )

    return Feature(
        name=name,
        type=cast(ShapeType, ftype),
        crs=crs,
        coords=coords,
        description=description,
    )


def _normalize_coords(
    ftype: str, raw: object, name: str
) -> tuple[tuple[float, float], ...]:
    if raw is None or not isinstance(raw, (list, tuple)):
        raise ValueError(f"Feature '{name}': 'coords' must be a list")

    if ftype == "point":
        pairs = _normalize_point_coords(raw, name)
    else:
        pairs = [_coerce_pair(item, name) for item in raw]

    _validate_coords_count(ftype, pairs, name)
    return tuple(pairs)


def _normalize_point_coords(
    raw: object, name: str
) -> list[tuple[float, float]]:
    """Expect a single [lon, lat] pair. Raise if nested or wrong length."""
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise ValueError(
            f"Feature '{name}': point must have exactly 1 coordinate as [lon, lat]"
        )
    if isinstance(raw[0], (list, tuple)):
        raise ValueError(
            f"Feature '{name}': point must have exactly 1 coordinate as [lon, lat]"
        )
    return [(float(raw[0]), float(raw[1]))]


def _coerce_pair(item: object, name: str) -> tuple[float, float]:
    if not isinstance(item, (list, tuple)) or len(item) != 2:
        raise ValueError(
            f"Feature '{name}': each coordinate must be [lon, lat], got {item}"
        )
    return (float(item[0]), float(item[1]))


def _validate_coords_count(
    ftype: str, pairs: list[tuple[float, float]], name: str
) -> None:
    count = len(pairs)
    if ftype == "point" and count != 1:
        raise ValueError(f"Feature '{name}': point must have exactly 1 coordinate")
    if ftype == "line" and count < 2:
        raise ValueError(
            f"Feature '{name}': line must have at least 2 coordinates, got {count}"
        )
    if ftype == "polygon" and count < 3:
        raise ValueError(
            f"Feature '{name}': polygon must have at least 3 coordinates, got {count}"
        )


def _require_str(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Feature is missing required string field '{key}'")
    return value.strip()
