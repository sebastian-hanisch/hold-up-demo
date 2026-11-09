"""Kern (nur numpy): Reaktionen, Gleichgewichte der Investitionen, First-Best, Wirkungsgrad, Wiederholung und Rubinstein-Verhandlung.

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK 1b). `analyse_investment` ruft nur der Reihe nach auf."""

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

import hup_constants as C
from hup_scenario import Params, net_value, payoffs, welfare

_INV_PHI = (math.sqrt(5.0) - 1.0) / 2.0


# --- Einheit 1: Reaktion einer Seite --------------------------------------------------------------------------------------------------------


def maximize_1d(fun, m: int, lo: float = 0.0, hi: float = C.X_MAX, n: int = C.N_BR_GRID):
    """Maximiert für m Fälle zugleich eine Funktion einer Variablen auf [lo, hi]: Gitter, dann Goldener Schnitt um den besten Gitterpunkt.

    `fun(x)` bekommt ein Array der Form (m, k) und liefert die Werte derselben Form (oder broadcastbar). Gibt (x*, f(x*)) zurück."""
    grid = np.linspace(lo, hi, n)
    vals = np.broadcast_to(np.asarray(fun(grid[None, :]), dtype=float), (m, n))
    best = np.argmax(vals, axis=1)
    grid_val = vals[np.arange(m), best]
    left = grid[np.maximum(best - 1, 0)].copy()
    right = grid[np.minimum(best + 1, n - 1)].copy()
    c = right - _INV_PHI * (right - left)
    d = left + _INV_PHI * (right - left)
    fc = np.broadcast_to(np.asarray(fun(c[:, None]), dtype=float), (m, 1))[:, 0]
    fd = np.broadcast_to(np.asarray(fun(d[:, None]), dtype=float), (m, 1))[:, 0]
    for _ in range(C.GOLDEN_STEPS):
        go_left = fc > fd   # das Maximum liegt in [left, d]
        right = np.where(go_left, d, right)
        left = np.where(go_left, left, c)
        x_new = np.where(go_left, right - _INV_PHI * (right - left), left + _INV_PHI * (right - left))
        f_new = np.broadcast_to(np.asarray(fun(x_new[:, None]), dtype=float), (m, 1))[:, 0]
        c_next = np.where(go_left, x_new, d)
        d_next = np.where(go_left, c, x_new)
        fc_next = np.where(go_left, f_new, fd)
        fd_next = np.where(go_left, fc, f_new)
        c, d, fc, fd = c_next, d_next, fc_next, fd_next
    x_gold = (left + right) / 2.0
    f_gold = np.broadcast_to(np.asarray(fun(x_gold[:, None]), dtype=float), (m, 1))[:, 0]
    use_gold = f_gold >= grid_val
    x_best = np.where(use_gold, x_gold, grid[best])
    return x_best, np.where(use_gold, f_gold, grid_val)


def best_response_v(xs, p: Params):
    """Beste Investition von V gegen die Investitionen `xs` von S (Array, ein Wert je Fall)."""
    xs = np.atleast_1d(np.asarray(xs, dtype=float))
    return maximize_1d(lambda x: payoffs(x, xs[:, None], p)[0], len(xs))[0]


def best_response_s(xv, p: Params):
    """Beste Investition von S gegen die Investitionen `xv` von V."""
    xv = np.atleast_1d(np.asarray(xv, dtype=float))
    return maximize_1d(lambda x: payoffs(xv[:, None], x, p)[1], len(xv))[0]


# --- Einheit 2: Gleichgewichte der Investitionen -----------------------------------------------------------------------------------------


def _fixed_point_gap(xv, p: Params):
    """V-Investition, auf die sich die doppelte Reaktion (S antwortet auf V, V auf S) abbildet, minus der Ausgangswert."""
    return best_response_v(best_response_s(xv, p), p) - xv


