"""Gemeinsame Fixtures: die Mini-Welt, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Handrechnung der Mini-Welt (a = kappa = 1, gamma = 0, theta = 1/2, keine Gegenmittel): Beide investieren 1, der Überschuss ist 2, jede Seite bekommt 1
und bezahlt 1/2 Kosten, also 1/2 netto. Investiert V nur 1/2 (S weiter 1), ist der Überschuss 3/2, V bekommt 3/4 und bezahlt 1/8, also 5/8 netto."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hup_scenario import Params  # noqa: E402


@pytest.fixture
def mini():
    """Die Mini-Welt: additiv, symmetrisch, hälftige Teilung, keine Gegenmittel."""
    return Params()
