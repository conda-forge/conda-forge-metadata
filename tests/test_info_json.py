from unittest.mock import MagicMock

import pytest
import requests

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
def test_info_json_rattler_build(backend: str):
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "linux-64",
        "jolt-physics-5.1.0-hff21bea_0.conda",
        backend=backend,
    )
    assert info is not None
    assert info["metadata_version"] == 1
    assert info["name"] == "jolt-physics"
    assert info["version"] == "5.1.0"
    assert info["index"]["name"] == "jolt-physics"
    assert info["index"]["version"] == "5.1.0"
    assert info["index"]["build"] == "hff21bea_0"
    assert info["index"]["subdir"] == "linux-64"
    assert "libstdcxx >=13" in info["index"]["depends"]
    assert "conda_version" not in info["about"]
    assert info["rendered_recipe"]["recipe"]["package"]["name"] == "jolt-physics"
    assert (
        info["rendered_recipe"]["recipe"]["source"][0]["sha256"]
        == "10fcc863ae2b9d48c2f22d8b0204034820e57a55f858b7c388ac9579d8cf4095"
    )
    assert info["raw_recipe"] is not None
    assert info["raw_recipe"].startswith("context:\n")
    assert info["conda_build_config"]["c_stdlib"] == "sysroot"
    assert "include/Jolt/AABBTree/AABBTreeBuilder.h" in info["files"]


@pytest.mark.parametrize("backend", info_json.VALID_BACKENDS)
def test_info_json_conda_unlucky_test_file(backend: str):
    """
    See https://github.com/conda-forge/conda-forge-metadata/pull/36

    This artifact has test/xxxx/something_index.json,
    which tripped the original info/ parsing logic.
    """
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "noarch",
        "nodeenv-1.9.1-pyhd8ed1ab_0.conda",
        backend=backend,
    )
    assert info is not None
    assert info["metadata_version"] == 1
    assert info["name"] == "nodeenv"
    assert info["version"] == "1.9.1"
    assert info["index"]["name"] == "nodeenv"
    assert info["index"]["version"] == "1.9.1"
    assert info["index"]["build"] == "pyhd8ed1ab_0"
    assert info["index"]["subdir"] == "noarch"


def test_info_json_custom_session_object():
    session = MagicMock()
    session.get.side_effect = requests.get

    info_json.get_artifact_info_as_json(
        "conda-forge",
        "noarch",
        "nodeenv-1.9.1-pyhd8ed1ab_0.conda",
        backend="streamed",
        session=session,
    )

    session.get.assert_called()


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


def test_files_skip_suffixes():
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "noarch",
        "abipy-0.9.6-pyhd8ed1ab_0.conda",
        backend="oci",
    )
    assert info is not None
    assert "site-packages/abipy/__init__.py" in info["files"]
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "noarch",
        "abipy-0.9.6-pyhd8ed1ab_0.conda",
        backend="oci",
        skip_files_suffixes=(".py",),
    )
    assert info is not None
    assert "site-packages/abipy/__init__.py" not in info["files"]


@pytest.mark.parametrize("backend", info_json.VALID_BACKENDS)
def test_duplicate_keys_allowed(backend: str):
    info = info_json.get_artifact_info_as_json(
        "conda-forge",
        "linux-64",
        "clangxx_osx-64-16.0.6-h027b494_6.conda",
        backend=backend,
    )
    assert info is not None
