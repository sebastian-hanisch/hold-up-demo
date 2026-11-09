"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und jedes Preset durchläuft die echte Rechnung mit der erwarteten Verdikt-Zeile
(DEMO-PLAYBOOK §11a Punkt 7: ein Preset ohne Effekt meldet keinen Effekt)."""

import math

import pytest

import hup_constants as C
import hup_evaluation as ev
import hup_presets as P

LIMITS = {
    "theta": C.THETA_PCT, "gamma": C.GAMMA_PCT, "kappa": C.KAPPA_PCT, "a": C.A_PCT, "lam_v": C.LAM_V_PCT, "lam_s": C.LAM_S_PCT,
    "phi": C.PHI_PCT, "psi": C.PSI_PCT, "delta": C.DELTA_PCT,
}
STANDARD = "Hälftige Teilung, additiv (75 %)"


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        for key, value in preset.items():
            lo, hi, _ = LIMITS[key]
            assert lo <= value <= hi, (name, key)


def test_default_preset_equals_the_default_settings_and_is_the_first_one():
    assert next(iter(C.PRESETS)) == STANDARD
    assert ev.Settings(**C.PRESETS[STANDARD]) == ev.Settings()


def test_setting_specs_cover_every_preset_key_and_match_the_constants():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for key, state_key in P.PRESET_KEYS.items():
        spec = P.SETTING_SPECS[state_key]
        assert (spec.lo, spec.hi, spec.default) == LIMITS[key]


def test_permalink_values_are_clamped_to_the_slider_bounds():
    spec = P.SETTING_SPECS["theta_slider"]
    assert P.clamp_to_bounds(spec, -5) == 0 and P.clamp_to_bounds(spec, 250) == 100 and P.clamp_to_bounds(spec, 37) == 37


def _expected():
    """Erwartete Messwerte je Preset (von Hand gerechnet, siehe README): (Wirkungsgrad, Zahl der Gleichgewichte, Art Kernfrage, Art Wiederholung)."""
    return {
        "Hälftige Teilung, additiv (75 %)": (0.75, 1, "warning", "info"),
        "Investierender bekommt 80 % (θ = 0,8)": (0.66, 1, "warning", "warning"),
        "Starke Komplementarität": (0.75, 2, "warning", "info"),
        "Eigentum für eine Seite": (0.855, 1, "warning", "warning"),
        "Vorab-Vertrag mit Flexibilitätsverlust": (0.8460937, 1, "warning", "info"),
        "Wiederholung mit hohem δ": (0.75, 1, "warning", "success"),
    }


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_runs_through_the_real_calculation_with_the_expected_verdict(name):
    eff, n_eq, kind_core, kind_rep = _expected()[name]
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    assert a.res.efficiency == pytest.approx(eff, abs=1e-5)
    assert len(a.res.equilibria) == n_eq
    assert ev.verdict_kernfrage(a)[0] == kind_core
    assert ev.verdict_repeated(a)[0] == kind_rep


def test_the_repeated_preset_changes_only_the_repeated_line():
    base = ev.analyse(ev.Settings(**C.PRESETS[STANDARD]))
    rep = ev.analyse(ev.Settings(**C.PRESETS["Wiederholung mit hohem δ"]))
    assert rep.res.efficiency == pytest.approx(base.res.efficiency, abs=1e-9)         # Einmalspiel unverändert: kein Effekt gemeldet
    assert rep.rep_efficiency == pytest.approx(1.0) and base.rep_efficiency == pytest.approx(0.75, abs=1e-6)


def test_the_complementarity_preset_has_the_same_efficiency_as_the_standard_but_a_second_equilibrium():
    base = ev.analyse(ev.Settings(**C.PRESETS[STANDARD]))
    comp = ev.analyse(ev.Settings(**C.PRESETS["Starke Komplementarität"]))
    assert comp.res.efficiency == pytest.approx(base.res.efficiency, abs=1e-6)
    assert comp.res.efficiency_worst == pytest.approx(0.0, abs=1e-9) and base.res.efficiency_worst == pytest.approx(0.75, abs=1e-6)


def test_the_one_sided_ownership_preset_raises_only_vs_investment():
    base = ev.analyse(ev.Settings(**C.PRESETS[STANDARD]))
    own = ev.analyse(ev.Settings(**C.PRESETS["Eigentum für eine Seite"]))
    assert own.res.eq[0] > base.res.eq[0] + 0.1
    assert own.res.eq[1] == pytest.approx(base.res.eq[1], abs=1e-6)


def test_the_preset_without_threshold_says_so():
    a = ev.analyse(ev.Settings(**C.PRESETS["Investierender bekommt 80 % (θ = 0,8)"]))
    assert math.isinf(a.rep.threshold)
    assert "Keine Schwelle" in ev.verdict_repeated(a)[1]
