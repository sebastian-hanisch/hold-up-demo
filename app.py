"""Hold-up: warum ein möglicher Gewinn manchmal gar nicht entsteht - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zwei Seiten investieren vor der Verhandlung in ihre Beziehung und teilen den Überschuss danach. Die App zeigt, wie viel vom möglichen Gewinn im
Gleichgewicht entsteht (Wirkungsgrad), und prüft Gegenmittel: Eigentum, Vorab-Vertrag, Wiederholung. Ein Modellbefund, kein Allgemeingesetz.

Lauffähig mit: streamlit run app.py
"""

import time

import pandas as pd
import streamlit as st

import hup_constants as C
import hup_evaluation as E
from hup_evaluation import Settings, num, pct
from hup_layout import dunkles_design, kopf_css
from hup_presets import bounds, init_session_state_defaults, load_permalink_settings, sidebar_presets, sync_query_params
from hup_texts import ASSUMPTIONS_MARKDOWN, LITERATUR, LITERATUR_HEAD
from hup_visualization import build_asymmetry, build_best_responses, build_contract, build_investments, build_remedies, build_theta

st.set_page_config(page_title="Hold-up – Sebastian Hanisch", layout="wide")


def _timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - start


# Jede Berechnung bekommt nur die Regler im Schlüssel, von denen sie abhängt (tests/test_cache_keys.py prüft das):
# Ein Regler, der sie nicht berührt, löst keine Neuberechnung aus.
@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _theta_rows(key):
    return _timed(E.sweep_theta, key)


@st.cache_data(show_spinner=False)
def _gamma_rows(key):
    return _timed(E.sweep_gamma, key)


@st.cache_data(show_spinner=False)
def _remedy_rows(key):
    return _timed(E.remedy_table, key)


@st.cache_data(show_spinner=False)
def _contract_rows(key):
    return _timed(E.contract_curve, key)


@st.cache_data(show_spinner=False)
def _asym_rows(key):
    return _timed(E.asymmetry_rows, key)


@st.cache_data(show_spinner=False)
def _multi_rows(key):
    return _timed(E.multiplicity_grid, key)


@st.cache_data(show_spinner=False)
def _procedure_rows(key):
    return _timed(E.procedure_rows, key)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in hup_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧱 Hold-up: warum ein möglicher Gewinn manchmal gar nicht entsteht")
