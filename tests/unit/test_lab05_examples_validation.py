import copy

import pytest
from test_lab05_examples import raw_fixture

from watermark_lab.lab05_examples import build_examples_trace


def test_rejects_wrong_mode_count_and_runtime_identity() -> None:
    raw, config = raw_fixture()
    with pytest.raises(ValueError, match="twenty generation records"):
        build_examples_trace({**raw, "records": raw["records"][:-1]}, config)
    for field, value in (("gpu_name", "A10"), ("dtype", "torch.float32")):
        changed = copy.deepcopy(raw)
        changed[field] = value
        with pytest.raises(ValueError, match="GPU or dtype"):
            build_examples_trace(changed, config)
    for field in ("secret_used", "volume_used"):
        changed = copy.deepcopy(raw)
        changed[field] = True
        with pytest.raises(ValueError, match="neither Secret nor Volume"):
            build_examples_trace(changed, config)


def test_rejects_bad_provenance_primary_detector_and_text() -> None:
    raw, config = raw_fixture()
    for field, value in (("source_commit", "short"), ("config_sha256", "short")):
        changed = copy.deepcopy(raw)
        changed[field] = value
        with pytest.raises(ValueError, match=field):
            build_examples_trace(changed, config)
    results = copy.deepcopy(raw)
    results["records"][0]["detector_results"] = []
    with pytest.raises(ValueError, match="four detector"):
        build_examples_trace(results, config)
    role = copy.deepcopy(raw)
    role["records"][0]["detector_results"][0]["key_role"] = "comparison"
    with pytest.raises(ValueError, match="generation key"):
        build_examples_trace(role, config)
    text = copy.deepcopy(raw)
    text["records"][0]["copied_text"] = ""
    with pytest.raises(ValueError, match="copied text"):
        build_examples_trace(text, config)
