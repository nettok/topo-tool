from __future__ import annotations

from pyproj import CRS, Transformer
from pyproj.exceptions import CRSError

from topo_tool.models import Feature, Projection

# KML requires WGS84 geographic coordinates
_TARGET_EPSG = 4326


def reproject_features(
    features: tuple[Feature, ...],
    projections: tuple[Projection, ...] = (),
) -> tuple[Feature, ...]:
    """Reproject features from their declared CRS to WGS84 (EPSG:4326).

    ``projections`` maps custom CRS names (e.g. ``GTM``) to PROJ strings.
    Built-in EPSG codes are resolved directly by pyproj.
    """
    proj_map = {p.name: p.definition for p in projections}

    reprojected: list[Feature] = []
    for feat in features:
        reprojected.append(_reproject_one(feat, proj_map))
    return tuple(reprojected)


def _reproject_one(
    feat: Feature, proj_map: dict[str, str]
) -> Feature:
    # Resolve the definition string for this feature's CRS
    if feat.crs in proj_map:
        defn = proj_map[feat.crs]
    elif feat.crs.startswith("EPSG:"):
        defn = feat.crs
    else:
        known = list(proj_map) + ["EPSG:4326"]
        raise ValueError(
            f"Feature '{feat.name}': unknown CRS '{feat.crs}'. "
            f"Known projections: {known}"
        )

    try:
        source_crs = CRS.from_user_input(defn)
    except CRSError as e:
        raise ValueError(
            f"Feature '{feat.name}': invalid CRS definition '{defn}': {e}"
        ) from None

    if source_crs.to_epsg() == _TARGET_EPSG:
        return feat  # Already WGS84 — nothing to do

    transformer = Transformer.from_crs(source_crs, _TARGET_EPSG, always_xy=True)
    new_coords = tuple(
        transformer.transform(x, y) for (x, y) in feat.coords
    )

    return Feature(
        name=feat.name,
        type=feat.type,  # type: ignore[arg-type]
        crs="EPSG:4326",
        coords=tuple(  # type: ignore[arg-type]
            (float(lon), float(lat)) for lon, lat in new_coords
        ),
        description=feat.description,
    )
