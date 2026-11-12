from core.fermat import fermat_test
from core.miller_rabin import miller_rabin_test
from core.solovay_strassen import solovay_strassen_test

CARMICHAEL_NUMBERS: list[int] = [
    561,
    1105,
    1729,
    2465,
    2821,
    6601,
    8911,
    10585,
    15841,
    29341,
    41041,
    825265,
]


def analyze_carmichael(n: int, k: int = 20) -> dict:
    """
    Analyzes behavior of Fermat, Solovay-Strassen, and Miller-Rabin tests on Carmichael numbers.
    Carmichael numbers fool the Fermat test for all coprime bases, but are detected
    as composite by Solovay-Strassen and Miller-Rabin.
    """
    fermat_res = fermat_test(n, k=k, skip_prefilter=True, coprime_only=True)
    ss_res = solovay_strassen_test(n, k=k, skip_prefilter=True, coprime_only=True)
    mr_res = miller_rabin_test(n, k=k, skip_prefilter=True, coprime_only=True)

    # Fermat was fooled if it reported prime for a number that Miller-Rabin (or true math) identified as composite
    fermat_fooled = bool(fermat_res.is_prime and not mr_res.is_prime)

    return {
        "n": n,
        "fermat": fermat_res,
        "solovay_strassen": ss_res,
        "miller_rabin": mr_res,
        "fermat_fooled": fermat_fooled,
    }
