from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from topo_tool.models import Feature
from topo_tool.writer import features_to_kml, write_kml

_KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


def _parse(kml_str: str) -> ET.Element:
    return ET.fromstring(kml_str)


def test_point_to_kml() -> None:
    feat = Feature(
        name="Test Point",
        type="point",
        crs="EPSG:4326",
        coords=((-89.6, 14.5),),
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    placemarks = root.findall(".//kml:Placemark", _KML_NS)
    assert len(placemarks) == 1

    name = placemarks[0].find("kml:name", _KML_NS)
    assert name is not None
    assert name.text == "Test Point"

    point = placemarks[0].find(".//kml:Point", _KML_NS)
    assert point is not None

    coords = point.find(".//kml:coordinates", _KML_NS)
    assert coords is not None
    assert coords.text is not None
    assert "-89.6,14.5" in coords.text


def test_polygon_to_kml() -> None:
    feat = Feature(
        name="Forest",
        type="polygon",
        crs="EPSG:4326",
        coords=(
            (-89.6, 14.5),
            (-89.7, 14.5),
            (-89.7, 14.6),
        ),
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    polygon = root.find(".//kml:Polygon", _KML_NS)
    assert polygon is not None

    outer = polygon.find(".//kml:outerBoundaryIs", _KML_NS)
    assert outer is not None

    linear_ring = outer.find(".//kml:LinearRing", _KML_NS)
    assert linear_ring is not None

    coords = linear_ring.find(".//kml:coordinates", _KML_NS)
    assert coords is not None
    assert coords.text is not None
    assert "-89.6,14.5" in coords.text
    assert "-89.7,14.5" in coords.text
    assert "-89.7,14.6" in coords.text


def test_line_to_kml() -> None:
    feat = Feature(
        name="Trail",
        type="line",
        crs="EPSG:4326",
        coords=((-89.6, 14.5), (-89.7, 14.6)),
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    linestring = root.find(".//kml:LineString", _KML_NS)
    assert linestring is not None

    coords = linestring.find(".//kml:coordinates", _KML_NS)
    assert coords is not None
    assert coords.text is not None
    assert "-89.6,14.5" in coords.text
    assert "-89.7,14.6" in coords.text


def test_description_included() -> None:
    feat = Feature(
        name="Sign",
        type="point",
        crs="EPSG:4326",
        coords=((-89.6, 14.5),),
        description="No entry",
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    desc = root.find(".//kml:description", _KML_NS)
    assert desc is not None
    assert desc.text == "No entry"


def test_no_description_element_when_none() -> None:
    feat = Feature(
        name="Sign",
        type="point",
        crs="EPSG:4326",
        coords=((-89.6, 14.5),),
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    placemark = root.find(".//kml:Placemark", _KML_NS)
    assert placemark is not None
    desc = placemark.find("kml:description", _KML_NS)
    assert desc is None


def test_multiple_features() -> None:
    feat1 = Feature(
        name="A", type="point", crs="EPSG:4326", coords=((-10.0, 20.0),)
    )
    feat2 = Feature(
        name="B", type="point", crs="EPSG:4326", coords=((-11.0, 21.0),)
    )
    kml_doc = features_to_kml((feat1, feat2))
    root = _parse(kml_doc.kml())

    placemarks = root.findall(".//kml:Placemark", _KML_NS)
    assert len(placemarks) == 2


def test_empty_features_produces_document() -> None:
    kml_doc = features_to_kml(())
    root = _parse(kml_doc.kml())

    doc = root.find("kml:Document", _KML_NS)
    assert doc is not None


def test_blank_description_treated_as_no_description() -> None:
    feat = Feature(
        name="Sign",
        type="point",
        crs="EPSG:4326",
        coords=((-89.6, 14.5),),
        description="",
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    placemark = root.find(".//kml:Placemark", _KML_NS)
    assert placemark is not None
    desc = placemark.find("kml:description", _KML_NS)
    assert desc is None


def test_write_kml_creates_file(tmp_path: Path) -> None:
    feat = Feature(
        name="P", type="point", crs="EPSG:4326", coords=((-10.0, 20.0),)
    )
    kml = features_to_kml((feat,))
    out_path = tmp_path / "output.kml"

    write_kml(out_path, kml)

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "P" in content
    assert "-10.0,20.0" in content


def test_polygon_auto_closes_when_open() -> None:
    feat = Feature(
        name="Area",
        type="polygon",
        crs="EPSG:4326",
        coords=((-89.6, 14.5), (-89.7, 14.5), (-89.7, 14.6)),
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    coords = root.find(".//kml:coordinates", _KML_NS)
    assert coords is not None
    assert coords.text is not None
    parts = coords.text.split()
    # Should have 4 entries: 3 original + first repeated
    assert len(parts) == 4
    assert parts[0] == parts[-1]


def test_already_closed_polygon_not_duplicated() -> None:
    feat = Feature(
        name="Area",
        type="polygon",
        crs="EPSG:4326",
        coords=((-89.6, 14.5), (-89.7, 14.5), (-89.7, 14.6), (-89.6, 14.5)),
    )
    kml_doc = features_to_kml((feat,))
    root = _parse(kml_doc.kml())

    coords = root.find(".//kml:coordinates", _KML_NS)
    assert coords is not None
    assert coords.text is not None
    parts = coords.text.split()
    # Should still have 4 entries, not 5
    assert len(parts) == 4