st.markdown(
    """
Ein Verlader und ein Spediteur investieren **vor** der Verhandlung in ihre Beziehung (eine Ladeschleuse mit Systemanbindung, Spezialfahrzeuge für genau diese Relation).
Der **Überschuss** entsteht erst danach und wird dann geteilt. Wer investiert, rechnet nur mit seinem **Anteil** am Ertrag, bezahlt aber die vollen Kosten: Ohne Gegenmittel wird im Modell
weniger investiert, als für beide zusammen am besten wäre. Die App misst den **Wirkungsgrad** (Netto im Gleichgewicht durch Netto im Optimum) und prüft **Gegenmittel**:
Eigentum, Vorab-Vertrag und Wiederholung. Das ist ein **Modellbefund unter Voraussetzungen**, kein Gesetz: Hold-up hängt am Verhandlungsverfahren.

Weiter unten: die Kernfrage, fünf Experimente (**🔬**), **🚧 Wo die Annahmen enden**, **⚠️ Annahmen, Grenzen und bekannte Probleme** und die **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Hold-up", expanded=True):
    st.markdown(
        """
1. **Investieren:** V und S wählen gleichzeitig, wie viel sie in die Beziehung stecken. Jede Investition kostet κ · x² / 2 und ist außerhalb der Beziehung nichts wert.
2. **Überschuss entsteht:** Aus den Beiträgen A = a · x_V und B = x_S entsteht der Überschuss. Bei Komplementarität γ = 0 addieren sich die Beiträge, bei γ = 1 braucht jede Seite die andere.
3. **Teilen:** Erst jetzt wird verhandelt. V bekommt den Anteil θ des verhandelten Überschusses, S den Rest. Jede Investition ist dann bereits versunken.
4. **Warum zu wenig investiert wird:** Jede Seite sieht nur ihren Anteil am Ertrag der eigenen Investition, die Kosten trägt sie allein. Sie hört auf, wenn der Anteil am Grenzertrag die Grenzkosten erreicht, also früher als für beide zusammen am besten.
"""
    )

with st.expander("📖 Benannte Regeln und Verfahren, mit Beispielrechnung"):
    st.markdown(
        """
Beispielwelt: a = 1, κ = 1, γ = 0, θ = ½, keine Gegenmittel. Beide investieren je 1, der Überschuss ist dann 2.

| Regel | Was sie tut | Beispielrechnung |
|---|---|---|
| **Nash-Verhandlung** | Jede Seite bekommt zuerst ihre Außenoption, den Rest teilen beide im Verhältnis θ : 1 − θ. | Beide investieren 1: Überschuss 2, jede Seite bekommt 1, nach Kosten ½. Investiert V nur ½, S weiter 1: Überschuss 1,5, V bekommt 0,75, nach Kosten 0,625. |
| **Eigentum** | Die Außenoption einer Seite wächst mit ihrer Investition: ω = λ · Beitrag. | V mit λ_V = 0,6 und Beitrag 1: V behält vorab 0,6, vom Rest 1,4 die Hälfte, also 0,6 + 0,7 = 1,3. Der Grenzanteil von V steigt von 0,5 auf 0,8. |
| **Vorab-Vertrag** | Ein Anteil φ des Überschusses wird vor der Investition im Verhältnis der Beiträge zugesagt; der Überschuss schrumpft auf (1 − ψ · φ) · S. | φ = ½, ψ = 10 %: der Überschuss 2 schrumpft auf 1,9, davon sind 0,95 zugesagt (je 0,475 bei gleichen Beiträgen), der Rest 0,95 wird nach θ geteilt. |
| **Grim-Trigger** | Wer abweicht, löst für immer das Gleichgewicht des Einmalspiels aus. Die Zusammenarbeit hält, wenn die Verführung T kleiner ist als der diskontierte Verlust: δ ≥ (T − R) / (T − P). | R = 0,5 (beide effizient), T = 0,625 (V weicht allein ab), P = 0,375 (beide im Einmal-Gleichgewicht): δ* = 0,125 / 0,25 = 0,5. |
| **Abwechselnde Angebote (Rubinstein)** | Die Seiten machen abwechselnd Angebote, jede Runde wird mit δ abgezinst. Der Erste bekommt (1 − δ₂) / (1 − δ₁ · δ₂). | δ = 0,9 für beide: der Erste bekommt 0,1 / 0,19 ≈ 0,526. |
"""
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Verhandlung und Technik**")
    theta = st.slider("Anteil θ von V am verhandelten Rest", *bounds("theta_slider"), key="theta_slider", format="%d %%",
                      help="Wie viel vom verhandelten Überschuss V bekommt; S bekommt den Rest. 50 %: hälftig.")
    gamma = st.slider("Komplementarität γ", *bounds("gamma_slider"), key="gamma_slider", format="%d %%",
                      help="0 %: die Beiträge addieren sich. 100 %: der Überschuss entsteht nur, wenn beide investieren (geometrisches Mittel).")
    kappa = st.slider("Kostenfaktor κ", *bounds("kappa_slider"), key="kappa_slider", format="%d %%",
                      help="Die Kosten je Seite sind κ · x² / 2. Er skaliert alle Investitionen und Auszahlungen, der Wirkungsgrad bleibt gleich (Test in der README).")
    a = st.slider("Produktivität a von V", *bounds("a_slider"), key="a_slider", format="%d %%",
                  help="Wie viel Beitrag eine Einheit Investition von V bringt, im Vergleich zu S (100 %).")
    st.markdown("**Gegenmittel (0 % heißt aus)**")
    lam_v = st.slider("Eigentum λ_V: Außenoption von V", *bounds("lam_v_slider"), key="lam_v_slider", format="%d %%",
                      help="Anteil seines Beitrags, den V behält, wenn die Verhandlung scheitert.")
    lam_s = st.slider("Eigentum λ_S: Außenoption von S", *bounds("lam_s_slider"), key="lam_s_slider", format="%d %%",
                      help="Anteil seines Beitrags, den S behält, wenn die Verhandlung scheitert.")
    phi = st.slider("Vorab-Vertrag φ: fest zugesagter Anteil", *bounds("phi_slider"), key="phi_slider", format="%d %%",
                    help="Dieser Anteil des Überschusses wird vor der Investition im Verhältnis der Beiträge zugesagt.")
    psi = st.slider("Vertragsverlust ψ bei voller Zusage", *bounds("psi_slider"), key="psi_slider", format="%d %%", disabled=(phi == 0),
                    help="Flexibilitätsverlust des Vertrags: der Überschuss schrumpft auf (1 − ψ · φ) mal S. Ohne Vertragsanteil wirkungslos, dann gesperrt.")
    delta = st.slider("Diskontfaktor δ der Wiederholung", *bounds("delta_slider"), key="delta_slider", format="%d %%",
                      help="Wie viel eine künftige Periode im Vergleich zur laufenden zählt. Wirkt auf den Wirkungsgrad mit Wiederholung.")

settings = Settings(int(theta), int(gamma), int(kappa), int(a), int(lam_v), int(lam_s), int(phi), int(psi), int(delta))
sync_query_params({k: v for k, v in zip(
    ("theta_slider", "gamma_slider", "kappa_slider", "a_slider", "lam_v_slider", "lam_s_slider", "phi_slider", "psi_slider", "delta_slider"),
    (settings.theta, settings.gamma, settings.kappa, settings.a, settings.lam_v, settings.lam_s, settings.phi, settings.psi, settings.delta))})

an = _analysis(settings)
res = an.res
params = settings.params()

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
if res.found:
    m1.metric("Wirkungsgrad im Gleichgewicht", pct(res.efficiency), delta=f"{num(100 * (res.efficiency - 1), 1)} Prozentpunkte gegen effizient")
    m2.metric("Netto: Gleichgewicht", num(res.net, 2), delta=f"{num(res.net - res.fb_net, 2)} gegen effizient {num(res.fb_net, 2)}")
    m3.metric("Investition V (Anteil am Effizienten)", pct(an.quote_v, 0), delta=f"{num(res.eq[0], 2)} statt {num(res.fb[0], 2)}", delta_color="off")
    m4.metric("Investition S (Anteil am Effizienten)", pct(an.quote_s, 0), delta=f"{num(res.eq[1], 2)} statt {num(res.fb[1], 2)}", delta_color="off")
else:
    m1.metric("Wirkungsgrad im Gleichgewicht", "–", delta="kein Gleichgewicht gefunden", delta_color="off")
    m2.metric("Netto: Gleichgewicht", "–", delta=f"effizient {num(res.fb_net, 2)}", delta_color="off")
    m3.metric("Investition V (Anteil am Effizienten)", "–", delta=f"effizient {num(res.fb[0], 2)}", delta_color="off")
    m4.metric("Investition S (Anteil am Effizienten)", "–", delta=f"effizient {num(res.fb[1], 2)}", delta_color="off")
c1, c2 = st.columns(2)
c1.plotly_chart(build_investments(res), width="stretch", key="main_chart")
c2.plotly_chart(build_best_responses(params, res), width="stretch", key="best_response_chart")
active = [name for name, on in (("Eigentum V", lam_v > 0), ("Eigentum S", lam_s > 0), ("Vorab-Vertrag", phi > 0)) if on]
st.caption("Links: Investition je Seite, effizient gegen Gleichgewicht. Rechts: Reaktionskurven; wo sie sich schneiden, ist ein Gleichgewicht, das Quadrat ist der effiziente Punkt. "
           + ("Aktive Gegenmittel: " + ", ".join(active) + "." if active else "Kein Gegenmittel aktiv."))

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viel vom möglichen Gewinn entsteht wirklich, und was hilft?")
kind, text = E.verdict_kernfrage(an)
getattr(st, kind)(text)
kind, text = E.verdict_repeated(an)
getattr(st, kind)(text)
st.caption("Zweite Zeile: Wiederholung als Gegenmittel (Grim-Trigger). Die Schwelle δ* ist der kleinste Diskontfaktor, ab dem die effiziente Investition hält.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Wie hängt der Wirkungsgrad am Verhandlungsanteil und an der Komplementarität?")
st.caption("Ohne Gegenmittel, mit Kostenfaktor, Produktivität und Komplementarität wie eingestellt. Der Anteil θ läuft von 0 bis 1 in Zehnerschritten.")
with st.spinner("Rechne 22 Gleichgewichte (wenige Sekunden beim ersten Aufruf) …"):
    rows1, sec1 = _theta_rows(E.key_world(settings))
    rows1g, sec1g = _gamma_rows(E.key_gamma_sweep(settings))
st.plotly_chart(build_theta(rows1), width="stretch", key="theta_chart")
kind, text = E.verdict_theta(rows1)
getattr(st, kind)(text)
gdf = pd.DataFrame({
    "Komplementarität γ": [f"{num(100 * r['gamma'], 0)} %" for r in rows1g],
    "Wirkungsgrad (bestes Gleichgewicht)": [100 * r["eff"] for r in rows1g],
    "Wirkungsgrad (schlechtestes Gleichgewicht)": [100 * r["eff_worst"] for r in rows1g],
    "Zahl der Gleichgewichte": [r["n_eq"] for r in rows1g],
})
st.dataframe(gdf, hide_index=True, width="stretch", column_config={
    "Wirkungsgrad (bestes Gleichgewicht)": st.column_config.NumberColumn(format="%.1f %%"),
    "Wirkungsgrad (schlechtestes Gleichgewicht)": st.column_config.NumberColumn(format="%.1f %%"),
})
st.caption(f"Unten: Komplementarität bei θ = {num(settings.theta / 100, 2)} wie eingestellt. Rechenzeit beim ersten Aufruf: {num(sec1 + sec1g, 1)} s.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Welches Gegenmittel hilft wie viel?")
st.caption(f"Basis ist die eingestellte Welt ohne Gegenmittel. Teststärken: Eigentum λ = {num(C.REMEDY_LAMBDA, 1)}, Vorab-Vertrag φ = {num(C.REMEDY_PHI, 1)} mit dem Verlust ψ aus der Seitenleiste, "
           "Wiederholung mit dem δ aus der Seitenleiste. Die Zählung läuft über 9 Zellen (θ mal γ).")
with st.spinner("Rechne die Wirkungstabelle (wenige Sekunden beim ersten Aufruf) …"):
    remedy, sec2 = _remedy_rows(E.key_remedy(settings))
    contract, sec2c = _contract_rows(E.key_contract(settings))
VOR = {
    E.REMEDY_NAMES[0]: "–",
    E.REMEDY_NAMES[1]: f"λ_V = λ_S = {num(C.REMEDY_LAMBDA, 1)}",
    E.REMEDY_NAMES[2]: f"λ_V = {num(C.REMEDY_LAMBDA, 1)}, λ_S = 0",
    E.REMEDY_NAMES[3]: f"λ_V = 0, λ_S = {num(C.REMEDY_LAMBDA, 1)}",
    E.REMEDY_NAMES[4]: f"φ = {num(C.REMEDY_PHI, 1)}, ψ = {num(remedy['psi'], 2)}",
    E.REMEDY_NAMES[5]: ("keine Schwelle (eine Seite steht schlechter als im Einmalspiel)" if remedy["threshold"] == float("inf")
                        else f"δ = {num(remedy['delta'], 2)}, Schwelle δ* = {num(remedy['threshold'], 2)}"),
}
rdf = pd.DataFrame({
    "Gegenmittel": [r["name"] for r in remedy["rows"]],
    "Voraussetzung": [VOR[r["name"]] for r in remedy["rows"]],
    "Wirkungsgrad hier": [100 * r["eff"] for r in remedy["rows"]],
    "Veränderung (Prozentpunkte)": [100 * r["gain"] for r in remedy["rows"]],
    "Zellen mit Verbesserung ab 5 Prozentpunkten (von 9)": [r["better"] for r in remedy["rows"]],
})
st.dataframe(rdf, hide_index=True, width="stretch", column_config={
    "Wirkungsgrad hier": st.column_config.NumberColumn(format="%.1f %%"),
    "Veränderung (Prozentpunkte)": st.column_config.NumberColumn(format="%+.1f"),
})
st.plotly_chart(build_remedies(remedy), width="stretch", key="remedy_chart")
kind, text = E.verdict_remedies(remedy)
getattr(st, kind)(text)
st.markdown("**Vorab-Vertrag: wie viel zusagen?** Wirkungsgrad über den fest zugesagten Anteil φ, mit dem Vertragsverlust ψ aus der Seitenleiste.")
st.plotly_chart(build_contract(contract), width="stretch", key="contract_chart")
kind, text = E.verdict_contract(contract, remedy["psi"])
getattr(st, kind)(text)
st.caption(f"Rechenzeit beim ersten Aufruf: {num(sec2 + sec2c, 1)} s.")

st.markdown("---")

st.subheader("🔬 Experiment 3: Asymmetrie – wer investiert zu wenig, und wo fehlt der Gewinn?")
st.caption("Ohne Gegenmittel. Je Anteil θ: wie viel jede Seite im Verhältnis zum Effizienten investiert. Verlust je Seite: wie viel gemeinsames Netto fehlt, "
           "wenn nur diese Seite auf ihrem Gleichgewichtsniveau investiert und die andere effizient.")
with st.spinner("Rechne die Asymmetrie-Tabelle …"):
    rows3, sec3 = _asym_rows(E.key_world(settings))
st.plotly_chart(build_asymmetry(rows3), width="stretch", key="asym_chart")
adf = pd.DataFrame({
    "θ": [r["theta"] for r in rows3],
    "Investition V (% des Effizienten)": [100 * r["quote_v"] for r in rows3],
    "Investition S (% des Effizienten)": [100 * r["quote_s"] for r in rows3],
    "Auszahlung V": [r["u_v"] for r in rows3],
    "Auszahlung S": [r["u_s"] for r in rows3],
    "Verlust durch V": [r["loss_v"] for r in rows3],
    "Verlust durch S": [r["loss_s"] for r in rows3],
    "Wirkungsgrad": [100 * r["eff"] for r in rows3],
})
st.dataframe(adf, hide_index=True, width="stretch", column_config={
    "θ": st.column_config.NumberColumn(format="%.1f"),
    "Investition V (% des Effizienten)": st.column_config.NumberColumn(format="%.0f %%"),
    "Investition S (% des Effizienten)": st.column_config.NumberColumn(format="%.0f %%"),
    "Auszahlung V": st.column_config.NumberColumn(format="%.3f"),
    "Auszahlung S": st.column_config.NumberColumn(format="%.3f"),
    "Verlust durch V": st.column_config.NumberColumn(format="%.3f"),
    "Verlust durch S": st.column_config.NumberColumn(format="%.3f"),
    "Wirkungsgrad": st.column_config.NumberColumn(format="%.1f %%"),
})
st.markdown("**Für die eingestellte Welt** (mit den Gegenmitteln aus der Seitenleiste):")
kind, text = E.verdict_asymmetry(an)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 4: Mehrere Gleichgewichte?")
st.caption("Zählung der reinen Gleichgewichte der Investitionen je Zelle (θ mal γ, 5 mal 5), mit a, κ und den Gegenmitteln wie eingestellt.")
with st.spinner("Zähle Gleichgewichte in 25 Zellen (wenige Sekunden beim ersten Aufruf) …"):
    rows4, sec4 = _multi_rows(E.key_multi(settings))
mdf = pd.DataFrame({"Komplementarität γ": [f"{num(100 * r['gamma'], 0)} %" for r in rows4]})
for i, th in enumerate(C.MULTI_THETAS):
    mdf[f"θ = {num(th, 2)}"] = [r["counts"][i] for r in rows4]
st.dataframe(mdf, hide_index=True, width="stretch")
kind, text = E.verdict_multi(rows4)
getattr(st, kind)(text)
st.caption("Bei γ = 100 % ist „niemand investiert“ ein Gleichgewicht: ohne den Partner bringt die eigene Investition nichts. "
           f"Rechenzeit beim ersten Aufruf: {num(sec4, 1)} s.")

st.markdown("---")

st.subheader("🔬 Experiment 5: Hängt der Befund am Verhandlungsverfahren?")
st.caption("Welt ohne Gegenmittel. Jedes Verfahren weist V einen Anteil zu; im Modell wirkt es nur darüber.")
with st.spinner("Rechne die Verfahren …"):
    rows5, sec5 = _procedure_rows(E.key_world(settings))
pdf = pd.DataFrame({
    "Verfahren": [r["label"] for r in rows5],
    "Anteil von V": [100 * r["theta"] for r in rows5],
    "Wirkungsgrad": [100 * r["eff"] for r in rows5],
})
st.dataframe(pdf, hide_index=True, width="stretch", column_config={
    "Anteil von V": st.column_config.NumberColumn(format="%.1f %%"),
    "Wirkungsgrad": st.column_config.NumberColumn(format="%.1f %%"),
})
kind, text = E.verdict_procedure(rows5)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
ultimatum = next(r for r in rows5 if r["label"] == "Ultimatum von V")
patient = next(r for r in rows5 if r["label"].endswith(f"δ = {num(C.RUBINSTEIN_DELTAS[-1], 2)}") and "V beginnt" in r["label"])
best_contract = max(contract, key=lambda r: r["eff"])
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Nash-Verhandlung nach der Investition** | Ein anderes Verfahren weist einen anderen Anteil zu: beim Ultimatum von V liegt der Wirkungsgrad in der eingestellten Welt bei {pct(ultimatum['eff'])}, bei abwechselnden Angeboten mit δ = {num(C.RUBINSTEIN_DELTAS[-1], 2)} bei {pct(patient['eff'])} (Experiment 5). | `verhandlung-demo` |
| **Investitionen lassen sich nicht vertraglich festlegen** | Ein Vorab-Vertrag über einen Anteil des Überschusses erreicht bei ψ = {num(100 * remedy['psi'], 0)} % im Raster höchstens {pct(best_contract['eff'])} (bei φ = {num(best_contract['phi'], 1)}, Experiment 2). Verträge bei verdecktem Handeln sind ein eigenes Thema. | `vertragsdesign-demo` |
| **Einmaliges Spiel** | In der Wiederholung hält die effiziente Investition ab einer Schwelle des Diskontfaktors, aber nur, wenn keine Seite in der Zusammenarbeit schlechter steht als im Einmalspiel. | `folk-theorem-demo`, `tit-for-tat-demo` |
| **Vollständige Information** | Private Werte sind nicht modelliert; was sie am Hold-up ändern, zeigt die Demo nicht. | `geheimnis-verhandlung-demo` |
| **Zwei Seiten und ein Überschuss** | Mehr als zwei Seiten sind nicht modelliert; wie sich die Anreize dann ändern, zeigt die Demo nicht. | `kern-demo` |
| **Kein Wettbewerb um den Partner** | Ersatz für den Partner würde die Außenoptionen verändern; nicht modelliert. | – |
"""
)

