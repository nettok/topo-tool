from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from topo_tool.cli import main


def test_missing_input_file(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["nonexistent.yaml"])
    assert exc.value.code == 1


def test_valid_conversion(tmp_path: Path) -> None:
    data = {
        "features": [
            {"name": "P", "type": "point", "crs": "EPSG:4326", "coords": [0, 0]}
        ]
    }
    infile = tmp_path / "input.yaml"
    outfile = tmp_path / "output.kml"
    with open(infile, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    main([str(infile), "-o", str(outfile)])

    assert outfile.exists()
    content = outfile.read_text(encoding="utf-8")
    assert "Point" in content
    assert "P" in content


def test_invalid_yaml_shows_clean_error(tmp_path: Path) -> None:
    data = {
        "features": [
            {"type": "point", "crs": "EPSG:4326", "coords": [0, 0]}
        ]
    }
    infile = tmp_path / "bad.yaml"
    with open(infile, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    with pytest.raises(SystemExit) as exc:
        main([str(infile)])
    assert exc.value.code == 1
