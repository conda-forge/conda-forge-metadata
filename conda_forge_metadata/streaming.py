"""
Use conda-package-streaming to fetch package metadata
"""

from contextlib import closing

from conda_package_streaming.package_streaming import stream_conda_component
from conda_package_streaming.url import conda_reader_for_url


def get_streamed_artifact_data(channel: str, subdir: str, artifact: str):
    if not channel.startswith("http"):
        if channel in ("pkgs/main", "pkgs/r", "pkgs/msys2"):
            channel = f"https://repo.anaconda.com/{channel}"
        else:
            channel = f"https://conda.anaconda.org/{channel}"

    # .conda artifacts can be streamed directly from an anaconda.org channel
    url = f"{channel}/{subdir}/{artifact}"
    filename, conda = conda_reader_for_url(url)

    with closing(conda):
        yield from stream_conda_component(filename, conda, component="info")
