# PLAN.md

## Overview

`topo-tool` converts geographic feature definitions from YAML to KML for use in outdoor navigation apps like Avenza. The initial use case is managing a mountain property: boundaries, protected forest areas, points of interest, and patrol trails.

## Input: YAML

A single YAML file defines custom coordinate reference systems and features.

Custom projections are defined once in a top-level `projections` mapping. Each feature references a projection by name, or a built-in `EPSG:xxxx` code.

```yaml
projections:
  GTM: "+proj=tmerc +lat_0=0 +lon_0=-90.5 +k=0.9998 +x_0=500000 +y_0=0 +datum=WGS84 +units=m"

features:
  - name: "Property Boundary"
    type: polygon          # point | polygon | line
    crs: GTM               # references a projection name, or "EPSG:xxxx"
    coords:
      - [496666, 1659194]
      - [497000, 1659194]
      - [497000, 1658800]
      - [496666, 1658800]

  - name: "Warning Sign"
    type: point
    crs: GTM
    coords: [496800, 1659194]       # single pair for points
    description: "No entry beyond this point"

  - name: "Patrol Trail"
    type: line
    crs: EPSG:4326                  # built-in EPSG codes work too
    coords:
      - [-89.6207, 14.5678]
      - [-89.6210, 14.5690]
```

### `projections` section

| Field        | Required | Notes                                          |
|--------------|----------|-------------------------------------------------|
| *(key)*      | yes      | Short name referenced by features (e.g. `GTM`) |
| *definition* | yes      | PROJ string describing the CRS                 |

PROJ strings can be obtained from QGIS, `gdalsrsinfo`, or the PROJ documentation.

### `features` section

| Field         | Required | Notes                                      |
|---------------|----------|--------------------------------------------|
| `name`        | yes      | Becomes KML Placemark `<name>`             |
| `type`        | yes      | `point`, `polygon`, or `line`              |
| `crs`         | yes      | A projection name from `projections`, or `EPSG:xxxx` |
| `coords`      | yes      | `[x, y]` for point; list of pairs otherwise |
| `description` | no       | Becomes KML Placemark `<description>`      |

## Output: KML

- `point` → KML `<Point>`
- `polygon` → KML `<Polygon>` with `<LinearRing>` (KML auto-closes to first point)
- `line` → KML `<LineString>` (open path)

All coordinates are reprojected to WGS84 geographic (EPSG:4326) before output, as required by KML.

## Architecture

### Module layout (`src/` layout)

```
src/topo_tool/
├── __init__.py    # Public API re-exports
├── models.py      # Projection, Feature, Document dataclasses (frozen)
├── reader.py      # YAML parsing + validation (pure)
├── converter.py   # CRS → EPSG:4326 reprojection via pyproj (pure)
├── writer.py      # Feature → KML transform (pure) + file I/O (side effect)
└── cli.py         # Argparse, wires modules (side effects at edge)
```

### Data flow (left-to-right, pure in middle)

```
YAML file  →  reader.load_document  →  converter.reproject_features  →  writer.features_to_kml  →  writer.write_kml  →  .kml file
    (I/O)         (pure)                     (pure)                        (pure)                    (I/O)
```

`reproject_features` receives both `doc.features` and `doc.projections`. The converter resolves custom projection names → PROJ strings, creates a pyproj `Transformer`, and converts all coordinates to WGS84. Already-WGS84 features pass through unchanged.

### Naming decisions

- **`line`** over `path` — consistent with `point`/`polygon` as generic shape names
- **`crs` per-feature** over per-file — maximum flexibility for mixed-source data
- **`[x, y]` order** — standard geospatial convention (easting/northing for projected, lon/lat for geographic)
- **`projections`** section — custom CRS definitions live in the same YAML, no separate mapping file needed

## Validation rules

| Rule                  | Error                                     |
|-----------------------|-------------------------------------------|
| Missing `name`/`type`/`crs` | `ValueError: missing required string field` |
| Invalid type          | `ValueError: invalid type, must be ...`   |
| Projection definition empty | `ValueError: definition must be a non-empty string` |
| Point ≠ 1 coord       | `ValueError: point must have exactly 1`   |
| Line < 2 coords       | `ValueError: line must have at least 2`   |
| Polygon < 3 coords    | `ValueError: polygon must have at least 3`|
| Unknown CRS name      | `ValueError: unknown CRS`                 |
| Invalid PROJ string   | `ValueError: invalid CRS definition`      |

## Roadmap

| Phase | Feature                                    | Status |
|-------|--------------------------------------------|--------|
| 1     | YAML → KML with custom projections         | done   |
| 2     | Style support (colors, opacity)             | done   |
| 3     | KML → CSV/GeoJSON (bidirectional)          | planned |
| 4     | Elevation (Z-axis) support                 | planned |
