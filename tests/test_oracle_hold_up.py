"""Orakel-Tests hold-up-demo: jede Kernroutine gegen einen anderen Rechenweg (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2: Spieltheorie).

1. Gleichgewicht der Investitionen gegen Aufzählung auf einem 2D-Gitter (Gitter-Gleichgewichte, Zusammenhangskomponenten) und gegen
   `scipy.optimize.minimize_scalar` (je Seite eine Reaktion auf das gefundene Gleichgewicht).
2. First-Best gegen ein 2D-Gitter und `scipy.optimize.minimize` (BFGS mit `jac="3-point"`, nur als Gegenprobe mit Band).
3. Wirkungsgrad gegen die geschlossene Formel (additiv; ausgeschrieben, ohne die Auszahlungsfunktion der Demo).
4. Nash-Aufteilung gegen Aufzählung über den Aufteilungsanteil (Nash-Produkt).
5. Grim-Trigger-Schwelle gegen Wertiteration auf dem Spiel mit Abweichung.
6. Rubinstein-Anteil gegen Rückwärtsrechnung über einen langen endlichen Horizont.

Handbeispiel vorab (siehe conftest.py): Mini-Welt, Gleichgewicht (1/2, 1/2), Wirkungsgrad 3/4, Schwelle 1/2. Der große Lauf mit 300 Zufallswelten (alle
Gleichgewichte durch scipy bestätigt, kein Wirkungsgrad über 1, First-Best gegen 2D-Gitter) lief im Scratch-Ordner, nicht im Repo.
Das Orakel für Gegenmittel und Komplementarität nutzt dieselben Auszahlungen wie die Demo (die Modelldefinition steht in hup_scenario.py);
der Test prüft die Suche, nicht die Definition: die Definition prüfen die Handrechnungen in test_algorithm.py."""

import math

import numpy as np
import pytest

import hup_algorithm as A
from hup_scenario import Params, nash_bargain, payoffs, welfare

scipy_optimize = pytest.importorskip("scipy.optimize")
scipy_ndimage = pytest.importorskip("scipy.ndimage")

WORLDS = [
    Params(),
    Params(theta=0.8),
    Params(theta=0.2, a=1.5),
    Params(gamma=0.5),
    Params(gamma=1.0),
    Params(gamma=0.5, theta=0.7, a=1.3),
    Params(lam_v=0.6),
    Params(lam_v=0.5, lam_s=0.5, gamma=0.5),
    Params(phi=0.5, psi=0.1),
    Params(phi=0.4, psi=0.2, lam_s=0.3, theta=0.6),
    Params(a=2.0, kappa=0.5, theta=0.5),
    Params(kappa=2.0, theta=0.9, gamma=0.8),
]


def _grid_equilibrium_components(p: Params, top: float = 4.0, n: int = 161, eps: float = 5e-4):
    """Aufzählung: alle Gitterzellen, in denen keine Seite durch eine Abweichung auf dem Gitter mehr als eps gewinnt; zusammenhängende Zellen zählen als ein Gleichgewicht."""
    g = np.linspace(0.0, top, n)
    xv, xs = np.meshgrid(g, g, indexing="ij")
    uv, us = payoffs(xv, xs, p)
    gain_v = uv.max(axis=0, keepdims=True) - uv      # Abweichung von V: Spalte (x_S fest) durchlaufen
    gain_s = us.max(axis=1, keepdims=True) - us      # Abweichung von S: Zeile (x_V fest) durchlaufen
    cells = (gain_v <= eps) & (gain_s <= eps)
    labels, count = scipy_ndimage.label(cells, structure=np.ones((3, 3)))
    centers = []
    for k in range(1, count + 1):
        idx = np.argwhere(labels == k)
        centers.append((float(g[idx[:, 0]].mean()), float(g[idx[:, 1]].mean())))
    return g, cells, centers


@pytest.mark.parametrize("p", WORLDS, ids=lambda p: f"th{p.theta}-g{p.gamma}-a{p.a}-k{p.kappa}-l{p.lam_v}{p.lam_s}-f{p.phi}")
def test_equilibria_match_the_grid_enumeration(p):
    res = A.analyse_investment(p)
    g, cells, centers = _grid_equilibrium_components(p, top=max(4.0, 1.3 * max(max(e) for e in res.equilibria)))
    h = g[1] - g[0]
    assert len(centers) == len(res.equilibria), (centers, res.equilibria)
    for xv, xs in res.equilibria:
        assert min(math.hypot(xv - cx, xs - cy) for cx, cy in centers) <= 2.5 * h, (xv, xs, centers)


