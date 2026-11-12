import pandas as pd
import pytest

from analytics.benchmark import run_benchmark
from analytics.carmichael import CARMICHAEL_NUMBERS, analyze_carmichael
from analytics.prime_generator import generate_prime, generate_rsa_pair
from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.models import PrimalityResult, RoundLog
from core.number_theory import (
    SMALL_PRIMES,
    check_small_primes,
    gcd,
    jacobi_symbol,
)
from core.solovay_strassen import solovay_strassen_test


# ==========================================
# 1. Models & Dataclass Tests
# ==========================================
def test_models_round_log():
    log = RoundLog(
        round_idx=1,
        witness_a=5,
        expression="5^16 mod 17",
        computed_value="1",
        passed=True,
        note="Passed",
    )
    assert log.round_idx == 1
    assert log.witness_a == 5
    assert log.passed is True


def test_models_primality_result():
    res = PrimalityResult(
        algorithm="Miller-Rabin",
        n=17,
        bit_length=5,
        is_prime=True,
        verdict="Probably Prime",
        rounds_requested=20,
        rounds_run=20,
        error_bound="<= (1/4)^20",
        elapsed_ms=1.23,
        pre_filtered=False,
        logs=[],
    )
    assert res.algorithm == "Miller-Rabin"
    assert res.is_prime is True
    assert res.logs == []


# ==========================================
# 2. Number Theory Tests
# ==========================================
def test_small_primes():
    assert len(SMALL_PRIMES) == 2000
    assert SMALL_PRIMES[0] == 2
    assert SMALL_PRIMES[1] == 3
    assert SMALL_PRIMES[-1] == 17389

    # Verify each number in SMALL_PRIMES is indeed prime using trial division
    for p in SMALL_PRIMES[:50]:
        for d in range(2, int(p**0.5) + 1):
            assert p % d != 0


def test_gcd():
    assert gcd(54, 24) == 6
    assert gcd(24, 54) == 6
    assert gcd(-54, 24) == 6
    assert gcd(54, -24) == 6
    assert gcd(101, 103) == 1
    assert gcd(0, 15) == 15
    assert gcd(15, 0) == 15
    assert gcd(0, 0) == 0


def test_jacobi_symbol_invalid_inputs():
    with pytest.raises(ValueError):
        jacobi_symbol(2, 0)
    with pytest.raises(ValueError):
        jacobi_symbol(2, -5)
    with pytest.raises(ValueError):
        jacobi_symbol(2, 6)  # Even n not allowed


def test_jacobi_symbol_known_values():
    assert jacobi_symbol(0, 1) == 1
    assert jacobi_symbol(0, 5) == 0
    assert jacobi_symbol(1, 15) == 1
    assert jacobi_symbol(2, 15) == 1  # 15 % 8 == 7 -> (2/15) = 1
    assert jacobi_symbol(3, 5) == -1
    assert jacobi_symbol(10, 21) == -1
    assert jacobi_symbol(7, 11) == -1
    assert jacobi_symbol(9, 13) == 1  # 9 = 3^2, quadratic residue

    # Multiplicative property test: (ab/n) = (a/n)(b/n)
    for a in range(1, 20):
        for b in range(1, 20):
            assert jacobi_symbol(a * b, 15) == jacobi_symbol(a, 15) * jacobi_symbol(b, 15)


def test_check_small_primes():
    # Negative and <= 1
    assert check_small_primes(-5)[0] is False
    assert check_small_primes(0)[0] is False
    assert check_small_primes(1)[0] is False

    # Small primes
    assert check_small_primes(2)[0] is True
    assert check_small_primes(3)[0] is True
    assert check_small_primes(17389)[0] is True

    # Small composites
    assert check_small_primes(4)[0] is False
    assert check_small_primes(9)[0] is False
    assert check_small_primes(15)[0] is False

    # Larger numbers not divisible by small primes
    large_cand = 2**61 - 1  # Mersenne prime M61
    assert check_small_primes(large_cand)[0] is None


# ==========================================
# 3. Fermat Primality Test
# ==========================================
def test_fermat_invalid_k():
    with pytest.raises(ValueError):
        fermat_test(17, k=0)


def test_fermat_small_and_prefiltered():
    res_neg = fermat_test(-1)
    assert res_neg.is_prime is False
    assert res_neg.pre_filtered is True

    res_two = fermat_test(2)
    assert res_two.is_prime is True
    assert res_two.verdict == "Prime"
    assert res_two.pre_filtered is True

    res_comp = fermat_test(15)
    assert res_comp.is_prime is False
    assert res_comp.verdict == "Composite"
    assert res_comp.pre_filtered is True


def test_fermat_primes():
    primes = [1009, 7919, 17389, 104729]
    for p in primes:
        res = fermat_test(p, k=10)
        assert res.is_prime is True
        assert res.verdict in ("Prime", "Probably Prime")


def test_fermat_composites_without_prefilter():
    # Test composite numbers with skip_prefilter to verify witness detection
    composites = [91, 119, 121, 209, 341]
    for c in composites:
        res = fermat_test(c, k=20, skip_prefilter=True)
        assert res.is_prime is False
        assert res.verdict == "Composite"
        assert res.rounds_run >= 1
        assert len(res.logs) == res.rounds_run
        assert res.logs[-1].passed is False


