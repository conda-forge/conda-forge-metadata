from __future__ import annotations

import hashlib
import os
from functools import lru_cache

import requests

AUTOTICK_BOT_GITHUB_BASE_URL = "https://github.com/regro/cf-graph-countyfair/raw/master"


@lru_cache(maxsize=1)
def _import_to_pkg_maps_num_letters() -> int:
    req = requests.get(
        f"{AUTOTICK_BOT_GITHUB_BASE_URL}"
        "/import_to_pkg_maps/import_to_pkg_maps_meta.json"
    )
    req.raise_for_status()
    return int(req.json()["num_letters"])


@lru_cache(maxsize=1)
def _import_to_pkg_maps_num_dirs() -> int:
    req = requests.get(
        f"{AUTOTICK_BOT_GITHUB_BASE_URL}"
        "/import_to_pkg_maps/import_to_pkg_maps_meta.json"
    )
    req.raise_for_status()
    return int(req.json()["num_dirs"])


def _get_bot_sharded_path(file_path, n_dirs=5):
    """computed a sharded location for the LazyJson file."""
    top_dir, file_name = os.path.split(file_path)

    if len(top_dir) == 0 or top_dir == "lazy_json":
        return file_name
    else:
        hx = hashlib.sha1(file_name.encode("utf-8")).hexdigest()[0:n_dirs]
        pth_parts = [top_dir] + [hx[i] for i in range(n_dirs)] + [file_name]
        return os.path.join(*pth_parts)


@lru_cache(maxsize=128)
def _import_to_pkg_maps_cache(import_first_letters: str) -> dict[str, set[str]]:
    pth = _get_bot_sharded_path(
        f"import_to_pkg_maps/{import_first_letters.lower()}.json",
        n_dirs=_import_to_pkg_maps_num_dirs(),
    )
    req = requests.get(f"{AUTOTICK_BOT_GITHUB_BASE_URL}/{pth}")
    req.raise_for_status()
    return {k: set(v["elements"]) for k, v in req.json().items()}


def _get_pkgs_for_import(import_name: str) -> set[str] | None:
    num_letters = _import_to_pkg_maps_num_letters()
    fllt = import_name[: min(len(import_name), num_letters)]
    import_to_pkg_map = _import_to_pkg_maps_cache(fllt)
    return import_to_pkg_map.get(import_name, None)


def get_pkgs_for_import(import_name: str) -> tuple[set[str] | None, str]:
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
    supplying_pkgs = _get_pkgs_for_import(import_name)
    return supplying_pkgs, import_name


@lru_cache(maxsize=1)
def _ranked_hubs_authorities() -> list[str]:
    req = requests.get(
        "https://raw.githubusercontent.com/regro/cf-graph-countyfair/"
        "master/ranked_hubs_authorities.json"
    )
    req.raise_for_status()
    return req.json()


def map_import_to_package(import_name: str) -> str:
    """Map an import name to the most likely package that has it.

    Parameters
    ----------
    import_name : str
        The name of the import.

    Returns
    -------
    pkg_name : str
        The name of the package.
    """
    supplying_pkgs, found_import_name = get_pkgs_for_import(import_name)
    if supplying_pkgs is None:
        return found_import_name

    if found_import_name in supplying_pkgs:
        # heuristic that import scipy comes from scipy
        return found_import_name
    else:
        hubs_auths = _ranked_hubs_authorities()
        return next(
            iter(k for k in hubs_auths if k in supplying_pkgs),
            found_import_name,
        )
