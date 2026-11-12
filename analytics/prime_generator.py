import math
import secrets
import time

from core.miller_rabin import miller_rabin_test
from core.number_theory import SMALL_PRIMES


def generate_prime(bits: int, k: int = 40) -> tuple[int, int, float]:
    """
    Generates a cryptographically strong probable prime of specified bit length.
    Returns: (prime_candidate, attempts_count, elapsed_ms)
    """
    if bits < 2:
        raise ValueError("Tub son hosil qilish uchun bits >= 2 bo'lishi kerak")

    t0 = time.perf_counter()
    if bits == 2:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return 3, 1, round(elapsed_ms, 3)

    attempts = 0
    while True:
        attempts += 1
        # Set highest bit (to guarantee bit length) and lowest bit (odd number)
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1

        # Fast pre-filtering using 2000 small primes
        divisible = False
        for p in SMALL_PRIMES:
            if candidate == p:
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                return candidate, attempts, round(elapsed_ms, 3)
            if candidate % p == 0:
                divisible = True
                break

        if divisible:
            continue

        # Full Miller-Rabin test with k rounds
        mr_res = miller_rabin_test(candidate, k=k, skip_prefilter=True)
        if mr_res.is_prime:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return candidate, attempts, round(elapsed_ms, 3)


def generate_rsa_pair(key_bits: int = 1024, k: int = 40) -> dict:
    """
    Generates an RSA key modulus pair (p, q, N, phi) with performance statistics.
    N has bit length approximately equal to key_bits.
    """
    if key_bits < 8:
        raise ValueError("RSA kalit uzunligi key_bits >= 8 bo'lishi kerak")

    t0 = time.perf_counter()
    p_bits = key_bits // 2
    q_bits = key_bits - p_bits

    p, attempts_p, _ = generate_prime(p_bits, k=k)

    while True:
        q, attempts_q, _ = generate_prime(q_bits, k=k)
        if p != q:
            # Check difference is not trivially small (Fermat factorization protection)
            min_bits = min(p_bits, q_bits)
            diff_threshold = 1 << max(1, min_bits - 100)
            if abs(p - q) > diff_threshold:
                break

    N = p * q
    phi = (p - 1) * (q - 1)
    total_candidates = attempts_p + attempts_q

    # PNT theoretical expected odd candidates: (key_bits * ln(2)) / 2
    theoretical_expected = round((key_bits * math.log(2)) / 2.0, 2)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)

    return {
        "p": p,
        "q": q,
        "N": N,
        "phi": phi,
        "total_candidates_tested": total_candidates,
        "theoretical_expected_tests": theoretical_expected,
        "elapsed_ms": elapsed_ms,
    }
