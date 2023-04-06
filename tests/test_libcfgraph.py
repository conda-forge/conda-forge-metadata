from conda_forge_metadata.libcfgraph import get_libcfgraph_pkgs_for_import

# get_libcfgraph_index():
# get_libcfgraph_artifact_data(channel, subdir, artifact):


def test_get_libcfgraph_pkgs_for_import():
    pkgs, nm = get_libcfgraph_pkgs_for_import("numpy")
    assert nm == "numpy"
    assert "numpy" in pkgs

    pkgs, nm = get_libcfgraph_pkgs_for_import("numpy.linalg")
    assert nm == "numpy"
    assert "numpy" in pkgs

    # something bespoke
    pkgs, nm = get_libcfgraph_pkgs_for_import("eastlake")
    assert nm == "eastlake"
    assert "des-eastlake" in pkgs
    assert len(pkgs) == 1

    pkgs, nm = get_libcfgraph_pkgs_for_import("scipy")
    assert nm == "scipy"
    assert "scipy" in pkgs

