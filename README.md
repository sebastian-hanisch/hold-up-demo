# Hold-up: warum ein möglicher Gewinn manchmal gar nicht entsteht – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-hold-up-demo.streamlit.app/)**

Stück der Linie **Gemeinsam gewinnen**. Der Vorgänger in der Linie ist `kuchen-vergroessern-demo`; die Kante ist ein **Kontrast**: dort muss der Überschuss erst entstehen, hier wirkt das Teilen auf die Investition zurück, aus der er entstehen soll. Vehikel ist die Beziehung zwischen einem **Verlader** (V) und einem **Spediteur** (S): V investiert in eine Ladeschleuse mit Systemanbindung, S in Spezialfahrzeuge für genau diese Relation; beides ist außerhalb der Beziehung nichts wert. Nachbarn im Portfolio: `verhandlung-demo` (Verhandlung nach dem Ablauf abwechselnder Angebote), `vertragsdesign-demo` (Verträge bei verdecktem Handeln), `folk-theorem-demo` und `tit-for-tat-demo` (Wiederholung als Gegenmittel), `kern-demo` (Aufteilung bei mehr als zwei Seiten) und `geheimnis-verhandlung-demo` (private Werte). **Verlader, Spediteur und die Gegenmittel sind Modellannahmen, keine Aussagen über echte Verträge.**

## Kernfrage

*Wenn beide Seiten vor der Verhandlung in die Beziehung investieren und der Überschuss danach geteilt wird, wie viel von dem möglichen Gewinn entsteht wirklich, und was hilft?* Von Hand, mit Überschuss x_V + x_S, Kosten x² / 2 je Seite und hälftiger Teilung nach der Investition: das gemeinsame Optimum ist x = 1 je Seite (Netto 1), im Gleichgewicht investiert jede Seite nur x = ½ (Netto 0,75). Der **Wirkungsgrad** (Netto im Gleichgewicht durch Netto im Optimum) ist **75 %**. Das ist ein **Modellbefund unter Voraussetzungen, kein Allgemeingesetz**: Hold-up hängt am Verhandlungsverfahren und am Gleichgewichtsbegriff (Ellingsen und Robles, Abstract gelesen). Hier wird nach Nash über den Bruttoüberschuss verhandelt, damit entsteht die Unterinvestition durch die Annahme.

## Befunde und Korrekturen gegenüber dem Plan

Der Einzelauftrag (`gemeinsam-gewinnen-planung/STUECK-G4-hold-up.md`, nicht in diesem Repo) nannte Hooks aus Handrechnung und Suchtreffern; alle Zahlen dieser README sind **neu mit dem Code der Demo gemessen**. Was sich nicht so bestätigte:

