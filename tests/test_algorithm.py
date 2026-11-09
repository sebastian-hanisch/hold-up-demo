"""Einheiten des Kerns gegen Handrechnung (Mini-Welt aus conftest.py), je Regel eine Aussage."""

import math
from dataclasses import replace

import numpy as np
import pytest

import hup_algorithm as A
import hup_scenario as S
from hup_scenario import Params


# --- Überschuss und Verhandlung -------------------------------------------------------------------------------------------------------------


def test_surplus_additive_is_the_sum_of_contributions():
    assert float(S.gross_surplus(1.0, 1.0, 0.0, 1.0)) == pytest.approx(2.0)
    assert float(S.gross_surplus(0.5, 1.0, 0.0, 2.0)) == pytest.approx(2.0)   # A = 2 * 0,5 = 1, B = 1


def test_surplus_complementary_is_twice_the_geometric_mean():
    assert float(S.gross_surplus(4.0, 1.0, 1.0, 1.0)) == pytest.approx(4.0)   # 2 * sqrt(4 * 1)
    assert float(S.gross_surplus(0.0, 3.0, 1.0, 1.0)) == pytest.approx(0.0)   # ohne den Partner nichts


def test_surplus_mixture_by_hand():
    # gamma = 1/2, A = 4, B = 1: 0,5 * 5 + 2 * 0,5 * 2 = 4,5
    assert float(S.gross_surplus(4.0, 1.0, 0.5, 1.0)) == pytest.approx(4.5)


def test_nash_bargain_splits_the_rest_after_the_outside_options():
    uv, us = S.nash_bargain(2.0, 0.5, 0.3, 0.5)    # Rest 1,2: je 0,6
    assert float(uv) == pytest.approx(1.1) and float(us) == pytest.approx(0.9)
    uv, us = S.nash_bargain(2.0, 0.0, 0.0, 0.75)
    assert float(uv) == pytest.approx(1.5) and float(us) == pytest.approx(0.5)


def test_nash_bargain_with_outside_options_above_the_pie_stays_inside_the_pie():
    uv, us = S.nash_bargain(1.0, 0.75, 0.75, 0.5)  # Außenoptionen 1,5 > 1: im Verhältnis verteilt
    assert float(uv) == pytest.approx(0.5) and float(us) == pytest.approx(0.5)
    uv, us = S.nash_bargain(1.0, 0.9, 0.3, 0.5)
    assert float(uv + us) == pytest.approx(1.0) and float(uv) == pytest.approx(0.75)


def test_payoffs_of_the_mini_world_by_hand(mini):
    uv, us = S.payoffs(1.0, 1.0, mini)
    assert (float(uv), float(us)) == pytest.approx((0.5, 0.5))
    uv, us = S.payoffs(0.5, 1.0, mini)             # Überschuss 1,5: V 0,75 - 0,125, S 0,75 - 0,5
    assert (float(uv), float(us)) == pytest.approx((0.625, 0.25))


def test_ownership_raises_the_investors_payoff_by_hand():
    p = Params(lam_v=0.6)
    uv, us = S.payoffs(1.0, 1.0, p)                # V: 0,6 + 0,5 * 1,4 - 0,5 = 0,8; S: 0,7 - 0,5 = 0,2
    assert (float(uv), float(us)) == pytest.approx((0.8, 0.2))


def test_contract_by_hand():
    p = Params(phi=0.5, psi=0.1)
    uv, us = S.payoffs(1.0, 1.0, p)                # Überschuss 1,9; zugesagt 0,95 (je 0,475), Rest 0,95 (je 0,475): 0,95 - 0,5
    assert (float(uv), float(us)) == pytest.approx((0.45, 0.45))


def test_contract_shares_follow_the_contributions():
    p = Params(phi=1.0)
    uv, us = S.payoffs(1.0, 3.0, p)                # alles zugesagt, im Verhältnis 1 : 3 von 4
    assert float(uv) == pytest.approx(1.0 - 0.5) and float(us) == pytest.approx(3.0 - 4.5)


def test_payoffs_without_any_contribution_do_not_divide_by_zero():
    uv, us = S.payoffs(0.0, 0.0, Params(phi=0.5, lam_v=0.5))
    assert float(uv) == 0.0 and float(us) == 0.0


