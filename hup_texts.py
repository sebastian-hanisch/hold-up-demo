"""Feste Texte der App, die auch in der README stehen (ein Test vergleicht sie): Annahmen, Grenzen, bekannte Probleme.

Zahlen stehen hier nur, wenn sie Einstellungen sind (Regler, Raster); Messzahlen kommen mit f-String aus der Rechnung oder stehen in der README mit Testverweis."""

ASSUMPTIONS_MARKDOWN = """\
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
"""

LITERATUR_HEAD = "**Literatur** (Autoren, Jahr, Zeitschrift und Seiten über Bibliographien bestätigt; Volltexte nicht gelesen, nur Abstracts und Zusammenfassungen)"
LITERATUR = [
    "- Klein, B., Crawford, R. G., Alchian, A. A. (1978): Vertical Integration, Appropriable Rents, and the Competitive Contracting Process. Journal of Law and Economics 21(2), 297–326.",
    "- Williamson, O. E. (1979): Transaction-Cost Economics: The Governance of Contractual Relations. Journal of Law and Economics 22(2), 233–261.",
    "- Grout, P. A. (1984): Investment and Wages in the Absence of Binding Contracts: A Nash Bargaining Approach. Econometrica 52(2), 449–460.",
    "- Grossman, S. J., Hart, O. D. (1986): The Costs and Benefits of Ownership: A Theory of Vertical and Lateral Integration. Journal of Political Economy 94(4), 691–719.",  # lint-ok: ascii-umlaut
    "- Tirole, J. (1986): Procurement and Renegotiation. Journal of Political Economy 94(2), 235–259.",
    "- Hart, O., Moore, J. (1990): Property Rights and the Nature of the Firm. Journal of Political Economy 98(6), 1119–1158.",
    "- Ellingsen, T., Robles, J. (2000): Does Evolution Solve the Hold-up Problem? SSE/EFI Working Paper Series in Economics and Finance Nr. 358 (die Zeitschriftenfassung von 2002 ist nicht geprüft). Abstract gelesen: Das übliche Unterinvestitionsergebnis hängt am Verhandlungsspiel und am Gleichgewichtsbegriff.",
    "- Nash, J. F. (1950): The Bargaining Problem. Econometrica 18(2), 155–162.",
    "- Rubinstein, A. (1982): Perfect Equilibrium in a Bargaining Model. Econometrica 50(1), ab Seite 97 (Seitenende nach Quelle 109 oder 110, nicht geklärt).",
]
