"""Kennzahlen, Experimente (Raster) und Verdikte als reine Funktionen `verdict_*(...) -> (Art, Text)`.

Alle Experimente rechnen mit `Settings` (ganze Prozent) und liefern Zeilen als Wörterbücher; die App zeichnet sie nur."""

import math
from dataclasses import dataclass, replace

import hup_algorithm as A
import hup_constants as C
from hup_scenario import Params, payoffs


@dataclass(frozen=True)
class Settings:
    theta: int = C.THETA_PCT[2]
    gamma: int = C.GAMMA_PCT[2]
    kappa: int = C.KAPPA_PCT[2]
    a: int = C.A_PCT[2]
    lam_v: int = C.LAM_V_PCT[2]
    lam_s: int = C.LAM_S_PCT[2]
    phi: int = C.PHI_PCT[2]
    psi: int = C.PSI_PCT[2]
    delta: int = C.DELTA_PCT[2]

    def params(self) -> Params:
        return Params(self.theta / 100, self.gamma / 100, self.kappa / 100, self.a / 100, self.lam_v / 100, self.lam_s / 100,
                      self.phi / 100, self.psi / 100)

    def base_params(self) -> Params:
        """Dieselbe Welt ohne Eigentum und Vorab-Vertrag."""
        return self.params().without_remedies()


def num(x: float, digits: int = 1) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 1) -> str:
    """Anteil (0 bis 1) als Prozentangabe mit Dezimalkomma, z. B. 0,75 -> '75,0 %'."""
    return f"{num(100.0 * x, digits)} %"


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    res: A.InvestmentResult
    rep: A.RepeatedResult
    delta: float
    rep_efficiency: float     # Wirkungsgrad mit Wiederholung
    quote_v: float            # Investition von V im Gleichgewicht durch First-Best
    quote_s: float
    loss_v: float             # fehlendes Netto, wenn nur V auf Gleichgewichtsniveau investiert
    loss_s: float


def analyse(settings: Settings) -> Analysis:
    p = settings.params()
    res = A.analyse_investment(p)
    rep = A.analyse_repeated(p, res)
    delta = settings.delta / 100
    quote_v = res.eq[0] / res.fb[0] if res.fb[0] > 0 else 1.0
    quote_s = res.eq[1] / res.fb[1] if res.fb[1] > 0 else 1.0
    loss_v, loss_s = A.side_losses(p, res.fb)
    return Analysis(settings, res, rep, delta, A.repeated_efficiency(p, res, rep, delta), quote_v, quote_s, loss_v, loss_s)


# --- Experiment 1: Wirkungsgrad über den Verhandlungsanteil theta --------------------------------------------------------------------------


def sweep_theta(settings: Settings, thetas=C.THETA_SWEEP) -> list[dict]:
    """Wirkungsgrad über theta (ohne Gegenmittel): Gitter bei der eingestellten Komplementarität, Gitter bei gamma = 0 und geschlossene Formel (gamma = 0)."""
    base = settings.base_params()
    rows = []
    for th in thetas:
        p = replace(base, theta=th)
        p0 = replace(p, gamma=0.0)
        eq0 = A.additive_equilibrium_formula(p0)
        rows.append({
            "theta": th,
            "eff": A.analyse_investment(p).efficiency,
            "eff_additive": A.analyse_investment(p0).efficiency,
            "eff_formula": A.efficiency_of(p0, *eq0),
        })
    return rows


def sweep_gamma(settings: Settings, gammas=C.GAMMA_SWEEP) -> list[dict]:
    """Wirkungsgrad über die Komplementarität bei eingestelltem theta (ohne Gegenmittel): bestes und schlechtestes Gleichgewicht, Zahl der Gleichgewichte."""
    base = settings.base_params()
    rows = []
    for g in gammas:
        res = A.analyse_investment(replace(base, gamma=g))
        nan = float("nan")
        rows.append({"gamma": g, "eff": res.efficiency if res.found else nan, "eff_worst": res.efficiency_worst if res.found else nan,
                     "n_eq": len(res.equilibria)})
    return rows


# --- Experiment 2: Wirkung der Gegenmittel -------------------------------------------------------------------------------------------------

REMEDY_NAMES = ("Basis (kein Gegenmittel)", "Eigentum für beide", "Eigentum nur für V", "Eigentum nur für S", "Vorab-Vertrag", "Wiederholung")


