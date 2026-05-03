from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ShapeType = Literal["point", "polygon", "line"]


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
    """

    name: str
    type: ShapeType
    crs: str
    coords: tuple[tuple[float, float], ...]
    description: str | None = None


@dataclass(frozen=True)
class Document:
    """A complete input document: custom projections + features."""

    projections: tuple[Projection, ...]
    features: tuple[Feature, ...]