- **Die Formel 1 − (1 − θ)² gilt für einen anderen Fall als angenommen.** Sie gilt, wenn **jede Seite den Anteil θ der Rendite ihrer eigenen Investition behält** (etwa symmetrisches Eigentum). Bei Nash-Verhandlung, in der V den Anteil θ des Überschusses bekommt und S den Anteil 1 − θ, ist der Wirkungsgrad 1 − (θ² + (1 − θ)²)/2 (additiv, a = κ = 1). Beide Formeln geben bei θ = ½ dieselben 75 %. Die App zeigt die zweite gegen das Gitter, die erste steht in den Tests (symmetrisches Eigentum).
- **„Komplementarität verschärft Hold-up“ bestätigte sich nur bei ungleicher Teilung und gleich produktiven Seiten (a = 1).** Bei hälftiger Teilung ist der Wirkungsgrad 75 % für γ ∈ {0; 0,25; 0,5; 0,75; 1} (auch mit doppelter Produktivität von V). Bei θ = 0,8 und a = 1 sinkt er von 66,0 % (γ = 0) auf 60,0 % (γ = 1). Bei ungleicher Produktivität kann Komplementarität den Wirkungsgrad auch heben: bei a = 2 und θ = 0,2 steigt er mit γ von 48,0 % auf 60,0 %. Was bei γ = 1 dazukommt, ist ein zweites Gleichgewicht: niemand investiert.
- **Mehrere Gleichgewichte treten in den gemessenen Rastern nur bei γ = 1 auf.** In 0 von 108 Welten mit γ < 1 (Raster in `tests/test_claims.py`) gibt es mehr als eines, bei γ = 1 in 33 von 36. In den 3 übrigen (a = 2, Eigentum V 0,5, Vertragsanteil 0,5) bleibt **nur** das Gleichgewicht ohne Investition: die beste Antwort von S springt, ein innerer Fixpunkt gibt es nicht (Deutung, an einer der drei Welten gegen ein Gitter geprüft; gemischte Gleichgewichte sind nicht untersucht).
- **Eigentum und Vorab-Vertrag wirken in der additiven Welt über denselben Mechanismus**: sie heben den Grenzanteil des Investierenden. Der Unterschied ist der Preis: Der Vertrag verliert Flexibilität (ψ), Eigentum im Modell nicht. Bei zu hohem ψ schadet der Vertrag (φ = 1, ψ = 50 %: Wirkungsgrad 25 %).
- **Wiederholung** ist als Spiel mit zwei Handlungen je Periode gebaut (effizient investieren oder nicht, Strafphase: Gleichgewicht des Einmalspiels). Sie hält die **effiziente Investition**, nicht „faire Teilung“. Bei starkem Ungleichgewicht gibt es **keine** Schwelle: S steht bei effizienter Investition schlechter als im Einmalspiel, und Ausgleichszahlungen sind nicht Teil des Modells. Das gilt bei θ = 0,8 und bei einseitigem Eigentum für V mit λ_V = 0,6; die Grenzen liegen bei θ > 0,59 bzw. λ_V > 0,29 (a = κ = 1, γ = 0), darunter gibt es Schwellen.
- **Rubinstein ist gebaut** (kleiner Baustein, Experiment 5): im Modell wirkt ein Verfahren nur über den Anteil, den es V zuweist.
- **Nicht gebaut:** PDF-Export (kein Auftrag), Zufall (die Demo ist deterministisch, daher keine Kopie von `abt_rng.py`).
- **Literatur:** der Auftrag nannte „Tirole 1986“ ohne Titel. Geprüft ist „Procurement and Renegotiation“ (Journal of Political Economy 94(2), 235–259), nicht „Hierarchies and Bureaucracies“ (nicht geprüft). Ergänzt: Grout (1984), Ellingsen und Robles (2000), Nash (1950), Rubinstein (1982).

## Modell

Investitionen x_V, x_S ≥ 0, Kosten κ · x² / 2 je Seite. Beiträge A = a · x_V und B = x_S. **Bruttoüberschuss** S = (1 − γ)(A + B) + 2γ√(AB), das Doppelte der Mischung aus arithmetischem und geometrischem Mittel: additiv bei γ = 0, komplementär bei γ = 1, konkav und homogen vom Grad 1. Nach der Investition: **Nash-Verhandlung**, V bekommt den Anteil θ des Rests, S den Rest. **Gleichgewicht**: jede Seite maximiert ihre Auszahlung nach Kosten gegeben die andere; **First-Best**: gemeinsames Maximum von S minus Kosten; **Wirkungsgrad** η = Netto im Gleichgewicht / Netto im First-Best. Bei mehreren Gleichgewichten wird das mit den höchsten Investitionen gezeigt, das schlechteste wird genannt.

Gegenmittel (alle drei Regler, 0 heißt aus): **Eigentum** (Außenoption ω = λ · Beitrag; übersteigen beide Außenoptionen den Rest, wird er im Verhältnis verteilt, damit die Auszahlungen nie mehr als den Überschuss ergeben), **Vorab-Vertrag** (Anteil φ des Überschusses wird vor der Investition im Verhältnis der Beiträge zugesagt, der Überschuss schrumpft auf (1 − ψ · φ) · S), **Wiederholung** (Grim-Trigger mit Diskontfaktor δ; Schwelle (T − R)/(T − P)). Die Formeln stehen im Expander „📐 Mathematische Formulierung“ der App, mit Lesehilfe und Literatur.

## Methodik

- **Reaktion einer Seite** (`maximize_1d`): Gitter über 0 bis 6, dann Goldener Schnitt um den besten Gitterpunkt; vektorisiert über viele Gegenspielerwerte.
- **Gleichgewichte** (`find_equilibria`): Nullstellen der doppelten Reaktion auf einem Gitter, Bisektion plus lineare Interpolation, jeder Kandidat durch eine Abweichungsprobe bestätigt. Nur reine Gleichgewichte.
- **First-Best** (`first_best`): Bedingungen erster Ordnung, eine monotone Gleichung in r = √(B/A), per Bisektion.
- **Gegenmittel-Tabelle:** 3 mal 3 Zellen (θ ∈ {0,3; 0,5; 0,7} mal γ ∈ {0; 0,5; 1}); gezählt wird, in wie vielen Zellen ein Gegenmittel den Wirkungsgrad um mindestens 5 Prozentpunkte hebt.
- **Gleichgewichtszählung:** 5 mal 5 Zellen (θ ∈ {0,2; 0,35; 0,5; 0,65; 0,8} mal γ ∈ {0; 0,5; 0,75; 0,9; 1}).

