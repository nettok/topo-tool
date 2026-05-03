from __future__ import annotations

import topo_tool


def test_import_star_includes_all_public_names() -> None:
    # Verify every name in __all__ is actually importable
    for name in topo_tool.__all__:
        assert hasattr(topo_tool, name), f"__all__ includes '{name}' but it is not in the module"


def test_all_names_are_correct() -> None:
    expected = {"Document", "Feature", "Projection", "Style", "load_document", "features_to_kml", "write_kml"}
    assert set(topo_tool.__all__) == expected
