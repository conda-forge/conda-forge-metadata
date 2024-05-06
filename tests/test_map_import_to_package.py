from conda_forge_metadata.autotick_bot import get_pkgs_for_import, map_import_to_package


def test_map_import_to_package():
    assert map_import_to_package("numpy") == "numpy"
    assert map_import_to_package("numpy.linalg") == "numpy"

    # something bespoke
    assert map_import_to_package("eastlake") == "des-eastlake"

    assert map_import_to_package("scipy") == "scipy"


def test_get_pkgs_for_import():
    pkgs, nm = get_pkgs_for_import("numpy")
    assert pkgs is not None
    assert nm == "numpy"
    assert "numpy" in pkgs

    pkgs, nm = get_pkgs_for_import("numpy.linalg")
    assert pkgs is not None
    assert nm == "numpy"
    assert "numpy" in pkgs

    # something bespoke
    pkgs, nm = get_pkgs_for_import("eastlake")
    assert pkgs is not None
    assert nm == "eastlake"
    assert "des-eastlake" in pkgs
    assert len(pkgs) == 1

    pkgs, nm = get_pkgs_for_import("scipy")
    assert pkgs is not None
    assert nm == "scipy"
    assert "scipy" in pkgs
