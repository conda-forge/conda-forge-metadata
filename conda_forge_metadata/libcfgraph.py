from __future__ import annotations

from functools import lru_cache

import requests
from deprecated import deprecated

from conda_forge_metadata.types import ArtifactData

_LIBCFGRAPH_INDEX = None


def _download_libcfgraph_index():
    global _LIBCFGRAPH_INDEX
    r = requests.get(
        "https://raw.githubusercontent.com/regro/libcfgraph"
        "/master/.file_listing_meta.json",
    )
    r.raise_for_status()
    n_files = r.json()["n_files"]
    _LIBCFGRAPH_INDEX = []
    for i in range(n_files):
        r = requests.get(
            "https://raw.githubusercontent.com/regro/libcfgraph"
            "/master/.file_listing_%d.json" % i,
        )
        r.raise_for_status()
        _LIBCFGRAPH_INDEX += r.json()


@deprecated(
    reason=(
        "conda-forge no longer maintains the libcfgraph metadata store. "
        "This API will be removed in a future release."
    )
)
def get_libcfgraph_index() -> list[str]:
    """Get a list of all artifacts indexed by libcfgraph.

    Each element of the list looks like

        "artifacts/21cmfast/conda-forge/linux-64/21cmfast-3.0.2-py36h2e3f83d_0.json"

    for the conda-forge artifact

        linux-64/21cmfast-3.0.2-py36h2e3f83d_0.{tar.bz2,conda}
    """
    if _LIBCFGRAPH_INDEX is None:
        _download_libcfgraph_index()
    assert _LIBCFGRAPH_INDEX is not None
    return _LIBCFGRAPH_INDEX


@deprecated(
    reason=(
        "conda-forge no longer maintains the libcfgraph metadata store. "
        "This API will be removed in a future release. "
        "Use conda_forge_metdata.artifact_info.get_artifact_info_as_json instead."
    )
)
@lru_cache(maxsize=1024)
def get_libcfgraph_artifact_data(
    channel: str, subdir: str, artifact: str
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

        If the artifact is not indexed, it returns None.
    """
    # urls look like this:
    # https://raw.githubusercontent.com/regro/libcfgraph/master/
    #   artifacts/21cmfast/conda-forge/osx-64/21cmfast-3.0.2-py36h13dd421_0.json
    nm_parts = artifact.rsplit("-", 2)
    if artifact.endswith(".tar.bz2"):
        nm = artifact[: -len(".tar.bz2")]
    else:
        nm = artifact[: -len(".conda")]

    libcfgraph_path = "artifacts/" f"{nm_parts[0]}/{channel}/{subdir}/{nm}.json"
    if libcfgraph_path in get_libcfgraph_index():
        url = (
            "https://raw.githubusercontent.com/regro/libcfgraph/master/"
            + libcfgraph_path
        )
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    else:
        return None


@lru_cache(maxsize=1)
def _import_to_pkg_maps_num_letters() -> int:
    req = requests.get(
        "https://raw.githubusercontent.com/regro/libcfgraph/master"
        "/import_to_pkg_maps_meta.json"
    )
    req.raise_for_status()
    return int(req.json()["num_letters"])


@lru_cache(maxsize=128)
def _import_to_pkg_maps_cache(import_first_letters: str) -> dict[str, set[str]]:
    req = requests.get(
        f"https://raw.githubusercontent.com/regro/libcfgraph"
        f"/master/import_to_pkg_maps/{import_first_letters.lower()}.json"
    )
    req.raise_for_status()
    return {k: set(v["elements"]) for k, v in req.json().items()}


def _get_libcfgraph_pkgs_for_import(import_name: str) -> set[str] | None:
    num_letters = _import_to_pkg_maps_num_letters()
    fllt = import_name[: min(len(import_name), num_letters)]
    import_to_pkg_map = _import_to_pkg_maps_cache(fllt)
    return import_to_pkg_map.get(import_name, None)


@deprecated(
    reason=(
        "conda-forge no longer maintains the libcfgraph metadata store. "
        "This API will be removed in a future release. "
        "Use conda_forge_metdata.autotick_bot.get_pks_for_import instead."
    )
)
def get_libcfgraph_pkgs_for_import(import_name: str) -> tuple[set[str] | None, str]:
    """Get a list of possible packages that supply a given import.

    **This data is approximate and may be wrong.**

    For a better guess, use the function

        `conda_forge_metadata.autotick_bot.map_import_to_package`

    which attempts to return the most likely supplying package.

    Parameters
    ----------
    import_name : str
        The name of the import.

    Returns
    -------
    packages : set
        A set of packages that possibly have the import.
        Will return `None` if the import was not found.
    found_import_name : str
        The import name found in the libcfgraph metadata. Only
        valid if `packages` is not None. This name will be the
        top-level import with all subpackages removed (e.g., foo.bar.baz
        will be returned as foo).
    """
    import_name = import_name.split(".")[0]
    supplying_pkgs = _get_libcfgraph_pkgs_for_import(import_name)
    return supplying_pkgs, import_name
