from conda_forge_metadata.feedstock_outputs import package_to_feedstock


def test_feedstock_outputs():
    assert package_to_feedstock("conda-forge-pinning") == ["conda-forge-pinning"]
    assert package_to_feedstock("tk") == ["tk"]
    assert "python" in package_to_feedstock("python")


def test_feedstock_outputs_autoreg():
    assert package_to_feedstock("libllvm29") == ["llvmdev"]
