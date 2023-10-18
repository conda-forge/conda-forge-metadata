import pytest

from conda_forge_metadata.artifact_info import info_json


@pytest.mark.parametrize("backend", info_json.VALID_BACKENDS)
def test_info_json_tar_bz2(backend: str):
    if backend == "streamed":
        pytest.xfail("streamed backend does not support .tar.bz2 artifacts")

    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "osx-64",
        "21cmfast-3.0.2-py36h13dd421_0.tar.bz2",
        backend=backend,
    )
    assert info is not None
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
    assert info["raw_recipe"] is not None
    assert info["raw_recipe"].startswith('{% set name = "21cmFAST" %}')
    assert info["conda_build_config"]["CI"] == "azure"
    assert "bin/21cmfast" in info["files"]


@pytest.mark.parametrize("backend", info_json.VALID_BACKENDS)
def test_info_json_conda(backend: str):
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "noarch",
        "abipy-0.9.6-pyhd8ed1ab_0.conda",
        backend=backend,
    )
    assert info is not None
    assert info["metadata_version"] == 1
    assert info["name"] == "abipy"
    assert info["version"] == "0.9.6"
    assert info["index"]["name"] == "abipy"
    assert info["index"]["version"] == "0.9.6"
    assert info["index"]["build"] == "pyhd8ed1ab_0"
    assert info["index"]["subdir"] == "noarch"
    assert "apscheduler" in info["index"]["depends"]
    assert info["about"]["conda_version"] == "23.3.1"
    assert info["rendered_recipe"]["package"]["name"] == "abipy"
    assert (
        info["rendered_recipe"]["source"]["sha256"]
        == "dc34c9179b9e53649353b30c1b37f0a36f5ea681fc541d60cafb3f4cf176cddf"
    )
    assert info["raw_recipe"] is not None
    assert info["raw_recipe"].startswith('{% set name = "abipy" %}')
    assert info["conda_build_config"]["CI"] == "azure"
    assert "site-packages/abipy/__init__.py" in info["files"]


@pytest.mark.parametrize("backend", info_json.VALID_BACKENDS)
def test_missing_conda_build_tar_bz2(backend: str):
    if backend == "streamed":
        pytest.xfail("streamed backend does not support .tar.bz2 artifacts")

    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "linux-64",
        "jinja2-2.10-py36_0.tar.bz2",
        backend=backend,
    )
    assert info is not None
    assert info["conda_build_config"] == {}
