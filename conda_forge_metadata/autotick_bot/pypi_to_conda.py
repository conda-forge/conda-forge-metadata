from __future__ import annotations

import typing
from functools import lru_cache

import requests
from ruamel import yaml

if typing.TYPE_CHECKING:
    from ..types import CondaPackageName, NameMappingEntry, PypiPackageName


@lru_cache(maxsize=1)
def get_pypi_name_mapping() -> list[NameMappingEntry]:
    req = requests.get(
        "https://raw.githubusercontent.com/regro/cf-graph-countyfair/"
        "master/mappings/pypi/name_mapping.yaml"
    )
    req.raise_for_status()
    return yaml.YAML(typ="safe").load(req.text)


@lru_cache(maxsize=1)
def get_grayskull_pypi_mapping() -> dict[PypiPackageName, NameMappingEntry]:
    req = requests.get(
        "https://raw.githubusercontent.com/regro/cf-graph-countyfair/"
        "master/mappings/pypi/grayskull_pypi_mapping.json"
    )
    req.raise_for_status()
    return req.json()


def map_pypi_to_conda(pypi_name: PypiPackageName) -> CondaPackageName:
    """Map a package's PyPi name to the most likely Conda name.

    Parameters
    ----------
    pypi_name : str
        The name on PyPi. This is case-sensitive.

    Returns
    -------
    conda_name : str
        The most likely Conda name.
    """
    pypi_map = get_grayskull_pypi_mapping()
    return pypi_map.get(pypi_name, {}).get("conda_name", pypi_name.lower())
