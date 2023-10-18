from __future__ import annotations

import json
import tarfile
from typing import Any, Generator, Tuple

from ruamel import yaml

from conda_forge_metadata.libcfgraph import get_libcfgraph_artifact_data
from conda_forge_metadata.types import ArtifactData

VALID_BACKENDS = ("libcfgraph", "oci", "streamed")


def get_artifact_info_as_json(
    channel: str, subdir: str, artifact: str, backend: str = "libcfgraph"
) -> ArtifactData | None:
    """Get a blob of artifact data from the conda info directory.

    Parameters
    ----------
    channel : str
        The channel (e.g., "conda-forge").
    subdir : str
        The subdir for the artifact (e.g., "noarch", "linux-64", etc.).
    artifact : str
        The full artifact name with extension (e.g.,
        "21cmfast-3.0.2-py36h13dd421_0.tar.bz2").

    Returns
    -------
    info_blob : dict
        A dictionary of data. Possible keys are

            "metadata_version": the metadata version format
            "name": the package name
            "version": the package version
            "index": the info/index.json file contents
            "about": the info/about.json file contents
            "rendered_recipe": the fully rendered recipe at
                either info/recipe/meta.yaml or info/meta.yaml
                as a dict
            "raw_recipe": the template recipe as a string from
                info/recipe/meta.yaml.template - could be
                the rendered recipe as a string if no template was found
            "conda_build_config": the conda_build_config.yaml used for building
                the recipe at info/recipe/conda_build_config.yaml
            "files": a list of files in the recipe from info/files with
                elements ending in .pyc or .txt filtered out.
    """
    if backend == "libcfgraph":
        return get_libcfgraph_artifact_data(channel, subdir, artifact)
    elif backend == "oci":
        from conda_forge_metadata.oci import get_oci_artifact_data

        tar = get_oci_artifact_data(channel, subdir, artifact)
        if tar is not None:
            return info_json_from_tar_generator(tar)
    elif backend == "streamed":
        if artifact.endswith(".tar.bz2"):
            raise ValueError("streamed backend does not support .tar.bz2 artifacts")
        from conda_forge_metadata.streaming import get_streamed_artifact_data

        return info_json_from_tar_generator(
            get_streamed_artifact_data(channel, subdir, artifact)
        )
    else:
        raise ValueError(
            f"Unknown backend {backend!r}. Valid backends are {VALID_BACKENDS}."
        )


def info_json_from_tar_generator(
    tar_tuples: Generator[Tuple[tarfile.TarFile, tarfile.TarInfo], None, None],
) -> ArtifactData | None:
    # https://github.com/regro/libcflib/blob/062858e90af/libcflib/harvester.py#L14
    data = {
        "metadata_version": 1,
        "name": "",
        "version": "",
        "index": {},
        "about": {},
        "rendered_recipe": {},
        "raw_recipe": "",
        "conda_build_config": {},
        "files": [],
    }
    YAML = yaml.YAML(typ="safe")
    for tar, member in tar_tuples:
        if member.name.endswith("index.json"):
            index = json.loads(_extract_read(tar, member, default="{}"))
            data["name"] = index.get("name", "")
            data["version"] = index.get("version", "")
            data["index"] = index
        elif member.name.endswith("about.json"):
            data["about"] = json.loads(_extract_read(tar, member, default="{}"))
        elif member.name.endswith("conda_build_config.yaml"):
            data["conda_build_config"] = YAML.load(
                _extract_read(tar, member, default="{}")
            )
        elif member.name.endswith("files"):
            data["files"] = [
                f
                for f in _extract_read(tar, member, default="").splitlines()
                if not f.lower().endswith((".pyc", ".txt"))
            ]
        elif member.name.endswith("meta.yaml.template"):
            data["raw_recipe"] = _extract_read(tar, member, default="")
        elif member.name.endswith("meta.yaml"):
            x = _extract_read(tar, member, default="{}")
            if ("{{" in x or "{%" in x) and not data["raw_recipe"]:
                data["raw_recipe"] = x
            else:
                data["rendered_recipe"] = YAML.load(x)
    if data["name"]:
        return data  # type: ignore


def _extract_read(
    tar: tarfile.TarFile, member: tarfile.TarInfo, default: Any = None
) -> str:
    f = tar.extractfile(member)
    if f:
        return f.read().decode() or default
    return default
