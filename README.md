# topo-tool

Convert YAML geographic feature definitions to KML for outdoor navigation apps like Avenza.

Define property boundaries, protected zones, points of interest, and patrol trails with custom projections (GTM, UTM, etc.). Coordinates are reprojected to WGS84 automatically.

## Install

```
pip install -e .
```

Requires Python 3.10+.

## Usage

```bash
topo-tool input.yaml -o output.kml
```

### YAML format

```yaml
styles:
  protected_forest:
    color: "#00ff00"  # hex RGB
    opacity: 0.30     # 0.0–1.0

projections:
  GTM: "+proj=tmerc +lat_0=0 +lon_0=-90.5 +k=0.9998 +x_0=500000 +y_0=0 +datum=WGS84 +units=m"

features:
  - name: "Gate"
    type: point
    crs: GTM
    coords: [496800, 1659194]

  - name: "Trail"
    type: line
    crs: GTM
    style: access_road
    coords:
      - [496800, 1659194]
      - [496850, 1659050]

  - name: "Property Boundary"
    type: polygon
    crs: GTM
    style: property_boundary
    coords:
      - [496666, 1659194]
      - [497000, 1659194]
      - [497000, 1658800]
```

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Becomes KML Placemark name |
| `type` | yes | `point`, `polygon`, or `line` |
| `crs` | yes | Projection name from `projections`, or `EPSG:xxxx` |
| `coords` | yes | `[x, y]` for point; list of pairs for polygon/line |
| `description` | no | Becomes KML Placemark description |
| `style` | no | References a named style from `styles` (polygons and lines) |

### Styles

Define named visual styles in the `styles` section. Each style has a hex RGB `color` and `opacity` (0.0–1.0). Reference them in features with `style: name`.

For polygons, the color applies to both fill and outline. Fill opacity is set via the style; the outline is always at full opacity. Un-styled polygons default to white fill at 50% opacity.

Lines use the style color for the stroke only (opacity is ignored, always full).

### Projections

Define custom CRS with PROJ strings in the `projections` section. Built-in EPSG codes (e.g. `EPSG:4326`) are handled by pyproj directly and don't need a definition.

## Examples

See [`examples/`](examples/) for a complete example with real property data.

## Development

```
pip install -e ".[dev]"
pytest tests/ -v
```

See [`AGENTS.md`](AGENTS.md) for coding conventions.
