from conda_forge_metadata.libcfgraph import get_libcfgraph_artifact_data


def get_artifact_info_as_json(channel, subdir, artifact, backend="libcfgraph"):
    """Get a blob of artifact data from the conda info directory.

    Parameters
    ----------
    channel : str
        The channel (e.g., "conda-forge").
    subdir : str
        The subdir for the artifact (e.g., "noarch", "linux-64", etc.).
    artifact : str
        The full artifact name with extension (e.g.,
        "21cmfast-3.0.2-py36h13dd421_0.tar.bz2").

    Returns
    -------
    info_blob : dict
        A dictionary of data. Possible keys are

            "metadata_version": the metadata version format
            "name": the package name
            "version": the package version
            "index": the info/index.json file contents
            "about": the info/about.json file contents
            "rendered_recipe": the fully rendered recipe at
                either info/recipe/meta.yaml or info/meta.yaml
                as a dict
            "raw_recipe": the template recipe as a string from
                info/recipe/meta.yaml.template - could be
                the rendered recipe as a string if no template was found
            "conda_build_config": the conda_build_config.yaml used for building
                the recipe at info/recipe/conda_build_config.yaml
            "files": a list of files in the recipe from info/files with
                elements ending in .pyc or .txt filtered out.
    """
    if backend == "libcfgraph":
        return get_libcfgraph_artifact_data(channel, subdir, artifact)
    elif backend == "oci":
        from conda_forge_metadata.oci import get_oci_artifact_data

        return get_oci_artifact_data(channel, subdir, artifact)
    else:
        raise ValueError(f"Unknown backend {backend!r}")
