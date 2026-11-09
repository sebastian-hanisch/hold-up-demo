"""Permalink (Begrenzen), Presets und Aktivmarkierung (Standardmuster aus dem Demo-Portfolio). Alle Regler laufen in ganzen Prozent."""

from dataclasses import dataclass

import streamlit as st

import hup_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None


def _spec(url_param: str, bounds: tuple[int, int, int]) -> SettingSpec:
    lo, hi, default = bounds
    return SettingSpec(url_param, int, default, lo, hi)


SETTING_SPECS = {
    "theta_slider": _spec("th", C.THETA_PCT),
    "gamma_slider": _spec("ga", C.GAMMA_PCT),
    "kappa_slider": _spec("ka", C.KAPPA_PCT),
    "a_slider": _spec("pa", C.A_PCT),
    "lam_v_slider": _spec("lv", C.LAM_V_PCT),
    "lam_s_slider": _spec("ls", C.LAM_S_PCT),
    "phi_slider": _spec("ph", C.PHI_PCT),
    "psi_slider": _spec("ps", C.PSI_PCT),
    "delta_slider": _spec("de", C.DELTA_PCT),
}
PRESET_KEYS = {
    "theta": "theta_slider", "gamma": "gamma_slider", "kappa": "kappa_slider", "a": "a_slider", "lam_v": "lam_v_slider",
    "lam_s": "lam_s_slider", "phi": "phi_slider", "psi": "psi_slider", "delta": "delta_slider",
}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp_to_bounds(spec: SettingSpec, value):
    """Begrenzt einen Wert auf die Reglergrenzen (Permalink: auch hand-editierte Adresszeilen dürfen den Regler nicht sprengen)."""
    if spec.lo is not None:
        value = max(spec.lo, value)
    if spec.hi is not None:
        value = min(spec.hi, value)
    return value


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            st.session_state[state_key] = clamp_to_bounds(spec, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden: es setzt alle Regler, danach sind sie wieder frei.")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )
