# conda-forge-metadata

[![tests](https://github.com/conda-forge/conda-forge-metadata/actions/workflows/tests.yml/badge.svg)](https://github.com/conda-forge/conda-forge-metadata/actions/workflows/tests.yml) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/conda-forge/conda-forge-metadata/main.svg)](https://results.pre-commit.ci/latest/github/conda-forge/conda-forge-metadata/main)
[![Publish to PyPI](https://github.com/conda-forge/conda-forge-metadata/actions/workflows/pypi.yml/badge.svg)](https://github.com/conda-forge/conda-forge-metadata/actions/workflows/pypi.yml)

programmatic access to conda-forge's metadata

## Versioning and Deprecations

`conda-forge-metadata` follows [CalVer](https://calver.org/) using the `YYYY.MM.DD` scheme.

`conda-forge-metadata`'s API is defined as the collection of all reachable symbols whose fully qualified import path does not feature a leading underscore in any of its components. The API covers renames and, if callable, changes in signatures (argument and keyword argument names and types, plus the return types). The API also covers the command-line interface. Any other symbol may change at any time and has no guaranteed API.

All API changes must undergo a 60-day deprecation period, must be clearly indicated via a `DeprecationWarning`.