st.markdown("---")

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(ASSUMPTIONS_MARKDOWN)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind die Regler (θ, γ, κ, a und die Gegenmittel). Gesucht sind die Investitionen $x_V, x_S$ im Gleichgewicht, ihr Netto und der Wirkungsgrad
gegenüber dem gemeinsamen Optimum.

| Symbol | Bedeutung |
|---|---|
| $x_V, x_S$ | Investitionen von V und S (nicht negativ) |
| $\kappa$ | Kostenfaktor, Kosten $\kappa x^2/2$ je Seite |
| $a$ | Produktivität von V (S hat 1) |
| $A, B$ | Beiträge der beiden Seiten zum Überschuss |
| $\gamma$ | Komplementarität: 0 additiv, 1 geometrisches Mittel |
| $S, S'$ | Bruttoüberschuss, Überschuss nach Flexibilitätsverlust |
| $\theta$ | Anteil von V am verhandelten Rest, S bekommt $1-\theta$ |
| $\lambda_V, \lambda_S$ | Eigentum: Anteil des eigenen Beitrags als Außenoption |
| $\omega_V, \omega_S$ | Außenoptionen |
| $\varphi, \psi$ | Vorab-Vertrag: zugesagter Anteil, Verlust an Flexibilität |
| $\eta$ | Wirkungsgrad: Netto im Gleichgewicht durch Netto im Optimum |
| $\delta$ | Diskontfaktor der Wiederholung |
| $R_i, T_i, P_i$ | Auszahlung von Seite $i$ bei effizienter Investition beider, bei bester einseitiger Abweichung, im Gleichgewicht des Einmalspiels |

