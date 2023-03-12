import conda_forge_metadata


def test_alive():
    assert hasattr(conda_forge_metadata, "__version__")