def remedy_params(base: Params, name: str, psi: float) -> Params:
    """Die Welt `base` mit genau einem Gegenmittel in der Teststärke (Eigentum REMEDY_LAMBDA, Vertrag REMEDY_PHI mit Verlust psi)."""
    if name == REMEDY_NAMES[0] or name == REMEDY_NAMES[5]:
        return base
    if name == REMEDY_NAMES[1]:
        return replace(base, lam_v=C.REMEDY_LAMBDA, lam_s=C.REMEDY_LAMBDA)
    if name == REMEDY_NAMES[2]:
        return replace(base, lam_v=C.REMEDY_LAMBDA)
    if name == REMEDY_NAMES[3]:
        return replace(base, lam_s=C.REMEDY_LAMBDA)
    if name == REMEDY_NAMES[4]:
        return replace(base, phi=C.REMEDY_PHI, psi=psi)
    raise ValueError(name)


def remedy_efficiency(base: Params, name: str, psi: float, delta: float) -> tuple[float, float]:
    """(Wirkungsgrad mit dem Gegenmittel, Wirkungsgrad der Basis) für eine Welt `base`."""
    res_base = A.analyse_investment(base)
    if name == REMEDY_NAMES[0]:
        return res_base.efficiency, res_base.efficiency
    if name == REMEDY_NAMES[5]:
        rep = A.analyse_repeated(base, res_base)
        return A.repeated_efficiency(base, res_base, rep, delta), res_base.efficiency
    return A.analyse_investment(remedy_params(base, name, psi)).efficiency, res_base.efficiency


def remedy_table(settings: Settings) -> dict:
    """Wirkungstabelle: je Gegenmittel der Wirkungsgrad in der eingestellten Welt und die Zahl der Zellen (von 3 x 3), in denen es den Wirkungsgrad
    um mindestens IMPROVE_PP Prozentpunkte hebt bzw. (Wiederholung) die effiziente Investition hält."""
    base = settings.base_params()
    psi, delta = settings.psi / 100, settings.delta / 100
    cells = [(th, g) for th in C.REMEDY_THETAS for g in C.REMEDY_GAMMAS]
    res_base = A.analyse_investment(base)
    threshold = A.analyse_repeated(base, res_base).threshold
    rows = []
    for name in REMEDY_NAMES:
        eff_here, base_here = remedy_efficiency(base, name, psi, delta)
        better = 0
        for th, g in cells:
            eff, eff0 = remedy_efficiency(replace(base, theta=th, gamma=g), name, psi, delta)
            if name != REMEDY_NAMES[0] and 100.0 * (eff - eff0) >= C.IMPROVE_PP:
                better += 1
        rows.append({"name": name, "eff": eff_here, "gain": eff_here - base_here, "better": better, "cells": len(cells)})
    return {"rows": rows, "psi": psi, "delta": delta, "threshold": threshold}


def contract_curve(settings: Settings, phis=tuple(i / 10 for i in range(11))) -> list[dict]:
    """Wirkungsgrad über den Vertragsanteil phi (Flexibilitätsverlust psi aus den Reglern, kein Eigentum)."""
    base = settings.base_params()
    return [{"phi": f, "eff": A.analyse_investment(replace(base, phi=f)).efficiency} for f in phis]


# --- Experiment 3: Asymmetrie --------------------------------------------------------------------------------------------------------------


def asymmetry_rows(settings: Settings, thetas=C.THETA_SWEEP) -> list[dict]:
    """Je theta (ohne Gegenmittel): Investition je Seite im Verhältnis zum Effizienten, Auszahlungen, Verlust je Seite und Wirkungsgrad."""
    base = settings.base_params()
    rows = []
    for th in thetas:
        p = replace(base, theta=th)
        res = A.analyse_investment(p)
        loss_v, loss_s = A.side_losses(p, res.fb)
        uv, us = (float(v) for v in payoffs(*res.eq, p))
        rows.append({"theta": th, "quote_v": res.eq[0] / res.fb[0], "quote_s": res.eq[1] / res.fb[1], "u_v": uv, "u_s": us,
                     "loss_v": loss_v, "loss_s": loss_s, "eff": res.efficiency})
    return rows


# --- Experiment 4: mehrere Gleichgewichte --------------------------------------------------------------------------------------------------


