"""Repeatable, educational Carmichael-561 demonstration.

Use fixed coprime bases to avoid random changes during a university defense.
This is an independent illustration, not a replacement for probabilistic tests.
"""
from core.number_theory import gcd, jacobi_symbol, is_prime_deterministic_64

N = 561
BASES = (2, 5, 10, 13, 17, 19)


def demo() -> None:
    print("Carmichael demonstration: n = 561 = 3 * 11 * 17")
    assert 3 * 11 * 17 == N
    assert not is_prime_deterministic_64(N)
    print("Ground truth: COMPOSITE")
    for a in BASES:
        assert gcd(a, N) == 1
        fermat = pow(a, N - 1, N) == 1
        ss = pow(a, (N - 1) // 2, N) == jacobi_symbol(a, N) % N
        d, s = N - 1, 0
        while d % 2 == 0:
            d //= 2
            s += 1
        x = pow(a, d, N)
        mr = x in (1, N - 1)
        for _ in range(s - 1):
            if mr:
                break
            x = pow(x, 2, N)
            if x == N - 1:
                mr = True
                break
        assert fermat, f"Fermat did not pass for coprime base {a}"
        print(f"a={a:2d} | Fermat={'PASS' if fermat else 'FAIL'} | Solovay-Strassen={'PASS' if ss else 'FAIL'} | Miller-Rabin={'PASS' if mr else 'FAIL'}")
    print("Conclusion: Fermat passes every coprime base for 561, despite 561 being composite.")


if __name__ == "__main__":
    demo()
