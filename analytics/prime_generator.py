import math
import secrets
import time

from core.miller_rabin import miller_rabin_test
from core.number_theory import SMALL_PRIMES


def _validate_rounds(k: int) -> None:
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("Miller–Rabin raundlari k >= 1 butun son bo'lishi kerak")


def generate_prime(bits: int, k: int = 40, max_attempts: int = 1_000_000) -> tuple[int, int, float]:
    """
    Generate a probable prime with exactly the requested bit length.
    Returns (candidate, attempts, elapsed_ms). This is educational generation,
    not a certified production key-generation routine.
    """
    if not isinstance(bits, int) or isinstance(bits, bool) or bits < 2:
        raise ValueError("Tub son yaratish uchun bits >= 2 butun son bo'lishi kerak")
    _validate_rounds(k)
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
        raise ValueError("max_attempts kamida 1 bo'lishi kerak")

    started = time.perf_counter()
    if bits == 2:
        return 3, 1, round((time.perf_counter() - started) * 1000.0, 3)

    for attempts in range(1, max_attempts + 1):
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1

        divisible = False
        for p in SMALL_PRIMES:
            if candidate == p:
                return candidate, attempts, round((time.perf_counter() - started) * 1000.0, 3)
            if candidate % p == 0:
                divisible = True
                break
        if divisible:
            continue

        result = miller_rabin_test(candidate, k=k, skip_prefilter=True)
        if result.is_prime:
            return candidate, attempts, round((time.perf_counter() - started) * 1000.0, 3)

    raise RuntimeError(
        f"{max_attempts} urinishda {bits}-bit ehtimoliy tub son topilmadi; limitni oshiring yoki qayta urinib ko'ring"
    )


def generate_rsa_pair(key_bits: int = 1024, k: int = 40, max_pair_attempts: int = 10_000) -> dict:
    """
    Generate educational RSA prime parameters p, q, N and phi(N).

    The returned modulus N is guaranteed to have exactly key_bits bits.
    p and q are independently generated probable primes. This function does
    not create e/d, CRT parameters, a serialized key, or a production RSA key.
    """
    if not isinstance(key_bits, int) or isinstance(key_bits, bool) or key_bits < 16:
        raise ValueError("RSA modul uzunligi key_bits >= 16 butun son bo'lishi kerak")
    _validate_rounds(k)
    if not isinstance(max_pair_attempts, int) or isinstance(max_pair_attempts, bool) or max_pair_attempts < 1:
        raise ValueError("max_pair_attempts kamida 1 bo'lishi kerak")

    started = time.perf_counter()
    p_bits = key_bits // 2
    q_bits = key_bits - p_bits
    p, attempts_p, _ = generate_prime(p_bits, k=k)
    attempts_q_total = 0

    for _ in range(max_pair_attempts):
        q, attempts_q, _ = generate_prime(q_bits, k=k)
        attempts_q_total += attempts_q

        if p == q:
            continue

        # Fermat factorization is especially effective when p and q are
        # unusually close. This is a basic educational sanity check only.
        min_prime_bits = min(p.bit_length(), q.bit_length())
        distance_exponent = max(1, min_prime_bits // 2)
        if abs(p - q) <= (1 << distance_exponent):
            continue

        modulus = p * q
        if modulus.bit_length() != key_bits:
            continue

        phi = (p - 1) * (q - 1)
        elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
        expected_candidates = round((p_bits + q_bits) * math.log(2) / 2.0, 2)

        return {
            "p": p,
            "q": q,
            "N": modulus,
            "phi": phi,
            "target_modulus_bits": key_bits,
            "modulus_bits": modulus.bit_length(),
            "p_bits": p.bit_length(),
            "q_bits": q.bit_length(),
            "attempts_p": attempts_p,
            "attempts_q": attempts_q_total,
            "total_candidates_tested": attempts_p + attempts_q_total,
            "theoretical_expected_tests": expected_candidates,
            "elapsed_ms": elapsed_ms,
        }

    raise RuntimeError(
        f"{max_pair_attempts} juftlik urinishida aynan {key_bits}-bit N moduli yaratilmadi"
    )
