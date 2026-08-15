"""Explicit public-demo and server-secret key policies for hosted watermarking."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KeyMaterial:
    """Process-local key material plus a non-secret version label."""

    value: int
    version: str
    is_public_demo: bool

    def __post_init__(self) -> None:
        if isinstance(self.value, bool):
            raise TypeError("key value must be an integer")
        if self.value < 0:
            raise ValueError("key value must be non-negative")
        if not self.version or not self.version.isascii():
            raise ValueError("key version must be non-empty ASCII text")

    def public_metadata(self) -> dict[str, str | bool]:
        """Return metadata safe to serialize without exposing the key value."""

        return {"key_version": self.version, "public_demo": self.is_public_demo}


def public_demo_key(*, value: int, version: str = "demo-v1") -> KeyMaterial:
    """Declare a reproducible key that provides no secrecy."""

    return KeyMaterial(value=value, version=version, is_public_demo=True)


def private_key_from_environment(
    *,
    variable: str = "WATERMARK_HASHING_KEY",
    version_variable: str = "WATERMARK_KEY_VERSION",
    environment: Mapping[str, str] | None = None,
) -> KeyMaterial:
    """Read a private integer key once from the server process environment."""

    source = os.environ if environment is None else environment
    raw_key = source.get(variable)
    if raw_key is None:
        raise RuntimeError(f"required secret environment variable {variable!r} is missing")
    try:
        value = int(raw_key, 10)
    except ValueError as error:
        raise RuntimeError(
            f"secret environment variable {variable!r} must be an integer"
        ) from error
    if value < 0:
        raise RuntimeError(f"secret environment variable {variable!r} must be non-negative")
    version = source.get(version_variable, "private-v1")
    return KeyMaterial(value=value, version=version, is_public_demo=False)
