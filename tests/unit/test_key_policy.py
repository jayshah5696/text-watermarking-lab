from dataclasses import asdict

import pytest

from watermark_lab.key_policy import private_key_from_environment, public_demo_key
from watermark_lab.service_contract import (
    GenerateRequest,
    public_generation_response,
)


def test_public_demo_key_is_reproducible_but_serialization_hides_value() -> None:
    key = public_demo_key(value=15485863)
    assert key.value == 15485863
    assert key.public_metadata() == {"key_version": "demo-v1", "public_demo": True}
    assert "value" not in key.public_metadata()


def test_private_key_loads_once_from_injected_environment() -> None:
    environment = {
        "WATERMARK_HASHING_KEY": "918273645",
        "WATERMARK_KEY_VERSION": "prod-2026-08",
    }
    key = private_key_from_environment(environment=environment)
    assert key.value == 918273645
    assert key.public_metadata() == {
        "key_version": "prod-2026-08",
        "public_demo": False,
    }


def test_private_key_errors_do_not_echo_secret_value() -> None:
    secret = "not-a-number-secret"
    with pytest.raises(RuntimeError) as raised:
        private_key_from_environment(environment={"WATERMARK_HASHING_KEY": secret})
    assert secret not in str(raised.value)
    with pytest.raises(RuntimeError, match="missing"):
        private_key_from_environment(environment={})


def test_public_generation_response_contains_version_but_not_key() -> None:
    key = private_key_from_environment(
        environment={"WATERMARK_HASHING_KEY": "1234", "WATERMARK_KEY_VERSION": "v7"}
    )
    response = public_generation_response(
        text="continuation",
        model_revision="model@revision",
        watermark_profile="kgw-reference-v1",
        key=key,
    )
    serialized = asdict(response)
    assert serialized["key_version"] == "v7"
    assert "1234" not in repr(serialized)
    assert "key" not in serialized


def test_generate_request_enforces_host_limits() -> None:
    assert GenerateRequest(prompt="hello").max_new_tokens == 200
    with pytest.raises(ValueError, match="prompt"):
        GenerateRequest(prompt="")
    with pytest.raises(ValueError, match="max_new_tokens"):
        GenerateRequest(prompt="hello", max_new_tokens=401)
    with pytest.raises(ValueError, match="temperature"):
        GenerateRequest(prompt="hello", temperature=3.0)
