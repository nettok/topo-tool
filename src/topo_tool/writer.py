from __future__ import annotations

from pathlib import Path

import simplekml

from topo_tool.models import Feature, Style

# Default polygon style: white fill at 50%, white outline
_DEFAULT_FILL = "80ffffff"
_DEFAULT_OUTLINE = "ffffffff"


def features_to_kml(
    features: tuple[Feature, ...],
    styles: tuple[Style, ...] = (),
) -> simplekml.Kml:
    """Transform Feature objects into a simplekml.Kml document.

    Pure transformation — does not write to disk.
    """
    style_map = {s.name: s for s in styles}
    kml = simplekml.Kml()

    for feat in features:
        _add_placemark(kml, feat, style_map)

    return kml


def write_kml(path: Path, kml: simplekml.Kml) -> None:
    """Write a Kml document to disk. Side effect at the program edge."""
    kml.save(str(path))


def _add_placemark(
    kml: simplekml.Kml,
    feat: Feature,
    style_map: dict[str, Style],
) -> None:
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
        if feat.style and feat.style in style_map:
            s = style_map[feat.style]
            placemark.style.linestyle.color = _to_kml_color(s.color, 1.0)
    elif poly is not None:
        placemark = poly(name=feat.name)
        coords = list(feat.coords)
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        placemark.outerboundaryis = coords
        _apply_polygon_style(placemark, feat.style, style_map)

    if placemark is None:
        raise ValueError(f"Unknown feature type: {feat.type}")

    if feat.description:
        placemark.description = feat.description


def _apply_polygon_style(
    poly: simplekml.Polygon,
    style_name: str | None,
    style_map: dict[str, Style],
) -> None:
    if style_name and style_name in style_map:
        s = style_map[style_name]
        fill = _to_kml_color(s.color, s.opacity)
        outline = _to_kml_color(s.color, 1.0)
    else:
        fill = _DEFAULT_FILL
        outline = _DEFAULT_OUTLINE

    poly.style.polystyle.color = fill
    poly.style.polystyle.fill = 1
    poly.style.linestyle.color = outline


def _to_kml_color(hex_rgb: str, opacity: float) -> str:
    """Convert '#rrggbb' + opacity to KML AABBGGRR hex format."""
    r = hex_rgb[1:3]
    g = hex_rgb[3:5]
    b = hex_rgb[5:7]
    a = hex(int(opacity * 255 + 0.5))[2:].zfill(2)
    return f"{a}{b}{g}{r}"