## Befunde (gemessen, keine Behauptungen)

Alle Werte sind Messungen des Codes dieser Demo. Die Gleichgewichte werden numerisch bestimmt (Genauigkeit rund 1e-6 in der Investition), daher prüfen die Tests mit Band. Die Läufe sind deterministische Raster, keine Zufallsläufe. Basis, wenn nicht anders genannt: a = κ = 1, γ = 0, θ = ½, keine Gegenmittel, ψ = 10 %, δ = 30 %.

| Frage | Befund (Voraussetzung) | Test in `tests/test_claims.py` |
|---|---|---|
| Wirkungsgrad bei hälftiger Teilung | 75,0 %: beide investieren 0,5 statt 1, Netto 0,75 von 1,00 (Basis) | `test_claim_half_split_additive_gives_75_percent` |
| Formel gegen Gitter | Abweichung unter 1e-6 in allen 11 Werten θ = 0 bis 1 in Zehnerschritten (Basis, a = κ = 1) | `test_claim_formula_matches_the_grid_over_eleven_thetas` |
| Verlauf über θ | höchster Wert 75,0 % bei θ = 0,5, 50,0 % bei θ = 0 und θ = 1, spiegelsymmetrisch; kein θ des Rasters erreicht 99,5 % | `test_claim_efficiency_over_theta_peaks_at_one_half_and_is_symmetric` |
| θ = 0,8 | Wirkungsgrad 66,0 %; V investiert 80 %, S 20 % des Effizienten; am Netto fehlen durch V 0,02, durch S 0,32 | `test_claim_theta_eighty_percent_gives_66_percent_and_unequal_investment` |
| Produktivere Seite | a = 2, θ = ½: beide investieren 50 %, am Netto fehlen durch V 0,50, durch S 0,125 (Faktor a², additiv); Wirkungsgrad 75,0 % | `test_claim_productive_v_with_equal_split_loses_four_times_as_much_as_s` |
| Komplementarität bei hälftiger Teilung | 75,0 % für γ ∈ {0; 0,25; 0,5; 0,75; 1}, bei a = 1 und a = 2 | `test_claim_complementarity_does_not_change_efficiency_at_an_equal_split` |
| Komplementarität bei θ = 0,8 | 66,0 / 63,6 / 62,0 / 60,9 / 60,0 % für γ = 0 bis 1 (Band ± 0,06 Prozentpunkte) | `test_claim_complementarity_lowers_efficiency_at_an_unequal_split` |
| Gleichgewichte im 5-mal-5-Raster | 5 von 25 Zellen haben zwei, alle bei γ = 1 (Basis, ψ = 10 %) | `test_claim_complementarity_one_adds_the_no_investment_equilibrium` |
| Gleichgewichte im breiten Raster | 144 Welten (θ 3, γ 4, a 3, Eigentum V 2, Vertrag 2): bei γ < 1 in 0 von 108 mehr als eines; bei γ = 1 in 33 von 36; in den übrigen 3 nur das Gleichgewicht ohne Investition | `test_claim_multiple_equilibria_on_a_wide_raster_only_at_gamma_one` |
| Schlechtestes Gleichgewicht bei γ = 1 | Wirkungsgrad 0,0 % (niemand investiert), gezeigt wird 75,0 % | `test_claim_the_equilibrium_shown_is_the_one_with_the_highest_investments_and_the_worst_is_zero_net` |
| Eigentum für beide, λ = 0,5 | 93,75 %; nur für V oder nur für S: je 84,375 % (Basis, 9 von 9 bzw. je 6 von 9 Zellen mit Verbesserung ab 5 Prozentpunkten) | `test_claim_remedy_table_for_the_standard_world` |
| Eigentum bei θ = 0,8 | nur für S: 90,0 %, nur für V: 67,5 % (Basis 66,0 %) | `test_claim_ownership_helps_the_disadvantaged_side_more_than_the_advantaged_one` |
| Symmetrisches Eigentum und Formel | λ = 0,5 für beide: 93,75 % gleich 1 − (1 − 0,75)²; λ = 1 für beide: 100 % | `test_claim_symmetric_ownership_matches_the_own_return_formula` |
| Vorab-Vertrag | φ = 0,5, ψ = 10 %: 84,6 %; bester Anteil im Raster (Schritt 0,1) φ = 0,6 mit 84,8 %; φ = 1: 81,0 %; 9 von 9 Zellen verbessert | `test_claim_contract_optimum_and_the_cost_of_a_full_contract`, `test_claim_remedy_table_for_the_standard_world` |
| Vertrag ohne und mit hohem Verlust | ψ = 0, φ = 1: 100 %; ψ = 50 %, φ = 1: 25,0 % (schlechter als ohne Vertrag) | `test_claim_contract_without_loss_is_efficient_and_with_half_loss_it_hurts` |
| Wiederholung, Schwelle | δ* = 0,50 (R = 0,5, T = 0,625, P = 0,375 je Seite); δ = 0,3: 75,0 %, δ = 0,8: 100 % | `test_claim_grim_trigger_threshold_half_in_the_standard_world`, `test_claim_repeated_efficiency_depends_on_delta_against_the_threshold` |
| Wiederholung und Komplementarität | δ* = 0,500 / 0,480 / 0,463 / 0,447 / 0,433 für γ = 0 bis 1 bei θ = ½ (Band ± 0,0002) | `test_claim_threshold_falls_with_complementarity_at_an_equal_split` |
| Wiederholung ohne Schwelle | θ = 0,8 und Eigentum nur für V (λ_V = 0,6; ohne Schwelle erst ab θ > 0,59 bzw. λ_V > 0,29, a = κ = 1, γ = 0): S steht bei effizienter Investition schlechter als im Einmalspiel | `test_claim_no_threshold_when_a_side_is_worse_off_cooperating` |
| Wiederholung im Raster | bei δ = 0,8 hält die effiziente Investition in 3 von 9 Zellen (θ = ½, alle γ), bei δ = 0,3 in 0 | `test_claim_remedy_counts_with_a_high_delta`, `test_claim_remedy_table_for_the_standard_world` |
| Verfahren | Wirkungsgrad 75,0 % (Nash hälftig), 72,2 / 74,9 / 75,0 % (abwechselnde Angebote, V beginnt, δ = 0,5 / 0,9 / 0,99), 50,0 % (Ultimatum von V oder S); Anteil von V bei δ = 0,9: 0,1/0,19 | `test_claim_procedures` |
| Kostenfaktor | ändert den Wirkungsgrad nicht: größte Abweichung unter 1e-5 über 32 Welten, je bei κ = 0,5 und 2 gegen κ = 1 | `test_claim_cost_factor_leaves_efficiency_unchanged_on_a_raster_of_worlds` |
| Rastergrößen und Grenzen | 9 und 25 Zellen, X_MAX = 6, 11 θ-Werte | `test_claim_raster_sizes_and_bounds_named_in_the_texts` |
| Beispielrechnungen der App-Tabelle | 0,5 / 0,625 / 1,3 / 0,95 / 0,8 / 0,526 | `test_claim_the_hand_example_numbers_of_the_app_table` |

