from __future__ import annotations

import sys
import time
from functools import lru_cache

import requests

if sys.version_info[:2] < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def get_hints() -> dict[str, str]:
    # ensure we refresh the cache every hour
    ttl = 3600
    time_salt = int(time.time() / ttl)
    return _get_hints_internal(time_salt)


@lru_cache(maxsize=1)
def _get_hints_internal(time_salt) -> dict[str, str]:
    req = requests.get(
        "https://raw.githubusercontent.com/conda-forge/"
        "conda-forge-pinning-feedstock/main/recipe/linter_hints/hints.toml"
    )
    req.raise_for_status()
    hints_toml_str = req.content.decode("utf-8")
    hints_dict = tomllib.loads(hints_toml_str)["hints"]
    return hints_dict
