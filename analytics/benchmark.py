import statistics
import time

import pandas as pd

from analytics.prime_generator import generate_prime
from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.solovay_strassen import solovay_strassen_test


ALGORITHMS = (
    ("Fermat", fermat_test),
    ("Solovay-Strassen", solovay_strassen_test),
    ("Miller-Rabin", miller_rabin_test),
)


def _make_semiprime(bits: int, k: int) -> int:
    """Create a composite product with exactly the requested bit length."""
    p_bits = bits // 2
    q_bits = bits - p_bits
    p, _, _ = generate_prime(p_bits, k=k)
    for _ in range(10_000):
        q, _, _ = generate_prime(q_bits, k=k)
        if p != q:
            candidate = p * q
            if candidate.bit_length() == bits:
                return candidate
    raise RuntimeError(f"{bits}-bit semiprime nomzodini yaratib bo'lmadi")


def run_benchmark(
    bit_sizes: list[int] | None = None,
    k: int = 20,
    trials: int = 3,
) -> pd.DataFrame:
    """
    Compare primality-test timing on the same prime and semiprime candidates.

    Candidate generation and one warm-up call are excluded from timed samples.
    Reports mean, median, population standard deviation, min/max and verdict.
    Timings are empirical and machine/load dependent; they are not complexity proofs.
    """
    if bit_sizes is None:
        bit_sizes = [64, 128, 256, 512, 1024, 2048]
    if (
        not isinstance(bit_sizes, (list, tuple))
        or not bit_sizes
        or any(not isinstance(bits, int) or isinstance(bits, bool) or bits < 8 or bits > 4096 for bits in bit_sizes)
    ):
        raise ValueError("bit_sizes 8 dan 4096 gacha bo'lgan butun sonlar ro'yxati bo'lishi kerak")
    if len(set(bit_sizes)) != len(bit_sizes):
        raise ValueError("bit_sizes ichida takroriy qiymatlar bo'lmasligi kerak")
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 256:
        raise ValueError("k 1 dan 256 gacha bo'lgan butun son bo'lishi kerak")
    if not isinstance(trials, int) or isinstance(trials, bool) or not 1 <= trials <= 100:
        raise ValueError("trials 1 dan 100 gacha bo'lgan butun son bo'lishi kerak")

    rows: list[dict] = []
    for bits in bit_sizes:
        prime, _, _ = generate_prime(bits, k=max(k, 20))
        composite = _make_semiprime(bits, k=max(k, 20))

        for candidate_type, candidate in (("Tub nomzod", prime), ("Murakkab (semiprime)", composite)):
            for algorithm_name, algorithm in ALGORITHMS:
                algorithm(candidate, k=k, skip_prefilter=True)  # warm-up, not timed

                samples: list[float] = []
                last_result = None
                for _ in range(trials):
                    started = time.perf_counter()
                    last_result = algorithm(candidate, k=k, skip_prefilter=True)
                    samples.append((time.perf_counter() - started) * 1000.0)

                rows.append({
                    "Bit_Length": bits,
                    "Candidate_Type": candidate_type,
                    "Algorithm": algorithm_name,
                    "Trials": trials,
                    "Rounds": k,
                    "Avg_Time_ms": round(statistics.mean(samples), 4),
                    "Median_Time_ms": round(statistics.median(samples), 4),
                    "Std_Dev_ms": round(statistics.pstdev(samples), 4),
                    "Min_Time_ms": round(min(samples), 4),
                    "Max_Time_ms": round(max(samples), 4),
                    "Verdict": last_result.verdict if last_result else "Unknown",
                    "Error_Bound": last_result.error_bound if last_result else "N/A",
                })

    return pd.DataFrame(rows, columns=[
        "Bit_Length", "Candidate_Type", "Algorithm", "Trials", "Rounds",
        "Avg_Time_ms", "Median_Time_ms", "Std_Dev_ms", "Min_Time_ms",
        "Max_Time_ms", "Verdict", "Error_Bound",
    ])
