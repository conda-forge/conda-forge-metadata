import json
from pathlib import Path

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


@pytest.fixture
def hsp2_dev_with_removed_cache(tmp_path: Path):
    repodata.fetch_repodata(label="hsp2_dev", force_download=True, cache_dir=tmp_path)
    noarch_json = tmp_path / "noarch.hsp2_dev.json"
    if noarch_json.is_file():
        noarch_repodata = json.loads(noarch_json.read_text())
    else:
        noarch_repodata = {"packages": {}, "packages.conda": {}, "removed": []}
    noarch_repodata.setdefault("removed", []).append("removed-package-1-0")
    noarch_json.write_text(json.dumps(noarch_repodata))
    yield tmp_path


def test_aggregated(hsp2_dev_with_removed_cache: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(repodata, "CACHE_DIR", hsp2_dev_with_removed_cache)
    reports = ["artifacts", "names", "size"]
    result = repodata.aggregated(
        reports=reports,  # type: ignore
        labels=("hsp2_dev",),
        include_broken=True,
    )
    assert reports == list(result.keys())
    for key, value in result.items():
        assert value > 0, f"{key}={value}"

    # Without the 'removed' entry, one less artifact
    result2 = repodata.aggregated(
        reports=reports,  # type: ignore
        labels=("hsp2_dev",),
        include_broken=False,
    )
    assert result["artifacts"] == (result2["artifacts"] + 1)