def multiplicity_grid(settings: Settings, thetas=C.MULTI_THETAS, gammas=C.MULTI_GAMMAS) -> list[dict]:
    """Zahl der reinen Gleichgewichte je Zelle (theta x gamma), mit den eingestellten Gegenmitteln, a und kappa."""
    p0 = settings.params()
    rows = []
    for g in gammas:
        counts = [len(A.find_equilibria(replace(p0, theta=th, gamma=g))) for th in thetas]
        rows.append({"gamma": g, "counts": counts})
    return rows


# --- Experiment 5: Verhandlungsverfahren ---------------------------------------------------------------------------------------------------


def procedure_rows(settings: Settings) -> list[dict]:
    """Verfahren, der Anteil von V, den es zuweist, und der Wirkungsgrad (Welt ohne Gegenmittel)."""
    base = settings.base_params()
    specs = [("Nash-Verhandlung, hälftig", "nash", 0.5)]
    for d in C.RUBINSTEIN_DELTAS:
        specs.append((f"Abwechselnde Angebote, V beginnt, δ = {num(d, 2)}", "rubinstein_v", d))
    specs.append((f"Abwechselnde Angebote, S beginnt, δ = {num(0.9, 2)}", "rubinstein_s", 0.9))
    specs.append(("Ultimatum von V", "ultimatum_v", 0.9))
    specs.append(("Ultimatum von S", "ultimatum_s", 0.9))
    rows = []
    for label, proc, d in specs:
        th = A.procedure_share_v(proc, d)
        rows.append({"label": label, "theta": th, "eff": A.analyse_investment(replace(base, theta=th)).efficiency})
    return rows


# --- Verdikte (rein) -----------------------------------------------------------------------------------------------------------------------

EFF_FULL = 0.995   # ab diesem Wirkungsgrad gilt der mögliche Gewinn als vollständig entstanden
EFF_MOST = 0.90    # ab hier "ein erheblicher Teil geht verloren" statt "ein großer Teil"


def verdict_kernfrage(a: Analysis) -> tuple[str, str]:
    """Verdikt der Kernfrage: wie viel vom möglichen Netto entsteht im (größten) Gleichgewicht."""
    r = a.res
    if not r.found:
        return "warning", ("Kein Gleichgewicht in reinen Strategien auf dem Raster gefunden: Die beste Antwort einer Seite springt, und bei keiner Kombination "
                           "ist jede Seite mit ihrer Investition zufrieden. Wirkungsgrad und Investitionen im Gleichgewicht sind deshalb nicht angegeben "
                           "(gemischte Gleichgewichte sind nicht untersucht).")
    head = (f"Von möglichen **{num(r.fb_net, 2)}** Netto entstehen im Gleichgewicht **{num(r.net, 2)}**, ein Wirkungsgrad von **{pct(r.efficiency)}**. "
            f"V investiert {pct(a.quote_v, 0)} und S {pct(a.quote_s, 0)} des effizienten Niveaus.")
    extra = ""
    if len(r.equilibria) > 1:
        extra = (f" Es gibt {len(r.equilibria)} Gleichgewichte; gezeigt ist das mit den höchsten Investitionen, das schlechteste erreicht {pct(r.efficiency_worst)}.")
    tail = " Das gilt für Nash-Verhandlung nach der Investition mit den eingestellten Voraussetzungen, nicht für jedes Verhandlungsverfahren."
    if r.efficiency >= EFF_FULL:
        return "success", f"Der mögliche Gewinn entsteht im Modell vollständig: Wirkungsgrad **{pct(r.efficiency)}** (Netto {num(r.net, 2)} von {num(r.fb_net, 2)}).{extra}"
    if r.efficiency >= EFF_MOST:
        return "info", head + extra + tail
    return "warning", head + extra + tail


