import pytest

from conda_forge_metadata import repodata


@pytest.mark.xfail(
    reason="See https://github.com/conda-forge/conda-forge-metadata/issues/97"
)
def test_labels_anaconda_org(monkeypatch):  # type: ignore
    monkeypatch.delenv("BINSTAR_TOKEN", raising=False)
    labels = repodata.all_labels()
    assert len(labels) >= 20
    assert "main" in labels
    assert "broken" in labels


def test_aggregated():
    reports = ["artifacts", "names", "size"]
    result = repodata.aggregated(reports=reports, labels=("hsp2_dev",))  # type: ignore
    assert reports == list(result.keys())
    for key, value in result.items():
        assert value > 0, f"{key}={value}"