Messung dieser README, nicht im Test: Der erste Lauf der App am Standard rechnet alle Experimente in rund 6 Sekunden (AppTest, ein Rechner, kein Browser; Cloud-Latenz kommt dazu); danach sind sie zwischengespeichert, und ein Regler, den eine Berechnung nicht braucht, löst sie nicht neu aus (`tests/test_cache_keys.py`).

## Ehrliche Grenzen

- **Modellbefund, kein Gesetz.** Die Unterinvestition entsteht, weil nach der Investition über den Bruttoüberschuss nach Nash verhandelt wird. Experiment 5 zeigt, dass ein anderes Verfahren nur über den Anteil von V wirkt: bei Ultimatum von V oder S sind es 50,0 %, bei abwechselnden Angeboten mit δ = 0,99 rund 75,0 %. Was ein Verfahren mit Außenoptionen, mit Verzögerung oder mit Lernen ergibt, ist nicht gerechnet.
- **Nur reine Gleichgewichte.** Gemischte Gleichgewichte und die Auswahl unter mehreren (hier: höchste Investitionen) sind nicht untersucht; in 3 von 36 Welten bei γ = 1 gibt es nur das Gleichgewicht ohne Investition.
- **Eigentum** wirkt nur als Außenoption der eigenen Investition, ohne Rückwirkung auf den Partner. **Grim-Trigger** ist eine von vielen Strafstrategien, ohne Ausgleichszahlungen, und die Schwelle gilt nur für das effiziente Ziel.
- Die Zählungen gelten für die genannten Raster und die übrigen Regler wie genannt. Die Literatur ist nach Autoren, Jahr, Zeitschrift und Seiten geprüft; Volltexte wurden nicht gelesen.
- Nicht modelliert: Vertragsrecht und Durchsetzung, Wettbewerb um den Partner, unvollständige Information, Kreditbeschränkungen, mehr als zwei Seiten.

