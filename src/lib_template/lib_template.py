"""Temporary test stub for lib_template."""

from __future__ import annotations


def hello_world() -> None:
    """Print a friendly greeting."""
    print("Hello World")


def i_should_fail() -> None:
    """Fails intentionally to test Error Behaviour"""
    raise RuntimeError("I should fail")