def test_net_value_is_the_sum_and_never_exceeds_the_surplus_minus_costs():
    for p in (Params(), Params(lam_v=1.0, lam_s=1.0, phi=0.5), Params(gamma=1.0, lam_v=0.9, a=2.0)):
        for xv, xs in ((0.3, 1.2), (1.0, 1.0), (2.0, 0.1)):
            uv, us = S.payoffs(xv, xs, p)
            cost = p.kappa * (xv**2 + xs**2) / 2
            pot = (1 - p.psi * p.phi) * float(S.gross_surplus(xv, xs, p.gamma, p.a))
            assert float(uv + us) == pytest.approx(pot - cost)


# --- Reaktionen und Gleichgewichte ------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("theta", [0.0, 0.3, 0.5, 0.8, 1.0])
def test_best_response_additive_is_the_marginal_share_over_kappa(theta):
    p = Params(theta=theta, kappa=2.0, a=1.5)
    assert float(A.best_response_v(np.array([0.7]), p)[0]) == pytest.approx(theta * 1.5 / 2.0, abs=1e-5)
    assert float(A.best_response_s(np.array([0.7]), p)[0]) == pytest.approx((1 - theta) / 2.0, abs=1e-5)


def test_equilibrium_of_the_mini_world_is_half_the_efficient_investment(mini):
    res = A.analyse_investment(mini)
    assert len(res.equilibria) == 1 and res.equilibria[0] == pytest.approx((0.5, 0.5), abs=1e-5)
    assert res.fb == pytest.approx((1.0, 1.0))
    assert res.efficiency == pytest.approx(0.75, abs=1e-6)
    assert res.net == pytest.approx(0.75, abs=1e-6) and res.fb_net == pytest.approx(1.0)


def test_unequal_split_gives_unequal_investments():
    res = A.analyse_investment(Params(theta=0.8))
    assert res.eq == pytest.approx((0.8, 0.2), abs=1e-5)
    assert res.efficiency == pytest.approx(0.66, abs=1e-6)


def test_complementarity_one_has_the_no_investment_equilibrium_and_the_interior_one():
    res = A.analyse_investment(Params(gamma=1.0))
    assert len(res.equilibria) == 2
    assert res.equilibria[0] == pytest.approx((0.0, 0.0), abs=1e-9)
    assert res.equilibria[1] == pytest.approx((0.5, 0.5), abs=1e-5)
    assert res.eq == pytest.approx((0.5, 0.5), abs=1e-5)           # gewählt: das mit den höchsten Investitionen
    assert res.efficiency_worst == pytest.approx(0.0, abs=1e-9)


def test_is_equilibrium_rejects_the_efficient_point_and_accepts_the_equilibrium(mini):
    assert A.is_equilibrium(0.5, 0.5, mini)
    assert not A.is_equilibrium(1.0, 1.0, mini)
    assert not A.is_equilibrium(0.5, 1.0, mini)


def test_first_best_closed_forms():
    assert A.first_best(0.0, 2.0, 0.5) == pytest.approx((4.0, 2.0))
    assert A.first_best(1.0, 1.0, 1.0) == pytest.approx((1.0, 1.0))
    xv, xs = A.first_best(1.0, 2.0, 1.0)            # r = a^(-1/2): x_V = a r / kappa = sqrt(2), x_S = 1 / (kappa r) = sqrt(2)
    assert xv == pytest.approx(math.sqrt(2.0)) and xs == pytest.approx(math.sqrt(2.0))


def test_efficiency_never_exceeds_one_in_a_world_with_every_remedy():
    p = Params(theta=0.4, gamma=0.5, a=1.5, lam_v=0.9, lam_s=0.9, phi=0.9, psi=0.1)
    assert A.analyse_investment(p).efficiency <= 1.0 + 1e-9


def test_each_remedy_changes_the_result_on_at_least_one_world():
    """Zweig-Test: jede Einheit mit Wirkung weicht auf mindestens einer Welt von der Basis ab (keine tote Variante)."""
    base = A.analyse_investment(Params()).efficiency
    for variant in (Params(lam_v=0.5), Params(lam_s=0.5), Params(phi=0.5, psi=0.1), Params(gamma=0.5, theta=0.8), Params(a=2.0, theta=0.8)):
        assert abs(A.analyse_investment(variant).efficiency - base) > 1e-3, variant