@pytest.mark.parametrize("p", WORLDS, ids=lambda p: f"th{p.theta}-g{p.gamma}-a{p.a}-k{p.kappa}-l{p.lam_v}{p.lam_s}-f{p.phi}")
def test_every_equilibrium_is_a_best_response_for_scipy(p):
    for xv, xs in A.analyse_investment(p).equilibria:
        best_v = scipy_optimize.minimize_scalar(lambda x: -float(payoffs(x, xs, p)[0]), bounds=(0.0, 6.0), method="bounded", options={"xatol": 1e-10})
        best_s = scipy_optimize.minimize_scalar(lambda x: -float(payoffs(xv, x, p)[1]), bounds=(0.0, 6.0), method="bounded", options={"xatol": 1e-10})
        assert -best_v.fun - float(payoffs(xv, xs, p)[0]) <= 1e-6
        assert -best_s.fun - float(payoffs(xv, xs, p)[1]) <= 1e-6


def test_oracle_itself_on_the_hand_example(mini):
    """Das Orakel an der Mini-Welt: genau ein Gitter-Gleichgewicht, in der Nähe von (1/2, 1/2)."""
    g, cells, centers = _grid_equilibrium_components(mini)
    assert len(centers) == 1 and centers[0] == pytest.approx((0.5, 0.5), abs=0.03)


# --- First-Best ------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("p", WORLDS, ids=lambda p: f"g{p.gamma}-a{p.a}-k{p.kappa}")
def test_first_best_matches_a_grid_and_a_gradient_free_optimizer(p):
    fb = A.first_best(p.gamma, p.a, p.kappa)
    g = np.linspace(0.0, 5.0, 201)
    xv, xs = np.meshgrid(g, g, indexing="ij")
    w = welfare(xv, xs, p.gamma, p.a, p.kappa)
    assert float(welfare(*fb, p.gamma, p.a, p.kappa)) >= w.max() - 1e-12                 # kein Gitterpunkt ist besser
    start = np.array([1.0, 1.0])
    opt = scipy_optimize.minimize(lambda x: -float(welfare(x[0], x[1], p.gamma, p.a, p.kappa)), start, method="BFGS", jac="3-point", options={"gtol": 1e-9})
    assert opt.x == pytest.approx(fb, abs=1e-4)


# --- Wirkungsgrad gegen geschlossene Formel -----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("theta", [i / 10 for i in range(11)])
def test_efficiency_matches_the_closed_formula_symmetric_additive(theta):
    p = Params(theta=theta)
    assert A.analyse_investment(p).efficiency == pytest.approx(1.0 - (theta**2 + (1.0 - theta) ** 2) / 2.0, abs=1e-6)


def _closed_form_efficiency(p: Params) -> float:
    """Additiv (gamma = 0), ausgeschrieben ohne die Auszahlungsfunktion: Grenzanteile, Investitionen, Netto durch Netto im Optimum."""
    s = 1.0 - p.psi * p.phi
    share_v = s * (p.phi + p.theta * (1.0 - p.phi)) + (1.0 - p.theta) * p.lam_v
    share_s = s * (p.phi + (1.0 - p.theta) * (1.0 - p.phi)) + p.theta * p.lam_s
    xv, xs = p.a * share_v / p.kappa, share_s / p.kappa
    net = s * (p.a * xv + xs) - p.kappa * (xv**2 + xs**2) / 2.0
    return net / ((p.a**2 + 1.0) / (2.0 * p.kappa))


@pytest.mark.parametrize("p", [
    Params(theta=0.35, a=1.4, kappa=0.7),
    Params(theta=0.5, lam_v=0.4, lam_s=0.2),
    Params(theta=0.6, phi=0.3, psi=0.15, a=0.8),
    Params(theta=0.2, lam_v=0.2, phi=0.5, psi=0.1, kappa=1.6),
])
def test_efficiency_matches_the_closed_formula_with_remedies(p):
    # Gültigkeit der Formel: der verhandelte Rest deckt die Außenoptionen ((1 - phi) * s >= lam)
    s = 1.0 - p.psi * p.phi
    assert (1 - p.phi) * s >= max(p.lam_v, p.lam_s)
    assert A.analyse_investment(p).efficiency == pytest.approx(_closed_form_efficiency(p), abs=1e-6)


def test_own_return_formula_matches_symmetric_ownership():
    """Symmetrisches Eigentum bei theta = 1/2 gibt jeder Seite den Anteil (1 + lam) / 2 an der eigenen Rendite: 1 - (1 - Anteil)^2."""
    for lam in (0.0, 0.2, 0.5, 1.0):
        p = Params(lam_v=lam, lam_s=lam)
        assert A.analyse_investment(p).efficiency == pytest.approx(A.own_return_efficiency_formula((1 + lam) / 2), abs=1e-6)


