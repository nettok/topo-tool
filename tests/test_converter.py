from __future__ import annotations

import pytest

from topo_tool.converter import reproject_features
from topo_tool.models import Feature, Projection

_GTM_DEF = (
    "+proj=tmerc +lat_0=0 +lon_0=-90.5 +k=0.9998 "
    "+x_0=500000 +y_0=0 +datum=WGS84 +units=m"
)


def test_wgs84_features_passthrough() -> None:
    features = (
        Feature(name="A", type="point", crs="EPSG:4326", coords=((-89.6, 14.5),)),
        Feature(
            name="B",
            type="polygon",
            crs="EPSG:4326",
            coords=((-89.6, 14.5), (-89.7, 14.5), (-89.7, 14.6)),
        ),
    )
    result = reproject_features(features)
    assert result == features
    assert len(result) == 2


def test_empty_features_passthrough() -> None:
    result = reproject_features(())
    assert result == ()


def test_gtm_to_wgs84_point() -> None:
    proj = Projection(name="GTM", definition=_GTM_DEF)
    feat = Feature(
        name="Gate",
        type="point",
        crs="GTM",
        coords=((496666, 1659194),),
    )
    result = reproject_features((feat,), (proj,))
    assert len(result) == 1
    assert result[0].crs == "EPSG:4326"
    lon, lat = result[0].coords[0]
    assert -91 < lon < -90
    assert 14 < lat < 16


def test_gtm_to_wgs84_polygon() -> None:
    proj = Projection(name="GTM", definition=_GTM_DEF)
    feat = Feature(
        name="Property",
        type="polygon",
        crs="GTM",
        coords=(
            (496666, 1659194),
            (497000, 1659194),
            (497000, 1658800),
        ),
    )
    result = reproject_features((feat,), (proj,))
    assert len(result) == 1
    assert result[0].crs == "EPSG:4326"
    for lon, lat in result[0].coords:
        assert -91 < lon < -90
        assert 14 < lat < 16


def test_gtm_to_wgs84_line() -> None:
    proj = Projection(name="GTM", definition=_GTM_DEF)
    feat = Feature(
        name="Trail",
        type="line",
        crs="GTM",
        coords=(
            (496666, 1659194),
            (497000, 1658800),
        ),
    )
    result = reproject_features((feat,), (proj,))
    assert len(result) == 1
    assert result[0].crs == "EPSG:4326"
    assert len(result[0].coords) == 2


def test_unknown_crs_raises() -> None:
    feat = Feature(
        name="X", type="point", crs="NonExistent", coords=((0, 0),)
    )
    with pytest.raises(ValueError, match="unknown CRS 'NonExistent'"):
        reproject_features((feat,), ())


def test_invalid_crs_definition_raises() -> None:
    proj = Projection(name="BAD", definition="not a valid proj string")
    feat = Feature(
        name="X", type="point", crs="BAD", coords=((0, 0),)
    )
    with pytest.raises(ValueError, match="invalid CRS definition"):
        reproject_features((feat,), (proj,))


def test_duplicate_projection_names_raises() -> None:
    proj1 = Projection(name="GTM", definition=_GTM_DEF)
    proj2 = Projection(name="GTM", definition="+proj=latlong")
    feat = Feature(
        name="X", type="point", crs="GTM", coords=((0, 0),)
    )
    with pytest.raises(ValueError, match="Duplicate projection name 'GTM'"):
        reproject_features((feat,), (proj1, proj2))


def test_mixed_crs_features() -> None:
    """Some features are already WGS84, others need reprojection."""
    proj = Projection(name="GTM", definition=_GTM_DEF)
    wgs84_feat = Feature(
        name="WGS84 Point", type="point", crs="EPSG:4326", coords=((-89.6, 14.5),)
    )
    gtm_feat = Feature(
        name="GTM Point", type="point", crs="GTM", coords=((496666, 1659194),)
    )
    result = reproject_features((wgs84_feat, gtm_feat), (proj,))
    assert len(result) == 2
    # WGS84 feature passes through unchanged (same coords)
    assert result[0].coords == wgs84_feat.coords
    # GTM feature is reprojected
    assert result[1].crs == "EPSG:4326"
    lon, lat = result[1].coords[0]
    assert -91 < lon < -90
    assert 14 < lat < 16


def test_reprojection_preserves_style() -> None:
    proj = Projection(name="GTM", definition=_GTM_DEF)
    feat = Feature(
        name="Forest",
        type="polygon",
        crs="GTM",
        coords=((496666, 1659194), (497000, 1659194), (497000, 1658800)),
        style="protected_forest",
    )
    result = reproject_features((feat,), (proj,))
    assert len(result) == 1
    assert result[0].style == "protected_forest"
