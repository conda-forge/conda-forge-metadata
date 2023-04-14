from conda_forge_metadata.autotick_bot import get_pypi_name_mapping, map_pypi_to_conda


def test_map_pypi_to_conda():
    assert map_pypi_to_conda("numpy") == "numpy"
    assert map_pypi_to_conda("scipy") == "scipy"
    assert map_pypi_to_conda("21cmFAST") == "21cmfast"


def test_get_pypi_name_mapping():
    nmap = get_pypi_name_mapping()
    assert nmap is not None
    assert "conda_name" in nmap[0]
