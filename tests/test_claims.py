"""Jede Zahl der README (Abschnitt „Befunde“) und der Apptexte, mit ihrer Voraussetzung: hier steht, was gemessen wurde und mit welchem Band.

Zahl -> Test: siehe die Tabelle in der README. Alle Werte sind Messungen des Codes dieser Demo (Gleichgewichte numerisch, Genauigkeit rund 1e-6);
exakt verglichen wird nur, was von Hand zu rechnen ist, sonst mit Band. Die unabhängige Prüfung der Rechnung steht in test_oracle_hold_up.py."""

import itertools
import math
from dataclasses import replace

import pytest

import hup_algorithm as A
import hup_constants as C
import hup_evaluation as ev
from hup_scenario import Params, payoffs


def eff(p: Params) -> float:
    return A.analyse_investment(p).efficiency


# --- Befund 1: Wirkungsgrad bei hälftiger Teilung -------------------------------------------------------------------------------------------


def test_claim_half_split_additive_gives_75_percent():
    r = A.analyse_investment(Params())            # theta = 1/2, gamma = 0, a = kappa = 1, keine Gegenmittel
    assert r.efficiency == pytest.approx(0.75, abs=1e-6)
    assert r.eq == pytest.approx((0.5, 0.5), abs=1e-5) and r.fb == pytest.approx((1.0, 1.0))
    assert r.net == pytest.approx(0.75, abs=1e-6) and r.fb_net == pytest.approx(1.0)


def test_claim_formula_matches_the_grid_over_eleven_thetas():
    rows = ev.sweep_theta(ev.Settings())
    assert len(rows) == 11
    assert max(abs(r["eff_additive"] - r["eff_formula"]) for r in rows) < 1e-6
    assert max(abs(r["eff_additive"] - A.additive_efficiency_formula(r["theta"])) for r in rows) < 1e-6


def test_claim_efficiency_over_theta_peaks_at_one_half_and_is_symmetric():
    rows = {round(r["theta"], 1): r["eff_additive"] for r in ev.sweep_theta(ev.Settings())}
    assert max(rows, key=rows.get) == 0.5 and rows[0.5] == pytest.approx(0.75, abs=1e-6)
    assert rows[0.0] == pytest.approx(0.5, abs=1e-6) and rows[1.0] == pytest.approx(0.5, abs=1e-6)
    assert all(rows[t] == pytest.approx(rows[round(1 - t, 1)], abs=1e-6) for t in rows)
    assert sum(1 for v in rows.values() if v >= ev.EFF_FULL) == 0          # kein theta aus dem Raster erreicht 99,5 %


def test_claim_theta_eighty_percent_gives_66_percent_and_unequal_investment():
    a = ev.analyse(ev.Settings(theta=80))
    assert a.res.efficiency == pytest.approx(0.66, abs=1e-6)
    assert (a.quote_v, a.quote_s) == pytest.approx((0.8, 0.2), abs=1e-5)
    assert (a.loss_v, a.loss_s) == pytest.approx((0.02, 0.32), abs=1e-5)


def test_claim_productive_v_with_equal_split_loses_four_times_as_much_as_s():
    """a = 2, theta = 1/2, additiv: beide investieren die Hälfte des Effizienten, am Netto fehlt durch V 0,5, durch S 0,125 (Faktor a^2)."""
    a = ev.analyse(ev.Settings(a=200))
    assert a.res.efficiency == pytest.approx(0.75, abs=1e-6)
    assert (a.quote_v, a.quote_s) == pytest.approx((0.5, 0.5), abs=1e-5)
    assert (a.loss_v, a.loss_s) == pytest.approx((0.5, 0.125), abs=1e-5)


# --- Befund 2: Komplementarität -----------------------------------------------------------------------------------------------------------


def test_claim_complementarity_does_not_change_efficiency_at_an_equal_split():
    for a in (1.0, 2.0):
        for g in C.GAMMA_SWEEP:
            assert eff(Params(gamma=g, a=a)) == pytest.approx(0.75, abs=1e-6), (a, g)


def test_claim_complementarity_lowers_efficiency_at_an_unequal_split():
    expected = {0.0: 0.66, 0.25: 0.636, 0.5: 0.6201, 0.75: 0.6086, 1.0: 0.6}          # theta = 0,8, a = kappa = 1
    values = [eff(Params(theta=0.8, gamma=g)) for g in expected]
    assert values == pytest.approx(list(expected.values()), abs=6e-4)
    assert all(x > y for x, y in zip(values, values[1:]))


