from functools import lru_cache

import requests


@lru_cache(maxsize=1)
def feedstock_outputs_config():
    ref = "main"
    req = requests.get(
        "https://raw.githubusercontent.com/conda-forge/feedstock-outputs/"
        f"{ref}/config.json"
    )
    req.raise_for_status()
    return req.json()


def sharded_path(name) -> str:
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


@lru_cache(maxsize=1024)
def package_to_feedstock(name, **request_kwargs):
    """Map a package name to the feedstock name(s).

    Parameters
    ----------
    package : str
        The name of the package.

    Returns
    -------
    feedstock : str
        The name of the feedstock, without the ``-feedstock`` suffix.
    request_kwargs : dict
        Keyword arguments to pass to ``requests.get``.
    """
    assert name, "name must not be empty"

    ref = "main"
    path = sharded_path(name)
    req = requests.get(
        f"https://raw.githubusercontent.com/conda-forge/feedstock-outputs/{ref}/{path}",
        **request_kwargs,
    )
    req.raise_for_status()
    return req.json()["feedstocks"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m conda_forge_metadata.feedstock_outputs <package>")
        sys.exit(1)

    for name in sys.argv[1:]:
        print(name, "->", package_to_feedstock(name))
