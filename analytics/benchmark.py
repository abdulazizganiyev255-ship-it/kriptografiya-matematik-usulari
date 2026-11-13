import time
import pandas as pd

from analytics.prime_generator import generate_prime
from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.solovay_strassen import solovay_strassen_test


def run_benchmark(
    bit_sizes: list[int] = [64, 128, 256, 512, 1024, 2048],
    k: int = 20,
    trials: int = 3,
) -> pd.DataFrame:
    """
    Runs comprehensive performance benchmark across primality testing algorithms.
    Evaluates Fermat, Solovay-Strassen, and Miller-Rabin tests for various bit sizes.

    Columns:
      - Bit_Length
      - Algorithm
      - Avg_Time_ms
      - Min_Time_ms
      - Max_Time_ms
      - Error_Bound
    """
    if bit_sizes is None:
        bit_sizes = [64, 128, 256, 512, 1024, 2048]
    if not bit_sizes or any(not isinstance(bits, int) or bits < 2 for bits in bit_sizes):
        raise ValueError("bit_sizes kamida bitta 2 yoki undan katta butun qiymatdan iborat bo'lishi kerak")
    if not isinstance(k, int) or k < 1:
        raise ValueError("k kamida 1 bo'lishi kerak")
    if not isinstance(trials, int) or trials < 1:
        raise ValueError("trials kamida 1 bo'lishi kerak")

    algorithms = [
        ("Fermat", fermat_test),
        ("Solovay-Strassen", solovay_strassen_test),
        ("Miller-Rabin", miller_rabin_test),
    ]

    rows = []

    for bits in bit_sizes:
        # Generate a candidate prime for this bit size to benchmark k-round execution
        test_prime, _, _ = generate_prime(bits, k=20)

        for algo_name, algo_func in algorithms:
            times_ms: list[float] = []
            last_res = None

            for _ in range(trials):
                t0 = time.perf_counter()
                # Run with skip_prefilter=True to measure actual mathematical rounds
                last_res = algo_func(test_prime, k=k, skip_prefilter=True)
                t1 = time.perf_counter()
                times_ms.append((t1 - t0) * 1000.0)

            avg_time = round(sum(times_ms) / len(times_ms), 3)
            min_time = round(min(times_ms), 3)
            max_time = round(max(times_ms), 3)

            rows.append(
                {
                    "Bit_Length": bits,
                    "Algorithm": algo_name,
                    "Avg_Time_ms": avg_time,
                    "Min_Time_ms": min_time,
                    "Max_Time_ms": max_time,
                    "Error_Bound": last_res.error_bound if last_res else "N/A",
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "Bit_Length",
            "Algorithm",
            "Avg_Time_ms",
            "Min_Time_ms",
            "Max_Time_ms",
            "Error_Bound",
        ],
    )
