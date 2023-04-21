import pytest

from conda_forge_metadata.artifact_info import info_json


@pytest.mark.parametrize("backend", ["libcfgraph", "oci"])
def test_info_json(backend):
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "osx-64",
        "21cmfast-3.0.2-py36h13dd421_0.tar.bz2",
        backend=backend,
    )
    assert info["metadata_version"] == 1
    assert info["name"] == "21cmfast"
    assert info["version"] == "3.0.2"
    assert info["index"]["name"] == "21cmfast"
    assert info["index"]["version"] == "3.0.2"
    assert info["index"]["build"] == "py36h13dd421_0"
    assert info["index"]["subdir"] == "osx-64"
    assert "pyyaml" in info["index"]["depends"]
    assert info["about"]["conda_version"] == "4.8.4"
    assert info["rendered_recipe"]["package"]["name"] == "21cmfast"
    assert (
        info["rendered_recipe"]["source"]["sha256"]
        == "6e88960d134e98e4719343d853c63fc3c691438b57b2863f7834f07fae9eab4f"
    )
    assert info["raw_recipe"].startswith('{% set name = "21cmFAST" %}')
    assert info["conda_build_config"]["CI"] == "azure"
    assert "bin/21cmfast" in info["files"]
