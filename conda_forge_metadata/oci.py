import json
from functools import lru_cache
from logging import getLogger
from typing import Union

from conda_oci_mirror.repo import PackageRepo
from ruamel import yaml

logger = getLogger(__name__)


def _extract_read(infotar, *names) -> Union[str, None]:
    names_in_tar = infotar.getnames()
    for name in names:
        if name in names_in_tar:
            return infotar.extractfile(name).read().decode()


@lru_cache(maxsize=1024)
def get_oci_artifact_data(
    channel: str,
    subdir: str,
    artifact: str,
    registry: str = "ghcr.io/channel-mirrors",
) -> Union[dict, None]:
    """Get a blob of artifact data from the conda info directory.

    Note this function might need token authentication to access the registry.
    Export the following environment variables:
    - ORAS_USER: the username to use for authentication
    - ORAS_PASS: the password/token to use for authentication

    Parameters
    ----------
    channel : str
        The channel (e.g., "conda-forge").
    subdir : str
        The subdir for the artifact (e.g., "noarch", "linux-64", etc.).
    artifact : str
        The full artifact name with extension (e.g.,
        "21cmfast-3.0.2-py36h13dd421_0.tar.bz2").
    registry : str
        The registry to use for the OCI repository.

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

        If the artifact is not indexed, it returns None.
    """
    if artifact.endswith(".tar.bz2"):
        artifact = artifact[: -len(".tar.bz2")]
    elif artifact.endswith(".conda"):
        artifact = artifact[: -len(".conda")]
    else:
        raise ValueError(f"Artifact '{artifact}' is not a conda package")

    repo = PackageRepo(channel, subdir, None, registry=registry)

    parts = artifact.rsplit("-", 2)
    oci_name = f"{parts[0]}:{parts[1]}-{parts[2]}"
    try:
        infotar = repo.get_info(oci_name)
    except ValueError as exc:
        logger.debug("Failed to get info for %s", oci_name, exc_info=exc)
        return None

    YAML = yaml.YAML(typ="safe")

    index = json.loads(_extract_read(infotar, "index.json"))
    return {
        # https://github.com/regro/libcflib/blob/062858e90af2795d2eb098034728cace574a51b8/libcflib/harvester.py#L14
        "metadata_version": 1,
        "name": index.get("name", ""),
        "version": index.get("version", ""),
        "index": index,
        "about": json.loads(_extract_read(infotar, "about.json")),
        "rendered_recipe": YAML.load(
            _extract_read(infotar, "recipe/meta.yaml", "meta.yaml")
        ),
        "raw_recipe": _extract_read(
            infotar,
            "recipe/meta.yaml.template",
            "recipe/meta.yaml",
            "meta.yaml",
        ),
        "conda_build_config": YAML.load(
            _extract_read(infotar, "recipe/conda_build_config.yaml")
        ),
        "files": [
            f
            for f in _extract_read(infotar, "files").splitlines()
            if not f.lower().endswith((".pyc", ".txt"))
        ],
    }