**Beiträge und Überschuss.**

$$A = a\,x_V, \qquad B = x_S$$

$$S = (1-\gamma)(A+B) + 2\gamma\sqrt{AB}$$

$$S' = (1-\psi\varphi)\,S$$

**Ausgleich nach der Investition.** Die Außenoptionen sind $\omega_V = \lambda_V A$ und $\omega_S = \lambda_S B$. Solange $(1-\varphi)S' \ge \omega_V + \omega_S$ gilt:

$$u_V = \varphi S' \frac{A}{A+B} + \omega_V + \theta\,\big((1-\varphi)S' - \omega_V - \omega_S\big) - \frac{\kappa}{2}x_V^2$$

$$u_S = \varphi S' \frac{B}{A+B} + \omega_S + (1-\theta)\,\big((1-\varphi)S' - \omega_V - \omega_S\big) - \frac{\kappa}{2}x_S^2$$

Übersteigen die Außenoptionen den verhandelten Rest, wird er im Verhältnis $\omega_V : \omega_S$ verteilt (Modellannahme, damit die Auszahlungen nie mehr als den Überschuss ergeben).

**Gleichgewicht, Optimum und Wirkungsgrad.**

$$x_V^* \in \arg\max_{x \ge 0}\, u_V(x, x_S^*), \qquad x_S^* \in \arg\max_{x \ge 0}\, u_S(x_V^*, x)$$

