from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from topo_tool.reader import load_document


def _write_yaml(data: object, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


# ── projections ───────────────────────────────────────────────────────


def test_parse_projections(tmp_path: Path) -> None:
    data = {
        "projections": {
            "GTM": "+proj=tmerc +lat_0=0 +lon_0=-90.5 +k=0.9998 +x_0=500000 +y_0=0 +datum=WGS84 +units=m"
        },
        "features": [],
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert len(doc.projections) == 1
    assert doc.projections[0].name == "GTM"
    assert "tmerc" in doc.projections[0].definition


def test_projection_empty_definition_raises(tmp_path: Path) -> None:
    data = {"projections": {"BAD": ""}, "features": []}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="definition must be a non-empty string"):
        load_document(filepath)


def test_projection_not_a_mapping_raises(tmp_path: Path) -> None:
    data = {"projections": "not-a-mapping", "features": []}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="projections.* must be a mapping"):
        load_document(filepath)


# ── valid inputs ──────────────────────────────────────────────────────


def test_load_point(tmp_path: Path) -> None:
    data = {
        "features": [
            {
                "name": "Sign",
                "type": "point",
                "crs": "EPSG:4326",
                "coords": [-89.6, 14.5],
                "description": "Warning sign",
            }
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert len(doc.features) == 1
    feat = doc.features[0]
    assert feat.name == "Sign"
    assert feat.type == "point"
    assert feat.crs == "EPSG:4326"
    assert feat.coords == ((-89.6, 14.5),)
    assert feat.description == "Warning sign"


def test_load_polygon(tmp_path: Path) -> None:
    data = {
        "features": [
            {
                "name": "Forest",
                "type": "polygon",
                "crs": "EPSG:4326",
                "coords": [[10.0, 20.0], [11.0, 20.0], [10.5, 21.0]],
            }
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert len(doc.features) == 1
    feat = doc.features[0]
    assert feat.type == "polygon"
    assert len(feat.coords) == 3


def test_load_line(tmp_path: Path) -> None:
    data = {
        "features": [
            {
                "name": "Trail",
                "type": "line",
                "crs": "EPSG:4326",
                "coords": [[10.0, 20.0], [11.0, 21.0]],
            }
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert len(doc.features) == 1
    feat = doc.features[0]
    assert feat.type == "line"
    assert len(feat.coords) == 2


def test_load_multiple_features(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "A", "type": "point", "crs": "EPSG:4326", "coords": [0, 0]},
            {"name": "B", "type": "point", "crs": "EPSG:4326", "coords": [1, 1]},
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert len(doc.features) == 2


def test_empty_features_yields_empty_tuple(tmp_path: Path) -> None:
    data: dict = {"features": []}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert doc.features == ()


def test_description_optional(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "P", "type": "point", "crs": "EPSG:4326", "coords": [0, 0]}
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    doc = load_document(filepath)
    assert doc.features[0].description is None


# ── invalid inputs ────────────────────────────────────────────────────


def test_missing_name(tmp_path: Path) -> None:
    data = {"features": [{"type": "point", "crs": "EPSG:4326", "coords": [0, 0]}]}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="missing required string field 'name'"):
        load_document(filepath)


def test_missing_type(tmp_path: Path) -> None:
    data = {"features": [{"name": "X", "crs": "EPSG:4326", "coords": [0, 0]}]}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="missing required string field 'type'"):
        load_document(filepath)


def test_missing_crs(tmp_path: Path) -> None:
    data = {"features": [{"name": "X", "type": "point", "coords": [0, 0]}]}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="missing required string field 'crs'"):
        load_document(filepath)


def test_invalid_type(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "X", "type": "square", "crs": "EPSG:4326", "coords": [[0, 0], [1, 1]]}
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="invalid type 'square'"):
        load_document(filepath)


def test_point_with_zero_coords_raises(tmp_path: Path) -> None:
    data = {
        "features": [{"name": "X", "type": "point", "crs": "EPSG:4326", "coords": []}]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="point must have exactly 1 coordinate"):
        load_document(filepath)


def test_point_with_two_coords_raises(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "X", "type": "point", "crs": "EPSG:4326", "coords": [[0, 0], [1, 1]]}
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="point must have exactly 1 coordinate"):
        load_document(filepath)


def test_line_with_one_coord_raises(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "X", "type": "line", "crs": "EPSG:4326", "coords": [[0, 0]]}
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="line must have at least 2 coordinates"):
        load_document(filepath)


def test_polygon_with_two_coords_raises(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "X", "type": "polygon", "crs": "EPSG:4326", "coords": [[0, 0], [1, 1]]}
        ]
    }
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="polygon must have at least 3 coordinates"):
        load_document(filepath)


def test_yaml_root_not_mapping(tmp_path: Path) -> None:
    data = [1, 2, 3]
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="YAML root must be a mapping"):
        load_document(filepath)


def test_feature_not_a_mapping(tmp_path: Path) -> None:
    data = {"features": ["not a mapping"]}
    filepath = tmp_path / "test.yaml"
    _write_yaml(data, filepath)

    with pytest.raises(ValueError, match="Each feature must be a mapping"):
        load_document(filepath)
