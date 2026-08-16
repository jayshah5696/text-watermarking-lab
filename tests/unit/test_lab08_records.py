import copy
from pathlib import Path

import pytest

from watermark_lab.lab08_config import lab08_config_from_toml_bytes
from watermark_lab.lab08_records import score_trace

ROOT = Path(__file__).resolve().parents[2]
CONFIG = lab08_config_from_toml_bytes((ROOT / "configs/lab_08.toml").read_bytes())


def token_trace(green_positions: set[int], length: int = 80) -> list[dict[str, object]]:
    return [
        {
            "position": position,
            "token_id": 100 + position,
            "piece": str(position),
            "eligible": position > 0,
            "previous_token_id": 99 + position if position > 0 else None,
            "is_green": position in green_positions if position > 0 else None,
        }
        for position in range(length)
    ]


def test_score_trace_uses_first_80_copied_ids_and_strict_cutoff() -> None:
    trace = token_trace(set(range(1, 31)))
    score = score_trace(trace, CONFIG)
    assert score["copied_prefix"] == 80
    assert score["num_green_tokens"] == 30
    assert score["num_tokens_scored"] == 79
    assert score["prediction"] == (score["z_score"] > 3.0)


def test_score_trace_preserves_short_attack_as_insufficient() -> None:
    score = score_trace(token_trace({1, 2}, length=20), CONFIG)
    assert score == {
        "status": "insufficient_copied_tokens",
        "copied_prefix": 20,
        "num_green_tokens": 2,
        "num_tokens_scored": 19,
    }


def test_score_trace_rejects_token_identity_and_membership_drift() -> None:
    trace = token_trace({1})
    broken = copy.deepcopy(trace)
    broken[2]["position"] = 3
    with pytest.raises(ValueError, match="identity"):
        score_trace(broken, CONFIG)
    broken = copy.deepcopy(trace)
    broken[1]["is_green"] = None
    with pytest.raises(ValueError, match="Boolean"):
        score_trace(broken, CONFIG)
