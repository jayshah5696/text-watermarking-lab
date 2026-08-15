"""Provider-neutral request and response contracts for a keyed generation process."""

from __future__ import annotations

from dataclasses import dataclass

from watermark_lab.key_policy import KeyMaterial


@dataclass(frozen=True, slots=True)
class GenerateRequest:
    """The fields an authenticated transport may pass to generation."""

    prompt: str
    max_new_tokens: int = 200
    temperature: float = 0.8
    top_k: int = 40
    top_p: float = 0.95

    def __post_init__(self) -> None:
        if not self.prompt or len(self.prompt) > 8_000:
            raise ValueError("prompt must contain between 1 and 8000 characters")
        if not 1 <= self.max_new_tokens <= 400:
            raise ValueError("max_new_tokens must be between 1 and 400")
        if not 0.05 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.05 and 2.0")
        if not 1 <= self.top_k <= 200:
            raise ValueError("top_k must be between 1 and 200")
        if not 0.05 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0.05 and 1.0")


@dataclass(frozen=True, slots=True)
class GenerateResponse:
    """Public generation data with a key version but never a key value."""

    text: str
    model_revision: str
    watermark_profile: str
    key_version: str
    public_demo: bool


def public_generation_response(
    *,
    text: str,
    model_revision: str,
    watermark_profile: str,
    key: KeyMaterial,
) -> GenerateResponse:
    """Build an allowlisted response from process-local key material."""

    if not text:
        raise ValueError("text must not be empty")
    metadata = key.public_metadata()
    return GenerateResponse(
        text=text,
        model_revision=model_revision,
        watermark_profile=watermark_profile,
        key_version=str(metadata["key_version"]),
        public_demo=bool(metadata["public_demo"]),
    )
