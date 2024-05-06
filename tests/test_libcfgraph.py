from conda_forge_metadata.libcfgraph import (
    get_libcfgraph_artifact_data,
    get_libcfgraph_index,
    get_libcfgraph_pkgs_for_import,
)


def test_get_libcfgraph_index():
    lcfi = get_libcfgraph_index()
    assert len(lcfi) > 0
    assert isinstance(lcfi, list)
    assert isinstance(lcfi[0], str)
    assert lcfi[0].startswith("artifacts/")


def test_get_libcfgraph_artifact_data():
    data = get_libcfgraph_artifact_data(
        "conda-forge",
        "noarch",
        "flake8-6.0.0-pyhd8ed1ab_0.conda",
    )
    assert data is not None
    assert data["name"] == "flake8"
    assert data["version"] == "6.0.0"


def test_get_libcfgraph_artifact_data_none():
    data = get_libcfgraph_artifact_data(
        "conda-forge",
        "noarchhh",
        "flake8-6.0.0-pyhd8ed1ab_0.conda",
    )
    assert data is None


def test_get_libcfgraph_pkgs_for_import():
    pkgs, nm = get_libcfgraph_pkgs_for_import("numpy")
    assert pkgs is not None
    assert nm == "numpy"
    assert "numpy" in pkgs

    pkgs, nm = get_libcfgraph_pkgs_for_import("numpy.linalg")
    assert pkgs is not None
    assert nm == "numpy"
    assert "numpy" in pkgs

    # something bespoke
    pkgs, nm = get_libcfgraph_pkgs_for_import("eastlake")
    assert pkgs is not None
    assert nm == "eastlake"
    assert "des-eastlake" in pkgs
    assert len(pkgs) == 1

    pkgs, nm = get_libcfgraph_pkgs_for_import("scipy")
    assert pkgs is not None
    assert nm == "scipy"
    assert "scipy" in pkgs
