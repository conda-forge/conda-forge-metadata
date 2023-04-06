from functools import lru_cache
import requests

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


def get_libcfgraph_index():
    if _LIBCFGRAPH_INDEX is None:
        _download_libcfgraph_index()
    return _LIBCFGRAPH_INDEX


@lru_cache(maxsize=1024)
def get_libcfgraph_artifact_data(channel, subdir, artifact):
    # urls look like this:
    # https://raw.githubusercontent.com/regro/libcfgraph/master/
    #   artifacts/21cmfast/conda-forge/osx-64/21cmfast-3.0.2-py36h13dd421_0.json
    nm_parts = artifact.rsplit("-", 2)
    if artifact.endswith(".tar.bz2"):
        nm = artifact[: -len(".tar.bz2")]
    else:
        nm = artifact[: -len(".conda")]

    url = (
        "https://raw.githubusercontent.com/regro/libcfgraph/master/artifacts/"
        f"{nm_parts[0]}/{channel}/{subdir}/{nm}.json"
    )
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


@lru_cache(maxsize=1)
def _import_to_pkg_maps_num_letters():
    req = requests.get(
        'https://raw.githubusercontent.com/regro/libcfgraph/master'
        '/import_to_pkg_maps_meta.json'
    )
    req.raise_for_status()
    return int(req.json()['num_letters'])


@lru_cache(maxsize=128)
def _import_to_pkg_maps_cache(import_first_letters):
    req = requests.get(
        f'https://raw.githubusercontent.com/regro/libcfgraph'
        f'/master/import_to_pkg_maps/{import_first_letters.lower()}.json')
    req.raise_for_status()
    return {k: set(v['elements']) for k, v in req.json().items()}


def get_libcfgraph_pkgs_for_import(import_name):
    num_letters = _import_to_pkg_maps_num_letters()
    fllt = import_name[:min(len(import_name), num_letters)]
    import_to_pkg_map = _import_to_pkg_maps_cache(fllt)
    return import_to_pkg_map.get(import_name, None)
