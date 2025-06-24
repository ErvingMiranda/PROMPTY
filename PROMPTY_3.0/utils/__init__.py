"""Utilidades comunes para PROMPTY 3.0."""

from .helpers import *  # noqa: F401,F403

try:
    from .scaling import ScalingMixin
except Exception:  # pragma: no cover - fallback when PyQt is unavailable
    class ScalingMixin:  # type: ignore
        """Implementación mínima usada en entornos sin PyQt."""
        pass

__all__ = ["ScalingMixin"]