def is_equilibrium(xv: float, xs: float, p: Params, tol: float = C.EQ_TOL) -> bool:
    """Keine Seite gewinnt mehr als `tol` durch eine einseitige Abweichung (Gitter und Goldener Schnitt über alle Investitionen)."""
    uv, us = payoffs(xv, xs, p)
    _, best_v = maximize_1d(lambda x: payoffs(x, np.array([[xs]]), p)[0], 1)
    _, best_s = maximize_1d(lambda x: payoffs(np.array([[xv]]), x, p)[1], 1)
    return bool(best_v[0] - float(uv) <= tol and best_s[0] - float(us) <= tol)


def find_equilibria(p: Params, n: int = C.N_EQ_GRID) -> list[tuple[float, float]]:
    """Alle reinen Gleichgewichte der Investitionen (x_V, x_S), aufsteigend nach x_V.

    Ein Gleichgewicht ist ein Fixpunkt der doppelten Reaktion. Gesucht werden Nullstellen von `_fixed_point_gap` auf einem Gitter
    (Vorzeichenwechsel, dann Bisektion), jeder Kandidat wird durch die Abweichungsprobe `is_equilibrium` bestätigt."""
    grid = np.linspace(0.0, C.X_MAX, n)
    gap = _fixed_point_gap(grid, p)
    candidates = [float(grid[i]) for i in range(n) if abs(gap[i]) < 1e-9]
    flips = np.where(np.sign(gap[:-1]) * np.sign(gap[1:]) < 0)[0]
    if len(flips):
        lo, hi = grid[flips].copy(), grid[flips + 1].copy()
        g_lo, g_hi = gap[flips], gap[flips + 1]
        for _ in range(C.BISECT_STEPS):
            mid = (lo + hi) / 2.0
            g_mid = _fixed_point_gap(mid, p)
            same = np.sign(g_mid) == np.sign(g_lo)
            lo = np.where(same, mid, lo)
            hi = np.where(same, hi, mid)
            g_lo = np.where(same, g_mid, g_lo)
            g_hi = np.where(same, g_hi, g_mid)
        spread = g_lo - g_hi
        step = np.where(np.abs(spread) > 0, g_lo / np.where(np.abs(spread) > 0, spread, 1.0), 0.5)
        candidates.extend(float(v) for v in lo + np.clip(step, 0.0, 1.0) * (hi - lo))
    found: list[tuple[float, float]] = []
    for xv in sorted(candidates):
        xs = float(best_response_s(np.array([xv]), p)[0])
        if not is_equilibrium(xv, xs, p):
            continue
        if any(abs(xv - fv) < C.EQ_DEDUP and abs(xs - fs) < C.EQ_DEDUP for fv, fs in found):
            continue
        found.append((xv, xs))
    return found


# --- Einheit 3: First-Best -------------------------------------------------------------------------------------------------------------


