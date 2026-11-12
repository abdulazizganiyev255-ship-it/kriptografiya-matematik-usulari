def _generate_small_primes(count: int = 2000) -> list[int]:
    """Generates the first `count` prime numbers using the Sieve of Eratosthenes."""
    limit = 25000
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    primes = [i for i, is_p in enumerate(sieve) if is_p]
    return primes[:count]


# First 2000 prime numbers (2 to 17389)
SMALL_PRIMES: list[int] = _generate_small_primes(2000)
_SMALL_PRIMES_SET: set[int] = set(SMALL_PRIMES)


def gcd(a: int, b: int) -> int:
    """Computes the Greatest Common Divisor (EKUB) of a and b using Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def jacobi_symbol(a: int, n: int) -> int:
    """
    Computes the Jacobi symbol (a / n) in pure Python.
    n must be an odd positive integer.
    Returns: 1, -1, or 0.
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be an odd positive integer")

    a = a % n
    result = 1

    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result

        # Quadratic reciprocity
        if a % 4 == 3 and n % 4 == 3:
            result = -result

        a, n = n, a
        a = a % n

    return result if n == 1 else 0


def check_small_primes(n: int) -> tuple[bool | None, str]:
    """
    Pre-filter test against the first 2000 prime numbers.
    Returns:
      (True, reason)  - Definitely prime (found in SMALL_PRIMES)
      (False, reason) - Definitely composite (<= 1, or divisible by a small prime)
      (None, reason)  - Passed pre-filter, requires probabilistic testing
    """
    if n < 2:
        return False, f"n = {n} <= 1 bo'lgani sababli tub son emas"

    if n in _SMALL_PRIMES_SET:
        return True, f"n = {n} kichik tub sonlar jadvalida mavjud (aniq tub)"

    if n <= SMALL_PRIMES[-1]:
        return False, f"n = {n} <= {SMALL_PRIMES[-1]} va kichik tub sonlar jadvalida yo'q (murakkab son)"

    for p in SMALL_PRIMES:
        if n % p == 0:
            return False, f"n = {n} soni kichik tub son {p} ga qoldiqsiz bo'linadi (murakkab son)"

    return None, f"{len(SMALL_PRIMES)} ta kichik tub son bo'yicha tekshiruvdan muvaffaqiyatli o'tdi"
