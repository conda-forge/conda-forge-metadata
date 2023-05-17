"""Commonly used type annotions for conda-forge-metadata."""

from typing import TypedDict

from typing_extensions import TypeAlias

CondaPackageName: TypeAlias = str
PypiPackageName: TypeAlias = str


class NameMappingEntry(TypedDict):
    pypi_name: PypiPackageName
    conda_name: CondaPackageName
    import_name: str
    mapping_source: str


class ArtifactData(TypedDict):
    """The data for a single artifact."""

    # the metadata version format
    metadata_version: int
    # the package name
    name: CondaPackageName
    # the package version
    version: str
    # the info/index.json file contents
    index: dict
    # the info/about.json file contents
    about: dict
    # the fully rendered recipe at either info/recipe/meta.yaml or info/meta.yaml as
    # a dict
    rendered_recipe: dict
    # the template recipe as a string from info/recipe/meta.yaml.template - could be
    # the rendered recipe as a string if no template was found
    raw_recipe: "str | None"
    # the conda_build_config.yaml used for building the recipe at
    # info/recipe/conda_build_config.yaml
    conda_build_config: dict
    # a list of files in the recipe from info/files with elements ending in .pyc or
    # .txt filtered out.
    files: "list[str]"