def test_claim_complementarity_one_adds_the_no_investment_equilibrium():
    rows = ev.multiplicity_grid(ev.Settings())
    assert [len(r["counts"]) for r in rows] == [5] * 5
    assert [r["counts"] for r in rows] == [[1] * 5, [1] * 5, [1] * 5, [1] * 5, [2] * 5]     # nur die Zeile gamma = 1 hat zwei
    assert sum(1 for r in rows for k in r["counts"] if k > 1) == 5                          # 5 von 25 Zellen


def test_claim_multiple_equilibria_on_a_wide_raster_only_at_gamma_one():
    """Breites Raster von 144 Welten (theta 3 x gamma 4 x a 3 x Eigentum V 2 x Vertrag 2), Kostenfaktor 1."""
    cnt = {"g<1": [0, 0], "g=1": [0, 0]}
    single_at_one = []
    for th, g, a, lam, phi in itertools.product((0.2, 0.5, 0.8), (0.0, 0.5, 0.9, 1.0), (0.5, 1.0, 2.0), (0.0, 0.5), (0.0, 0.5)):
        eqs = A.analyse_investment(Params(theta=th, gamma=g, a=a, lam_v=lam, phi=phi, psi=0.1)).equilibria
        key = "g=1" if g == 1.0 else "g<1"
        cnt[key][0] += 1
        cnt[key][1] += len(eqs) > 1
        if g == 1.0 and len(eqs) == 1:
            single_at_one.append((th, a, lam, phi, eqs[0]))
    assert cnt["g<1"] == [108, 0]                       # bei gamma < 1: in keiner der 108 Welten mehr als ein Gleichgewicht
    assert cnt["g=1"] == [36, 33]                       # bei gamma = 1: in 33 von 36 Welten mehr als eines
    # die 3 übrigen: a = 2, Eigentum V 0,5, Vertrag 0,5; dort bleibt nur das Gleichgewicht ohne Investition (die Reaktion von S springt)
    assert [(t, a, lam, phi) for t, a, lam, phi, _ in single_at_one] == [(0.2, 2.0, 0.5, 0.5), (0.5, 2.0, 0.5, 0.5), (0.8, 2.0, 0.5, 0.5)]
    assert all(e == pytest.approx((0.0, 0.0), abs=1e-9) for *_, e in single_at_one)


def test_no_pure_equilibrium_is_reported_as_not_found_instead_of_a_made_up_zero_equilibrium():
    """γ = 0,9, a = 2, λ_V = 0,5, φ = 0,5: die Reaktion von S springt, auf dem Raster gibt es kein reines Gleichgewicht; (0; 0) ist keines."""
    from hup_evaluation import Analysis, Settings, analyse, verdict_kernfrage
    p = Params(theta=0.5, gamma=0.9, a=2.0, lam_v=0.5, phi=0.5, psi=0.1)
    assert A.find_equilibria(p) == []
    res = A.analyse_investment(p)
    assert res.found is False and res.equilibria == ()
    # (0; 0) ist tatsächlich kein Gleichgewicht: V gewinnt durch Abweichung
    uv0 = float(payoffs(0.0, 0.0, p)[0])
    assert max(float(payoffs(x, 0.0, p)[0]) for x in (i / 100 for i in range(0, 101))) > uv0 + 1e-3
    an = analyse(Settings(theta=50, gamma=90, kappa=100, a=200, lam_v=50, lam_s=0, phi=50, psi=10))
    assert isinstance(an, Analysis) and not an.res.found
    kind, text = verdict_kernfrage(an)
    assert kind == "warning" and "Kein Gleichgewicht in reinen Strategien auf dem Raster gefunden" in text
    assert "Wirkungsgrad **" not in text


def test_claim_the_equilibrium_shown_is_the_one_with_the_highest_investments_and_the_worst_is_zero_net():
    r = A.analyse_investment(Params(gamma=1.0))
    assert r.eq == pytest.approx((0.5, 0.5), abs=1e-5)
    assert r.efficiency == pytest.approx(0.75, abs=1e-6) and r.efficiency_worst == pytest.approx(0.0, abs=1e-9)


# --- Befund 3: Gegenmittel --------------------------------------------------------------------------------------------------------------


