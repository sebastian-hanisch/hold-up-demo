"""Modell des Hold-up: Bruttoüberschuss, Gegenmittel und Auszahlungen (nur numpy; jede Regel eine eigene Funktion).

Verlader V und Spediteur S investieren vor der Verhandlung (x_V, x_S >= 0, Kosten kappa * x^2 / 2 je Seite). Danach wird der
Überschuss nach Nash verhandelt: V bekommt den Anteil theta, S den Anteil 1 - theta.

Bruttoüberschuss mit A = a * x_V und B = x_S (V hat die Produktivität a, S die Produktivität 1):

    S(x_V, x_S) = (1 - gamma) * (A + B) + 2 * gamma * sqrt(A * B)

Das ist 2 mal die Mischung aus arithmetischem (Gewicht 1 - gamma) und geometrischem Mittel (Gewicht gamma) von A und B. Bei gamma = 0
ist der Überschuss additiv, bei gamma = 1 komplementär (ohne den Partner bringt die eigene Investition nichts). Der Überschuss ist
konkav und in (x_V, x_S) positiv homogen vom Grad 1.

Gegenmittel (alle drei sind Regler, 0 heißt aus):
* Eigentum: Außenoption w_V = lam_v * A, w_S = lam_s * B (die Seite behält diesen Teil ihres Beitrags, wenn die Verhandlung scheitert).
* Vorab-Vertrag: ein Anteil phi des Überschusses wird vor der Investition im Verhältnis der Beiträge A : B fest zugesagt; der Vertrag
  kostet Flexibilität: der Überschuss schrumpft auf (1 - psi * phi) mal S. Verhandelt wird nur der Rest (1 - phi) * S'.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Params:
    theta: float = 0.5   # Verhandlungsanteil von V am verhandelten Rest
    gamma: float = 0.0   # Komplementarität: 0 additiv, 1 rein komplementär
    kappa: float = 1.0   # Kostenfaktor: Kosten je Seite kappa * x^2 / 2
    a: float = 1.0       # Produktivität von V (S hat 1)
    lam_v: float = 0.0   # Eigentum: Außenoption von V als Anteil von A
    lam_s: float = 0.0   # Eigentum: Außenoption von S als Anteil von B
    phi: float = 0.0     # Vorab-Vertrag: fest zugesagter Anteil des Überschusses
    psi: float = 0.0     # Vorab-Vertrag: Verlust an Flexibilität (Überschuss mal 1 - psi * phi)

    def without_remedies(self) -> "Params":
        """Dieselbe Welt ohne Eigentum und ohne Vorab-Vertrag (Basis für die Wirkungstabelle)."""
        return Params(self.theta, self.gamma, self.kappa, self.a, 0.0, 0.0, 0.0, self.psi)


def contributions(xv, xs, a):
    """Beiträge der beiden Seiten A = a * x_V und B = x_S."""
    return a * np.asarray(xv, dtype=float), np.asarray(xs, dtype=float) + 0.0 * np.asarray(xv, dtype=float)


def gross_surplus(xv, xs, gamma, a):
    """Bruttoüberschuss S = (1 - gamma) * (A + B) + 2 * gamma * sqrt(A * B)."""
    big_a, big_b = contributions(xv, xs, a)
    return (1.0 - gamma) * (big_a + big_b) + 2.0 * gamma * np.sqrt(big_a * big_b)


def contract_pot(surplus, phi, psi):
    """Überschuss nach dem Flexibilitätsverlust des Vorab-Vertrags: (1 - psi * phi) * S."""
    return (1.0 - psi * phi) * surplus


def input_share_v(big_a, big_b):
    """Anteil von V an den Beiträgen A / (A + B); ohne Beiträge 1/2."""
    total = big_a + big_b
    return np.where(total > 0, big_a / np.where(total > 0, total, 1.0), 0.5)


def nash_bargain(pie, w_v, w_s, theta):
    """Nash-Verhandlung über `pie` mit Außenoptionen: jede Seite bekommt ihre Außenoption plus ihren Anteil am Rest.

    Übersteigen die beiden Außenoptionen zusammen den Kuchen, gibt es keinen Rest; der Kuchen wird dann im Verhältnis der Außenoptionen
    verteilt (Modellannahme: es wird gehandelt, die Summe der Auszahlungen übersteigt nie den Kuchen)."""
    total = w_v + w_s
    scale = np.where(total > pie, pie / np.where(total > 0, total, 1.0), 1.0)
    rest = np.maximum(pie - total, 0.0)
    return w_v * scale + theta * rest, w_s * scale + (1.0 - theta) * rest


def payoffs(xv, xs, p: Params):
    """Auszahlungen (u_V, u_S) nach Kosten, mit den Gegenmitteln aus `p`; Arrays werden gebroadcastet."""
    big_a, big_b = contributions(xv, xs, p.a)
    pot = contract_pot(gross_surplus(xv, xs, p.gamma, p.a), p.phi, p.psi)
    share_v = input_share_v(big_a, big_b)
    fixed_v = p.phi * pot * share_v
    fixed_s = p.phi * pot * (1.0 - share_v)
    got_v, got_s = nash_bargain((1.0 - p.phi) * pot, p.lam_v * big_a, p.lam_s * big_b, p.theta)
    cost_v = p.kappa * np.asarray(xv, dtype=float) ** 2 / 2.0
    cost_s = p.kappa * np.asarray(xs, dtype=float) ** 2 / 2.0
    return fixed_v + got_v - cost_v, fixed_s + got_s - cost_s


def net_value(xv, xs, p: Params):
    """Netto beider Seiten zusammen: Summe der Auszahlungen."""
    uv, us = payoffs(xv, xs, p)
    return uv + us


def welfare(xv, xs, gamma, a, kappa):
    """Gemeinsames Netto ohne Gegenmittel: S - kappa * (x_V^2 + x_S^2) / 2 (die Zielfunktion des First-Best)."""
    xv = np.asarray(xv, dtype=float)
    xs = np.asarray(xs, dtype=float)
    return gross_surplus(xv, xs, gamma, a) - kappa * (xv**2 + xs**2) / 2.0
