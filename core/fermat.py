import secrets
import time

from core.models import PrimalityResult, RoundLog
from core.number_theory import check_small_primes, gcd


def fermat_test(
    n: int,
    k: int = 20,
    skip_prefilter: bool = False,
    coprime_only: bool = False,
) -> PrimalityResult:
    """
    Fermat probabilistic primality test.
    Checks whether a^(n-1) == 1 (mod n) for k random bases a in [2, n-2].
    """
    if k < 1:
        raise ValueError("Raundlar soni k >= 1 bo'lishi kerak")

    t0 = time.perf_counter()
    bit_length = n.bit_length() if n > 0 else 0

    if not skip_prefilter:
        is_small, reason = check_small_primes(n)
        if is_small is True:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Fermat",
                n=n,
                bit_length=bit_length,
                is_prime=True,
                verdict="Prime",
                rounds_requested=k,
                rounds_run=0,
                error_bound="0",
                elapsed_ms=round(elapsed, 4),
                pre_filtered=True,
                logs=[],
            )
        if is_small is False:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Fermat",
                n=n,
                bit_length=bit_length,
                is_prime=False,
                verdict="Composite",
                rounds_requested=k,
                rounds_run=0,
                error_bound="0",
                elapsed_ms=round(elapsed, 4),
                pre_filtered=True,
                logs=[],
            )
    else:
        if n < 2:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Fermat",
                n=n,
                bit_length=bit_length,
                is_prime=False,
                verdict="Composite",
                rounds_requested=k,
                rounds_run=0,
                error_bound="0",
                elapsed_ms=round(elapsed, 4),
                pre_filtered=False,
                logs=[],
            )
        if n in (2, 3):
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Fermat",
                n=n,
                bit_length=bit_length,
                is_prime=True,
                verdict="Prime",
                rounds_requested=k,
                rounds_run=0,
                error_bound="0",
                elapsed_ms=round(elapsed, 4),
                pre_filtered=False,
                logs=[],
            )
        if n % 2 == 0:
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Fermat",
                n=n,
                bit_length=bit_length,
                is_prime=False,
                verdict="Composite",
                rounds_requested=k,
                rounds_run=0,
                error_bound="0",
                elapsed_ms=round(elapsed, 4),
                pre_filtered=False,
                logs=[],
            )

    logs: list[RoundLog] = []
    seen_a: set[int] = set()
    num_possible = n - 3

    for round_idx in range(1, k + 1):
        # Pick random witness a in [2, n-2] using secrets
        attempts = 0
        while attempts < 100:
            a = secrets.randbelow(num_possible) + 2
            if coprime_only and gcd(a, n) != 1:
                attempts += 1
                continue
            if len(seen_a) < num_possible and a in seen_a:
                attempts += 1
                continue
            break
        else:
            # Fallback if range is small
            a = secrets.randbelow(num_possible) + 2
            if coprime_only:
                while gcd(a, n) != 1:
                    a = secrets.randbelow(num_possible) + 2

        seen_a.add(a)
        val = pow(a, n - 1, n)
        expr = f"{a}^({n}-1) mod {n}"

        if val != 1:
            note = f"Fermat guvohi (witness) topildi: {a}^({n}-1) ≡ {val} != 1 (mod {n})"
            logs.append(
                RoundLog(
                    round_idx=round_idx,
                    witness_a=a,
                    expression=expr,
                    computed_value=str(val),
                    passed=False,
                    note=note,
                )
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Fermat",
                n=n,
                bit_length=bit_length,
                is_prime=False,
                verdict="Composite",
                rounds_requested=k,
                rounds_run=round_idx,
                error_bound="0",
                elapsed_ms=round(elapsed, 4),
                pre_filtered=False,
                logs=logs,
            )

        note = f"Fermat shartini bajardi: {a}^({n}-1) ≡ 1 (mod {n})"
        logs.append(
            RoundLog(
                round_idx=round_idx,
                witness_a=a,
                expression=expr,
                computed_value="1",
                passed=True,
                note=note,
            )
        )

    elapsed = (time.perf_counter() - t0) * 1000.0
    return PrimalityResult(
        algorithm="Fermat",
        n=n,
        bit_length=bit_length,
        is_prime=True,
        verdict="Probably Prime",
        rounds_requested=k,
        rounds_run=k,
        error_bound="No universal bound: Carmichael numbers can pass every coprime base",
        elapsed_ms=round(elapsed, 4),
        pre_filtered=False,
        logs=logs,
    )
