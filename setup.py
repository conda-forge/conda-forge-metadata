from setuptools import setup, find_packages

__version__ = None
with open("conda_forge_metadata/_version.py") as fp:
    exec(fp.read().strip())

setup(
    name="conda-forge-metadata",
    version=__version__,
    description=(
        "programatic access to conda-forge's metadata"
    ),
    author="Conda-forge-tick Development Team",
    author_email="",
    url="https://github.com/regro/conda-forge-metadata",
    packages=find_packages(exclude=["tests"]),
)