Dieselben Annahmen, Grenzen und bekannten Probleme stehen in der App im Expander „⚠️ Annahmen, Grenzen und bekannte Probleme“ (ein Test vergleicht den Wortlaut):

**Annahmen**

- Zwei Seiten, Verlader V und Spediteur S, investieren je einmal in die Beziehung. Die Investition ist beziehungsspezifisch: außerhalb der Beziehung ist sie nichts wert (Ausnahme: das Gegenmittel Eigentum, dort steht ein einstellbarer Außenwert). Die Kosten betragen κ · x² / 2 je Seite.
- Die Höhe der Investition lässt sich nicht vertraglich festlegen. Nur das Gegenmittel „Vorab-Vertrag“ sagt vor der Investition einen Anteil des Überschusses zu.
- Nach der Investition wird der Überschuss nach Nash verhandelt: V bekommt den Anteil θ des verhandelten Rests, S den Anteil 1 − θ, ohne Verzögerung und bei vollständiger Information.
- Gleichgewicht heißt: kein Spieler gewinnt durch eine einseitige Abweichung seiner Investition (reines Gleichgewicht). Gibt es mehrere, zeigt die App das mit den höchsten Investitionen und nennt ihre Zahl.
- Wiederholung: Grim-Trigger. Weicht eine Seite von der effizienten Investition ab, spielen beide danach für immer das Gleichgewicht des Einmalspiels. Es gibt keine Ausgleichszahlungen zwischen den Seiten.

**Grenzen**

- Das Ergebnis ist ein Modellbefund, kein Gesetz. Hold-up hängt am Verhandlungsverfahren und am Gleichgewichtsbegriff (Ellingsen und Robles, Abstract gelesen). Hier wird nach Nash über den Bruttoüberschuss verhandelt; die Unterinvestition entsteht damit durch die Annahme.
- Eigentum wirkt nur als Außenoption der eigenen Investition. Rückwirkungen auf die Anreize des Partners sind nicht modelliert.
- Nicht modelliert: Vertragsrecht und Durchsetzung, Wettbewerb um den Partner, unvollständige Information, Kreditbeschränkungen, mehr als zwei Seiten.
- Die Investition ist auf 0 bis 6 begrenzt; die Tests prüfen, dass kein Gleichgewicht und kein effizienter Punkt in den Reglergrenzen an diese Grenze stößt.
- „Verlader“ und „Spediteur“ sind eine Kulisse für das Modell. Die Demo macht keine Rechts- oder Anlageaussagen; „Allianz“ und „Pool“ sind in dieser Linie Modellbegriffe.

**Bekannte Probleme und Unsicherheiten**

- Gleichgewichte werden numerisch bestimmt (Gitter, Goldener Schnitt, Bisektion; Genauigkeit rund 1e-6 in der Investition). Angezeigte Zahlen sind gerundet, die Tests prüfen Bänder.
- Die Zählungen in den Experimenten gelten für das jeweils genannte Raster (die Wirkungstabelle hat 9 Zellen, die Gleichgewichtszählung 25) und mit den übrigen Reglern wie eingestellt, nicht für jede Welt.
- Grim-Trigger ist eine von vielen Strafstrategien; die Schwelle gilt nur dafür, und nur für das effiziente Ziel.
- Mit mehreren Gleichgewichten hängt der Wirkungsgrad an der Auswahl; die App wählt das mit den höchsten Investitionen und nennt das schlechteste.
- Gibt es auf dem Raster kein reines Gleichgewicht (Beispiel: γ = 0,9, a = 2, λ_V = 0,5, φ = 0,5, wo die beste Antwort von S springt), meldet die App „Kein Gleichgewicht in reinen Strategien auf dem Raster gefunden“ und zeigt keinen Wirkungsgrad; gemischte Gleichgewichte sind nicht untersucht. Die Angabe zur Genauigkeit gilt nur dort, wo ein Gleichgewicht gefunden wird.
- Die Literaturangaben sind nach Autoren, Jahr, Zeitschrift und Seiten geprüft; Volltexte wurden nicht gelesen, nur Abstracts und Zusammenfassungen.

