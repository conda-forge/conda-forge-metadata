from functools import lru_cache
import requests


@lru_cache(maxsize=1024)
def package_to_feedstock(name):
    """Map a package name to the feedstock name.
    
    Parameters
    ----------
    package : str
        The name of the package.
    
    Returns
    -------
    feedstock : str
        The name of the feedstock, without the ``-feedstock`` suffix.
    """
    assert name, "name must not be empty"

    # See https://github.com/conda-forge/feedstock-outputs/blob/c35451f2fb8b7/scripts/shard_repo.py
    # for sharding details.
    shard_size = 3
    name = name.lower()
    chars = [c for c in name if c.isalnum()][:shard_size]
    while len(chars) < shard_size:
        chars.append("z")

    ref = "main"
    req = requests.get(
        f"https://raw.githubusercontent.com/conda-forge/feedstock-outputs/{ref}/outputs"
        f"/{'/'.join(chars)}/{name}.json"
    )
    req.raise_for_status()
    return req.json()["feedstocks"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m conda_forge_metadata.feedstock_outputs <package>"
        )
        sys.exit(1)

    for name in sys.argv[1:]:
        print(name, "->", package_to_feedstock(name))
