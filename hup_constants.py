"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets.

Alle Regler laufen in ganzen Prozent (Streamlit-Regler und Permalink bleiben ganzzahlig, der Vergleich der Presets exakt)."""

# Regler in Prozent: (Minimum, Maximum, Standard)
THETA_PCT = (0, 100, 50)     # Verhandlungsanteil von V
GAMMA_PCT = (0, 100, 0)      # Komplementarität
KAPPA_PCT = (50, 200, 100)   # Kostenfaktor
A_PCT = (50, 200, 100)       # Produktivität von V (S hat 100 %)
LAM_V_PCT = (0, 100, 0)      # Eigentum V
LAM_S_PCT = (0, 100, 0)      # Eigentum S
PHI_PCT = (0, 100, 0)        # Vorab-Vertrag: fest zugesagter Anteil
PSI_PCT = (0, 50, 10)        # Vorab-Vertrag: Verlust an Flexibilität (wirkt nur bei Vertragsanteil > 0)
DELTA_PCT = (0, 99, 30)      # Diskontfaktor der Wiederholung

# Numerik. Komplexität der Gleichgewichtssuche: N_EQ_GRID Gegenspielerwerte mal N_BR_GRID Kandidaten je Reaktion, O(N_EQ_GRID * N_BR_GRID).
X_MAX = 6.0          # obere Grenze der Investition; größte Investition im Modell: unter 4 (Tests prüfen, dass keine Reaktion an der Grenze liegt)
N_BR_GRID = 241      # Gitterpunkte der Reaktionssuche (Gitter, dann Goldener Schnitt)
N_EQ_GRID = 151      # Stützstellen der Gleichgewichtssuche
GOLDEN_STEPS = 24    # Schritte des Goldenen Schnitts: Klammer 2 * X_MAX / N_BR_GRID mal 0.618^24 unter 1e-6
BISECT_STEPS = 14    # Schritte der Bisektion: X_MAX / N_EQ_GRID / 2^14 unter 1e-5, danach lineare Interpolation
EQ_TOL = 1e-7       # erlaubter Gewinn aus einer Abweichung, damit ein Punkt als Gleichgewicht gilt
EQ_DEDUP = 1e-4      # Gleichgewichte näher als das gelten als dasselbe

# Raster der Experimente
THETA_SWEEP = tuple(i / 10 for i in range(11))
GAMMA_SWEEP = (0.0, 0.25, 0.5, 0.75, 1.0)
REMEDY_THETAS = (0.3, 0.5, 0.7)    # Raster der Wirkungstabelle: 3 x 3 Zellen
REMEDY_GAMMAS = (0.0, 0.5, 1.0)
REMEDY_LAMBDA = 0.5                # Stärke von Eigentum in der Wirkungstabelle
REMEDY_PHI = 0.5                   # Stärke des Vorab-Vertrags in der Wirkungstabelle
MULTI_THETAS = (0.2, 0.35, 0.5, 0.65, 0.8)   # Raster der Gleichgewichtszählung: 5 x 5 Zellen
MULTI_GAMMAS = (0.0, 0.5, 0.75, 0.9, 1.0)
RUBINSTEIN_DELTAS = (0.5, 0.9, 0.99)
IMPROVE_PP = 5.0                   # eine Verbesserung zählt ab so vielen Prozentpunkten Wirkungsgrad

COLOR_FB = "#2F6B65"
COLOR_EQ = "#c0504d"
COLOR_V = "#4c78a8"
COLOR_S = "#f58518"
COLOR_LINE = "#4c78a8"
COLOR_FORMULA = "#7f7f7f"

PRESETS = {
    "Hälftige Teilung, additiv (75 %)": {"theta": 50, "gamma": 0, "kappa": 100, "a": 100, "lam_v": 0, "lam_s": 0, "phi": 0, "psi": 10, "delta": 30},
    "Investierender bekommt 80 % (θ = 0,8)": {"theta": 80, "gamma": 0, "kappa": 100, "a": 100, "lam_v": 0, "lam_s": 0, "phi": 0, "psi": 10, "delta": 30},
    "Starke Komplementarität": {"theta": 50, "gamma": 100, "kappa": 100, "a": 100, "lam_v": 0, "lam_s": 0, "phi": 0, "psi": 10, "delta": 30},
    "Eigentum für eine Seite": {"theta": 50, "gamma": 0, "kappa": 100, "a": 100, "lam_v": 60, "lam_s": 0, "phi": 0, "psi": 10, "delta": 30},
    "Vorab-Vertrag mit Flexibilitätsverlust": {"theta": 50, "gamma": 0, "kappa": 100, "a": 100, "lam_v": 0, "lam_s": 0, "phi": 50, "psi": 10, "delta": 30},
    "Wiederholung mit hohem δ": {"theta": 50, "gamma": 0, "kappa": 100, "a": 100, "lam_v": 0, "lam_s": 0, "phi": 0, "psi": 10, "delta": 80},
}
PRESET_HELP = {
    "Hälftige Teilung, additiv (75 %)": "Beide investieren, der Überschuss wird nach der Investition hälftig geteilt, jede Investition wirkt nur für sich. Das Gleichgewicht liegt bei halber Investition, im Modell bleiben 75 % des möglichen Nettos.",
    "Investierender bekommt 80 % (θ = 0,8)": "V bekommt 80 % des verhandelten Überschusses, S nur 20 %. V investiert 80 %, S nur 20 % des Effizienten: ein ungleiches Ergebnis, das der Gesamtwirkungsgrad verdeckt.",
    "Starke Komplementarität": "Der Überschuss entsteht nur, wenn beide investieren (geometrisches Mittel). Neben dem Gleichgewicht mit Investitionen gibt es dann auch eines ohne jede Investition.",
    "Eigentum für eine Seite": "V behält 60 % des Werts der eigenen Investition als Außenoption (V besitzt, was es aufbaut). S bleibt ohne Außenoption: nur V investiert mehr.",
    "Vorab-Vertrag mit Flexibilitätsverlust": "Die Hälfte des Überschusses wird vor der Investition im Verhältnis der Beiträge zugesagt. Bei voller Zusage ginge 10 % des Überschusses verloren, hier ist die Hälfte zugesagt.",
    "Wiederholung mit hohem δ": "Die Beziehung wird wiederholt, Diskontfaktor 0,8: Im Modell hält die effiziente Investition ab der Schwelle δ*, weil Abweichen die künftigen Perioden kostet (Grim-Trigger).",
}