## Verifikation

- **Orakel** (`tests/test_oracle_hold_up.py`): Gleichgewicht der Investitionen gegen Aufzählung auf einem 2D-Gitter (Zusammenhangskomponenten) und gegen `scipy.optimize.minimize_scalar` in 12 Welten; First-Best gegen 2D-Gitter und BFGS; Wirkungsgrad gegen die ausgeschriebene geschlossene Formel (additiv, mit und ohne Gegenmittel); Nash-Aufteilung gegen Aufzählung des Nash-Produkts; Grim-Trigger-Schwelle gegen Wertiteration; Rubinstein gegen Rückwärtsrechnung über 3000 Runden. Ein größerer Lauf mit 300 Zufallswelten (Scratch, nicht im Repo): jedes gefundene Gleichgewicht durch `scipy` bestätigt, kein Wirkungsgrad über 1, First-Best nie schlechter als ein Punkt des 2D-Gitters, die geschlossene Formel in allen additiven Welten ohne Gegenmittel getroffen, kein Fall an der Grenze der Investition.
- **Einheiten** (`tests/test_algorithm.py`): Überschuss, Verhandlung, Gegenmittel, Reaktion, Gleichgewicht, First-Best, Wiederholung und Rubinstein gegen Handrechnung; jedes Gegenmittel ändert das Ergebnis auf mindestens einer Welt (kein toter Zweig).
- **Randfälle** (`tests/test_edge_cases.py`): jeder Regler einzeln am Minimum und Maximum und alle Minima und alle Maxima durch die ganze Rechnung, θ = 0 und 1, Eigentum 1, Vertrag ohne und mit hohem Verlust.
- **Verdikte** (`tests/test_verdicts.py`): jede Schwelle und jede Zahl im Text an handgesetzten Werten; `tests/test_presets.py`: jedes Preset durch die echte Rechnung mit der erwarteten Verdikt-Zeile.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, fester Kopf, aktives Preset hervorgehoben, jede Regleränderung hebt die Markierung auf), Permalink, Cache-Schlüssel, Footer, Laufzeit-Importe.

## Tests

245 Tests, lokal in rund 123 Sekunden mit `pytest tests -q` (gemessen 2 min 3 s, ohne `-n`; Windows, Python 3.14; die CI läuft mit 3.12 <!-- lint-ok: dezimalpunkt -->): Einheiten gegen Handrechnung, Orakel, Claims (Zahl und Test in der Tabelle oben), Randfälle, Verdikte, Presets, Cache-Schlüssel, Layout, AppTest, Texte und Permalink, Footer, Laufzeit-Importe. Die langsamsten sind die AppTest-Läufe über alle Regler (rund 43 Sekunden), der Zählung im breiten Raster (rund 9 Sekunden) und der erste App-Lauf.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Grenzen, Formeln |
| `hup_algorithm.py` | Kern: Reaktion, Gleichgewichte, First-Best, Wirkungsgrad, Wiederholung, Rubinstein |
| `hup_constants.py` | Regler-Grenzen, Numerik, Raster, Farben, Presets |
| `hup_evaluation.py` | Experimente (Raster), Verdikte als reine Funktionen, Schlüssel für den Cache |
| `hup_layout.py` | Fester Kopf (Stylesheet) |
| `hup_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `hup_scenario.py` | Modell: Überschuss, Gegenmittel, Auszahlungen |
| `hup_texts.py` | Annahmen, Grenzen und bekannte Probleme (App und README) |
| `hup_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur Orakel) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): streamlit, numpy, pandas, plotly |
| `tests/` | Einheiten, Orakel, Claims, Randfälle, Verdikte, Presets, Layout, AppTest, Cache-Schlüssel, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

Vertragsrecht und Durchsetzung, Wettbewerb um den Partner (Bolton und Whinston, Che und Hausch: nicht geprüft), unvollständige Information, Kreditbeschränkungen, gemischte Gleichgewichte, andere Strafstrategien als Grim-Trigger, Ausgleichszahlungen in der Wiederholung, PDF-Export.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die Python-Version der Streamlit-Cloud-Einstellung ist hier nicht festgelegt; die CI läuft mit 3.12. <!-- lint-ok: dezimalpunkt -->

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
