from __future__ import annotations

import argparse
import sys
from pathlib import Path

from topo_tool.converter import reproject_features
from topo_tool.reader import load_document
from topo_tool.writer import features_to_kml, write_kml


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="topo-tool",
        description="Convert YAML feature definitions to KML for outdoor navigation.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="YAML file with feature definitions",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output.kml"),
        help="Output KML file path (default: output.kml)",
    )
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    doc = load_document(args.input)
    features = reproject_features(doc.features, doc.projections)
    kml = features_to_kml(features)
    write_kml(args.output, kml)
    print(f"Written {len(features)} feature(s) to {args.output}")


if __name__ == "__main__":
    main()
