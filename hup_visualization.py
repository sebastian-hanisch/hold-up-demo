"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import hup_algorithm as A
import hup_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.22), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_investments(res):
    """Investition je Seite: effizient (First-Best) gegen Gleichgewicht."""
    sides = ["V (Verlader)", "S (Spediteur)"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sides, y=list(res.fb), name="Effizient (First-Best)", marker_color=C.COLOR_FB, hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Bar(x=sides, y=list(res.eq), name="Gleichgewicht", marker_color=C.COLOR_EQ, hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Investition x")
    return _base(fig, 320)


def build_best_responses(p, res, points=61):
    """Reaktionskurven im (x_V, x_S)-Feld: die Schnittpunkte sind die Gleichgewichte, das Quadrat ist der effiziente Punkt."""
    top = max(1.2 * max(res.fb), 1.2 * max((max(e) for e in res.equilibria), default=0.0), 0.5)
    grid = np.linspace(0.0, top, points)
    s_reacts = A.best_response_s(grid, p)   # S antwortet auf x_V
    v_reacts = A.best_response_v(grid, p)   # V antwortet auf x_S
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grid, y=s_reacts, mode="lines", name="Antwort von S auf x_V", line=dict(color=C.COLOR_S, width=3),
                             hovertemplate="x_V = %{x:.2f}: S wählt %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=v_reacts, y=grid, mode="lines", name="Antwort von V auf x_S", line=dict(color=C.COLOR_V, width=3),
                             hovertemplate="x_S = %{y:.2f}: V wählt %{x:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[e[0] for e in res.equilibria], y=[e[1] for e in res.equilibria], mode="markers", name="Gleichgewichte",
                             marker=dict(color=C.COLOR_EQ, size=12, symbol="circle"), hovertemplate="Gleichgewicht (%{x:.2f}; %{y:.2f})<extra></extra>"))
    fig.add_trace(go.Scatter(x=[res.fb[0]], y=[res.fb[1]], mode="markers", name="Effizient", marker=dict(color=C.COLOR_FB, size=13, symbol="square"),
                             hovertemplate="Effizient (%{x:.2f}; %{y:.2f})<extra></extra>"))
    fig.update_xaxes(title_text="Investition von V", range=[0, top])
    fig.update_yaxes(title_text="Investition von S", range=[0, top])
    return _base(fig, 380)


def build_theta(rows):
    """Wirkungsgrad über theta: Gitter bei der eingestellten Komplementarität, Gitter additiv und die geschlossene Formel."""
    xs = [r["theta"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[100 * r["eff_formula"] for r in rows], mode="lines", name="Geschlossene Formel (additiv)",
                             line=dict(color=C.COLOR_FORMULA, width=2, dash="dot"), hovertemplate="θ = %{x:.1f}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100 * r["eff_additive"] for r in rows], mode="markers", name="Gitter (additiv)",
                             marker=dict(color=C.COLOR_V, size=9), hovertemplate="θ = %{x:.1f}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100 * r["eff"] for r in rows], mode="lines+markers", name="Gitter (eingestellte Komplementarität)",
                             line=dict(color=C.COLOR_EQ, width=2), hovertemplate="θ = %{x:.1f}: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Anteil θ von V am verhandelten Überschuss")
    fig.update_yaxes(title_text="Wirkungsgrad (%)", range=[0, 105])
    return _base(fig)


def build_remedies(table):
    """Wirkungsgrad je Gegenmittel in der eingestellten Welt."""
    rows = table["rows"]
    fig = go.Figure(go.Bar(x=[r["name"] for r in rows], y=[100 * r["eff"] for r in rows], marker_color=[C.COLOR_FORMULA] + [C.COLOR_FB] * (len(rows) - 1),
                           hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_yaxes(title_text="Wirkungsgrad (%)", range=[0, 105])
    return _base(fig, 320)


def build_contract(rows):
    """Wirkungsgrad über den Vertragsanteil phi."""
    fig = go.Figure(go.Scatter(x=[100 * r["phi"] for r in rows], y=[100 * r["eff"] for r in rows], mode="lines+markers", line=dict(color=C.COLOR_LINE, width=3),
                               hovertemplate="φ = %{x:.0f} %: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Fest zugesagter Anteil φ (%)")
    fig.update_yaxes(title_text="Wirkungsgrad (%)", range=[0, 105])
    return _base(fig, 320)


def build_asymmetry(rows):
    """Investitionsquote je Seite über theta."""
    xs = [r["theta"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[100 * r["quote_v"] for r in rows], mode="lines+markers", name="V", line=dict(color=C.COLOR_V, width=3),
                             hovertemplate="θ = %{x:.1f}: V investiert %{y:.0f} % des Effizienten<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100 * r["quote_s"] for r in rows], mode="lines+markers", name="S", line=dict(color=C.COLOR_S, width=3),
                             hovertemplate="θ = %{x:.1f}: S investiert %{y:.0f} % des Effizienten<extra></extra>"))
    fig.update_xaxes(title_text="Anteil θ von V am verhandelten Überschuss")
    fig.update_yaxes(title_text="Investition im Verhältnis zum Effizienten (%)", range=[0, 105])
    return _base(fig, 320)
