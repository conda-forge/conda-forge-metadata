from functools import lru_cache
import requests


@lru_cache(maxsize=1)
def _import_to_pkg_maps_num_letters():
    req = requests.get(
        'https://raw.githubusercontent.com/regro/libcfgraph/master'
        '/import_to_pkg_maps_meta.json'
    )
    req.raise_for_status()
    return int(req.json()['num_letters'])


@lru_cache(maxsize=1024)
def _import_to_pkg_maps_cache(import_first_letters):
    req = requests.get(
        f'https://raw.githubusercontent.com/regro/libcfgraph'
        f'/master/import_to_pkg_maps/{import_first_letters.lower()}.json')
    req.raise_for_status()
    return {k: set(v['elements']) for k, v in req.json().items()}


@lru_cache(maxsize=1)
def _ranked_hubs_authorities():
    req = requests.get(
        'https://raw.githubusercontent.com/regro/cf-graph-countyfair/'
        'master/ranked_hubs_authorities.json'
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
    num_letters = _import_to_pkg_maps_num_letters()
    original_import_name = import_name
    while True:
        try:
            fllt = import_name[:min(len(import_name), num_letters)]
            import_to_pkg_map = _import_to_pkg_maps_cache(fllt)
            supplying_pkgs = import_to_pkg_map[import_name]
        except KeyError:
            if '.' not in import_name:
                return original_import_name
            import_name = import_name.rsplit('.', 1)[0]
            pass
        else:
            break

    if import_name in supplying_pkgs:
        # heuristic that import scipy comes from scipy
        return import_name
    else:
        hubs_auths = _ranked_hubs_authorities()
        return next(
            iter(k for k in hubs_auths if k in supplying_pkgs),
            import_name
        )
