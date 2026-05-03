from __future__ import annotations

from pathlib import Path

import simplekml

from topo_tool.models import Feature


def features_to_kml(features: tuple[Feature, ...]) -> simplekml.Kml:
    """Transform Feature objects into a simplekml.Kml document.

    Pure transformation — does not write to disk.
    """
    kml = simplekml.Kml()

    for feat in features:
        _add_placemark(kml, feat)

    return kml


def write_kml(path: Path, kml: simplekml.Kml) -> None:
    """Write a Kml document to disk. Side effect at the program edge."""
    kml.save(str(path))


def _add_placemark(kml: simplekml.Kml, feat: Feature) -> None:
    point = kml.newpoint if feat.type == "point" else None
    line = kml.newlinestring if feat.type == "line" else None
    poly = kml.newpolygon if feat.type == "polygon" else None

    placemark: simplekml.Feature | None = None
    if point is not None:
        placemark = point(name=feat.name)
        placemark.coords = [feat.coords[0]]
    elif line is not None:
        placemark = line(name=feat.name)
        placemark.coords = list(feat.coords)
    elif poly is not None:
        placemark = poly(name=feat.name)
        coords = list(feat.coords)
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        placemark.outerboundaryis = coords

    if placemark is None:
        raise ValueError(f"Unknown feature type: {feat.type}")

    if feat.description:
        placemark.description = feat.description
