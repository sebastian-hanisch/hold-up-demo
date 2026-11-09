"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Schwelle der Art und jede Zahl im Text steht hier.

Ein Verdikt ist eine reine Funktion `verdict_*(...) -> (Art, Text)`; die Tests bauen die Eingaben von Hand (keine Rechnung des Kerns), damit sie
Schwellen und Textzahlen direkt prüfen. `test_presets.py` lässt jedes Preset und die Ränder durch die echte Rechnung laufen."""

import math

import hup_algorithm as A
import hup_evaluation as ev
from hup_scenario import Params


def _analysis(eff, quote_v=0.5, quote_s=0.5, n_eq=1, worst=None, fb_net=1.0, loss_v=0.125, loss_s=0.125, rep_threshold=0.5, delta=0.3,
              thresholds=None, rep_eff=None):
    eqs = tuple((0.5, 0.5) for _ in range(n_eq))
    res = A.InvestmentResult(Params(), (1.0, 1.0), fb_net, eqs, (0.5, 0.5), eff * fb_net, eff, eff if worst is None else worst)
    th = thresholds if thresholds is not None else (rep_threshold, rep_threshold)
    rep = A.RepeatedResult((0.5, 0.5), (0.625, 0.625), (0.375, 0.375), th, max(th))
    return ev.Analysis(ev.Settings(), res, rep, delta, eff if rep_eff is None else rep_eff, quote_v, quote_s, loss_v, loss_s)


# --- Kernfrage ----------------------------------------------------------------------------------------------------------------------------


def test_kernfrage_full_efficiency_is_success_and_inclusive_at_the_threshold():
    kind, text = ev.verdict_kernfrage(_analysis(0.995))
    assert kind == "success" and "Wirkungsgrad **99,5 %**" in text
    assert ev.verdict_kernfrage(_analysis(0.9949))[0] != "success"


def test_kernfrage_info_band_is_inclusive_at_ninety_percent():
    assert ev.verdict_kernfrage(_analysis(0.90))[0] == "info"
    assert ev.verdict_kernfrage(_analysis(0.8999))[0] == "warning"


def test_kernfrage_text_names_netto_efficiency_and_both_quotes():
    kind, text = ev.verdict_kernfrage(_analysis(0.75, quote_v=0.8, quote_s=0.2, fb_net=2.0))
    assert kind == "warning"
    assert "**2,00** Netto" in text and "**1,50**" in text and "**75,0 %**" in text
    assert "V investiert 80 % und S 20 %" in text
    assert "nicht für jedes Verhandlungsverfahren" in text


def test_kernfrage_names_the_number_of_equilibria_and_the_worst_efficiency_only_with_several():
    one = ev.verdict_kernfrage(_analysis(0.75))[1]
    assert "Gleichgewichte" not in one
    two = ev.verdict_kernfrage(_analysis(0.75, n_eq=2, worst=0.0))[1]
    assert "Es gibt 2 Gleichgewichte" in two and "das schlechteste erreicht 0,0 %" in two


# --- Wiederholung ---------------------------------------------------------------------------------------------------------------------


def test_repeated_without_threshold_names_who_stands_worse():
    kind, text = ev.verdict_repeated(_analysis(0.66, thresholds=(0.03, math.inf)))
    assert kind == "warning" and "Keine Schwelle: S steht" in text and "bleibt 66,0 %" in text
    assert "V steht" in ev.verdict_repeated(_analysis(0.66, thresholds=(math.inf, 0.1)))[1]
    assert "beide Seiten stehen" in ev.verdict_repeated(_analysis(0.66, thresholds=(math.inf, math.inf)))[1]


def test_repeated_holding_is_inclusive_at_the_threshold_and_names_both_efficiencies():
    kind, text = ev.verdict_repeated(_analysis(0.75, rep_threshold=0.5, delta=0.5, rep_eff=1.0))
    assert kind == "success" and "Diskontfaktor von **0,50**" in text and "δ = 0,50" in text and "**100,0 %** statt 75,0 %" in text
    kind, text = ev.verdict_repeated(_analysis(0.75, rep_threshold=0.5, delta=0.49))
    assert kind == "info" and "δ* = **0,50**" in text and "δ = 0,49" in text and "bleibt 75,0 %" in text


# --- Experimente --------------------------------------------------------------------------------------------------------------------------


def _theta_rows(effs, formula=None):
    return [{"theta": i / (len(effs) - 1), "eff": e, "eff_additive": e, "eff_formula": e if formula is None else formula[i]} for i, e in enumerate(effs)]


def test_theta_verdict_names_best_worst_and_the_deviation_from_the_formula():
    rows = _theta_rows([0.5, 0.75, 0.5], formula=[0.5, 0.75, 0.5 + 1e-7])
    kind, text = ev.verdict_theta(rows)
    assert kind == "info"
    assert "allen 3 θ-Werten" in text and "0,0000 Prozentpunkte" in text
    assert "Bester Wert: 75,0 % bei θ = 0,5" in text and "schlechtester: 50,0 % bei θ = 0,0" in text
    assert "Kein θ aus dem Raster erreicht 99,5 %" in text


def test_theta_verdict_counts_the_cells_that_reach_full_efficiency():
    kind, text = ev.verdict_theta(_theta_rows([0.5, 0.996, 1.0, 0.7]))
    assert "2 von 4 θ-Werten erreichen 99,5 %" in text and "Kein θ" not in text


def test_theta_verdict_reports_a_deviation_of_one_percentage_point():
    rows = _theta_rows([0.5, 0.75], formula=[0.5, 0.76])
    assert "um höchstens 1,0000 Prozentpunkte" in ev.verdict_theta(rows)[1]


def _remedy_table(betters):
    names = ev.REMEDY_NAMES
    return {"rows": [{"name": n, "eff": 0.8, "gain": 0.0, "better": b, "cells": 9} for n, b in zip(names, betters)], "psi": 0.1, "delta": 0.3, "threshold": 0.5}


def test_remedy_verdict_counts_cells_per_remedy_and_warns_when_nothing_helps():
    kind, text = ev.verdict_remedies(_remedy_table([0, 9, 6, 6, 9, 0]))
    assert kind == "info"
    for part in ("Eigentum für beide: 9 von 9", "Eigentum nur für V: 6 von 9", "Eigentum nur für S: 6 von 9", "Vorab-Vertrag: 9 von 9", "Wiederholung: 0 von 9"):
        assert part in text
    assert "mindestens 5 Prozentpunkte" in text
    assert ev.verdict_remedies(_remedy_table([0, 0, 0, 0, 0, 0]))[0] == "warning"


def test_contract_verdict_three_branches():
    rows = [{"phi": i / 10, "eff": e} for i, e in enumerate([0.75, 0.8, 0.85, 0.84, 0.83, 0.82, 0.81, 0.8, 0.79, 0.78, 0.77])]
    kind, text = ev.verdict_contract(rows, 0.1)
    assert kind == "info" and "10 % des Überschusses" in text and "φ = 0,2 mit 85,0 %" in text and "(φ = 1) sind es 77,0 %" in text and "ohne Vertrag 75,0 %" in text
    rows = [{"phi": i / 10, "eff": 0.75 + 0.02 * i} for i in range(11)]
    kind, text = ev.verdict_contract(rows, 0.0)
    assert kind == "info" and "φ = 1,0 mit 95,0 %" in text and "bei vollem Vertrag" not in text
    rows = [{"phi": i / 10, "eff": 0.75 - 0.01 * i} for i in range(11)]
    kind, text = ev.verdict_contract(rows, 0.5)
    assert kind == "warning" and "50 % des Überschusses" in text and "hilft der Vertrag in keinem Anteil" in text and "ohne Vertrag 75,0 %" in text


def test_asymmetry_verdict_names_the_weaker_investor_and_the_bigger_loss():
    kind, text = ev.verdict_asymmetry(_analysis(0.66, quote_v=0.8, quote_s=0.2, loss_v=0.02, loss_s=0.32))
    assert kind == "warning" and text.startswith("S investiert weniger")
    assert "V 80 %, S 20 %" in text and "durch V 0,02" in text and "durch S 0,32" in text and "kommt von S" in text
    kind, text = ev.verdict_asymmetry(_analysis(0.75, quote_v=0.5, quote_s=0.5, loss_v=0.5, loss_s=0.125))
    assert kind == "info" and "Beide Seiten investieren gleich viel: 50 %" in text and "0,50 (V) und 0,12 (S)" in text
    assert ev.verdict_asymmetry(_analysis(0.7, quote_v=0.3, quote_s=0.6, loss_v=0.4, loss_s=0.1))[1].startswith("V investiert weniger")


def test_multi_verdict_counts_cells_and_names_the_gammas():
    rows = [{"gamma": 0.0, "counts": [1, 1]}, {"gamma": 1.0, "counts": [2, 2]}]
    kind, text = ev.verdict_multi(rows)
    assert kind == "warning" and "In 2 von 4 Zellen" in text and "höchstens 2" in text and "γ = 1,00" in text
    kind, text = ev.verdict_multi([{"gamma": 0.0, "counts": [1, 1]}, {"gamma": 1.0, "counts": [1, 3]}])
    assert "In 1 von 4 Zellen" in text and "höchstens 3" in text
    kind, text = ev.verdict_multi([{"gamma": 0.0, "counts": [1, 1]}])
    assert kind == "success" and "In allen 2 Zellen gibt es genau ein Gleichgewicht" in text
    assert "γ ∈ {0,50; 1,00}" in ev.verdict_multi([{"gamma": 0.5, "counts": [2]}, {"gamma": 1.0, "counts": [2]}])[1]


def test_procedure_verdict_names_the_range():
    rows = [{"label": "A", "theta": 0.5, "eff": 0.75}, {"label": "B", "theta": 1.0, "eff": 0.5}, {"label": "C", "theta": 0.6, "eff": 0.74}]
    kind, text = ev.verdict_procedure(rows)
    assert kind == "info" and "Über 3 Verfahren reicht der Wirkungsgrad von 50,0 % (B) bis 75,0 % (A)" in text
    assert "nur über den Anteil" in text


def test_number_formatting_uses_decimal_commas():
    assert ev.num(0.5, 2) == "0,50" and ev.pct(0.755) == "75,5 %" and ev.pct(1.0, 0) == "100 %"
