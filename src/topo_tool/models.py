from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ShapeType = Literal["point", "polygon", "line"]


@dataclass(frozen=True)
class Style:
    """A named visual style for features.

    ``color`` is a hex RGB string (e.g. ``#00ff00``).
    ``opacity`` is a float in 0.0–1.0.
    """

    name: str
    color: str
    opacity: float


@dataclass(frozen=True)
class Projection:
    """A named coordinate reference system definition.

    ``definition`` is a PROJ string or ``EPSG:xxxx`` code.
    """

    name: str
    definition: str


@dataclass(frozen=True)
class Feature:
    """A geographic feature: point, polygon, or line (path).

    Coordinates are always a tuple of (lon/x, lat/y) pairs.
    For points, this is a single-element tuple.

    ``crs`` references a projection name defined in the YAML
    ``projections`` section, or a built-in ``EPSG:xxxx`` code.

    ``style`` optionally references a named style from the
    ``styles`` section. If omitted, polygons get a default
    (white fill at 50% opacity) and lines/points are unstyled.
    """

    name: str
    type: ShapeType
    crs: str
    coords: tuple[tuple[float, float], ...]
    description: str | None = None
    style: str | None = None


@dataclass(frozen=True)
class Document:
    """A complete input document: styles, projections + features."""

    styles: tuple[Style, ...] = ()
    projections: tuple[Projection, ...] = ()
    features: tuple[Feature, ...] = ()