$$(x_V^{FB}, x_S^{FB}) = \arg\max_{x_V, x_S \ge 0}\; S - \frac{\kappa}{2}\big(x_V^2 + x_S^2\big)$$

$$\eta = \frac{u_V(x^*) + u_S(x^*)}{S(x^{FB}) - \frac{\kappa}{2}\big((x_V^{FB})^2 + (x_S^{FB})^2\big)}$$

**Geschlossene Formeln (additiv, $\gamma = 0$).** Mit $s = 1-\psi\varphi$ und den Grenzanteilen $\sigma_V = s\,(\varphi + \theta(1-\varphi)) + (1-\theta)\lambda_V$ und $\sigma_S = s\,(\varphi + (1-\theta)(1-\varphi)) + \theta\lambda_S$ (gültig, solange der verhandelte Rest die Außenoptionen deckt):

$$x_V^* = \frac{a\,\sigma_V}{\kappa}$$

$$x_S^* = \frac{\sigma_S}{\kappa}$$

Ohne Gegenmittel, mit $a = \kappa = 1$:

$$\eta = 1 - \frac{\theta^2 + (1-\theta)^2}{2}$$

Behält jede Seite denselben Anteil $\sigma$ der Rendite ihrer eigenen Investition (etwa durch symmetrisches Eigentum bei $\theta = \tfrac12$ mit $\sigma = (1+\lambda)/2$):

$$\eta = 1 - (1-\sigma)^2$$

**Wiederholung (Grim-Trigger).** Mit dem Diskontfaktor $\delta$ hält die effiziente Investition für Seite $i$ genau dann, wenn

$$\delta \ge \delta_i^* = \frac{T_i - R_i}{T_i - P_i}$$

Die Schwelle der Beziehung ist $\max(\delta_V^*, \delta_S^*)$; steht eine Seite bei effizienter Investition schlechter als im Einmal-Gleichgewicht ($R_i < P_i$), gibt es keine.

**Abwechselnde Angebote (Rubinstein).** Mit Diskontfaktoren $\delta_1$ (Erster) und $\delta_2$ (Zweiter) je Runde bekommt der Erste

$$\frac{1-\delta_2}{1-\delta_1\delta_2}$$
        """
    )
    st.markdown(LITERATUR_HEAD + "\n\n" + "\n".join(LITERATUR))

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
