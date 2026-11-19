"""Reconstruct educational arithmetic traces from the exact sampled witness.

This module does not rerun a probabilistic test or draw new random bases.
It recomputes selected arithmetic using the witness in a RoundLog and checks
whether its conclusion agrees with the original algorithm's recorded round.
"""
from dataclasses import dataclass

from core.models import RoundLog
from core.number_theory import gcd, jacobi_symbol

# Guard the interface against huge traces for specially crafted n - 1 values.
MAX_VISIBLE_SQUARES = 128

ALGORITHMS = ("Fermat", "Solovay-Strassen", "Miller-Rabin")


@dataclass(frozen=True)
class TraceStep:
    title: str
    formula: str
    value: str
    explanation: str
    status: str = "info"


@dataclass(frozen=True)
class RoundTrace:
    steps: tuple[TraceStep, ...]
    matches_log: bool
    computed_pass: bool
    truncated: bool = False


def build_round_trace(algorithm: str, n: int, log: RoundLog) -> RoundTrace:
    """Build steps for one previously executed round, without randomness.

    "matches_log" checks both the result and recorded computed value.
    A genuine mismatch should be shown as an error, not silently discarded.
    """
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Noma'lum algoritm: {algorithm}")
    if not isinstance(n, int) or isinstance(n, bool) or n < 5 or n % 2 == 0:
        raise ValueError("Raund tafsilotlari uchun n >= 5 toq butun son bo'lishi kerak")
    a = log.witness_a
    if not isinstance(a, int) or isinstance(a, bool) or not (2 <= a <= n - 2):
        raise ValueError("Raunddagi asos a ruxsat etilgan oraliqda emas")

    steps: list[TraceStep] = []
    truncated = False

    def add(title: str, formula: str, value: object, explanation: str,
            status: str = "info") -> None:
        steps.append(TraceStep(
            title=title, formula=formula, value=str(value),
            explanation=explanation, status=status,
        ))

    def finish(passed: bool, value: str, explanation: str) -> RoundTrace:
        add(
            "Raund xulosasi",
            r"\text{guvoh topildi yoki sinovdan o'tildi}",
            "Sinovdan o'tdi" if passed else "Murakkablik guvohi topildi",
            explanation,
            "pass" if passed else "fail",
        )
        return RoundTrace(
            steps=tuple(steps),
            computed_pass=passed,
            matches_log=(passed == log.passed and value == log.computed_value),
            truncated=truncated,
        )

    add(
        "Tanlangan tasodifiy asos",
        r"2 \leq a \leq n - 2",
        f"a = {a}",
        f"Algoritm avval bajargan {log.round_idx}-raunddagi asos saqlandi. "
        "Qayta tasodifiy son tanlanmaydi.",
    )
    factor = gcd(a, n)
    add(
        "O'zaro tublikni tekshirish",
        r"g = \gcd(a,n)",
        f"g = {factor}",
        "Agar EKUB 1 dan katta bo'lsa, umumiy bo'luvchi topilgan va n murakkab.",
        "fail" if factor > 1 else "pass",
    )
    if factor > 1:
        return finish(False, str(factor), f"EKUB({a}, {n}) = {factor} > 1.")

    if algorithm == "Fermat":
        value = pow(a, n - 1, n)
        add(
            "Modul bo'yicha darajaga oshirish",
            r"v = a^{n-1}\bmod n",
            f"v = {value}",
            "Fermatning kichik teoremasi bo'yicha tub n uchun v = 1 bo'lishi shart.",
        )
        passed = value == 1
        add(
            "Fermat shartini solishtirish",
            r"v \stackrel{?}{=} 1",
            f"{value} {'=' if passed else '≠'} 1",
            "Shart bajarilishi tublikni isbotlamaydi: Karmaykl sonlari ham "
            "buni bajarishi mumkin."
            if passed else "Tenglik bajarilmadi, demak n aniq murakkab.",
            "pass" if passed else "fail",
        )
        return finish(passed, str(value), "Fermat sinovining ushbu raundi yakunlandi.")

    if algorithm == "Solovay-Strassen":
        j = jacobi_symbol(a, n)
        j_mod = j % n
        value = pow(a, (n - 1) // 2, n)
        add(
            "Yakobi belgisini hisoblash",
            r"J = \left(\frac{a}{n}\right), \quad J_n = J \bmod n",
            f"J = {j}; J mod n = {j_mod}",
            "Yakobi belgisi -1, 0 yoki 1 bo'lishi mumkin.",
        )
        add(
            "Eyler darajasini hisoblash",
            r"v = a^{(n-1)/2}\bmod n",
            f"v = {value}",
            "Yakobi belgisi bilan taqqoslanadigan modul bo'yicha qoldiq.",
        )
        passed = value == j_mod
        add(
            "Eyler–Yakobi mezoni",
            r"v \stackrel{?}{\equiv} J \pmod n",
            f"{value} {'=' if passed else '≠'} {j_mod} (mod {n})",
            "Ushbu asos sinovdan o'tdi; bu hali tublik isboti emas."
            if passed else "Mos kelmadi: murakkablik guvohi topildi.",
            "pass" if passed else "fail",
        )
        recorded = f"{value} vs {j_mod} (J={j})"
        return finish(passed, recorded, "Solovay–Strassen raundi yakunlandi.")

    # Miller–Rabin: construct the *real* squaring chain for the recorded base.
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    add(
        "n − 1 ni ajratish",
        r"n-1 = 2^s d, \quad d\ \text{toq}",
        f"s = {s}; d = {d}",
        "Miller–Rabin testi toq d va kvadratlashlar ketma-ketligidan foydalanadi.",
    )

    x = pow(a, d, n)
    add(
        "Dastlabki qoldiq",
        r"x_0 = a^d\bmod n",
        f"x0 = {x}",
        "x0 = 1 yoki x0 = n − 1 bo'lsa, raund shu yerda sinovdan o'tadi.",
    )
    if x in (1, n - 1):
        return finish(True, str(x), "Dastlabki Miller–Rabin sharti bajarildi.")

    passed = False
    for r in range(1, s):
        previous = x
        x = pow(x, 2, n)
        if r <= MAX_VISIBLE_SQUARES:
            add(
                f"Kvadratlash: {r}-qadam",
                rf"x_{{{r}}} = x_{{{r-1}}}^2\bmod n",
                f"{previous}² mod {n} = {x}",
                "Agar n − 1 ga yetilsa, raund o'tadi. Agar 1 ga "
                "kutilmaganda qaytilsa, n murakkab.",
                "pass" if x == n - 1 else ("fail" if x == 1 else "info"),
            )
        else:
            truncated = True

        if x == n - 1:
            passed = True
            break
        if x == 1:
            break

    if x == 1:
        explanation = (
            "1 ning trivial bo'lmagan kvadrat ildizi topildi: "
            f"{previous}² ≡ 1 (mod {n})."
        )
    elif passed:
        explanation = f"Kvadratlash zanjirida n − 1 = {n-1} ga erishildi."
    else:
        explanation = f"n − 1 = {n-1} ga erishilmadi; murakkablik guvohi bor."

    if truncated:
        explanation += (
            f" Dastlabki {MAX_VISIBLE_SQUARES} ta kvadratlash ko'rsatildi; "
            "qolganlari natijani hisoblashda hisobga olindi."
        )
    return finish(passed, str(x), explanation)
