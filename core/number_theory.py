def _generate_small_primes(count: int = 2000) -> list[int]:
    """Generate the first count primes using the Sieve of Eratosthenes."""
    limit = 25000
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    primes = [i for i, is_p in enumerate(sieve) if is_p]
    return primes[:count]

SMALL_PRIMES: list[int] = _generate_small_primes(2000)
_SMALL_PRIMES_SET: set[int] = set(SMALL_PRIMES)
_DETERMINISTIC_MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
_UINT64_LIMIT = 1 << 64

def gcd(a: int, b: int) -> int:
    """Compute the greatest common divisor using the Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a

def is_prime_deterministic_64(n: int) -> bool:
    """Exact primality test for 0 <= n < 2**64 using a proven fixed MR base set."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n butun son bo'lishi kerak")
    if n < 0:
        return False
    if n >= _UINT64_LIMIT:
        raise ValueError("Aniq 64-bit tekshiruv faqat n < 2**64 uchun kafolatlangan")
    if n < 2:
        return False
    for prime in SMALL_PRIMES[:25]:
        if n == prime:
            return True
        if n % prime == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in _DETERMINISTIC_MR_BASES_64:
        a = base % n
        if a in (0, 1):
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
            if x == 1:
                return False
        else:
            return False
    return True

def jacobi_symbol(a: int, n: int) -> int:
    """Compute the Jacobi symbol (a / n); n must be odd and positive."""
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be an odd positive integer")
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a, n = n, a
        a %= n
    return result if n == 1 else 0

def check_small_primes(n: int) -> tuple[bool | None, str]:
    """Pre-filter against the first 2000 primes; None means further testing is required."""
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
