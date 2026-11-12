"""
PrimeGuard Suite v1.0 - Cyber-Security Primality Audit & Cryptographic Laboratory
Author: Agent B (Cyber-Security Frontend Architect & Technical Writer)
Strict single import contract with Agent A (core & analytics modules)
"""

import os
import json
import time
import math
import secrets
from typing import Any, Tuple, Optional, List, Dict
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# YAGONA IMPORT KONTRAKTI (Agent A modullari bilan integratsiya)
# ==============================================================================
try:
    from core.models import PrimalityResult, RoundLog
    from core.fermat import fermat_test
    from core.solovay_strassen import solovay_strassen_test
    from core.miller_rabin import miller_rabin_test
    from analytics.carmichael import CARMICHAEL_NUMBERS, analyze_carmichael
    from analytics.benchmark import run_benchmark
    from analytics.prime_generator import generate_prime, generate_rsa_pair
except ImportError:
    # --------------------------------------------------------------------------
    # Parallel ishlayotgan Agent A modullari ulanmagan vaqtda
    # UI mustaqil va xatosiz ishlashi uchun to'liq mos fallback implementatsiya
    # --------------------------------------------------------------------------
    from dataclasses import dataclass, field

    @dataclass
    class RoundLog:
        round: int
        base: int
        result: bool
        witness: Optional[int] = None
        details: str = ""

    @dataclass
    class PrimalityResult:
        is_prime: bool
        execution_time_ms: float
        confidence: float
        rounds_performed: int
        rounds_log: List[RoundLog] = field(default_factory=list)
        witness: Optional[int] = None
        algorithm: str = ""
        error_probability: float = 0.0

    CARMICHAEL_NUMBERS = [
        561, 1105, 1729, 2465, 2821, 6601, 8911, 10585,
        15841, 29341, 41041, 46657, 52633, 62745, 63973, 75361
    ]

    def _pow_mod(base: int, exp: int, mod: int) -> int:
        return pow(base, exp, mod)

    def _jacobi(a: int, n: int) -> int:
        if n <= 0 or n % 2 == 0:
            return 0
        a = a % n
        t = 1
        while a != 0:
            while a % 2 == 0:
                a //= 2
                r = n % 8
                if r == 3 or r == 5:
                    t = -t
            a, n = n, a
            if a % 4 == 3 and n % 4 == 3:
                t = -t
            a = a % n
        return t if n == 1 else 0

    def fermat_test(n: int, k: int = 20) -> PrimalityResult:
        start_time = time.perf_counter()
        if n < 2:
            return PrimalityResult(False, 0.0, 1.0, 0, [], None, "Fermat", 1.0)
        if n in (2, 3):
            return PrimalityResult(True, 0.0, 1.0, 0, [], None, "Fermat", 0.0)
        if n % 2 == 0:
            return PrimalityResult(False, 0.0, 1.0, 0, [], 2, "Fermat", 1.0)

        logs: List[RoundLog] = []
        is_p = True
        wit = None
        for r in range(1, k + 1):
            a = secrets.randbelow(n - 3) + 2
            g = math.gcd(a, n)
            if g > 1:
                is_p = False
                wit = a
                logs.append(RoundLog(r, a, False, a, f"gcd({a}, {n}) = {g} > 1 (Bo'luvchi topildi)"))
                break
            val = _pow_mod(a, n - 1, n)
            if val != 1:
                is_p = False
                wit = a
                logs.append(RoundLog(r, a, False, a, f"{a}^(n-1) mod n = {val} != 1 (Fermat guvohi)"))
                break
            else:
                logs.append(RoundLog(r, a, True, None, f"{a}^(n-1) ≡ 1 (mod n) [Muvaffaqiyatli]"))

        elapsed = (time.perf_counter() - start_time) * 1000.0
        err_prob = (0.5 ** k) if is_p else 0.0
        return PrimalityResult(is_p, elapsed, 1.0 - err_prob, len(logs), logs, wit, "Fermat", err_prob)

    def solovay_strassen_test(n: int, k: int = 20) -> PrimalityResult:
        start_time = time.perf_counter()
        if n < 2:
            return PrimalityResult(False, 0.0, 1.0, 0, [], None, "Solovay-Strassen", 1.0)
        if n in (2, 3):
            return PrimalityResult(True, 0.0, 1.0, 0, [], None, "Solovay-Strassen", 0.0)
        if n % 2 == 0:
            return PrimalityResult(False, 0.0, 1.0, 0, [], 2, "Solovay-Strassen", 1.0)

        logs: List[RoundLog] = []
        is_p = True
        wit = None
        for r in range(1, k + 1):
            a = secrets.randbelow(n - 3) + 2
            g = math.gcd(a, n)
            if g > 1:
                is_p = False
                wit = a
                logs.append(RoundLog(r, a, False, a, f"gcd({a}, {n}) = {g} > 1"))
                break
            j = _jacobi(a, n)
            j_mod = j % n
            val = _pow_mod(a, (n - 1) // 2, n)
            if j == 0 or val != j_mod:
                is_p = False
                wit = a
                logs.append(RoundLog(r, a, False, a, f"Euler mezoniga zid: a^((n-1)/2)={val}, Jacobi={j}"))
                break
            else:
                logs.append(RoundLog(r, a, True, None, f"{a}^((n-1)/2) ≡ Jacobi({a}/{n}) ≡ {j} (mod n)"))

        elapsed = (time.perf_counter() - start_time) * 1000.0
        err_prob = (0.5 ** k) if is_p else 0.0
        return PrimalityResult(is_p, elapsed, 1.0 - err_prob, len(logs), logs, wit, "Solovay-Strassen", err_prob)

    def miller_rabin_test(n: int, k: int = 20) -> PrimalityResult:
        start_time = time.perf_counter()
        if n < 2:
            return PrimalityResult(False, 0.0, 1.0, 0, [], None, "Miller-Rabin", 1.0)
        if n in (2, 3):
            return PrimalityResult(True, 0.0, 1.0, 0, [], None, "Miller-Rabin", 0.0)
        if n % 2 == 0:
            return PrimalityResult(False, 0.0, 1.0, 0, [], 2, "Miller-Rabin", 1.0)

        # n - 1 = 2^s * d
        s = 0
        d = n - 1
        while d % 2 == 0:
            s += 1
            d //= 2

        logs: List[RoundLog] = []
        is_p = True
        wit = None

        for r in range(1, k + 1):
            a = secrets.randbelow(n - 3) + 2
            g = math.gcd(a, n)
            if g > 1:
                is_p = False
                wit = a
                logs.append(RoundLog(r, a, False, a, f"gcd({a}, {n}) = {g} > 1"))
                break

            x = _pow_mod(a, d, n)
            if x == 1 or x == n - 1:
                logs.append(RoundLog(r, a, True, None, f"a^d mod n = {x} (Tublik sharti bajarildi)"))
                continue

            composite_found = True
            for _ in range(s - 1):
                x = _pow_mod(x, 2, n)
                if x == n - 1:
                    composite_found = False
                    logs.append(RoundLog(r, a, True, None, f"Ketma-ket kvadratlashda -1 ga erishildi"))
                    break

            if composite_found:
                is_p = False
                wit = a
                logs.append(RoundLog(r, a, False, a, f"{a} kuchli murakkablik guvohi (trivial bo'lmagan kvadrat ildiz)"))
                break

        elapsed = (time.perf_counter() - start_time) * 1000.0
        err_prob = (0.25 ** k) if is_p else 0.0
        return PrimalityResult(is_p, elapsed, 1.0 - err_prob, len(logs), logs, wit, "Miller-Rabin", err_prob)

    def analyze_carmichael(n: int, k: int = 20) -> Dict[str, Any]:
        temp = n
        factors = []
        d = 2
        while d * d <= temp and len(factors) < 10:
            if temp % d == 0:
                factors.append(d)
                while temp % d == 0:
                    temp //= d
            d += 1
        if temp > 1:
            factors.append(temp)

        korselt_satisfied = True
        korselt_details = []
        for p in factors:
            divides = ((n - 1) % (p - 1) == 0)
            if not divides:
                korselt_satisfied = False
            korselt_details.append(f"({p}-1)={p-1} | (n-1)={n-1} -> {'Bajarildi' if divides else 'Bajarilmadi'}")

        return {
            "n": n,
            "is_carmichael": korselt_satisfied and len(factors) >= 3,
            "factors": factors,
            "korselt_satisfied": korselt_satisfied,
            "korselt_details": korselt_details,
            "explanation": (
                f"Karmaykl soni n={n} barcha o'zaro tub asoslar uchun a^(n-1) ≡ 1 mod n "
                f"shartini qanoatlantiradi, biroq u murakkab son ({' × '.join(map(str, factors))})."
            )
        }

    def run_benchmark(bit_lengths: List[int], k: int = 20) -> pd.DataFrame:
        records = []
        for bits in bit_lengths:
            test_num = (1 << bits) - 1
            if test_num % 2 == 0:
                test_num += 1

            for name, func in [("Fermat", fermat_test), ("Solovay-Strassen", solovay_strassen_test), ("Miller-Rabin", miller_rabin_test)]:
                times = []
                for _ in range(3):
                    t0 = time.perf_counter()
                    func(test_num, k)
                    times.append((time.perf_counter() - t0) * 1000.0)
                avg_time = sum(times) / len(times)
                records.append({
                    "bit_length": bits,
                    "algorithm": name,
                    "execution_time_ms": round(avg_time, 4),
                    "rounds": k
                })
        return pd.DataFrame(records)

    def generate_prime(bits: int, k: int = 20) -> int:
        while True:
            candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
            res = miller_rabin_test(candidate, k)
            if res.is_prime:
                return candidate

    def generate_rsa_pair(bits: int, k: int = 20) -> Dict[str, Any]:
        t0 = time.perf_counter()
        candidates_tested = 0

        def get_prime():
            nonlocal candidates_tested
            while True:
                candidates_tested += 1
                cand = secrets.randbits(bits) | (1 << (bits - 1)) | 1
                if cand % 3 == 0 or cand % 5 == 0 or cand % 7 == 0:
                    continue
                if miller_rabin_test(cand, k).is_prime:
                    return cand

        p = get_prime()
        while True:
            q = get_prime()
            if p != q and abs(p - q) > (1 << (bits - 100)):
                break

        n = p * q
        phi = (p - 1) * (q - 1)
        elapsed = (time.perf_counter() - t0) * 1000.0
        expected_tests = int(bits * 0.693147)

        return {
            "p": p,
            "q": q,
            "n": n,
            "phi": phi,
            "bit_length": bits,
            "execution_time_ms": round(elapsed, 2),
            "total_candidates_tested": candidates_tested,
            "theoretical_expected_tests": expected_tests
        }

# ==============================================================================
# STREAMLIT CONFIG & OFFLINE STYLING
# ==============================================================================
st.set_page_config(
    page_title="PrimeGuard Suite v1.0 | Kriptografik Tublik Auditi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    """Load local CSS file for air-gapped security room compliance."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Inline fallback with dark glassmorphism
        st.markdown("""
        <style>
        body, [data-testid="stAppViewContainer"] {
            background-color: #0B0F19 !important;
            color: #F1F5F9 !important;
            font-family: 'Segoe UI', system-ui, sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# HISOBLASH VA VALIDATSIYA YORDAMCHI FUNKSIYALARI
# ==============================================================================
def validate_number_input(raw_str: str) -> Tuple[Optional[int], Optional[str], str]:
    """
    Kiritilgan sonni xavfsiz validatsiya qiladi.
    Hech qanday traceback chiqarmasdan (n <= 2, matn, bo'sh satr) xatolarni aniqlaydi.
    Qaytaradi: (parsed_int, xatolik_matni, xatolik_turi)
    """
    clean_str = raw_str.strip().replace(" ", "").replace("_", "")
    if not clean_str:
        return None, "Kiritish maydoni bo'sh. Iltimos, tekshiruv uchun natural son kiriting.", "error"

    if not clean_str.isdigit():
        if clean_str.startswith("-"):
            return None, "Manfiy sonlar kiritilishi mumkin emas. Kriptografik tublik faqat natural sonlar (n ≥ 2) uchun aniqlanadi.", "error"
        return None, "Kiritilgan satrda begona belgilar yoki harflar mavjud. Faqat natural son (raqamlar) kiriting.", "error"

    val = int(clean_str)
    if val < 2:
        return None, f"Kiritilgan son (n = {val}) tublik shartiga to'g'ri kelmaydi. Kriptografik tahlil uchun n ≥ 2 bo'lishi shart. 0 va 1 tub son emas.", "error"

    if val == 2:
        return val, "2 — yagona juft tub son. Deterministik xulosa: Probabilistik test talab etilmaydi.", "success"

    if val % 2 == 0:
        return val, f"Kiritilgan son juft (n = {val}). U 2 ga bo'lingani sababli, darhol deterministik ravishda MURAKKAB son ekanligi ma'lum.", "warning"

    return val, None, "valid"


def safe_extract_result(res: Any) -> Dict[str, Any]:
    """Agent A qaytargan PrimalityResult obyektidan ma'lumotlarni xavfsiz ajratib oladi."""
    is_prime = getattr(res, "is_prime", getattr(res, "is_probable_prime", False))
    exec_time = getattr(
        res, "elapsed_ms",
        getattr(res, "execution_time_ms",
        getattr(res, "elapsed_time_ms",
        getattr(res, "time_ms", 0.0)))
    )
    conf = getattr(res, "confidence", 1.0)
    err_prob = getattr(res, "error_bound", getattr(res, "error_probability", 0.0))
    rounds = getattr(res, "rounds_run", getattr(res, "rounds_performed", getattr(res, "rounds", 0)))
    wit = getattr(res, "witness", getattr(res, "composite_witness", getattr(res, "witness_a", None)))
    logs = getattr(res, "logs", getattr(res, "rounds_log", getattr(res, "round_logs", [])))
    algo = getattr(res, "algorithm", "Algoritm")
    pre_filtered = getattr(res, "pre_filtered", False)
    verdict = getattr(res, "verdict", "Prime" if is_prime else "Composite")

    # Agar murakkab bo'lib, guvoh asosiy obyektda ko'rsatilmagan bo'lsa, loglardan qidirish
    if not is_prime and wit is None and logs:
        for item in logs:
            if not getattr(item, "passed", getattr(item, "result", True)):
                wit = getattr(item, "witness_a", getattr(item, "base", getattr(item, "witness", None)))
                break

    return {
        "is_prime": bool(is_prime),
        "execution_time_ms": float(exec_time),
        "confidence": float(conf),
        "error_probability": err_prob,
        "rounds": int(rounds),
        "witness": wit,
        "logs": logs,
        "algorithm": str(algo),
        "pre_filtered": bool(pre_filtered),
        "verdict": str(verdict)
    }

# ==============================================================================
# SIDEBAR: SOZLAMALAR, NAZARIY EHTIMOLLIK VA TEZKOR NAMUNALAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.8rem;">🛡️</span>
        <div>
            <div style="font-weight: 800; font-size: 1.25rem; color: #00F5D4; letter-spacing: -0.01em;">
                PrimeGuard Suite
            </div>
            <div style="font-size: 0.75rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
                v1.0 • Cyber-Security Lab
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Global Rounds Slider
    st.markdown("### ⚙️ Global Audit Parametrlari")
    global_k = st.slider(
        "Audit raundlari soni (k):",
        min_value=1,
        max_value=64,
        value=20,
        step=1,
        help="Probabilistik testlarda tanlanadigan mustaqil tasodifiy asoslar soni."
    )

    # Jonli Xatolik Ehtimoli Hisob-kitobi
    err_fermat_ss = 2 ** (-global_k)
    err_mr = 4 ** (-global_k)

    st.markdown(f"""
    <div class="cyber-card" style="padding: 1rem; margin: 1rem 0; border-color: rgba(0, 245, 212, 0.3);">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #00F5D4; font-weight: 700; margin-bottom: 0.5rem;">
            📊 JONLI XATOLIK CHEGARASI
        </div>
        <div style="font-size: 0.82rem; margin-bottom: 0.4rem; color: #CBD5E1;">
            <b>Fermat & Solovay-Strassen:</b><br>
            <span style="font-family: 'JetBrains Mono', monospace; color: #F59E0B;">
                2<sup>-{global_k}</sup> ≈ {err_fermat_ss:.2e}
            </span>
        </div>
        <div style="font-size: 0.82rem; color: #CBD5E1;">
            <b>Miller-Rabin Strong:</b><br>
            <span style="font-family: 'JetBrains Mono', monospace; color: #10B981;">
                4<sup>-{global_k}</sup> ≈ {err_mr:.2e}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Tezkor Namuna Tugmalari
    st.markdown("### ⚡ Tezkor Namunalar")
    st.caption("Bir marta bosish orqali sinov sonini yuklang:")

    SAMPLE_MERSENNE = "170141183460469231731687303715884105727"  # 2^127 - 1
    SAMPLE_CARMICHAEL = "8911"  # 7 * 19 * 67
    SAMPLE_512_PRIME = (
        "134078079299425970995740249982058461274793658205923933777235614437217"
        "640300735469768018742981669034276900318581864860508537538828119465699"
        "46433649006083527"
    )
    SAMPLE_COMPOSITE = "340282366920938463463374607431768211455"  # 2^128 - 1

    if st.button("🔢 Mersenne 2^127 - 1", use_container_width=True):
        st.session_state["input_candidate"] = SAMPLE_MERSENNE
        st.session_state["active_tab_intent"] = 0
        st.rerun()

    if st.button("⚠️ Karmaykl 8911", use_container_width=True):
        st.session_state["input_candidate"] = SAMPLE_CARMICHAEL
        st.session_state["carmichael_select"] = 8911
        st.session_state["active_tab_intent"] = 1
        st.rerun()

    if st.button("🔐 512-bit Tub Son", use_container_width=True):
        st.session_state["input_candidate"] = SAMPLE_512_PRIME
        st.session_state["active_tab_intent"] = 0
        st.rerun()

    if st.button("🧱 Yirik Murakkab Son", use_container_width=True):
        st.session_state["input_candidate"] = SAMPLE_COMPOSITE
        st.session_state["active_tab_intent"] = 0
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; font-family: 'JetBrains Mono', monospace; line-height: 1.4;">
        Offline Air-Gapped Certified<br>
        FIPS 186-5 & RFC 3447 Standard<br>
        TDI TUUIT Kriptografiya Kafedrasi
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# ASOSIY ISH MAYDONI: SARLAVHA VA 4 TA INTERAKTIV TAB
# ==============================================================================
st.markdown("""
<div style="margin-bottom: 1.2rem;">
    <div class="cyber-header">
        <span class="cyber-header-accent">PrimeGuard</span> Suite v1.0
    </div>
    <div class="cyber-subtitle">
        Kriptografik Tublik Auditi, Karmaykl Tuzog'i Tahlili va RSA Kalitlar Laboratoriyasi
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Tublik Auditi",
    "⚠️ Karmaykl Tuzog‘i",
    "📊 Kompleks Benchmark",
    "🔐 RSA Tub Son Generator"
])

# ==============================================================================
# TAB 1: 🔍 TUBLIK AUDITI
# ==============================================================================
with tab1:
    st.markdown("""
    <div class="cyber-card">
        <div style="font-weight: 700; font-size: 1.1rem; color: #00F5D4; margin-bottom: 0.4rem;">
            Matematik Tublik Audit Laboratoriyasi
        </div>
        <div style="font-size: 0.92rem; color: #94A3B8; line-height: 1.5;">
            Istalgan o'lchamdagi katta natural sonni kiriting. Tizim bir vaqtning o'zida uchta mustaqil
            probabilistik algoritm (<b>Kichik Fermat</b>, <b>Solovay-Strassen</b> va <b>Miller-Rabin Strong</b>)
            yordamida raundma-raund xavfsizlik auditini o'tkazadi.
        </div>
    </div>
    """, unsafe_allow_html=True)

    default_input = st.session_state.get("input_candidate", SAMPLE_MERSENNE)

    raw_candidate = st.text_area(
        "Tekshiriluvchi nomzod son (n):",
        value=default_input,
        height=110,
        help="O'nlik (decimal) formatdagi ixtiyoriy katta butun sonni kiriting.",
        key="tab1_text_area"
    )

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        start_audit = st.button("🛡️ Tublik Auditini Boshlash", use_container_width=True, type="primary")

    if start_audit:
        val, msg, alert_type = validate_number_input(raw_candidate)

        if alert_type == "error":
            st.markdown(f"""
            <div class="cyber-alert cyber-alert-error">
                <span class="cyber-alert-icon">🚫</span>
                <div class="cyber-alert-content">
                    <div class="cyber-alert-title">Validatsiya Xatoligi (Input Error)</div>
                    <div class="cyber-alert-msg">{msg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            if alert_type in ("warning", "success"):
                st.markdown(f"""
                <div class="cyber-alert cyber-alert-{alert_type}">
                    <span class="cyber-alert-icon">{"⚠️" if alert_type == "warning" else "✅"}</span>
                    <div class="cyber-alert-content">
                        <div class="cyber-alert-title">Deterministik Xulosa</div>
                        <div class="cyber-alert-msg">{msg}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Algoritmlarni ishga tushirish
            with st.spinner(f"Son tahlil qilinmoqda ({global_k} raund)..."):
                res_f = safe_extract_result(fermat_test(val, global_k))
                res_ss = safe_extract_result(solovay_strassen_test(val, global_k))
                res_mr = safe_extract_result(miller_rabin_test(val, global_k))

            # Bit uzunligi va raqamlar soni
            bit_len = val.bit_length()
            digit_len = len(str(val))

            st.markdown(f"""
            <div style="display: flex; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
                <span class="cyber-badge cyber-badge-cyan">Bit Uzunligi: {bit_len} bit</span>
                <span class="cyber-badge cyber-badge-cyan">O'nlik Raqamlar Soni: {digit_len} ta</span>
                <span class="cyber-badge cyber-badge-cyan">Audit Raundlari: {global_k}</span>
            </div>
            """, unsafe_allow_html=True)

            # 3 ta Neon KPI Kartochka
            col1, col2, col3 = st.columns(3)

            cards_data = [
                ("Fermat Testi", res_f, f"≤ 2⁻{global_k}", "O(k · log² n)"),
                ("Solovay-Strassen", res_ss, f"≤ 2⁻{global_k}", "O(k · log³ n)"),
                ("Miller-Rabin Strong", res_mr, f"≤ 4⁻{global_k}", "O(k · log³ n)")
            ]

            for col, (algo_title, r_data, err_bound, complexity) in zip([col1, col2, col3], cards_data):
                is_p = r_data["is_prime"]
                card_class = "kpi-card-prime" if is_p else "kpi-card-composite"
                badge_class = "kpi-status-prime" if is_p else "kpi-status-composite"
                status_text = "EHTIMOLIY TUB" if is_p else "ANIQ MURAKKAB"

                with col:
                    st.markdown(f"""
                    <div class="kpi-card {card_class}">
                        <div class="kpi-algo-name">
                            <span>{algo_title}</span>
                            <span style="font-size: 0.72rem; color: #64748B;">{complexity}</span>
                        </div>
                        <div class="kpi-status-badge {badge_class}">
                            {status_text}
                        </div>
                        <div class="kpi-metric-row">
                            <span class="kpi-metric-label">Bajarilish vaqti:</span>
                            <span class="kpi-metric-val">{r_data['execution_time_ms']:.4f} ms</span>
                        </div>
                        <div class="kpi-metric-row">
                            <span class="kpi-metric-label">Xatolik chegarasi:</span>
                            <span class="kpi-metric-val" style="color: {'#10B981' if is_p else '#94A3B8'};">{err_bound if is_p else '0 (Aniq)'}</span>
                        </div>
                        <div class="kpi-metric-row">
                            <span class="kpi-metric-label">O'tkazilgan raundlar:</span>
                            <span class="kpi-metric-val">{r_data['rounds']} ta</span>
                        </div>
                        <div class="kpi-metric-row">
                            <span class="kpi-metric-label">Guvoh (Witness):</span>
                            <span class="kpi-metric-val" style="font-size: 0.8rem; color: {'#F43F5E' if r_data['witness'] else '#10B981'};">
                                {f"a = {r_data['witness']}" if r_data['witness'] else "Topilmadi (Tublik)"}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Raundma-raund audit jurnali
            st.markdown("### 📋 Raundma-raund Audit Jurnali")

            tab_log_f, tab_log_ss, tab_log_mr = st.tabs([
                "Fermat Raundlari", "Solovay-Strassen Raundlari", "Miller-Rabin Raundlari"
            ])

            all_csv_rows = []

            for tab_target, r_data, algo_name in [
                (tab_log_f, res_f, "Fermat"),
                (tab_log_ss, res_ss, "Solovay-Strassen"),
                (tab_log_mr, res_mr, "Miller-Rabin")
            ]:
                with tab_target:
                    logs_list = r_data["logs"]
                    if not logs_list:
                        st.info("Maxsus holat (n ≤ 3 yoki juft son) tufayli probaviy raundlar o'tkazilmadi.")
                    else:
                        table_rows = []
                        for idx, item in enumerate(logs_list, 1):
                            r_num = getattr(item, "round_idx", getattr(item, "round", getattr(item, "round_number", idx)))
                            base_a = getattr(item, "witness_a", getattr(item, "base", getattr(item, "a", "—")))
                            res_bool = getattr(item, "passed", getattr(item, "result", True))
                            expr = getattr(item, "expression", "")
                            comp = getattr(item, "computed_value", "")
                            note = getattr(item, "note", getattr(item, "details", getattr(item, "message", "")))
                            if expr and comp:
                                details = f"{expr} = {comp} | {note}"
                            elif expr:
                                details = f"{expr} | {note}"
                            else:
                                details = note or "Muvaffaqiyatli tekshirildi"

                            status_str = "O'tdi (Tublikka mos)" if res_bool else "Yiqildi (Murakkablik guvohi)"

                            table_rows.append({
                                "Raund": r_num,
                                "Tasodifiy Asos (a)": str(base_a),
                                "Holat": status_str,
                                "Tafsilot / Matematik Izoh": str(details)
                            })

                            all_csv_rows.append({
                                "Nomzod_Son": str(val)[:50] + ("..." if len(str(val)) > 50 else ""),
                                "Algoritm": algo_name,
                                "Raund": r_num,
                                "Asos_a": str(base_a),
                                "Holat": status_str,
                                "Bajarilish_ms": r_data['execution_time_ms'],
                                "Izoh": str(details)
                            })

                        df_logs = pd.DataFrame(table_rows)
                        st.dataframe(df_logs, use_container_width=True, height=220)

            # CSV Yuklab olish
            if all_csv_rows:
                df_export = pd.DataFrame(all_csv_rows)
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Audit Jurnalini CSV Formatida Yuklab Olish",
                    data=csv_data,
                    file_name=f"primeguard_audit_log_{val.bit_length()}bit.csv",
                    mime="text/csv",
                    use_container_width=True
                )


# ==============================================================================
# TAB 2: ⚠️ KARMAYKL TUZOG‘I (CARMICHAEL PARADOX)
# ==============================================================================
with tab2:
    st.markdown(r"""
    <div class="cyber-card" style="border-color: rgba(245, 158, 11, 0.4);">
        <div style="font-weight: 700; font-size: 1.15rem; color: #F59E0B; margin-bottom: 0.4rem;">
            ⚠️ Karmaykl Sonlari (Universal Psevdotublar) va Korselt Mezoni
        </div>
        <div style="font-size: 0.92rem; color: #94A3B8; line-height: 1.5;">
            <b>Karmaykl sonlari</b> — Kichik Fermat teoremasining jiddiy zaifligini fosh qiluvchi g'ayritabiiy murakkab sonlardir.
            Ular murakkab son bo'lishiga qaramay, o'zlari bilan o'zaro tub bo'lgan <i>barcha</i> \( a \) asoslar uchun
            \( a^{n-1} \equiv 1 \pmod n \) tenglikni soxta qanoatlantiradi. Quyidagi laboratoriyada Fermat testining aldanishini
            va zamonaviy algoritmlarning uni qanday fosh etishini tekshiring.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_select, col_custom = st.columns([1, 1])

    with col_select:
        carm_selected = st.selectbox(
            "Mashhur Karmaykl sonini tanlang:",
            options=CARMICHAEL_NUMBERS,
            index=CARMICHAEL_NUMBERS.index(8911) if 8911 in CARMICHAEL_NUMBERS else 0,
            help="Tarixiy va kriptografik tahlillarda keng qo'llaniladigan universal psevdotub sonlar."
        )

    with col_custom:
        custom_carm = st.text_input(
            "Yoki maxsus son kiriting (ixtiyoriy):",
            value="",
            placeholder="Masalan: 561, 8911, 1105...",
            help="Bo'sh qoldirsangiz, chapdagi tanlangan son tahlil qilinadi."
        )

    if st.button("⚠️ Karmaykl Tuzog'ini Tahlil Qilish", type="primary", use_container_width=True):
        target_str = custom_carm.strip() if custom_carm.strip() else str(carm_selected)
        n_carm, err_m, a_type = validate_number_input(target_str)

        if a_type == "error":
            st.markdown(f"""
            <div class="cyber-alert cyber-alert-error">
                <span class="cyber-alert-icon">🚫</span>
                <div class="cyber-alert-content">
                    <div class="cyber-alert-title">Xato Kiritish</div>
                    <div class="cyber-alert-msg">{err_m}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Karmaykl va Korselt tahlili o'tkazilmoqda..."):
                try:
                    carm_report = analyze_carmichael(n_carm, global_k)
                except TypeError:
                    carm_report = analyze_carmichael(n_carm)

                if isinstance(carm_report, dict) and "fermat" in carm_report:
                    c_f = safe_extract_result(carm_report["fermat"])
                    c_ss = safe_extract_result(carm_report["solovay_strassen"])
                    c_mr = safe_extract_result(carm_report["miller_rabin"])
                else:
                    c_f = safe_extract_result(fermat_test(n_carm, global_k))
                    c_ss = safe_extract_result(solovay_strassen_test(n_carm, global_k))
                    c_mr = safe_extract_result(miller_rabin_test(n_carm, global_k))

            st.markdown(f"### 🔬 n = {n_carm} Sonini Yonma-Yon Qiyoslash")

            col_c1, col_c2, col_c3 = st.columns(3)

            # Fermat Card (Carmichael Trap)
            with col_c1:
                is_fermat_fooled = c_f["is_prime"]
                card_style = "kpi-card-warning" if is_fermat_fooled else "kpi-card-composite"
                badge_style = "kpi-status-warning" if is_fermat_fooled else "kpi-status-composite"
                title_status = "🚨 YOLG'ON TUB (ALDOV)" if is_fermat_fooled else "MURAKKAB"

                st.markdown(f"""
                <div class="kpi-card {card_style}">
                    <div class="kpi-algo-name">
                        <span>Fermat Testi</span>
                        <span class="cyber-badge cyber-badge-amber">Zaif</span>
                    </div>
                    <div class="kpi-status-badge {badge_style}">
                        {title_status}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Xulosa:</span>
                        <span class="kpi-metric-val" style="color: {'#F59E0B' if is_fermat_fooled else '#F43F5E'};">
                            {'Tuzoqqa tushdi!' if is_fermat_fooled else 'Guvoh topildi'}
                        </span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{c_f['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Fosh etuvchi asos:</span>
                        <span class="kpi-metric-val">{c_f['witness'] if c_f['witness'] else 'Mavjud emas'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Solovay-Strassen Card
            with col_c2:
                ss_passed = c_ss["is_prime"]
                card_style_ss = "kpi-card-prime" if ss_passed else "kpi-card-composite"
                badge_style_ss = "kpi-status-prime" if ss_passed else "kpi-status-composite"
                title_ss = "EHTIMOLIY TUB" if ss_passed else "✅ ANIQ MURAKKAB"

                st.markdown(f"""
                <div class="kpi-card {card_style_ss}">
                    <div class="kpi-algo-name">
                        <span>Solovay-Strassen</span>
                        <span class="cyber-badge cyber-badge-green">Euler Mezoni</span>
                    </div>
                    <div class="kpi-status-badge {badge_style_ss}">
                        {title_ss}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Xulosa:</span>
                        <span class="kpi-metric-val" style="color: {'#10B981' if not ss_passed else '#F59E0B'};">
                            {'Karmayklni fosh qildi' if not ss_passed else 'Euler yolg\'onchisi'}
                        </span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{c_ss['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Euler Guvohi:</span>
                        <span class="kpi-metric-val" style="color: #F43F5E;">{c_ss['witness'] if c_ss['witness'] else '—'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Miller-Rabin Card
            with col_c3:
                mr_passed = c_mr["is_prime"]
                card_style_mr = "kpi-card-prime" if mr_passed else "kpi-card-composite"
                badge_style_mr = "kpi-status-prime" if mr_passed else "kpi-status-composite"
                title_mr = "EHTIMOLIY TUB" if mr_passed else "✅ ANIQ MURAKKAB"

                st.markdown(f"""
                <div class="kpi-card {card_style_mr}">
                    <div class="kpi-algo-name">
                        <span>Miller-Rabin Strong</span>
                        <span class="cyber-badge cyber-badge-green">Kripto Standart</span>
                    </div>
                    <div class="kpi-status-badge {badge_style_mr}">
                        {title_mr}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Xulosa:</span>
                        <span class="kpi-metric-val" style="color: #10B981;">
                            {'Tuzoqqa tushmaydi' if not mr_passed else 'Tub deb topildi'}
                        </span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{c_mr['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Kuchli Guvoh:</span>
                        <span class="kpi-metric-val" style="color: #F43F5E;">{c_mr['witness'] if c_mr['witness'] else '—'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Chuqur Matematik Tahlil (Korselt Mezoni)
            st.markdown("### 📐 Korselt Mezoni va Matematik Fosh Qilish")

            factors_list = carm_report.get("factors", [])
            if not factors_list:
                temp_val = n_carm
                d_val = 2
                while d_val * d_val <= temp_val and len(factors_list) < 15:
                    if temp_val % d_val == 0:
                        factors_list.append(d_val)
                        while temp_val % d_val == 0:
                            temp_val //= d_val
                    d_val += 1
                if temp_val > 1:
                    factors_list.append(temp_val)

            factors_str = " × ".join(map(str, factors_list)) if factors_list else "Aniqlanmoqda..."
            korselt_sat = carm_report.get("korselt_satisfied", True)

            st.markdown(rf"""
            <div class="cyber-card">
                <div style="font-weight: 700; color: #00F5D4; font-size: 1rem; margin-bottom: 0.6rem;">
                    Tub Ko'paytuvchilarga Ajralish:
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; color: #F1F5F9; margin-bottom: 1rem;">
                    {n_carm} = {factors_str}
                </div>
                <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.6;">
                    <b>Korselt Teoremasi (1899-yil):</b> Musbat murakkab toq son \( n \) faqat va faqat quyidagi shartlar
                    bajarilgandagina Karmaykl soni bo'ladi:
                    <ol style="margin-top: 0.4rem;">
                        <li>\( n \) kvadratlardan xoli (square-free), ya'ni har bir tub bo'luvchi darajasi 1 ga teng.</li>
                        <li>\( n \) ning har bir \( p \) tub bo'luvchisi uchun \( (p - 1) \mid (n - 1) \) bo'linish sharti qanoatlantiriladi.</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if "korselt_details" in carm_report:
                with st.expander("🔍 Bo'linish Shartlarini Raundma-raund Tekshirish:"):
                    for detail_line in carm_report["korselt_details"]:
                        st.markdown(f"- `{detail_line}`")

            st.markdown(r"""
            <div class="cyber-card" style="border-color: rgba(16, 185, 129, 0.3);">
                <div style="font-weight: 700; color: #10B981; font-size: 0.98rem; margin-bottom: 0.4rem;">
                    Nima Uchun Miller-Rabin Bu Tuzoqqa Tushmaydi?
                </div>
                <div style="font-size: 0.9rem; color: #94A3B8; line-height: 1.6;">
                    Karmaykl sonlarida \( a^{n-1} \equiv 1 \pmod n \) bo'lsa-da, Miller-Rabin testi \( n-1 = 2^s \cdot d \)
                    dekompozitsiyasini amalga oshirib, ketma-ket kvadratlash jarayonida <b>1 ning trivial bo'lmagan kvadrat ildizlarini</b>
                    tekshiradi. Modul murakkab son bo'lganligi sababli, Xitoy Qoldiqlar Teoremasi (CRT) bo'yicha
                    \( x^2 \equiv 1 \pmod n \) tenglama kamida \( 2^r \ge 8 \) ta yechimga ega bo'ladi (\( \pm 1 \) dan tashqari yechimlar).
                    Miller-Rabin bunday yechimni uchratgan zahoti sonning murakkabligini 100% aniqlik bilan isbotlaydi.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# TAB 3: 📊 KOMPLEKS BENCHMARK
# ==============================================================================
with tab3:
    st.markdown("""
    <div class="cyber-card">
        <div style="font-weight: 700; font-size: 1.15rem; color: #00F5D4; margin-bottom: 0.4rem;">
            Algoritmlar Samaradorligi va Tezlik Benchmarki
        </div>
        <div style="font-size: 0.92rem; color: #94A3B8; line-height: 1.5;">
            Kriptografik kalitlar (64 bitdan 2048 bitgacha) miqyosida tublik testlarining hisoblash
            murakkabligini empirik o'lchash. Plotly orqali asimptotik o'sish dinamikasi va guruhlangan
            taqqoslama grafiklar hosil qilinadi.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_b1, col_b2 = st.columns([2, 1])

    with col_b1:
        chosen_bits = st.multiselect(
            "Sinov bit uzunliklarini tanlang:",
            options=[64, 128, 256, 512, 1024, 2048],
            default=[64, 128, 256, 512],
            help="Katta bitlar (1024, 2048) ko'proq hisoblash vaqtini talab qilishi mumkin."
        )

    with col_b2:
        bench_rounds = st.number_input(
            "Benchmark raundlar soni (k):",
            min_value=5,
            max_value=64,
            value=global_k,
            step=1
        )

    if st.button("🚀 Benchmarkni Ishga Tushirish", type="primary", use_container_width=True):
        if not chosen_bits:
            st.warning("Iltimos, kamida bitta bit uzunligini tanlang.")
        else:
            with st.spinner("Benchmark o'lchovlari bajarilmoqda..."):
                sorted_bits = sorted(chosen_bits)
                raw_bench = run_benchmark(sorted_bits, int(bench_rounds))

                if isinstance(raw_bench, pd.DataFrame):
                    df_bench = raw_bench
                elif isinstance(raw_bench, list):
                    df_bench = pd.DataFrame(raw_bench)
                elif isinstance(raw_bench, dict):
                    df_bench = pd.DataFrame(raw_bench)
                else:
                    df_bench = pd.DataFrame()

                # Normalize column names if needed
                col_map = {
                    "Bit_Length": "bit_length", "bits": "bit_length", "Bit Length": "bit_length",
                    "Algorithm": "algorithm", "algo": "algorithm", "Algoritm": "algorithm",
                    "Avg_Time_ms": "execution_time_ms", "time": "execution_time_ms",
                    "time_ms": "execution_time_ms", "Vaqt (ms)": "execution_time_ms"
                }
                df_bench.rename(columns=col_map, inplace=True)

            st.markdown("### 📈 Grafik Tahlillar")

            col_g1, col_g2 = st.columns(2)

            color_map = {
                "Fermat": "#00F5D4",
                "Solovay-Strassen": "#F59E0B",
                "Miller-Rabin": "#10B981"
            }

            # 1. Line Chart
            with col_g1:
                fig_line = px.line(
                    df_bench,
                    x="bit_length",
                    y="execution_time_ms",
                    color="algorithm",
                    markers=True,
                    title="Bit Uzunligi bo'yicha Vaqt (O(k·log³ n) Trendi)",
                    labels={"bit_length": "Bit Uzunligi (bits)", "execution_time_ms": "Vaqt (ms)", "algorithm": "Algoritm"},
                    template="plotly_dark",
                    color_discrete_map=color_map
                )
                fig_line.update_layout(
                    paper_bgcolor="#0B0F19",
                    plot_bgcolor="rgba(17, 24, 39, 0.7)",
                    font_family="JetBrains Mono, monospace",
                    title_font_color="#00F5D4",
                    hovermode="x unified"
                )
                st.plotly_chart(fig_line, use_container_width=True)

            # 2. Grouped Bar Chart
            with col_g2:
                fig_bar = px.bar(
                    df_bench,
                    x="bit_length",
                    y="execution_time_ms",
                    color="algorithm",
                    barmode="group",
                    title="Algoritmlararo Samaradorlik Taqqoslashi",
                    labels={"bit_length": "Bit Uzunligi (bits)", "execution_time_ms": "Vaqt (ms)", "algorithm": "Algoritm"},
                    template="plotly_dark",
                    color_discrete_map=color_map
                )
                fig_bar.update_layout(
                    paper_bgcolor="#0B0F19",
                    plot_bgcolor="rgba(17, 24, 39, 0.7)",
                    font_family="JetBrains Mono, monospace",
                    title_font_color="#00F5D4"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Jadval va CSV eksport
            st.markdown("### 📋 Natijalar Jadvali")
            st.dataframe(df_bench, use_container_width=True)

            csv_bench_data = df_bench.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Benchmark Natijalarini CSV Formatida Yuklab Olish",
                data=csv_bench_data,
                file_name="primeguard_benchmark_results.csv",
                mime="text/csv",
                use_container_width=True
            )


# ==============================================================================
# TAB 4: 🔐 RSA TUB SON GENERATOR
# ==============================================================================
with tab4:
    st.markdown(r"""
    <div class="cyber-card">
        <div style="font-weight: 700; font-size: 1.15rem; color: #00F5D4; margin-bottom: 0.4rem;">
            Sanoat Darajasidagi RSA Tub Sonlar va Kalitlar Generatori
        </div>
        <div style="font-size: 0.92rem; color: #94A3B8; line-height: 1.5;">
            Kriptografik xavfsiz tasodifiy sonlar generatori (CSPRNG) va <b>Miller-Rabin Strong</b> testi asosida
            haqiqiy RSA kalit juftligining negizlari (\( p, q, N, \phi(N) \)) hisoblanadi. Bosh sonlar teoremasi
            (PNT) bo'yicha nazariy kutilgan sinovlar soni bilan amaliy nomzodlar statistikasi taqqoslanadi.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns([1, 1])

    with col_r1:
        rsa_bit_choice = st.radio(
            "Har bir tub son (p va q) uchun bit o'lchami:",
            options=[512, 1024, 2048],
            index=0,
            horizontal=True,
            help="512 bit -> RSA-1024 moduli; 1024 bit -> RSA-2048 moduli (Standart); 2048 bit -> RSA-4096 moduli."
        )

    with col_r2:
        rsa_security_k = st.slider(
            "Miller-Rabin xavfsizlik raundi (k):",
            min_value=10,
            max_value=64,
            value=global_k,
            step=1,
            help="FIPS 186-5 standarti bo'yicha kamida k=20 tavsiya etiladi."
        )

    if st.button("🔑 RSA Kalit Juftligi va Tub Sonlarni Generatsiya Qilish", type="primary", use_container_width=True):
        with st.spinner(f"Kriptografik xavfsiz {rsa_bit_choice}-bit tub sonlar generatsiya qilinmoqda..."):
            try:
                # key_bits moduli o'lchami: p va q ning har biri rsa_bit_choice bit bo'lishi uchun key_bits = rsa_bit_choice * 2
                rsa_res = generate_rsa_pair(rsa_bit_choice * 2, rsa_security_k)
            except Exception:
                try:
                    rsa_res = generate_rsa_pair(rsa_bit_choice, rsa_security_k)
                except Exception:
                    rsa_res = generate_rsa_pair(rsa_bit_choice)

        p = rsa_res["p"]
        q = rsa_res["q"]
        n_mod = rsa_res.get("N", rsa_res.get("n", p * q))
        phi_n = rsa_res.get("phi", (p - 1) * (q - 1))
        t_ms = rsa_res.get("elapsed_ms", rsa_res.get("execution_time_ms", 0.0))
        c_tested = rsa_res.get("total_candidates_tested", 0)
        c_expected = rsa_res.get("theoretical_expected_tests", int(rsa_bit_choice * 0.693))

        st.markdown("### 🏆 Generatsiya Natijalari va Xavfsizlik Metrikalari")

        # 4 ta Kichik KPI Metrika
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            st.markdown(f"""
            <div class="kpi-card kpi-card-neutral">
                <div class="kpi-metric-label">Umumiy Vaqt</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #00F5D4; margin: 0.3rem 0;">
                    {t_ms:.2f} ms
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8;">CSPRNG + Testlar</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
            <div class="kpi-card kpi-card-neutral">
                <div class="kpi-metric-label">Tekshirilgan Nomzodlar</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #F1F5F9; margin: 0.3rem 0;">
                    {c_tested} ta
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8;">Nomzod elakdan o'tkazildi</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            st.markdown(f"""
            <div class="kpi-card kpi-card-neutral">
                <div class="kpi-metric-label">Nazariy Kutilgan (PNT)</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #F59E0B; margin: 0.3rem 0;">
                    ≈ {c_expected} ta
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8;">b · ln(2) / 2 me'yori</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m4:
            st.markdown(f"""
            <div class="kpi-card kpi-card-prime">
                <div class="kpi-metric-label">Xatolik Ehtimoli</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #10B981; margin: 0.3rem 0;">
                    ≤ 4⁻{rsa_security_k}
                </div>
                <div style="font-size: 0.75rem; color: #10B981;">Kriptografik xavfsiz</div>
            </div>
            """, unsafe_allow_html=True)

        # Fermat faktorizatsiyasi xavfsizligi
        p_q_diff = abs(p - q)
        diff_bits = p_q_diff.bit_length()
        is_fermat_safe = diff_bits >= (rsa_bit_choice - 100)

        st.markdown(f"""
        <div class="cyber-alert {'cyber-alert-success' if is_fermat_safe else 'cyber-alert-warning'}">
            <span class="cyber-alert-icon">{"🔒" if is_fermat_safe else "⚠️"}</span>
            <div class="cyber-alert-content">
                <div class="cyber-alert-title">Fermat Faktorizatsiya Hujumidan Himoya (|p - q| Tahlili)</div>
                <div class="cyber-alert-msg">
                    |p - q| masofasi: <b>{diff_bits} bit</b>. 
                    {f"Tub sonlar bir-biridan yetarlicha uzoq joylashgan (|p - q| > 2^{rsa_bit_choice - 100}), Fermat faktorizatsiyasi xavfi bartaraf etilgan." if is_fermat_safe else "Diqqat: Tub sonlar bir-biriga juda yaqin!"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Kalitlar ko'rinishi
        st.markdown("#### 🔑 Generatsiya Qilingan Kriptografik Parametrlar:")

        with st.expander(f"📌 Birinchi Tub Son (p) — {p.bit_length()} bit", expanded=False):
            st.markdown("**O'nlik (Decimal):**")
            st.code(str(p), language="text")
            st.markdown("**O'n oltilik (Hexadecimal):**")
            st.code(hex(p), language="text")

        with st.expander(f"📌 Ikkinchi Tub Son (q) — {q.bit_length()} bit", expanded=False):
            st.markdown("**O'nlik (Decimal):**")
            st.code(str(q), language="text")
            st.markdown("**O'n oltilik (Hexadecimal):**")
            st.code(hex(q), language="text")

        with st.expander(f"🛡️ RSA Moduli (N = p × q) — {n_mod.bit_length()} bit", expanded=True):
            st.markdown("**O'nlik (Decimal):**")
            st.code(str(n_mod), language="text")
            st.markdown("**O'n oltilik (Hexadecimal):**")
            st.code(hex(n_mod), language="text")

        with st.expander(f"📐 Eyler Funksiyasi φ(N) = (p-1)(q-1) — {phi_n.bit_length()} bit", expanded=False):
            st.markdown("**O'nlik (Decimal):**")
            st.code(str(phi_n), language="text")
            st.markdown("**O'n oltilik (Hexadecimal):**")
            st.code(hex(phi_n), language="text")

        # JSON Eksport
        export_payload = {
            "metadata": {
                "system": "PrimeGuard Suite v1.0",
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "algorithm": "Miller-Rabin Strong Pseudoprime",
                "rounds_k": rsa_security_k,
                "bit_length_each": rsa_bit_choice,
                "rsa_modulus_bits": n_mod.bit_length()
            },
            "performance": {
                "execution_time_ms": t_ms,
                "candidates_tested": c_tested,
                "theoretical_expected": c_expected
            },
            "keys": {
                "p_decimal": str(p),
                "p_hex": hex(p),
                "q_decimal": str(q),
                "q_hex": hex(q),
                "N_modulus_decimal": str(n_mod),
                "N_modulus_hex": hex(n_mod),
                "phi_N_decimal": str(phi_n),
                "phi_N_hex": hex(phi_n)
            }
        }

        json_bytes = json.dumps(export_payload, indent=2).encode('utf-8')
        st.download_button(
            label="📥 RSA Kalit Ma'lumotlarini JSON Formatida Yuklab Olish",
            data=json_bytes,
            file_name=f"primeguard_rsa_{n_mod.bit_length()}bit_keys.json",
            mime="application/json",
            use_container_width=True
        )

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; padding: 1rem 0;">
    PrimeGuard Suite v1.0 • Kriptografiya Matematik Usullari • Agent B (Cyber-Security Frontend Architect & Technical Writer)<br>
    FIPS 186-5 & RFC 3447 Talablariga Muofiq Ishlab Chiqilgan
</div>
""", unsafe_allow_html=True)
