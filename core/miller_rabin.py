import secrets
import time

from core.models import PrimalityResult, RoundLog
from core.number_theory import check_small_primes, gcd


def miller_rabin_test(
    n: int,
    k: int = 20,
    skip_prefilter: bool = False,
    coprime_only: bool = False,
) -> PrimalityResult:
    """
    Miller-Rabin probabilistic primality test.
    Decomposes n - 1 = 2^s * d (d odd), then tests whether a^d == 1 (mod n)
    or a^(d * 2^r) == n - 1 (mod n) for some 0 <= r < s.
    Error bound: <= (1/4)^k.
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
                algorithm="Miller-Rabin",
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
                algorithm="Miller-Rabin",
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
                algorithm="Miller-Rabin",
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
                algorithm="Miller-Rabin",
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
                algorithm="Miller-Rabin",
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

    # Decompose n - 1 = 2^s * d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    logs: list[RoundLog] = []
    seen_a: set[int] = set()
    num_possible = n - 3

    for round_idx in range(1, k + 1):
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
            a = secrets.randbelow(num_possible) + 2
            if coprime_only:
                while gcd(a, n) != 1:
                    a = secrets.randbelow(num_possible) + 2

        seen_a.add(a)

        x = pow(a, d, n)
        expr_init = f"{a}^{d} mod {n}"

        if x == 1 or x == n - 1:
            target = "1" if x == 1 else "n-1"
            note = f"Dastlabki Miller-Rabin sharti bajarildi: x0 = {x} ≡ {target} (mod {n})"
            logs.append(
                RoundLog(
                    round_idx=round_idx,
                    witness_a=a,
                    expression=expr_init,
                    computed_value=str(x),
                    passed=True,
                    note=note,
                )
            )
            continue

        composite_witness = True
        for r in range(1, s):
            x = pow(x, 2, n)
            expr_sq = f"{a}^({d}*2^{r}) mod {n}"

            if x == n - 1:
                composite_witness = False
                note = f"Kvadratga oshirishning r={r}-bosqichida x = {x} ≡ n-1 (mod {n}) ga erishildi"
                logs.append(
                    RoundLog(
                        round_idx=round_idx,
                        witness_a=a,
                        expression=expr_sq,
                        computed_value=str(x),
                        passed=True,
                        note=note,
                    )
                )
                break

            if x == 1:
                # Non-trivial square root of 1 modulo n
                note = f"1 ning no-trivial kvadrat ildizi topildi: x ≡ 1 (mod {n}), n murakkab son"
                logs.append(
                    RoundLog(
                        round_idx=round_idx,
                        witness_a=a,
                        expression=expr_sq,
                        computed_value=str(x),
                        passed=False,
                        note=note,
                    )
                )
                elapsed = (time.perf_counter() - t0) * 1000.0
                return PrimalityResult(
                    algorithm="Miller-Rabin",
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

        if composite_witness:
            note = f"Miller-Rabin guvohi topildi: {s-1} ta kvadratga oshirishdan so'ng ham n-1 ga erishilmadi (oxirgi qiymat: {x})"
            logs.append(
                RoundLog(
                    round_idx=round_idx,
                    witness_a=a,
                    expression=f"{a}^(2^{s}*{d}) zanjiri",
                    computed_value=str(x),
                    passed=False,
                    note=note,
                )
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            return PrimalityResult(
                algorithm="Miller-Rabin",
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

    elapsed = (time.perf_counter() - t0) * 1000.0
    return PrimalityResult(
        algorithm="Miller-Rabin",
        n=n,
        bit_length=bit_length,
        is_prime=True,
        verdict="Probably Prime",
        rounds_requested=k,
        rounds_run=k,
        error_bound=f"<= (1/4)^{k}",
        elapsed_ms=round(elapsed, 4),
        pre_filtered=False,
        logs=logs,
    )
