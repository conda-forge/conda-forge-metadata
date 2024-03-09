from conda_forge_metadata import repodata


def test_labels_anaconda_org(monkeypatch):  # type: ignore
    monkeypatch.delenv("BINSTAR_TOKEN", raising=False)
    labels = repodata.all_labels()
    assert len(labels) >= 20
    assert "main" in labels
    assert "broken" in labels