def test_additive_closed_form_matches_the_numbers_by_hand():
    assert A.additive_efficiency_formula(0.5) == pytest.approx(0.75)
    assert A.additive_efficiency_formula(0.8) == pytest.approx(0.66)
    assert A.own_return_efficiency_formula(0.5) == pytest.approx(0.75)
    assert A.own_return_efficiency_formula(1.0) == pytest.approx(1.0)
    assert A.additive_equilibrium_formula(Params(lam_v=0.6)) == pytest.approx((0.8, 0.5))


def test_side_losses_of_the_mini_world_and_of_a_productive_v():
    lv, ls = A.side_losses(Params(), A.first_best(0.0, 1.0, 1.0))
    assert (lv, ls) == pytest.approx((0.125, 0.125), abs=1e-6)       # (1 - 1/2)^2 / 2 je Seite
    p = Params(a=2.0)
    lv, ls = A.side_losses(p, A.first_best(0.0, 2.0, 1.0))           # a^2 (1 - theta)^2 / (2 kappa) = 0,5 und 0,125
    assert (lv, ls) == pytest.approx((0.5, 0.125), abs=1e-6)


# --- Wiederholung -------------------------------------------------------------------------------------------------------------------------


def test_grim_trigger_threshold_by_hand():
    assert A.grim_trigger_threshold(0.5, 0.625, 0.375) == pytest.approx(0.5)     # (0,625 - 0,5) / (0,625 - 0,375)
    assert A.grim_trigger_threshold(0.5, 0.5, 0.375) == 0.0                      # keine Verführung
    assert A.grim_trigger_threshold(0.5, 0.6, 0.55) == math.inf                  # in der Zusammenarbeit schlechter als in der Strafphase


def test_repeated_game_of_the_mini_world(mini):
    res = A.analyse_investment(mini)
    rep = A.analyse_repeated(mini, res)
    assert rep.reward == pytest.approx((0.5, 0.5)) and rep.temptation == pytest.approx((0.625, 0.625), abs=1e-6)
    assert rep.punishment == pytest.approx((0.375, 0.375), abs=1e-6)
    assert rep.threshold == pytest.approx(0.5, abs=1e-5)
    assert A.repeated_efficiency(mini, res, rep, 0.5) == pytest.approx(1.0)
    assert A.repeated_efficiency(mini, res, rep, 0.49) == pytest.approx(0.75, abs=1e-6)


def test_repeated_game_without_threshold_when_a_side_is_worse_off_cooperating():
    p = Params(theta=0.8)
    res = A.analyse_investment(p)
    rep = A.analyse_repeated(p, res)
    assert math.isinf(rep.thresholds[1]) and math.isinf(rep.threshold)         # S: -0,1 bei effizienter Investition gegen 0,18 im Einmalspiel
    assert A.repeated_efficiency(p, res, rep, 0.99) == pytest.approx(res.efficiency)


# --- Verhandlungsverfahren -----------------------------------------------------------------------------------------------------------------


def test_rubinstein_shares_by_hand():
    assert A.rubinstein_share_first(0.9, 0.9) == pytest.approx(0.1 / 0.19)
    assert A.rubinstein_share_first(0.5, 0.5) == pytest.approx(2 / 3)
    assert A.rubinstein_share_first(0.9, 0.0) == pytest.approx(1.0)               # ohne Geduld des Zweiten bekommt der Erste alles


def test_procedure_shares():
    assert A.procedure_share_v("nash") == 0.5
    assert A.procedure_share_v("rubinstein_v", 0.9) + A.procedure_share_v("rubinstein_s", 0.9) == pytest.approx(1.0)
    assert A.procedure_share_v("ultimatum_v") == 1.0 and A.procedure_share_v("ultimatum_s") == 0.0
    with pytest.raises(ValueError):
        A.procedure_share_v("unbekannt")


def test_params_without_remedies_keeps_the_world():
    p = replace(Params(theta=0.3, gamma=0.4, a=1.2, kappa=0.8), lam_v=0.5, lam_s=0.4, phi=0.3, psi=0.2)
    q = p.without_remedies()
    assert (q.theta, q.gamma, q.a, q.kappa, q.psi) == (0.3, 0.4, 1.2, 0.8, 0.2)
    assert (q.lam_v, q.lam_s, q.phi) == (0.0, 0.0, 0.0)
