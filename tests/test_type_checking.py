"""
Type checking validation tests.

This test suite validates that the codebase passes strict type checking
using mypy. This ensures type safety and catches type-related bugs early.
"""
import subprocess
import pytest


def test_mypy_strict_passes_on_src():
    """
    Code must pass mypy --strict type checking.

    This test runs mypy with --strict mode on the entire src/ directory.
    Strict mode enables all optional checks for maximum type safety:
    - Disallows untyped function definitions
    - Disallows untyped calls
    - Disallows incomplete definitions
    - Checks for untyped decorators
    - Warns about unused ignores
    - And many more...

    If this test fails, it means there are type annotation issues that
    need to be fixed for proper type safety.
    """
    result = subprocess.run(
        ["uv", "run", "mypy", "src/", "--strict"],
        capture_output=True,
        text=True,
        cwd="C:\\Users\\Antoine\\Desktop\\exemple_api_post_hexagonal"
    )

    if result.returncode != 0:
        error_msg = f"mypy --strict found type errors:\n\n{result.stdout}\n\n{result.stderr}"
        pytest.fail(error_msg)

    assert result.returncode == 0, "mypy --strict should pass with no errors"


def test_mypy_strict_passes_on_domain():
    """
    Domain layer must pass mypy --strict type checking.

    The domain is the core of our application and must have perfect type safety.
    This test specifically validates the domain layer in isolation.
    """
    result = subprocess.run(
        ["uv", "run", "mypy", "src/domain/", "--strict"],
        capture_output=True,
        text=True,
        cwd="C:\\Users\\Antoine\\Desktop\\exemple_api_post_hexagonal"
    )

    if result.returncode != 0:
        error_msg = f"mypy --strict found type errors in domain:\n\n{result.stdout}\n\n{result.stderr}"
        pytest.fail(error_msg)

    assert result.returncode == 0, "Domain layer must have perfect type hints"


def test_mypy_strict_passes_on_ports():
    """
    Port interfaces must pass mypy --strict type checking.

    Ports define the contracts between layers, so they must have
    complete and correct type annotations.
    """
    result = subprocess.run(
        ["uv", "run", "mypy", "src/ports/", "--strict"],
        capture_output=True,
        text=True,
        cwd="C:\\Users\\Antoine\\Desktop\\exemple_api_post_hexagonal"
    )

    if result.returncode != 0:
        error_msg = f"mypy --strict found type errors in ports:\n\n{result.stdout}\n\n{result.stderr}"
        pytest.fail(error_msg)

    assert result.returncode == 0, "Port interfaces must have perfect type hints"
