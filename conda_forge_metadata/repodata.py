"""
Utilities to deal with repodata
"""

import bz2
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from itertools import product
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Tuple, Union
from urllib.request import urlretrieve

import bs4
import requests

logger = getLogger(__name__)

SUBDIRS = (
    "linux-64",
    "linux-aarch64",
    "linux-ppc64le",
    "osx-64",
    "osx-arm64",
    "win-64",
    "win-arm64",
    "noarch",
)
CACHE_DIR = Path(".repodata_cache")


@lru_cache
def all_labels(use_remote_cache: bool = False) -> List[str]:
    if use_remote_cache:
        r = requests.get(
            "https://raw.githubusercontent.com/conda-forge/"
            "by-the-numbers/main/data/labels.json"
        )
        r.raise_for_status()
        return r.json()

    if token := os.environ.get("BINSTAR_TOKEN"):
        label_info = requests.get(
            "https://api.anaconda.org/channels/conda-forge",
            headers={"Authorization": f"token {token}"},
        ).json()

        return sorted(label for label in label_info if "/" not in label)

    logger.info("No token detected. Fetching labels from anaconda.org HTML. Slow...")
    r = requests.get("https://anaconda.org/conda-forge/repo")
    r.raise_for_status()
    html = r.text
    soup = bs4.BeautifulSoup(html, "html.parser")
    labels = []
    len_prefix = len("/conda-forge/repo?label=")
    for element in soup.select("ul#Label > li > a"):
        href = element.get("href")
        if not href:
            continue
        label = href[len_prefix:]
        if label and label not in ("all", "empty") and "/" not in label:
            labels.append(label)
    return sorted(labels)


def fetch_repodata(
    subdirs: Iterable[str] = SUBDIRS,
    force_download: bool = False,
    cache_dir: Union[str, Path] = CACHE_DIR,
    label: str = "main",
) -> List[Path]:
    assert all(subdir in SUBDIRS for subdir in subdirs)
    paths = []
    for subdir in subdirs:
        if label == "main":
            repodata = f"https://conda.anaconda.org/conda-forge/{subdir}/repodata.json"
        else:
            repodata = (
                "https://conda.anaconda.org/conda-forge/"
                f"label/{label}/{subdir}/repodata.json"
            )
        local_fn = Path(cache_dir, f"{subdir}.{label}.json")
        local_fn_bz2 = Path(str(local_fn) + ".bz2")
        paths.append(local_fn)
        if force_download or not local_fn.exists():
            logger.info(f"Downloading {repodata} to {local_fn}")
            local_fn.parent.mkdir(parents=True, exist_ok=True)
            # Download the file
            urlretrieve(f"{repodata}.bz2", local_fn_bz2)
            with open(local_fn_bz2, "rb") as compressed, open(local_fn, "wb") as f:
                f.write(bz2.decompress(compressed.read()))
            local_fn_bz2.unlink()
    return paths


def list_artifacts(
    repodata_jsons: Iterable[Union[str, Path]],
    include_broken: bool = True,
) -> Generator[str, None, None]:
    for repodata in sorted(repodata_jsons):
        repodata = Path(repodata)
        subdir = repodata.stem.split(".")[0]
        assert (
            subdir in SUBDIRS
        ), "Invalid repodata file name. Must be '<subdir>.<label>.json'."
        data = json.loads(repodata.read_text())
        keys = ["packages", "packages.conda"]
        if include_broken:
            keys.append("removed")
        for key in keys:
            for pkg in data.get(key, ()):
                yield f"{subdir}/{pkg}"


def repodata(subdir: str) -> Dict[str, Any]:
    assert subdir in SUBDIRS
    path = fetch_repodata(subdirs=(subdir,))[0]
    return json.loads(path.read_text())


def n_artifacts(labels: Iterable[str] = ("main",)) -> Tuple[int, int]:
    """
    To get _all_ artifacts ever published, use `n_artifacts(all_labels())`.

    Returns number of artifacts and number of unique package names.
    """
    seen_artifacts, seen_package_names = set(), set()
    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for label, subdir in product(labels, SUBDIRS):
            future = executor.submit(fetch_repodata, (subdir,), False, CACHE_DIR, label)
            futures.append(future)
        for future in as_completed(futures):
            repodatas = future.result()
            artifacts = list_artifacts(repodatas, include_broken=True)
            for artifact in artifacts:
                seen_artifacts.add(artifact)
                seen_package_names.add(artifact.split("/")[-1].rsplit("-", 2)[0])

    return len(seen_artifacts), len(seen_package_names)
