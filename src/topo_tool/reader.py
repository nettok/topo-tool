from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import yaml

from topo_tool.models import Document, Feature, Projection, ShapeType, Style

_VALID_TYPES: set[ShapeType] = {"point", "polygon", "line"}
_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def load_document(path: Path) -> Document:
    """Parse a YAML file and return a validated Document."""
    raw = _read_yaml(path)
    styles = _parse_styles(raw.get("styles", {}))
    style_names = {s.name for s in styles}
    projections = _parse_projections(raw.get("projections", {}))
    features_data = raw.get("features", [])
    if not isinstance(features_data, list):
        raise ValueError("'features' must be a list")
    features = tuple(_parse_feature(fd, style_names) for fd in features_data)
    return Document(styles=styles, projections=projections, features=features)


def _read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return data


def _parse_styles(data: object) -> tuple[Style, ...]:
    if not isinstance(data, dict):
        raise ValueError("'styles' must be a mapping of name → {color, opacity}")
    result = []
    for name, style_data in data.items():
        if not isinstance(style_data, dict):
            raise ValueError(
                f"Style '{name}': must be a mapping with 'color' and 'opacity'"
            )
        color = style_data.get("color")
        opacity = style_data.get("opacity")

        if not isinstance(color, str) or not _COLOR_PATTERN.match(color):
            raise ValueError(
                f"Style '{name}': 'color' must be a hex RGB like '#00ff00', got {color!r}"
            )
        if not isinstance(opacity, (int, float)):
            raise ValueError(
                f"Style '{name}': 'opacity' must be a number in 0.0–1.0, got {opacity!r}"
            )
        opacity_f = float(opacity)
        if not (0.0 <= opacity_f <= 1.0):
            raise ValueError(
                f"Style '{name}': 'opacity' must be between 0.0 and 1.0, got {opacity_f}"
            )

        stripped_name = str(name).strip()
        result.append(Style(name=stripped_name, color=color.strip(), opacity=opacity_f))
    return tuple(result)


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


def _parse_feature(data: object, style_names: set[str]) -> Feature:
    if not isinstance(data, dict):
        raise ValueError(f"Each feature must be a mapping, got {type(data).__name__}")

    name = _require_str(data, "name")
    ftype = _require_str(data, "type")
    crs = _require_str(data, "crs")
    coords_raw = data.get("coords")
    description = data.get("description")
    style_name = data.get("style")

    if ftype not in _VALID_TYPES:
        raise ValueError(
            f"Feature '{name}': invalid type '{ftype}', must be one of {_VALID_TYPES}"
        )

    coords = _normalize_coords(ftype, coords_raw, name)

    if description is not None and not isinstance(description, str):
        raise ValueError(
            f"Feature '{name}': 'description' must be a string, got {type(description).__name__}"
        )

    if style_name is not None:
        if not isinstance(style_name, str) or not style_name.strip():
            raise ValueError(
                f"Feature '{name}': 'style' must be a string referencing a style name"
            )
        style_name = style_name.strip()
        if style_name not in style_names:
            raise ValueError(
                f"Feature '{name}': style '{style_name}' is not defined. "
                f"Available styles: {sorted(style_names)}"
            )

    return Feature(
        name=name,
        type=cast(ShapeType, ftype),
        crs=crs,
        coords=coords,
        description=description,
        style=style_name,
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