def test_claim_remedy_table_for_the_standard_world():
    t = ev.remedy_table(ev.Settings())               # psi = 10 %, delta = 30 %
    rows = {r["name"]: r for r in t["rows"]}
    assert rows[ev.REMEDY_NAMES[0]]["eff"] == pytest.approx(0.75, abs=1e-6)
    assert rows[ev.REMEDY_NAMES[1]]["eff"] == pytest.approx(0.9375, abs=1e-6)
    assert rows[ev.REMEDY_NAMES[2]]["eff"] == pytest.approx(0.84375, abs=1e-6)
    assert rows[ev.REMEDY_NAMES[3]]["eff"] == pytest.approx(0.84375, abs=1e-6)
    assert rows[ev.REMEDY_NAMES[4]]["eff"] == pytest.approx(0.8460937, abs=1e-5)
    assert rows[ev.REMEDY_NAMES[5]]["eff"] == pytest.approx(0.75, abs=1e-6)
    assert [rows[n]["better"] for n in ev.REMEDY_NAMES] == [0, 9, 6, 6, 9, 0]
    assert t["threshold"] == pytest.approx(0.5, abs=1e-5)


def test_claim_remedy_counts_with_a_high_delta():
    t = ev.remedy_table(ev.Settings(delta=80))
    assert [r["better"] for r in t["rows"]][5] == 3          # Wiederholung hält in 3 von 9 Zellen (theta = 1/2, alle drei gamma)
    assert t["rows"][5]["eff"] == pytest.approx(1.0)


def test_claim_ownership_helps_the_disadvantaged_side_more_than_the_advantaged_one():
    """theta = 0,8 (V stark): Eigentum nur für S hebt den Wirkungsgrad von 66 % auf 90 %, nur für V auf 67,5 %."""
    base = ev.Settings(theta=80).base_params()
    own_v = eff(replace(base, lam_v=0.5))
    own_s = eff(replace(base, lam_s=0.5))
    assert own_s == pytest.approx(0.9, abs=1e-5) and own_v == pytest.approx(0.675, abs=1e-5)


def test_claim_symmetric_ownership_matches_the_own_return_formula():
    assert eff(Params(lam_v=0.5, lam_s=0.5)) == pytest.approx(0.9375, abs=1e-6)
    assert eff(Params(lam_v=0.5, lam_s=0.5)) == pytest.approx(A.own_return_efficiency_formula(0.75), abs=1e-6)
    assert eff(Params(lam_v=1.0, lam_s=1.0)) == pytest.approx(1.0, abs=1e-6)


def test_claim_contract_optimum_and_the_cost_of_a_full_contract():
    rows = {round(r["phi"], 1): r["eff"] for r in ev.contract_curve(ev.Settings())}      # psi = 10 %
    best = max(rows, key=rows.get)
    assert best == 0.6 and rows[0.6] == pytest.approx(0.8482560, abs=1e-5)
    assert rows[1.0] == pytest.approx(0.81, abs=1e-6) and rows[0.0] == pytest.approx(0.75, abs=1e-6)
    assert rows[0.5] == pytest.approx(0.8460937, abs=1e-5)


def test_claim_contract_without_loss_is_efficient_and_with_half_loss_it_hurts():
    assert eff(Params(phi=1.0, psi=0.0)) == pytest.approx(1.0, abs=1e-6)
    assert eff(Params(phi=1.0, psi=0.5)) == pytest.approx(0.25, abs=1e-6)
    assert eff(Params(phi=1.0, psi=0.5)) < eff(Params())


# --- Befund 4: Wiederholung -----------------------------------------------------------------------------------------------------------


def test_claim_grim_trigger_threshold_half_in_the_standard_world():
    p = Params()
    rep = A.analyse_repeated(p, A.analyse_investment(p))
    assert rep.threshold == pytest.approx(0.5, abs=1e-5)
    assert rep.reward == pytest.approx((0.5, 0.5)) and rep.temptation == pytest.approx((0.625, 0.625), abs=1e-6) and rep.punishment == pytest.approx((0.375, 0.375), abs=1e-6)


def test_claim_threshold_falls_with_complementarity_at_an_equal_split():
    expected = {0.0: 0.5, 0.25: 0.4801, 0.5: 0.4626, 0.75: 0.4468, 1.0: 0.4325}
    values = []
    for g in expected:
        p = Params(gamma=g)
        values.append(A.analyse_repeated(p, A.analyse_investment(p)).threshold)
    assert values == pytest.approx(list(expected.values()), abs=2e-4)
    assert all(x > y for x, y in zip(values, values[1:]))


