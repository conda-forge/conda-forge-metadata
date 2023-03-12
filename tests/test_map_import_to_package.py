from conda_forge_metadata.autotick_bot import map_import_to_package


def test_map_import_to_package():
    assert map_import_to_package("numpy") == "numpy"
    assert map_import_to_package("numpy.linalg") == "numpy"

    # something bespoke
    assert map_import_to_package("eastlake") == "des-eastlake"

    assert map_import_to_package("scipy") == "scipy"