def verdict_repeated(a: Analysis) -> tuple[str, str]:
    """Verdikt der Wiederholung: Schwelle des Diskontfaktors und ob der eingestellte Wert reicht."""
    rep = a.rep
    if not a.res.found:
        return "info", "Ohne Gleichgewicht der Einmalspiel-Phase ist die Strafphase nicht bestimmt; die Schwelle des Diskontfaktors wird nicht berechnet."
    if math.isinf(rep.threshold):
        who = "V steht" if math.isinf(rep.thresholds[0]) else "S steht"
        if math.isinf(rep.thresholds[0]) and math.isinf(rep.thresholds[1]):
            who = "beide Seiten stehen"
        return "warning", (f"Keine Schwelle: {who} bei effizienter Investition schlechter als im Einmalspiel. Ohne Ausgleichszahlung hält Grim-Trigger die "
                           "effiziente Investition bei keinem δ, der Wirkungsgrad bleibt " + pct(a.res.efficiency) + ".")
    if a.delta >= rep.threshold:
        return "success", (f"Grim-Trigger hält die effiziente Investition ab einem Diskontfaktor von **{num(rep.threshold, 2)}**; mit δ = {num(a.delta, 2)} "
                           f"gilt der Wirkungsgrad **{pct(a.rep_efficiency)}** statt {pct(a.res.efficiency)}.")
    return "info", (f"Die Schwelle liegt bei δ* = **{num(rep.threshold, 2)}**; mit δ = {num(a.delta, 2)} ist die Zukunft zu wenig wert, "
                    f"der Wirkungsgrad bleibt {pct(a.res.efficiency)}.")


def verdict_theta(rows: list[dict]) -> tuple[str, str]:
    """Verdikt Experiment 1: Gitter gegen geschlossene Formel (gamma = 0) und beste theta über das Raster."""
    gap = max(abs(r["eff_additive"] - r["eff_formula"]) for r in rows)
    best = max(rows, key=lambda r: (r["eff_additive"], -abs(r["theta"] - 0.5)))
    full = [r for r in rows if r["eff_additive"] >= EFF_FULL]
    worst = min(rows, key=lambda r: r["eff_additive"])
    text = (f"Additiv (γ = 0) weicht das Gitter in allen {len(rows)} θ-Werten um höchstens {num(100 * gap, 4)} Prozentpunkte von der geschlossenen Formel ab "
            "(mit a = 1 und Kostenfaktor 1: Wirkungsgrad 1 − (θ² + (1 − θ)²)/2). ")
    text += (f"Bester Wert: {pct(best['eff_additive'])} bei θ = {num(best['theta'], 1)}; schlechtester: {pct(worst['eff_additive'])} bei θ = {num(worst['theta'], 1)}. "
             f"Kein θ aus dem Raster erreicht {pct(EFF_FULL, 1)}." if not full else
             f"Bester Wert: {pct(best['eff_additive'])} bei θ = {num(best['theta'], 1)}; {len(full)} von {len(rows)} θ-Werten erreichen {pct(EFF_FULL, 1)}.")
    return "info", text


def verdict_remedies(table: dict) -> tuple[str, str]:
    """Verdikt Experiment 2: je Gegenmittel die Zahl der Zellen mit Verbesserung."""
    parts = []
    for r in table["rows"][1:]:
        parts.append(f"{r['name']}: {r['better']} von {r['cells']}")
    helped = [r for r in table["rows"][1:] if r["better"] > 0]
    kind = "info" if helped else "warning"
    return kind, ("Zahl der Zellen (von 9, θ ∈ {0,3; 0,5; 0,7} mal γ ∈ {0; 0,5; 1}), in denen das Gegenmittel den Wirkungsgrad um mindestens "
                  f"{num(C.IMPROVE_PP, 0)} Prozentpunkte hebt (Wiederholung: die effiziente Investition hält): " + "; ".join(parts) + ".")


def verdict_contract(rows: list[dict], psi: float) -> tuple[str, str]:
    """Verdikt zur Vertragskurve: bester Anteil phi im Raster und der Wirkungsgrad bei vollem Vertrag (phi = 1)."""
    base, full = rows[0], rows[-1]
    best = max(rows, key=lambda r: r["eff"])
    if best["eff"] - base["eff"] < 1e-9:
        return "warning", (f"Bei einem Flexibilitätsverlust von {pct(psi, 0)} des Überschusses bei voller Zusage hilft der Vertrag in keinem Anteil des Rasters: "
                           f"ohne Vertrag {pct(base['eff'])}.")
    if abs(best["phi"] - full["phi"]) < 1e-9:
        return "info", (f"Bei einem Flexibilitätsverlust von {pct(psi, 0)} des Überschusses bei voller Zusage liegt der beste Anteil im Raster bei φ = {num(best['phi'], 1)} "
                        f"mit {pct(best['eff'])} (ohne Vertrag {pct(base['eff'])}).")
    return "info", (f"Bei einem Flexibilitätsverlust von {pct(psi, 0)} des Überschusses bei voller Zusage liegt der beste Anteil im Raster bei φ = {num(best['phi'], 1)} "
                    f"mit {pct(best['eff'])}; bei vollem Vertrag (φ = 1) sind es {pct(full['eff'])}, ohne Vertrag {pct(base['eff'])}.")


