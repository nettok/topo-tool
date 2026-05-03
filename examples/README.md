# Examples

## `example01.yaml`

A mountain property with three features in GTM (Guatemala Transverse Mercator) projection:

- **Property Boundary** — polygon (8 vertices)
- **Protected Forest** — polygon (18 vertices)
- **Rótulo de Área Protegida** — point (protected area sign)

### Convert to KML

```
topo-tool examples/example01.yaml -o my-property.kml
```

The GTM projection is defined inline as a PROJ string in the YAML `projections` section.
Coordinates are automatically reprojected to WGS84 on output, as required by KML.

Import the `.kml` file into Avenza or any KML-compatible mapping app.

## `example02.yaml`

A simple example using standard WGS84 coordinates (EPSG:4326) — no custom projection needed.

- **Viewpoint** — point
- **Access Road** — line
- **Visitor Area** — polygon

### Convert to KML

```
topo-tool examples/example02.yaml -o visitors.kml
```

When features are already in WGS84, reprojection is a no-op.
