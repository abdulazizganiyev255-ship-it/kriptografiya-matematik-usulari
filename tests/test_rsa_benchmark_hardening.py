"""Regression coverage for RSA input bounds and benchmark result consistency."""

from types import SimpleNamespace

import pytest

import analytics.benchmark as benchmark
from analytics.prime_generator import generate_prime, generate_rsa_pair


@pytest.mark.parametrize("k", [True, 0, -1, 4097, 1.5, "3"])
def test_generator_rejects_invalid_rounds(k):
    with pytest.raises(ValueError):
        generate_prime(16, k=k)
    with pytest.raises(ValueError):
        generate_rsa_pair(64, k=k)


@pytest.mark.parametrize("bits", [0, 1, 4097, True, 32.5, "64"])
def test_prime_generator_rejects_invalid_bit_sizes(bits):
    with pytest.raises((ValueError, TypeError)):
        generate_prime(bits)


@pytest.mark.parametrize("bits", [0, 15, 8193, True, 128.5, "64"])
def test_rsa_generator_rejects_invalid_modulus_sizes(bits):
    with pytest.raises((ValueError, TypeError)):
        generate_rsa_pair(bits)


@pytest.mark.parametrize("attempts", [0, -1, True, 1_000_001, 1.2, "5"])
def test_prime_generator_attempt_bounds(attempts):
    with pytest.raises(ValueError):
        generate_prime(32, max_attempts=attempts)


@pytest.mark.parametrize("attempts", [0, -1, True, 10_001, 1.2, "5"])
def test_rsa_pair_attempt_bounds(attempts):
    with pytest.raises(ValueError):
        generate_rsa_pair(64, max_pair_attempts=attempts)


def test_benchmark_marks_disagreeing_verdicts(monkeypatch):
    monkeypatch.setattr(benchmark, "generate_prime", lambda bits, k: (257, 1, 0))
    monkeypatch.setattr(benchmark, "_make_semiprime", lambda bits, k: 259)
    sequence = iter([
        ("Probably Prime", 5, "<= (1/4)^5"),
        ("Composite", 2, "0"),
        ("Probably Prime", 5, "<= (1/4)^5"),
        ("Composite", 1, "0"),
        ("Composite", 1, "0"),
        ("Composite", 1, "0"),
        ("Composite", 1, "0"),
        ("Composite", 1, "0"),
    ])
    def test_algorithm(n, k, skip_prefilter):
        verdict, rounds, bound = next(sequence)
        return SimpleNamespace(verdict=verdict, rounds_run=rounds, error_bound=bound)

    monkeypatch.setattr(benchmark, "ALGORITHMS", (("Controlled", test_algorithm),))
    frame = benchmark.run_benchmark(bit_sizes=[9], k=5, trials=3)
    prime = frame[frame["Candidate_Type"] == "Tub nomzod"].iloc[0]
    composite = frame[frame["Candidate_Type"] != "Tub nomzod"].iloc[0]
    assert prime["Verdict"] == "Mixed"
    assert prime["Verdict_Consistency"] == "Mixed"
    assert prime["Error_Bound"] == "Varies"
    assert prime["Avg_Rounds_Run"] == pytest.approx((2 + 5 + 1) / 3)
    assert prime["Min_Rounds_Run"] == 1
    assert prime["Max_Rounds_Run"] == 5
    assert composite["Verdict"] == "Composite"
    assert composite["Verdict_Consistency"] == "Consistent"


def test_benchmark_has_actual_round_metrics():
    frame = benchmark.run_benchmark(bit_sizes=[64], k=5, trials=2)
    assert (frame["Avg_Rounds_Run"] >= 0).all()
    assert (frame["Min_Rounds_Run"] <= frame["Max_Rounds_Run"]).all()
    assert set(frame["Verdict_Consistency"]).issubset({"Consistent", "Mixed"})
