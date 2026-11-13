from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.solovay_strassen import solovay_strassen_test

CARMICHAEL_NUMBERS: list[int] = [
    561, 1105, 1729, 2465, 2821, 6601, 8911, 10585,
    15841, 29341, 41041, 825265,
]


def factorize_distinct(n: int, max_steps: int = 1_000_000) -> tuple[list[tuple[int, int]], bool]:
    """Return (prime_factors_with_powers, complete). Limited trial division avoids UI freezes."""
    if n < 2:
        return [], True
    remaining = n
    factors: list[tuple[int, int]] = []
    divisor = 2
    steps = 0
    while divisor * divisor <= remaining and steps < max_steps:
        if remaining % divisor == 0:
            exponent = 0
            while remaining % divisor == 0:
                remaining //= divisor
                exponent += 1
            factors.append((divisor, exponent))
        divisor = 3 if divisor == 2 else divisor + 2
        steps += 1
    if remaining > 1:
        if divisor * divisor > remaining:
            factors.append((remaining, 1))
        else:
            return factors, False
    return factors, True


def check_korselt_criterion(n: int, max_steps: int = 1_000_000) -> dict:
    """Check Korselt's criterion. None means factorization was not completed within the limit."""
    if n < 3 or n % 2 == 0:
        return {"is_carmichael": False, "complete": True, "factors": [], "details": ["n musbat toq murakkab son bo'lishi kerak"]}
    factors, complete = factorize_distinct(n, max_steps=max_steps)
    factor_values = [p for p, _ in factors]
    if not complete:
        return {"is_carmichael": None, "complete": False, "factors": factor_values, "factor_powers": factors, "details": ["Faktorizatsiya limitiga yetildi; Korselt mezoni to'liq tekshirilmadi."]}
    is_composite = len(factors) >= 2
    square_free = all(power == 1 for _, power in factors)
    square_free_label = "ha" if square_free else "yo'q"
    details = [f"Square-free: {square_free_label}"]
    divisibility_ok = True
    for p, _ in factors:
        divides = (n - 1) % (p - 1) == 0
        divisibility_ok = divisibility_ok and divides
        division_label = "ha" if divides else "yo'q"
        details.append(f"{p}-1 = {p - 1}; n-1 = {n - 1}; bo'linadi: {division_label}")
    is_carmichael = is_composite and square_free and divisibility_ok
    return {
        "is_carmichael": is_carmichael,
        "complete": True,
        "factors": factor_values,
        "factor_powers": factors,
        "square_free": square_free,
        "divisibility_ok": divisibility_ok,
        "details": details,
    }


def analyze_carmichael(n: int, k: int = 20) -> dict:
    """Compare three probabilistic tests and independently check Korselt's criterion."""
    korselt = check_korselt_criterion(n)
    fermat_res = fermat_test(n, k=k, skip_prefilter=True, coprime_only=True)
    ss_res = solovay_strassen_test(n, k=k, skip_prefilter=True, coprime_only=True)
    mr_res = miller_rabin_test(n, k=k, skip_prefilter=True, coprime_only=True)
    fermat_fooled = bool(korselt["is_carmichael"] is True and fermat_res.is_prime)
    return {
        "n": n,
        "fermat": fermat_res,
        "solovay_strassen": ss_res,
        "miller_rabin": mr_res,
        "fermat_fooled": fermat_fooled,
        "is_carmichael": korselt["is_carmichael"],
        "factors": korselt["factors"],
        "factor_powers": korselt.get("factor_powers", []),
        "factorization_complete": korselt["complete"],
        "korselt_satisfied": korselt["is_carmichael"],
        "korselt_details": korselt["details"],
    }
