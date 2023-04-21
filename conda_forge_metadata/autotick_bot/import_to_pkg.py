from functools import lru_cache

import requests

from conda_forge_metadata.libcfgraph import get_libcfgraph_pkgs_for_import


@lru_cache(maxsize=1)
def _ranked_hubs_authorities():
    req = requests.get(
        "https://raw.githubusercontent.com/regro/cf-graph-countyfair/"
        "master/ranked_hubs_authorities.json"
    )
    req.raise_for_status()
    return req.json()


def map_import_to_package(import_name):
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
    supplying_pkgs, found_import_name = get_libcfgraph_pkgs_for_import(import_name)
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
