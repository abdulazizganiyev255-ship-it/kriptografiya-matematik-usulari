"""Mathematical and UI regression checks for PrimeGuard's round explorer."""
from dataclasses import replace
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import core.witness as witness
from analytics.round_explainer import build_round_trace
from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.solovay_strassen import solovay_strassen_test


def use_base(monkeypatch, base):
    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: base - 2)


@pytest.mark.parametrize(
    "algorithm,n,base,function,expect_pass",
    [
        ("Fermat", 561, 2, fermat_test, True),  # Carmichael liar.
        ("Fermat", 15, 2, fermat_test, False),
        ("Solovay-Strassen", 561, 5, solovay_strassen_test, False),
        ("Solovay-Strassen", 17, 2, solovay_strassen_test, True),
        ("Miller-Rabin", 17, 2, miller_rabin_test, True),
        ("Miller-Rabin", 21, 2, miller_rabin_test, False),
        ("Miller-Rabin", 561, 2, miller_rabin_test, False),
    ],
)
def test_trace_matches_actual_round(
    monkeypatch, algorithm, n, base, function, expect_pass
):
    use_base(monkeypatch, base)
    outcome = function(n, k=1, skip_prefilter=True)
    assert len(outcome.logs) == 1
    trace = build_round_trace(algorithm, n, outcome.logs[0])
    assert trace.matches_log
    assert trace.computed_pass is expect_pass
    assert len(trace.steps) >= 4
    assert trace.steps[0].value == f"a = {base}"
    assert trace.steps[-1].status == ("pass" if expect_pass else "fail")


@pytest.mark.parametrize(
    "algorithm,function",
    [
        ("Fermat", fermat_test),
        ("Solovay-Strassen", solovay_strassen_test),
        ("Miller-Rabin", miller_rabin_test),
    ],
)
def test_gcd_composite_witness(monkeypatch, algorithm, function):
    use_base(monkeypatch, 3)
    outcome = function(21, k=1, skip_prefilter=True)
    trace = build_round_trace(algorithm, 21, outcome.logs[-1])
    assert trace.matches_log
    assert not trace.computed_pass
    assert any("O'zaro tublik" in step.title for step in trace.steps)


def test_trace_detects_tampered_log(monkeypatch):
    use_base(monkeypatch, 2)
    outcome = miller_rabin_test(17, k=1, skip_prefilter=True)
    altered = replace(outcome.logs[0], computed_value="forged")
    trace = build_round_trace("Miller-Rabin", 17, altered)
    assert not trace.matches_log


def test_trace_rejects_unsupported_inputs(monkeypatch):
    use_base(monkeypatch, 2)
    record = fermat_test(17, k=1, skip_prefilter=True).logs[0]
    with pytest.raises(ValueError):
        build_round_trace("Unknown", 17, record)
    with pytest.raises(ValueError):
        build_round_trace("Fermat", 4, record)


def test_streamlit_reuses_sampled_bases_after_navigation():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=30).run()
    assert not app.exception
    app.button(key="primeguard_start_audit").click().run()
    assert not app.exception
    before = app.session_state["primeguard_last_audit"]
    initial_bases = [round_log.witness_a for round_log in before["miller_rabin"]["logs"]]
    assert len(initial_bases) > 0

    # Navigate the trace; this must not execute probabilistic tests again.
    app.button(key="primeguard_audit_next").click().run()
    assert not app.exception
    after = app.session_state["primeguard_last_audit"]
    assert [round_log.witness_a for round_log in after["miller_rabin"]["logs"]] == initial_bases
    assert app.session_state["primeguard_audit_trace_step"] == 1

    app.button(key="primeguard_audit_previous").click().run()
    assert not app.exception
    assert app.session_state["primeguard_audit_trace_step"] == 0


def test_carmichael_navigator_persists_original_witnesses():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=30).run()
    app.button(key="primeguard_start_carmichael").click().run()
    assert not app.exception
    saved = app.session_state["primeguard_last_carmichael"]
    assert saved["report"]["is_carmichael"] is True
    witnesses = [
        round_log.witness_a for round_log in saved["fermat"]["logs"]
    ]
    assert witnesses

    app.button(key="primeguard_carmichael_next").click().run()
    assert not app.exception
    after = app.session_state["primeguard_last_carmichael"]
    assert [round_log.witness_a for round_log in after["fermat"]["logs"]] == witnesses
    assert app.session_state["primeguard_carmichael_trace_step"] == 1
