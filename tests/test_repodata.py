import pytest

from conda_forge_metadata import repodata


@pytest.xfail(
    reason="See https://github.com/conda-forge/conda-forge-metadata/issues/97"
)
def test_labels_anaconda_org(monkeypatch):  # type: ignore
    monkeypatch.delenv("BINSTAR_TOKEN", raising=False)
    labels = repodata.all_labels()
    assert len(labels) >= 20
    assert "main" in labels
    assert "broken" in labels
