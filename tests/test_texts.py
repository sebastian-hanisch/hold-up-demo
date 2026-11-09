"""Texte: App und README tragen denselben Wortlaut der Annahmen (DEMO-PLAYBOOK §5), keine Platzhalter, Permalink begrenzt Werte auf die Reglergrenzen."""

import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

import hup_constants as C
from hup_texts import ASSUMPTIONS_MARKDOWN

ROOT = Path(__file__).resolve().parent.parent
APP = str(ROOT / "app.py")


def _app(**query) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in query.items():
        at.query_params[k] = v
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_readme_contains_the_assumptions_text_of_the_app_verbatim():
    assert ASSUMPTIONS_MARKDOWN.rstrip("\n") in (ROOT / "README.md").read_text(encoding="utf-8")


def test_app_shows_the_assumptions_text_in_its_expander():
    at = _app()
    expander = next(e for e in at.expander if e.label == "⚠️ Annahmen, Grenzen und bekannte Probleme")
    assert ASSUMPTIONS_MARKDOWN.strip() in " ".join(m.value for m in expander.markdown)


def test_app_has_the_required_sections_by_title():
    at = _app()
    labels = {e.label for e in at.expander}
    assert {"📐 Mathematische Formulierung", "⚠️ Annahmen, Grenzen und bekannte Probleme", "So funktioniert Hold-up"} <= labels
    subheads = [s.value for s in at.subheader]
    assert sum(1 for s in subheads if s.startswith("🔬")) == 5 and any(s.startswith("🚧") for s in subheads)


def test_no_placeholders_or_forbidden_words_remain():
    for path in list(ROOT.glob("*.py")) + [ROOT / "README.md"] + list((ROOT / "tests").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if path.name == "README.md":
            text = re.sub(r"<!-- TODO nach dem Deploy.*?-->", "", text, flags=re.S)      # der Live-Link-Platzhalter des Gerüsts bleibt bis zum Deploy
        if path.name == "test_texts.py":
            continue
        assert "TODO" not in text, path.name
        assert "Saatwert" not in text and "Schwanz" not in text, path.name


def test_math_expander_has_one_display_equation_per_block():
    """Je Display-Gleichung ein eigener $$-Block (sonst KaTeX-Fehler): kein Block enthält ein zweites $$ oder eine Leerzeile."""
    text = (ROOT / "app.py").read_text(encoding="utf-8")
    blocks = re.findall(r"\$\$(.*?)\$\$", text, flags=re.S)
    assert len(blocks) >= 12
    for b in blocks:
        assert "\n\n" not in b and "$" not in b


def test_permalink_clamps_out_of_range_values_to_the_slider_bounds():
    at = _app(th="500", ga="-20", ka="1", pa="abc")
    values = {s.key: s.value for s in at.sidebar.slider}
    assert values["theta_slider"] == C.THETA_PCT[1]
    assert values["gamma_slider"] == C.GAMMA_PCT[0]
    assert values["kappa_slider"] == C.KAPPA_PCT[0]
    assert values["a_slider"] == C.A_PCT[2]            # nicht lesbar: Standardwert


def test_permalink_roundtrip_of_a_preset():
    at = _app()
    at.sidebar.button(key="preset_Eigentum für eine Seite").click().run()
    assert at.query_params["lv"] == ["60"] or at.query_params["lv"] == "60"
