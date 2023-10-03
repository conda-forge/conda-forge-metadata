import tarfile
from logging import getLogger
from typing import Generator

from conda_oci_mirror.repo import PackageRepo

logger = getLogger(__name__)


def get_oci_artifact_data(
    channel: str,
    subdir: str,
    artifact: str,
    registry: str = "ghcr.io/channel-mirrors",
) -> "Generator[tuple[tarfile.TarFile, tarfile.TarInfo], None, None] | None":
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
        tar = repo.get_info(oci_name)
    except ValueError as exc:
        logger.debug("Failed to get info for %s", oci_name, exc_info=exc)
        return None
    else:
        try:
            for member in tar:
                yield tar, member
        finally:
            tar.close()