# ==========================================
# 4. Solovay-Strassen Primality Test
# ==========================================
def test_solovay_strassen_invalid_k():
    with pytest.raises(ValueError):
        solovay_strassen_test(17, k=0)


def test_solovay_strassen_primes():
    primes = [2, 3, 17, 101, 1009, 104729]
    for p in primes:
        res = solovay_strassen_test(p, k=10)
        assert res.is_prime is True


def test_solovay_strassen_composites():
    composites = [4, 9, 15, 91, 121]
    for c in composites:
        res = solovay_strassen_test(c, k=10)
        assert res.is_prime is False


def test_solovay_strassen_rejects_carmichael():
    # Solovay-Strassen must detect Carmichael number 561 as composite even without pre-filter
    res = solovay_strassen_test(561, k=20, skip_prefilter=True, coprime_only=True)
    assert res.is_prime is False
    assert res.verdict == "Composite"


# ==========================================
# 5. Miller-Rabin Primality Test
# ==========================================
def test_miller_rabin_invalid_k():
    with pytest.raises(ValueError):
        miller_rabin_test(17, k=0)


def test_miller_rabin_primes():
    primes = [2, 3, 13, 101, 1009, 2147483647]  # 2^31 - 1
    for p in primes:
        res = miller_rabin_test(p, k=15)
        assert res.is_prime is True
        assert res.verdict in ("Prime", "Probably Prime")
        assert res.error_bound == "<= (1/4)^15" or res.pre_filtered is True


def test_miller_rabin_composites():
    composites = [0, 1, 4, 15, 91, 121, 1000]
    for c in composites:
        res = miller_rabin_test(c, k=10)
        assert res.is_prime is False
        assert res.verdict == "Composite"


def test_miller_rabin_rejects_carmichael():
    # Miller-Rabin must detect Carmichael numbers as composite even with coprime bases
    for c in [561, 1105, 1729]:
        res = miller_rabin_test(c, k=20, skip_prefilter=True, coprime_only=True)
        assert res.is_prime is False
        assert res.verdict == "Composite"


# ==========================================
# 6. Carmichael Analytics Tests
# ==========================================
def test_carmichael_constants():
    expected = [561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341, 41041, 825265]
    assert CARMICHAEL_NUMBERS == expected


def test_analyze_carmichael():
    analysis = analyze_carmichael(561, k=20)
    assert analysis["n"] == 561
    assert "fermat" in analysis
    assert "solovay_strassen" in analysis
    assert "miller_rabin" in analysis
    assert "fermat_fooled" in analysis

    # Fermat must be fooled (is_prime == True) for coprime bases on Carmichael numbers
    assert analysis["fermat"].is_prime is True
    # Solovay-Strassen and Miller-Rabin must NOT be fooled
    assert analysis["solovay_strassen"].is_prime is False
    assert analysis["miller_rabin"].is_prime is False
    assert analysis["fermat_fooled"] is True


# ==========================================
# 7. Prime & RSA Generator Tests
# ==========================================
def test_generate_prime_invalid():
    with pytest.raises(ValueError):
        generate_prime(1)


def test_generate_prime():
    prime, attempts, elapsed_ms = generate_prime(64, k=20)
    assert prime.bit_length() == 64
    assert prime % 2 == 1
    assert attempts >= 1
    assert elapsed_ms >= 0
    # Confirm with 40 rounds of Miller-Rabin
    assert miller_rabin_test(prime, k=40).is_prime is True


def test_generate_rsa_pair_invalid():
    with pytest.raises(ValueError):
        generate_rsa_pair(key_bits=4)


def test_generate_rsa_pair():
    rsa = generate_rsa_pair(key_bits=128, k=20)
    required_keys = [
        "p",
        "q",
        "N",
        "phi",
        "total_candidates_tested",
        "theoretical_expected_tests",
        "elapsed_ms",
    ]
    for key in required_keys:
        assert key in rsa

    p = rsa["p"]
    q = rsa["q"]
    N = rsa["N"]
    phi = rsa["phi"]

    assert p != q
    assert N == p * q
    assert phi == (p - 1) * (q - 1)
    assert abs(N.bit_length() - 128) <= 1
    assert rsa["total_candidates_tested"] >= 2
    assert rsa["theoretical_expected_tests"] > 0
    assert rsa["elapsed_ms"] >= 0


# ==========================================
# 8. Benchmark Tests
# ==========================================
def test_run_benchmark():
    df = run_benchmark(bit_sizes=[64, 128], k=5, trials=1)
    assert isinstance(df, pd.DataFrame)
    expected_cols = [
        "Bit_Length",
        "Algorithm",
        "Avg_Time_ms",
        "Min_Time_ms",
        "Max_Time_ms",
        "Error_Bound",
    ]
    assert list(df.columns) == expected_cols
    assert len(df) == 6  # 2 bit sizes * 3 algorithms
    algorithms = set(df["Algorithm"])
    assert algorithms == {"Fermat", "Solovay-Strassen", "Miller-Rabin"}
