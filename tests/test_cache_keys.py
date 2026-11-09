"""Cache-Schlüssel der App: jede teure Berechnung bekommt nur die Regler, von denen sie abhängt. Hier: Rechnung mit dem Schlüssel = Rechnung mit allen Reglern,
auch wenn die übrigen Regler verstellt sind (sonst zeigte der Cache ein falsches Ergebnis)."""

import pytest

import hup_evaluation as ev

SETTINGS = [
    ev.Settings(),
    ev.Settings(theta=80, gamma=60, kappa=150, a=130, lam_v=40, lam_s=20, phi=30, psi=20, delta=70),
    ev.Settings(theta=20, gamma=100, kappa=60, a=70, lam_v=0, lam_s=60, phi=0, psi=0, delta=99),
]

CASES = [
    ("theta", ev.sweep_theta, ev.key_world),
    ("gamma", ev.sweep_gamma, ev.key_gamma_sweep),
    ("asym", ev.asymmetry_rows, ev.key_world),
    ("procedure", ev.procedure_rows, ev.key_world),
    ("contract", ev.contract_curve, ev.key_contract),
    ("remedy", ev.remedy_table, ev.key_remedy),
    ("multi", ev.multiplicity_grid, ev.key_multi),
]


@pytest.mark.parametrize("name,func,key", CASES, ids=[c[0] for c in CASES])
@pytest.mark.parametrize("settings", SETTINGS, ids=["standard", "alles-verstellt", "raender"])
def test_result_with_the_key_equals_result_with_all_settings(name, func, key, settings):
    assert func(settings) == func(key(settings))


def test_keys_ignore_exactly_the_irrelevant_regler():
    s = SETTINGS[1]
    assert ev.key_world(s) == ev.key_world(ev.Settings(gamma=s.gamma, kappa=s.kappa, a=s.a, theta=1, lam_v=99, phi=50, psi=40, delta=3))
    assert ev.key_multi(s) == ev.key_multi(ev.Settings(**{**s.__dict__, "delta": 0}))
    assert ev.key_remedy(s) != ev.key_remedy(ev.Settings(**{**s.__dict__, "delta": 0}))