def first_best(gamma: float, a: float, kappa: float) -> tuple[float, float]:
    """Gemeinsam beste Investitionen (x_V, x_S) ohne Gegenmittel.

    Bedingungen erster Ordnung: kappa * x_V = a * ((1 - gamma) + gamma * r) und kappa * x_S = (1 - gamma) + gamma / r mit r = sqrt(B / A).
    Eingesetzt in r^2 = x_S / (a * x_V) bleibt eine Gleichung in r, deren linke Seite in r wächst: eine Nullstelle, per Bisektion."""
    if gamma <= 0.0:
        return a / kappa, 1.0 / kappa

    def g(r: float) -> float:
        return a * a * r * r * ((1.0 - gamma) + gamma * r) - ((1.0 - gamma) + gamma / r)

    lo, hi = 1e-6, 1e6
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if g(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    r = math.sqrt(lo * hi)
    return (a / kappa) * ((1.0 - gamma) + gamma * r), (1.0 / kappa) * ((1.0 - gamma) + gamma / r)


@lru_cache(maxsize=512)
def first_best_net(gamma: float, a: float, kappa: float) -> float:
    xv, xs = first_best(gamma, a, kappa)
    return float(welfare(xv, xs, gamma, a, kappa))


# --- Einheit 4: Wirkungsgrad und Auswertung eines Szenarios ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class InvestmentResult:
    p: Params
    fb: tuple[float, float]           # First-Best (x_V, x_S)
    fb_net: float                     # Netto im First-Best (ohne Gegenmittel)
    equilibria: tuple[tuple[float, float], ...]
    eq: tuple[float, float]           # gewähltes Gleichgewicht: das mit den höchsten Investitionen
    net: float                        # Netto im gewählten Gleichgewicht
    efficiency: float                 # net / fb_net
    efficiency_worst: float           # Wirkungsgrad des schlechtesten Gleichgewichts
    found: bool = True                # False: auf dem Raster kein reines Gleichgewicht gefunden; eq ist dann nur ein Platzhalter (0; 0)


def efficiency_of(p: Params, xv: float, xs: float) -> float:
    """Wirkungsgrad: Netto bei den Investitionen (x_V, x_S) durch Netto im First-Best."""
    return float(net_value(xv, xs, p)) / first_best_net(p.gamma, p.a, p.kappa)


@lru_cache(maxsize=4096)
def analyse_investment(p: Params) -> InvestmentResult:
    """Ein Szenario: First-Best, alle Gleichgewichte, das größte davon und sein Wirkungsgrad."""
    fb = first_best(p.gamma, p.a, p.kappa)
    eqs = find_equilibria(p)
    fb_net = first_best_net(p.gamma, p.a, p.kappa)
    if not eqs:   # Randfall (z. B. springende Reaktion von S): kein reines Gleichgewicht; (0; 0) ist nur Platzhalter und wird nicht als Gleichgewicht gemeldet
        eff0 = efficiency_of(p, 0.0, 0.0)
        return InvestmentResult(p, fb, fb_net, (), (0.0, 0.0), eff0 * fb_net, eff0, eff0, found=False)
    chosen = max(eqs, key=lambda e: (e[0] + e[1], e[0]))
    effs = [efficiency_of(p, *e) for e in eqs]
    eff = effs[eqs.index(chosen)]
    return InvestmentResult(p, fb, fb_net, tuple(eqs), chosen, eff * fb_net, eff, min(effs))


def additive_efficiency_formula(theta: float) -> float:
    """Geschlossene Formel (additiv, a = kappa = 1, keine Gegenmittel): 1 - (theta^2 + (1 - theta)^2) / 2."""
    return 1.0 - (theta**2 + (1.0 - theta) ** 2) / 2.0


def own_return_efficiency_formula(share: float) -> float:
    """Behält jede Seite den Anteil `share` der Rendite der eigenen Investition (additiv, a = kappa = 1): 1 - (1 - share)^2."""
    return 1.0 - (1.0 - share) ** 2


def additive_equilibrium_formula(p: Params) -> tuple[float, float]:
    """Gleichgewicht im additiven Modell (gamma = 0), geschlossen: kappa * x_i = Grenzanteil m_i an der eigenen Rendite.

    m_V = a * (s * (phi + theta * (1 - phi)) + (1 - theta) * lam_v), m_S = s * (phi + (1 - theta) * (1 - phi)) + theta * lam_s mit s = 1 - psi * phi.
    Gilt, solange der verhandelte Rest die Außenoptionen deckt: (1 - phi) * s >= lam_v und >= lam_s."""
    s = 1.0 - p.psi * p.phi
    m_v = p.a * (s * (p.phi + p.theta * (1.0 - p.phi)) + (1.0 - p.theta) * p.lam_v)
    m_s = s * (p.phi + (1.0 - p.theta) * (1.0 - p.phi)) + p.theta * p.lam_s
    return m_v / p.kappa, m_s / p.kappa


def side_losses(p: Params, fb: tuple[float, float]) -> tuple[float, float]:
    """Verlust je Seite: wie viel gemeinsames Netto fehlt, wenn nur diese Seite statt effizient auf ihrem Gleichgewichtsniveau investiert.

    Maßstab ist das Netto ohne Gegenmittel (W); `eq` kommt aus dem gewählten Gleichgewicht."""
    res = analyse_investment(p)
    fb_net = first_best_net(p.gamma, p.a, p.kappa)
    loss_v = fb_net - float(welfare(res.eq[0], fb[1], p.gamma, p.a, p.kappa))
    loss_s = fb_net - float(welfare(fb[0], res.eq[1], p.gamma, p.a, p.kappa))
    return loss_v, loss_s


# --- Einheit 5: Wiederholung (Grim-Trigger) -------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RepeatedResult:
    reward: tuple[float, float]      # Auszahlung je Seite bei effizienter Investition beider
    temptation: tuple[float, float]  # beste einseitige Abweichung
    punishment: tuple[float, float]  # Auszahlung im Gleichgewicht des Einmalspiels (Strafphase)
    thresholds: tuple[float, float]  # Schwelle des Diskontfaktors je Seite (inf: nie)
    threshold: float                 # größte der beiden, inf wenn eine Seite nie mitmacht


def grim_trigger_threshold(reward: float, temptation: float, punishment: float) -> float:
    """Kleinster Diskontfaktor, ab dem Grim-Trigger die Zusammenarbeit hält: (T - R) / (T - P).

    Gewinnt die Seite durch Abweichen nichts (T <= R), reicht jeder Diskontfaktor (0). Steht sie in der Zusammenarbeit schlechter
    als in der Strafphase (R < P), gibt es keinen (inf)."""
    if temptation <= reward + 1e-12:
        return 0.0
    if reward < punishment - 1e-12:
        return math.inf
    return (temptation - reward) / (temptation - punishment)


def analyse_repeated(p: Params, res: InvestmentResult) -> RepeatedResult:
    """Spiel mit zwei Handlungen je Periode: effizient investieren (First-Best) oder nicht. Strafphase: das Gleichgewicht des Einmalspiels."""
    xv_fb, xs_fb = res.fb
    ru, rs = (float(v) for v in payoffs(xv_fb, xs_fb, p))
    dev_v = float(best_response_v(np.array([xs_fb]), p)[0])
    dev_s = float(best_response_s(np.array([xv_fb]), p)[0])
    tv = float(payoffs(dev_v, xs_fb, p)[0])
    ts = float(payoffs(xv_fb, dev_s, p)[1])
    pv, ps = (float(v) for v in payoffs(*res.eq, p))
    th = (grim_trigger_threshold(ru, tv, pv), grim_trigger_threshold(rs, ts, ps))
    return RepeatedResult((ru, rs), (tv, ts), (pv, ps), th, max(th))


def repeated_efficiency(p: Params, res: InvestmentResult, rep: RepeatedResult, delta: float) -> float:
    """Wirkungsgrad mit Wiederholung: hält die Zusammenarbeit (delta >= Schwelle), gilt das Netto bei effizienter Investition, sonst das des Einmalspiels."""
    if delta >= rep.threshold:
        return efficiency_of(p, *res.fb)
    return res.efficiency


# --- Einheit 6: Verhandlungsverfahren (Rubinstein) --------------------------------------------------------------------------------------------


def rubinstein_share_first(delta_first: float, delta_second: float) -> float:
    """Anteil des Ersten bei abwechselnden Angeboten mit Diskontfaktoren je Runde: (1 - delta_second) / (1 - delta_first * delta_second)."""
    return (1.0 - delta_second) / (1.0 - delta_first * delta_second)


def procedure_share_v(procedure: str, delta: float = 0.9) -> float:
    """Anteil von V, den ein Verfahren zuweist: `nash` (hälftig), `rubinstein_v` (V bietet zuerst), `rubinstein_s`, `ultimatum_v`, `ultimatum_s`."""
    if procedure == "nash":
        return 0.5
    if procedure == "rubinstein_v":
        return rubinstein_share_first(delta, delta)
    if procedure == "rubinstein_s":
        return 1.0 - rubinstein_share_first(delta, delta)
    if procedure == "ultimatum_v":
        return 1.0
    if procedure == "ultimatum_s":
        return 0.0
    raise ValueError(f"unbekanntes Verfahren: {procedure}")
