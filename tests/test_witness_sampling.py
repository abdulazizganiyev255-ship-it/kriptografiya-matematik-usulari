import pytest
import core.witness as witness
from core.fermat import fermat_test
from core.solovay_strassen import solovay_strassen_test
from core.miller_rabin import miller_rabin_test

ALGORITHMS = (fermat_test, solovay_strassen_test, miller_rabin_test)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("invalid", [0, -1, True, 1.5, "3", 4097])
def test_invalid_rounds(algorithm, invalid):
    with pytest.raises(ValueError):
        algorithm(17, k=invalid)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("invalid", [True, 17.0, "17"])
def test_invalid_candidate_type(algorithm, invalid):
    with pytest.raises(TypeError):
        algorithm(invalid)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_independent_draws_allow_repeated_base(algorithm, monkeypatch):
    calls = []
    def randbelow(upper):
        calls.append(upper)
        return 0
    monkeypatch.setattr(witness.secrets, "randbelow", randbelow)
    result = algorithm(17, k=5, skip_prefilter=True)
    assert result.verdict == "Probably Prime"
    assert result.rounds_run == 5
    assert [log.witness_a for log in result.logs] == [2] * 5
    assert calls == [14] * 5


def test_coprime_rejection_sampling(monkeypatch):
    values = iter([1, 0])
    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: next(values))
    assert witness.draw_witness(21, coprime_only=True) == 2


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_gcd_witness_is_composite(algorithm, monkeypatch):
    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: 1)
    result = algorithm(21, k=1, skip_prefilter=True)
    assert result.verdict == "Composite"
    assert result.rounds_run == 1
    assert "EKUB" in result.logs[-1].note


def test_carmichael_base_two(monkeypatch):
    monkeypatch.setattr(witness.secrets, "randbelow", lambda upper: 0)
    assert fermat_test(561, k=1, skip_prefilter=True, coprime_only=True).verdict == "Probably Prime"
    assert solovay_strassen_test(561, k=1, skip_prefilter=True, coprime_only=True).verdict == "Composite"
    assert miller_rabin_test(561, k=1, skip_prefilter=True, coprime_only=True).verdict == "Composite"
