import time
from fnmatch import fnmatch
from functools import lru_cache
from typing import Any, List, TypedDict

import requests
from ruamel.yaml import YAML

from conda_forge_metadata.types import CondaPackageName


class FeedstockOutputsConfig(TypedDict):
    outputs_path: str
    shard_level: int
    shard_fill: str


@lru_cache(maxsize=1)
def _feedstock_outputs_config(time_int: int) -> FeedstockOutputsConfig:
    ref = "main"
    req = requests.get(
        "https://raw.githubusercontent.com/conda-forge/feedstock-outputs/"
        f"{ref}/config.json"
    )
    req.raise_for_status()
    return req.json()


def feedstock_outputs_config() -> FeedstockOutputsConfig:
    return _feedstock_outputs_config(int(time.monotonic()) // 120)


def sharded_path(name: CondaPackageName) -> str:
    """
    Get the path to the sharded JSON path in the feedstock_outputs repository.

    Parameters
    ----------
    name : str
        The name of the package.

    Returns
    -------
    path : str
        The path to the sharded JSON file. Leading slash is omitted.
    """
    # See https://github.com/conda-forge/feedstock-outputs/
    #     blob/c35451f2fb8b7/scripts/shard_repo.py
    # for sharding details.
    config = feedstock_outputs_config()
    outputs_path = config["outputs_path"]
    shard_level = config["shard_level"]
    shard_fill = config["shard_fill"]

    name = name.lower()
    chars = [c for c in name if c.isalnum()][:shard_level]
    while len(chars) < shard_level:
        chars.append(shard_fill)

    return f"{outputs_path}/{'/'.join(chars)}/{name}.json"


@lru_cache(maxsize=1)
def _fetch_allowed_autoreg_feedstock_globs(time_int: int):
    r = requests.get(
        "https://raw.githubusercontent.com/conda-forge/feedstock-outputs/"
        "main/feedstock_outputs_autoreg_allowlist.yml"
    )
    r.raise_for_status()
    yaml = YAML(typ="safe")
    return yaml.load(r.text)


def fetch_allowed_autoreg_feedstock_globs():
    return _fetch_allowed_autoreg_feedstock_globs(int(time.monotonic()) // 120)


fetch_allowed_autoreg_feedstock_globs.cache_clear = (
    _fetch_allowed_autoreg_feedstock_globs.cache_clear
)


@lru_cache(maxsize=1024)
def _package_to_feedstock(
    name: CondaPackageName, time_int: int, **request_kwargs: Any
) -> List[str]:
    assert name, "name must not be empty"

    feedstocks = set()
    fs_pats = fetch_allowed_autoreg_feedstock_globs()
    for autoreg_feedstock, pats in fs_pats.items():
        for pat in pats:
            if fnmatch(name, pat):
                feedstocks.add(autoreg_feedstock)

    ref = "main"
    path = sharded_path(name)
    req = requests.get(
        f"https://raw.githubusercontent.com/conda-forge/feedstock-outputs/{ref}/{path}",
        **request_kwargs,
    )
    if not feedstocks:
        req.raise_for_status()
    if req.status_code == 200:
        feedstocks |= set(req.json()["feedstocks"])

    return list(feedstocks)


def package_to_feedstock(name: CondaPackageName, **request_kwargs: Any) -> List[str]:
    """Map a package name to the feedstock name(s).

    Parameters
    ----------
    package : str
        The name of the package.
    request_kwargs : dict
        Keyword arguments to pass to ``requests.get``.

    Returns
    -------
    feedstock : list of str
        The name of the feedstock, without the ``-feedstock`` suffix.
    """
    return _package_to_feedstock(name, int(time.monotonic()) // 120, **request_kwargs)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m conda_forge_metadata.feedstock_outputs <package>")
        sys.exit(1)

    for name in sys.argv[1:]:
        print(name, "->", package_to_feedstock(name))