def test_claim_no_threshold_when_a_side_is_worse_off_cooperating():
    for p in (Params(theta=0.8), Params(lam_v=0.6)):
        rep = A.analyse_repeated(p, A.analyse_investment(p))
        assert math.isinf(rep.thresholds[1]) and math.isinf(rep.threshold), p
        assert rep.reward[1] < rep.punishment[1]


def test_claim_repeated_efficiency_depends_on_delta_against_the_threshold():
    a = ev.analyse(ev.Settings(delta=80))
    assert a.rep_efficiency == pytest.approx(1.0) and a.res.efficiency == pytest.approx(0.75, abs=1e-6)
    b = ev.analyse(ev.Settings(delta=30))
    assert b.rep_efficiency == pytest.approx(0.75, abs=1e-6)


# --- Befund 5: Verfahren ------------------------------------------------------------------------------------------------------------------


def test_claim_procedures():
    rows = {r["label"]: r for r in ev.procedure_rows(ev.Settings())}
    assert len(rows) == 7
    nash = rows["Nash-Verhandlung, hälftig"]
    assert nash["theta"] == 0.5 and nash["eff"] == pytest.approx(0.75, abs=1e-6)
    r9 = rows["Abwechselnde Angebote, V beginnt, δ = 0,90"]
    assert r9["theta"] == pytest.approx(0.1 / 0.19) and r9["eff"] == pytest.approx(0.7493, abs=1e-4)
    r5 = rows["Abwechselnde Angebote, V beginnt, δ = 0,50"]
    assert r5["theta"] == pytest.approx(2 / 3) and r5["eff"] == pytest.approx(0.7222, abs=1e-4)
    r99 = rows["Abwechselnde Angebote, V beginnt, δ = 0,99"]
    assert r99["eff"] == pytest.approx(0.75, abs=1e-4)
    assert rows["Ultimatum von V"]["eff"] == pytest.approx(0.5, abs=1e-6) and rows["Ultimatum von S"]["eff"] == pytest.approx(0.5, abs=1e-6)


# --- Befund 6: Kostenfaktor und Modellgrenzen ---------------------------------------------------------------------------------------------


def test_claim_cost_factor_leaves_efficiency_unchanged_on_a_raster_of_worlds():
    worst = 0.0
    for th, g, a, lam, phi in itertools.product((0.2, 0.8), (0.0, 0.7), (0.5, 2.0), (0.0, 0.5), (0.0, 0.5)):
        base = Params(theta=th, gamma=g, a=a, lam_v=lam, phi=phi, psi=0.1)
        e1 = eff(base)
        for kappa in (0.5, 2.0):
            worst = max(worst, abs(eff(replace(base, kappa=kappa)) - e1))
    assert worst < 1e-5


def test_claim_raster_sizes_and_bounds_named_in_the_texts():
    assert C.X_MAX == 6.0
    assert len(C.REMEDY_THETAS) * len(C.REMEDY_GAMMAS) == 9
    assert len(C.MULTI_THETAS) * len(C.MULTI_GAMMAS) == 25
    assert len(C.THETA_SWEEP) == 11 and C.IMPROVE_PP == 5.0
    assert (C.REMEDY_LAMBDA, C.REMEDY_PHI) == (0.5, 0.5)
    assert C.DELTA_PCT[2] == 30 and C.PSI_PCT[2] == 10
    assert C.RUBINSTEIN_DELTAS == (0.5, 0.9, 0.99)


def test_claim_the_hand_example_numbers_of_the_app_table():
    """Beispielrechnungen der App-Tabelle „Benannte Regeln und Verfahren“."""
    from hup_scenario import payoffs
    uv, us = payoffs(1.0, 1.0, Params())
    assert (float(uv), float(us)) == pytest.approx((0.5, 0.5))
    assert float(payoffs(0.5, 1.0, Params())[0]) == pytest.approx(0.625)
    assert float(payoffs(1.0, 1.0, Params(lam_v=0.6))[0] + 0.5) == pytest.approx(1.3)          # V vor Kosten: 0,6 + 0,7
    p = Params(phi=0.5, psi=0.1)
    uv, us = payoffs(1.0, 1.0, p)
    assert float(uv + 0.5) == pytest.approx(0.95) and float(uv + us) == pytest.approx(0.9)     # 1,9 - 1,0 Kosten
    assert A.analyse_investment(Params(lam_v=0.6)).eq[0] == pytest.approx(0.8, abs=1e-5)         # Grenzanteil 0,5 -> 0,8
    assert A.rubinstein_share_first(0.9, 0.9) == pytest.approx(0.526, abs=5e-4)
