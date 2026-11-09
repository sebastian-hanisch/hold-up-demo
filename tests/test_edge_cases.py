"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): Reglerränder, Entartungen, Gleichstände.

Die Ränder der Regler (Prozent in hup_constants) sind hier einzeln und als alle Minima und alle Maxima durchgerechnet; kein Fall darf an die
Investitionsgrenze X_MAX stoßen oder einen Wirkungsgrad über 1 liefern."""

import math
from dataclasses import fields

import pytest

import hup_algorithm as A
import hup_constants as C
import hup_evaluation as ev
from hup_scenario import Params, payoffs

LIMITS = {
    "theta": C.THETA_PCT, "gamma": C.GAMMA_PCT, "kappa": C.KAPPA_PCT, "a": C.A_PCT, "lam_v": C.LAM_V_PCT, "lam_s": C.LAM_S_PCT,
    "phi": C.PHI_PCT, "psi": C.PSI_PCT, "delta": C.DELTA_PCT,
}


def _edge_settings():
    """Jeder Regler einzeln am Minimum und am Maximum, dazu alle Minima und alle Maxima."""
    cases = []
    for name, (lo, hi, _) in LIMITS.items():
        cases.append((f"{name}-min", ev.Settings(**{name: lo})))
        cases.append((f"{name}-max", ev.Settings(**{name: hi})))
    cases.append(("alle-min", ev.Settings(**{n: lim[0] for n, lim in LIMITS.items()})))
    cases.append(("alle-max", ev.Settings(**{n: lim[1] for n, lim in LIMITS.items()})))
    return cases


def test_limits_cover_every_setting_field():
    assert set(LIMITS) == {f.name for f in fields(ev.Settings)}


@pytest.mark.parametrize("label,settings", _edge_settings(), ids=[c[0] for c in _edge_settings()])
def test_every_regler_edge_runs_and_stays_inside_the_model_bounds(label, settings):
    a = ev.analyse(settings)
    r = a.res
    assert r.equilibria, label
    assert max(max(e) for e in r.equilibria) < C.X_MAX - 0.05 and max(r.fb) < C.X_MAX - 0.05      # nichts stößt an die Grenze
    assert -1e-9 <= r.efficiency <= 1.0 + 1e-9
    assert -1e-9 <= r.efficiency_worst <= r.efficiency + 1e-9
    for kind, text in (ev.verdict_kernfrage(a), ev.verdict_repeated(a), ev.verdict_asymmetry(a)):
        assert kind in ("success", "info", "warning") and text
        assert "nan" not in text.lower() and "inf" not in text.lower()


def test_v_gets_nothing_at_theta_zero_and_s_gets_nothing_at_theta_one():
    res = A.analyse_investment(Params(theta=0.0))
    assert res.eq == pytest.approx((0.0, 1.0), abs=1e-5) and res.efficiency == pytest.approx(0.5, abs=1e-6)
    res = A.analyse_investment(Params(theta=1.0))
    assert res.eq == pytest.approx((1.0, 0.0), abs=1e-5) and res.efficiency == pytest.approx(0.5, abs=1e-6)


def test_ownership_equal_to_the_whole_contribution_removes_the_hold_up():
    """lambda = 1 für beide: jede Seite behält ihren ganzen Beitrag, es bleibt nichts zu verhandeln, die Investition ist effizient."""
    res = A.analyse_investment(Params(lam_v=1.0, lam_s=1.0))
    assert res.efficiency == pytest.approx(1.0, abs=1e-6)
    assert res.eq == pytest.approx(res.fb, abs=1e-5)


def test_contract_without_flexibility_loss_removes_the_hold_up_and_with_loss_it_can_hurt():
    assert A.analyse_investment(Params(phi=1.0, psi=0.0)).efficiency == pytest.approx(1.0, abs=1e-6)
    # phi = 1, psi = 1/2: s = 1/2, Anteil 1: Wirkungsgrad s^2 * 1 * (2 - 1) = 1/4, schlechter als ohne Vertrag (3/4)
    assert A.analyse_investment(Params(phi=1.0, psi=0.5)).efficiency == pytest.approx(0.25, abs=1e-6)


def test_contract_with_phi_zero_ignores_psi():
    assert A.analyse_investment(Params(phi=0.0, psi=0.5)).efficiency == pytest.approx(A.analyse_investment(Params()).efficiency, abs=1e-9)


def test_equal_split_gives_equal_efficiency_for_any_productivity():
    """Gleichstand der Anteile (theta = 1/2, additiv): der Wirkungsgrad ist 3/4, auch wenn V doppelt so produktiv ist."""
    for a in (0.5, 1.0, 2.0):
        assert A.analyse_investment(Params(a=a)).efficiency == pytest.approx(0.75, abs=1e-6)


def test_cost_factor_does_not_change_the_efficiency():
    for kappa in (0.5, 1.0, 2.0):
        for p in (Params(kappa=kappa, theta=0.8), Params(kappa=kappa, gamma=1.0, theta=0.3, a=1.5), Params(kappa=kappa, lam_v=0.5, phi=0.4, psi=0.1)):
            base = A.analyse_investment(Params(**{**p.__dict__, "kappa": 1.0})).efficiency
            assert A.analyse_investment(p).efficiency == pytest.approx(base, abs=1e-5)


def test_zero_investments_give_zero_payoffs_and_zero_loss():
    uv, us = payoffs(0.0, 0.0, Params(gamma=1.0, lam_v=1.0, phi=1.0))
    assert float(uv) == 0.0 and float(us) == 0.0


def test_no_threshold_is_reported_as_infinity_and_never_as_a_number():
    a = ev.analyse(ev.Settings(theta=80))
    assert math.isinf(a.rep.threshold)
    assert a.rep_efficiency == pytest.approx(a.res.efficiency)


def test_maximize_1d_finds_an_interior_maximum_and_the_boundary_maximum():
    import numpy as np
    x, f = A.maximize_1d(lambda t: -(t - 1.7) ** 2, 1)
    assert float(x[0]) == pytest.approx(1.7, abs=1e-5) and float(f[0]) == pytest.approx(0.0, abs=1e-9)
    x, _ = A.maximize_1d(lambda t: t, 1)
    assert float(x[0]) == pytest.approx(C.X_MAX, abs=1e-6)
    x, _ = A.maximize_1d(lambda t: -t, 1)
    assert float(x[0]) == pytest.approx(0.0, abs=1e-6)
    x, _ = A.maximize_1d(lambda t: np.zeros_like(t) + 0.0 * t, 1)      # konstante Funktion: Gleichstand, der erste Gitterpunkt zählt
    assert 0.0 <= float(x[0]) <= C.X_MAX
