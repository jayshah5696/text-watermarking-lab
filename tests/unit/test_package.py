from watermark_lab import __version__


def test_package_version_matches_project_version() -> None:
    assert __version__ == "0.1.0"
