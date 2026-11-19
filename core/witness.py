"""Uniform, independent random bases for educational primality tests."""
import secrets
from core.number_theory import gcd

MAX_ROUNDS = 4096


def validate_inputs(n: int, k: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n butun son bo'lishi kerak")
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= MAX_ROUNDS:
        raise ValueError(f"k 1 dan {MAX_ROUNDS} gacha butun son bo'lishi kerak")


def draw_witness(n: int, coprime_only: bool = False) -> int:
    """Draw a fresh uniform base in [2, n-2] with replacement."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 5 or n % 2 == 0:
        raise ValueError("Asos tanlash uchun n >= 5 toq butun son bo'lishi kerak")
    while True:
        a = secrets.randbelow(n - 3) + 2
        if not coprime_only or gcd(a, n) == 1:
            return a
