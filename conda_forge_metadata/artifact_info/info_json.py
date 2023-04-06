from conda_forge_metadata.libcfgraph import get_libcfgraph_artifact_data


def get_artifact_info_as_json(channel, subdir, artifact):
    return get_libcfgraph_artifact_data(channel, subdir, artifact)
