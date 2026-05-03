from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from topo_tool.models import Document, Feature, Projection


def test_projection_creation() -> None:
    proj = Projection(name="GTM", definition="+proj=tmerc +lat_0=0 +lon_0=-90.5")
    assert proj.name == "GTM"
    assert "tmerc" in proj.definition


def test_feature_creation_with_all_fields() -> None:
    feat = Feature(
        name="Test Point",
        type="point",
        crs="GTM",
        coords=((496666, 1659194),),
        description="A point of interest",
    )
    assert feat.name == "Test Point"
    assert feat.type == "point"
    assert feat.crs == "GTM"
    assert feat.coords == ((496666, 1659194),)
    assert feat.description == "A point of interest"


def test_feature_creation_without_description() -> None:
    feat = Feature(
        name="Test Line",
        type="line",
        crs="EPSG:4326",
        coords=((-89.6, 14.5), (-89.7, 14.6)),
    )
    assert feat.description is None


def test_feature_is_frozen() -> None:
    feat = Feature(
        name="Test",
        type="point",
        crs="EPSG:4326",
        coords=((-89.6, 14.5),),
    )
    with pytest.raises(FrozenInstanceError):
        feat.name = "Changed"


def test_document_creation() -> None:
    proj = Projection(name="GTM", definition="+proj=tmerc")
    feat = Feature(
        name="P", type="point", crs="GTM", coords=((100, 200),)
    )
    doc = Document(projections=(proj,), features=(feat,))
    assert len(doc.projections) == 1
    assert len(doc.features) == 1
    assert doc.projections[0].name == "GTM"
    assert doc.features[0].name == "P"
