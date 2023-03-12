from conda_forge_metadata.autotick_bot import map_pypi_to_conda


def test_map_pypi_to_conda():
    assert map_pypi_to_conda("numpy") == "numpy"
    assert map_pypi_to_conda("scipy") == "scipy"
    assert map_pypi_to_conda("21cmFAST") == "21cmfast"