def verdict_asymmetry(a: Analysis) -> tuple[str, str]:
    """Verdikt Experiment 3: welche Seite investiert weniger, welche fehlt mehr (eingestellte Welt)."""
    low = "V" if a.quote_v < a.quote_s else "S"
    if abs(a.quote_v - a.quote_s) < 1e-6:
        return "info", (f"Beide Seiten investieren gleich viel: {pct(a.quote_v, 0)} des effizienten Niveaus. Ein Verlust von {num(a.loss_v, 2)} (V) und {num(a.loss_s, 2)} (S) "
                        "am gemeinsamen Netto entsteht je Seite.")
    big = "V" if a.loss_v > a.loss_s else "S"
    return "warning", (f"{low} investiert weniger (V {pct(a.quote_v, 0)}, S {pct(a.quote_s, 0)} des effizienten Niveaus). Am gemeinsamen Netto fehlen durch V {num(a.loss_v, 2)} "
                       f"und durch S {num(a.loss_s, 2)}; der größere Verlust kommt von {big}.")


def verdict_multi(rows: list[dict]) -> tuple[str, str]:
    """Verdikt Experiment 4: Zellen mit mehr als einem Gleichgewicht, und wo."""
    total = sum(len(r["counts"]) for r in rows)
    multi = [(r["gamma"], k) for r in rows for k in r["counts"] if k > 1]
    where = sorted({g for g, _ in multi})
    most = max((k for r in rows for k in r["counts"]), default=0)
    if not multi:
        return "success", f"In allen {total} Zellen gibt es genau ein Gleichgewicht der Investitionen."
    at = f"γ = {num(where[0], 2)}" if len(where) == 1 else "γ ∈ {" + "; ".join(num(g, 2) for g in where) + "}"
    return "warning", f"In {len(multi)} von {total} Zellen gibt es mehr als ein Gleichgewicht (höchstens {most}), bei {at}."


def verdict_procedure(rows: list[dict]) -> tuple[str, str]:
    """Verdikt Experiment 5: Spannweite des Wirkungsgrads über die Verfahren."""
    lo = min(rows, key=lambda r: r["eff"])
    hi = max(rows, key=lambda r: r["eff"])
    return "info", (f"Über {len(rows)} Verfahren reicht der Wirkungsgrad von {pct(lo['eff'])} ({lo['label']}) bis {pct(hi['eff'])} ({hi['label']}). "
                    "Im Modell wirkt ein Verfahren nur über den Anteil, den es V zuweist.")


# --- Schlüssel für den Cache der App: nur die Regler, von denen ein Experiment abhängt ---------------------------------------------------------
# (tests/test_cache_keys.py prüft, dass die Rechnung mit dem Schlüssel dasselbe liefert wie mit allen Reglern)


def key_world(s: Settings) -> Settings:
    """Experimente 1 (Komplementarität), 3 und 5: Welt ohne Gegenmittel, theta läuft über das Raster."""
    return replace(Settings(), gamma=s.gamma, kappa=s.kappa, a=s.a)


def key_gamma_sweep(s: Settings) -> Settings:
    """Wirkungsgrad über die Komplementarität bei eingestelltem theta."""
    return replace(Settings(), theta=s.theta, kappa=s.kappa, a=s.a)


def key_remedy(s: Settings) -> Settings:
    """Experiment 2, Wirkungstabelle."""
    return replace(Settings(), theta=s.theta, gamma=s.gamma, kappa=s.kappa, a=s.a, psi=s.psi, delta=s.delta)


def key_contract(s: Settings) -> Settings:
    """Experiment 2, Vertragskurve."""
    return replace(Settings(), theta=s.theta, gamma=s.gamma, kappa=s.kappa, a=s.a, psi=s.psi)


def key_multi(s: Settings) -> Settings:
    """Experiment 4: alles außer dem Diskontfaktor."""
    return replace(s, delta=C.DELTA_PCT[2])