# --- Nash-Aufteilung --------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("pie,w_v,w_s,theta", [(2.0, 0.0, 0.0, 0.5), (2.0, 0.5, 0.3, 0.5), (3.0, 1.0, 0.2, 0.8), (1.0, 0.1, 0.6, 0.25), (5.0, 2.0, 2.0, 0.5)])
def test_nash_bargain_matches_the_enumeration_of_the_nash_product(pie, w_v, w_s, theta):
    shares = np.linspace(w_v, pie - w_s, 200001)      # u_V läuft über alle Aufteilungen mit u_V >= w_V und u_S = pie - u_V >= w_S
    product = (shares - w_v) ** theta * (pie - shares - w_s) ** (1.0 - theta)
    best = shares[int(np.argmax(product))]
    uv, us = nash_bargain(pie, w_v, w_s, theta)
    assert float(uv) == pytest.approx(best, abs=2e-5) and float(us) == pytest.approx(pie - best, abs=2e-5)


# --- Wiederholung -------------------------------------------------------------------------------------------------------------------------


def _cooperation_holds(reward: float, temptation: float, punishment: float, delta: float) -> bool:
    """Wertiteration für den Abweichler gegen Grim-Trigger: zwei Zustände (Zusammenarbeit, Strafe), Bellman-Gleichung bis zum Fixpunkt."""
    v_coop, v_pun = 0.0, 0.0
    for _ in range(4000):
        v_pun_new = punishment + delta * v_pun
        v_coop_new = max(reward + delta * v_coop, temptation + delta * v_pun)
        if abs(v_pun_new - v_pun) + abs(v_coop_new - v_coop) < 1e-13:
            v_pun, v_coop = v_pun_new, v_coop_new
            break
        v_pun, v_coop = v_pun_new, v_coop_new
    return reward + delta * v_coop >= temptation + delta * v_pun - 1e-9


def _threshold_by_value_iteration(reward: float, temptation: float, punishment: float) -> float:
    if _cooperation_holds(reward, temptation, punishment, 0.0):
        return 0.0
    lo, hi = 0.0, 0.999
    if not _cooperation_holds(reward, temptation, punishment, hi):
        return math.inf
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if _cooperation_holds(reward, temptation, punishment, mid):
            hi = mid
        else:
            lo = mid
    return hi


@pytest.mark.parametrize("r,t,p", [(0.5, 0.625, 0.375), (1.0, 1.5, 0.2), (0.3, 0.9, 0.1), (2.0, 2.0, 1.0), (1.0, 3.0, 0.9)])
def test_grim_trigger_threshold_matches_value_iteration(r, t, p):
    assert A.grim_trigger_threshold(r, t, p) == pytest.approx(_threshold_by_value_iteration(r, t, p), abs=1e-6)


@pytest.mark.parametrize("p", [Params(), Params(gamma=0.5), Params(gamma=1.0), Params(phi=0.5, psi=0.1), Params(lam_v=0.5, lam_s=0.5)],
                         ids=lambda p: f"g{p.gamma}-f{p.phi}-l{p.lam_v}")
def test_repeated_thresholds_of_the_worlds_match_value_iteration(p):
    res = A.analyse_investment(p)
    rep = A.analyse_repeated(p, res)
    for i in range(2):
        expected = _threshold_by_value_iteration(rep.reward[i], rep.temptation[i], rep.punishment[i])
        assert rep.thresholds[i] == pytest.approx(expected, abs=1e-6) or (math.isinf(expected) and math.isinf(rep.thresholds[i]))


def test_repeated_threshold_of_one_sided_ownership_is_infinite_for_s_in_both_computations():
    p = Params(lam_v=0.6)
    res = A.analyse_investment(p)
    rep = A.analyse_repeated(p, res)
    assert math.isinf(rep.thresholds[1])
    assert math.isinf(_threshold_by_value_iteration(rep.reward[1], rep.temptation[1], rep.punishment[1]))


# --- Rubinstein -------------------------------------------------------------------------------------------------------------------------


def _backward_share(delta_first: float, delta_second: float, rounds: int = 3000) -> float:
    """Rückwärtsrechnung: in der letzten Runde bekommt der Anbietende alles; davor bietet er dem Antwortenden genau dessen abgezinsten Fortsetzungswert."""
    share = 1.0                              # Anteil des Anbietenden der letzten Runde (Index `rounds`)
    proposer_is_first = (rounds % 2 == 1)    # der Erste bietet in den ungeraden Runden
    for _ in range(rounds - 1):
        proposer_is_first = not proposer_is_first               # eine Runde zurück: der andere bietet
        responder_delta = delta_second if proposer_is_first else delta_first
        # der Antwortende wird in der nächsten Runde Anbietender und bekommt `share`, abgezinst mit seinem eigenen Faktor
        share = 1.0 - responder_delta * share
    assert proposer_is_first                                    # Runde 1 gehört dem Ersten
    return share


@pytest.mark.parametrize("d1,d2", [(0.9, 0.9), (0.5, 0.5), (0.7, 0.9), (0.95, 0.6), (0.0, 0.8), (0.3, 0.0)])
def test_rubinstein_matches_backward_induction(d1, d2):
    assert A.rubinstein_share_first(d1, d2) == pytest.approx(_backward_share(d1, d2), abs=1e-9)
