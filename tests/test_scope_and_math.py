"""Regression checks for strict project scope and mathematical truthfulness."""
from pathlib import Path

import pytest
import core.witness as witness
from core.miller_rabin import miller_rabin_test
from core.solovay_strassen import solovay_strassen_test
from core.fermat import fermat_test

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("n", "base", "d", "s", "expected"),
    [
        (21, 2, 5, 2, 16),  # last squared residue: 2**10 mod 21, NOT 2**20
        (15, 2, 7, 1, 8),  # no squaring: the last residue is 2**7 mod 15
        (9, 2, 1, 3, 7),   # two squarings: 2**4 mod 9
    ],
)
def test_miller_rabin_composite_log_is_correct_exponent(
    monkeypatch, n, base, d, s, expected
):
    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: base - 2)
    result = miller_rabin_test(n, k=1, skip_prefilter=True)
    assert result.verdict == "Composite"
    record = result.logs[-1]
    assert record.computed_value == str(expected)
    assert record.expression == f"{base}^({d}*2^{s - 1}) mod {n}"
    assert pow(base, d * 2 ** (s - 1), n) == expected


def test_carmichael_solovay_strassen_has_liar_and_witness(monkeypatch):
    # A single randomized round does not always expose a Carmichael number.
    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: 0)
    assert fermat_test(561, k=1, skip_prefilter=True).verdict == "Probably Prime"
    assert solovay_strassen_test(561, k=1, skip_prefilter=True).verdict == "Probably Prime"

    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: 3)
    result = solovay_strassen_test(561, k=1, skip_prefilter=True)
    assert result.verdict == "Composite"
    assert result.logs[-1].witness_a == 5


def test_only_topic_required_sections_in_main_app():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'tab1, tab3 = st.tabs([' in source
    assert "🔍 Sonni tekshirish" in source
    assert "📊 Algoritmlarni taqqoslash" in source
    assert "primeguard_show_carmichael" in source
    assert "with tab4:" not in source
    assert "generate_rsa_pair(" not in source
    assert "rsa_security_k" not in source
    assert "candidate > 1_000_000" in source
    assert "at least 8" not in source
