"""PrimeGuard: ehtimollik asosidagi tublik algoritmlari laboratoriyasi."""

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

# Asosiy matematik algoritmlar va tahlil modullari.
from core.models import PrimalityResult, RoundLog
from core.fermat import fermat_test
from core.solovay_strassen import solovay_strassen_test
from core.miller_rabin import miller_rabin_test
from core.number_theory import is_prime_deterministic_64
from analytics.carmichael import CARMICHAEL_NUMBERS, analyze_carmichael
from analytics.benchmark import run_benchmark
from ui.round_explorer import render_round_explorer

# ==============================================================================
# STREAMLIT CONFIG & OFFLINE STYLING
# ==============================================================================
st.set_page_config(
    page_title="PrimeGuard | Ehtimoliy tublik laboratoriyasi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    """Load the local PrimeGuard theme stylesheet."""
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
            color: #F2F6FA !important;
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
        return None, "Kiritish maydoni bo'sh. Tekshirish uchun natural son kiriting.", "error"

    if len(clean_str.lstrip("-")) > 2048:
        return None, "Kiritilgan son juda uzun. Ko'pi bilan 2048 ta raqam kiriting.", "error"

    if not clean_str.isascii() or not clean_str.isdigit():
        if clean_str.startswith("-"):
            return None, "Manfiy sonlar kiritilishi mumkin emas. Kriptografik tublik faqat natural sonlar (n ≥ 2) uchun aniqlanadi.", "error"
        return None, "Kiritilgan qiymatda harf yoki ruxsat etilmagan belgi bor. Faqat natural son kiriting.", "error"

    val = int(clean_str)
    if val < 2:
        return None, f"Kiritilgan son (n = {val}) tublik shartiga to'g'ri kelmaydi. Kriptografik tahlil uchun n ≥ 2 bo'lishi shart. 0 va 1 tub son emas.", "error"

    if val == 2:
        return val, "2 — yagona juft tub son. Deterministik xulosa: Probabilistik test talab etilmaydi.", "success"

    if val % 2 == 0:
        return val, f"Kiritilgan son juft (n = {val}). U 2 ga bo'lingani sababli, darhol deterministik ravishda MURAKKAB son ekanligi ma'lum.", "warning"

    return val, None, "valid"


def safe_extract_result(res: PrimalityResult) -> Dict[str, Any]:
    """Algoritm natijasini interfeys ko'rsatadigan oddiy lug'atga o'tkazadi."""
    witness = next((log.witness_a for log in res.logs if not log.passed), None)
    return {
        "is_prime": res.is_prime,
        "execution_time_ms": res.elapsed_ms,
        "rounds": res.rounds_run,
        "witness": witness,
        "logs": res.logs,
        "algorithm": res.algorithm,
        "pre_filtered": res.pre_filtered,
        "verdict": res.verdict,
        "error_bound": res.error_bound,
    }

# ==============================================================================
# SIDEBAR: SOZLAMALAR, NAZARIY EHTIMOLLIK VA TEZKOR NAMUNALAR
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.8rem;">🛡️</span>
        <div>
            <div style="font-weight: 800; font-size: 1.25rem; color: #69D6C5; letter-spacing: -0.01em;">
                PrimeGuard
            </div>
            <div style="font-size: 0.75rem; color: #ACBCCD; font-family: 'JetBrains Mono', monospace;">
                Ehtimoliy tublik laboratoriyasi
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Global Rounds Slider
    st.markdown("### Tekshiruv sozlamalari")
    global_k = st.slider(
        "Raundlar soni (k):",
        min_value=1,
        max_value=64,
        value=20,
        step=1,
        help="Ehtimoliy tublik testlarida ishlatiladigan tasodifiy asoslar soni."
    )

    # Tezkor Namuna Tugmalari
    st.markdown("### Tayyor sonlar")
    st.caption("Sonni yuklang, so‘ng tekshirishni boshlang.")

    SAMPLE_MERSENNE = "170141183460469231731687303715884105727"  # 2^127 - 1
    SAMPLE_CARMICHAEL = "8911"  # 7 * 19 * 67
    SAMPLE_512_PRIME = (
        "134078079299425970995740249982058461274793658205923933777235614437217"
        "640300735469768018742981669034276900318581864860508537538828119465699"
        "46433649006083527"
    )
    SAMPLE_COMPOSITE = "340282366920938463463374607431768211455"  # 2^128 - 1

    if st.button("127-bit tub son", width="stretch"):
        st.session_state["input_candidate"] = SAMPLE_MERSENNE
        st.session_state["tab1_text_area"] = SAMPLE_MERSENNE
        st.rerun()

    if st.button("Karmaykl soni: 8911", width="stretch"):
        st.session_state["input_candidate"] = SAMPLE_CARMICHAEL
        st.session_state["tab1_text_area"] = SAMPLE_CARMICHAEL
        st.session_state["carmichael_select"] = 8911
        st.session_state["primeguard_show_carmichael"] = True
        st.rerun()

    if st.button("512-bit tub son", width="stretch"):
        st.session_state["input_candidate"] = SAMPLE_512_PRIME
        st.session_state["tab1_text_area"] = SAMPLE_512_PRIME
        st.rerun()

    if st.button("128-bit murakkab son", width="stretch"):
        st.session_state["input_candidate"] = SAMPLE_COMPOSITE
        st.session_state["tab1_text_area"] = SAMPLE_COMPOSITE
        st.rerun()

    st.markdown("---")
    # Jonli Nazariy xatolik chegarasi Hisob-kitobi
    err_ss = 2 ** (-global_k)
    err_mr = 4 ** (-global_k)

    st.markdown(f"""
    <div class="cyber-card" style="padding: 1rem; margin: 1rem 0; border-color: rgba(0, 245, 212, 0.3);">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #69D6C5; font-weight: 700; margin-bottom: 0.5rem;">
            NAZARIY XATOLIK CHEGARALARI
        </div>
        <div style="font-size: 0.82rem; margin-bottom: 0.4rem; color: #CBD8E4;">
            <b>Fermat:</b> universal xatolik chegarasi yo'q (Karmaykl sonlari sababli).<br>
            <b>Solovay–Strassen:</b><br>
            <span style="font-family: 'JetBrains Mono', monospace; color: #F3C77B;">
                2<sup>-{global_k}</sup> ≈ {err_ss:.2e}
            </span>
        </div>
        <div style="font-size: 0.82rem; color: #CBD8E4;">
            <b>Miller–Rabin:</b><br>
            <span style="font-family: 'JetBrains Mono', monospace; color: #75D9AF;">
                4<sup>-{global_k}</sup> ≈ {err_mr:.2e}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-size: 0.75rem; color: #8C9FB3; font-family: 'JetBrains Mono', monospace; line-height: 1.4;">
        Akademik laboratoriya<br>
        Fermat · Solovay–Strassen · Miller–Rabin<br>
        Ehtimoliy natija matematik isbot emas
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# ASOSIY ISH MAYDONI: SARLAVHA VA 4 TA INTERAKTIV TAB
# ==============================================================================
st.markdown("""
<div style="margin-bottom: 1.2rem;">
    <div class="cyber-header">
        <span class="cyber-header-accent">PrimeGuard</span>
    </div>
    <div class="cyber-subtitle">
        Sonni tekshirish · Matematik izoh · Algoritmlarni taqqoslash
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab3 = st.tabs([
    "🔍 Sonni tekshirish",
    "📊 Algoritmlarni taqqoslash",
])

# ==============================================================================
# TAB 1: 🔍 TUBLIK AUDITI
# ==============================================================================
with tab1:
    st.markdown("""
    <div class="cyber-card">
        <div style="font-weight: 700; font-size: 1.1rem; color: #69D6C5; margin-bottom: 0.4rem;">
            Sonning tubligini tekshirish
        </div>
        <div style="font-size: 0.92rem; color: #ACBCCD; line-height: 1.5;">
            Natural sonni kiriting va tekshirishni boshlang. Natijalar <b>Fermat</b>,
            <b>Solovay–Strassen</b> hamda <b>Miller–Rabin</b> algoritmlari orqali
            bir xil son uchun hisoblanadi. Ehtimoliy natija matematik isbot emas.
        </div>
    </div>
    """, unsafe_allow_html=True)

    default_input = st.session_state.get("input_candidate", SAMPLE_MERSENNE)

    raw_candidate = st.text_area(
        "Tekshiriladigan son (n)",
        value=default_input,
        height=95,
        help="Faqat natural son kiriting. O'qish qulayligi uchun raqamlarni bo'sh joy bilan guruhlash mumkin.",
        key="tab1_text_area"
    )

    action_col, detail_col = st.columns([1, 2])
    with action_col:
        start_audit = st.button(
            "Sonni tekshirish", width="stretch", type="primary",
            key="primeguard_start_audit",
        )
    with detail_col:
        st.caption("3 algoritm · mustaqil raundlar · matematik izohli natijalar")

    if start_audit:
        candidate, feedback, feedback_type = validate_number_input(raw_candidate)
        if feedback_type == "error":
            st.session_state.pop("primeguard_last_audit", None)
            st.error(feedback)
        else:
            with st.spinner(f"Son tahlil qilinmoqda ({global_k} raund)..."):
                computed_fermat = safe_extract_result(fermat_test(candidate, global_k))
                computed_ss = safe_extract_result(solovay_strassen_test(candidate, global_k))
                computed_mr = safe_extract_result(miller_rabin_test(candidate, global_k))
            st.session_state["primeguard_last_audit"] = {
                "n": candidate,
                "k": global_k,
                "message": feedback,
                "alert_type": feedback_type,
                "fermat": computed_fermat,
                "solovay_strassen": computed_ss,
                "miller_rabin": computed_mr,
            }

    # Preserve the exact random witness logs across Streamlit widget reruns.
    last_audit = st.session_state.get("primeguard_last_audit")
    if last_audit is not None:
        val = last_audit["n"]
        audit_k = last_audit["k"]
        res_f = last_audit["fermat"]
        res_ss = last_audit["solovay_strassen"]
        res_mr = last_audit["miller_rabin"]
        if last_audit["alert_type"] == "warning":
            st.warning(last_audit["message"])
        elif last_audit["alert_type"] == "success":
            st.success(last_audit["message"])

        current_raw = raw_candidate.strip().replace(" ", "").replace("_", "")
        if current_raw != str(val) or global_k != audit_k:
            st.info(
                "Quyidagi natija avvalgi tekshiruvga tegishli. Yangi son yoki "
                "raund qiymatini qo'llash uchun «Sonni tekshirish» tugmasini bosing."
            )

        # Bit uzunligi va raqamlar soni
        bit_len = val.bit_length()
        digit_len = len(str(val))

        st.markdown(f"""
        <div style="display: flex; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
            <span class="cyber-badge cyber-badge-cyan">Uzunligi: {bit_len} bit</span>
            <span class="cyber-badge cyber-badge-cyan">Raqamlar: {digit_len} ta</span>
            <span class="cyber-badge cyber-badge-cyan">Raundlar: {audit_k}</span>
        </div>
        """, unsafe_allow_html=True)

        # Mustaqil deterministik etalon faqat 64-bit diapazonida kafolatlangan.
        audit_results = [res_f, res_ss, res_mr]
        deterministic_reference = (
            is_prime_deterministic_64(val) if val < (1 << 64) else None
        )
        if any(not result["is_prime"] for result in audit_results):
            st.error("Yakuniy xulosa: SON MURAKKAB. Kamida bitta algoritm murakkablik guvohini topdi.")
        elif deterministic_reference is True:
            st.success("Yakuniy xulosa: SON ANIQ TUB. n < 2⁶⁴ uchun deterministik Miller–Rabin etaloni bilan tasdiqlandi.")
        elif deterministic_reference is False:
            st.error("Yakuniy xulosa: SON MURAKKAB. 64-bit deterministik etalon murakkablikni tasdiqladi.")
        else:
            st.info("Yakuniy xulosa: SON EHTIMOLIY TUB. Uchala test ham guvoh topmadi; n ≥ 2⁶⁴ bo'lgani uchun ushbu dasturda deterministik etalon qo'llanmaydi.")


        # 3 ta Neon KPI Kartochka
        col1, col2, col3 = st.columns(3)

        cards_data = [
            ("Fermat testi", res_f, "Universal chegara yo'q", "Fermatning kichik teoremasi"),
            ("Solovay–Strassen", res_ss, f"≤ 2⁻{audit_k}", "Eyler–Yakobi mezoni"),
            ("Miller–Rabin", res_mr, f"≤ 4⁻{audit_k}", "Kuchli murakkablik guvohlari")
        ]

        for col, (algo_title, r_data, err_bound, complexity) in zip([col1, col2, col3], cards_data):
            is_p = r_data["is_prime"]
            card_class = "kpi-card-prime" if is_p else "kpi-card-composite"
            badge_class = "kpi-status-prime" if is_p else "kpi-status-composite"
            status_text = ("ANIQ TUB" if r_data["verdict"] == "Prime" else "EHTIMOLIY TUB") if is_p else "ANIQ MURAKKAB"
            shown_error = "0 (aniq)" if r_data["pre_filtered"] else err_bound
            witness_display = (
                f"a = {r_data['witness']}" if r_data["witness"] is not None
                else ("Oldindan tekshirildi" if r_data["pre_filtered"]
                      else "Topilmadi")
            )

            with col:
                st.markdown(f"""
                <div class="kpi-card {card_class}">
                    <div class="kpi-algo-name">
                        <span>{algo_title}</span>
                        <span style="font-size: 0.72rem; color: #8C9FB3;">{complexity}</span>
                    </div>
                    <div class="kpi-status-badge {badge_class}">
                        {status_text}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{r_data['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Nazariy xatolik chegarasi:</span>
                        <span class="kpi-metric-val" style="color: {'#75D9AF' if is_p else '#ACBCCD'};">{shown_error if is_p else '0 (Aniq)'}</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilgan raundlar:</span>
                        <span class="kpi-metric-val">{r_data['rounds']} ta</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Murakkablik guvohi:</span>
                        <span class="kpi-metric-val" style="font-size: 0.8rem; color: {'#FF8898' if r_data['witness'] else '#75D9AF'};">
                            {witness_display}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # The step explorer uses the exact RoundLog bases from this saved run.
        render_round_explorer(
            val,
            {
                "Fermat": res_f,
                "Solovay-Strassen": res_ss,
                "Miller-Rabin": res_mr,
            },
            namespace="primeguard_audit",
        )

        # Raundlar bo'yicha tekshiruv jurnali
        st.markdown("### 📋 Tekshiruv bosqichlari")

        tab_log_f, tab_log_ss, tab_log_mr = st.tabs([
            "Fermat bosqichlari", "Solovay–Strassen bosqichlari", "Miller–Rabin bosqichlari"
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
                    st.info("Maxsus holat (n ≤ 3 yoki juft son) tufayli ehtimoliy test raundlari o'tkazilmadi.")
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

                        status_str = "O'tdi (Tublikka mos)" if res_bool else "O'tmadi (murakkablik guvohi)"

                        table_rows.append({
                            "Bosqich": r_num,
                            "Tanlangan asos (a)": str(base_a),
                            "Holat": status_str,
                            "Hisoblash tafsiloti": str(details)
                        })

                        all_csv_rows.append({
                            "Nomzod_Son": str(val)[:50] + ("..." if len(str(val)) > 50 else ""),
                            "Algoritm": algo_name,
                            "Bosqich": r_num,
                            "Asos_a": str(base_a),
                            "Holat": status_str,
                            "Bajarilish_ms": r_data['execution_time_ms'],
                            "Izoh": str(details)
                        })

                    df_logs = pd.DataFrame(table_rows)
                    st.dataframe(df_logs, width="stretch", height=220)

        # CSV Yuklab olish
        if all_csv_rows:
            df_export = pd.DataFrame(all_csv_rows)
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇ Tekshiruv jurnalini CSV formatida yuklab olish",
                data=csv_data,
                file_name=f"primeguard_audit_log_{val.bit_length()}bit.csv",
                mime="text/csv",
                width="stretch"
            )

        # To'liq natijani JSON ko'rinishida saqlash
        json_results = {}
        for algo_label, algo_result in [
            ("Fermat", res_f),
            ("Solovay-Strassen", res_ss),
            ("Miller-Rabin", res_mr),
        ]:
            json_results[algo_label] = {
                "verdict": algo_result["verdict"],
                "is_probable_prime": algo_result["is_prime"],
                "execution_time_ms": algo_result["execution_time_ms"],
                "rounds_requested": audit_k,
                "rounds_completed": algo_result["rounds"],
                "error_bound": algo_result.get("error_bound"),
                "witness": algo_result["witness"],
                "steps": [
                    {
                        "round": getattr(item, "round_idx", None),
                        "base": getattr(item, "witness_a", None),
                        "expression": getattr(item, "expression", ""),
                        "computed_value": getattr(item, "computed_value", ""),
                        "passed": getattr(item, "passed", None),
                        "note": getattr(item, "note", ""),
                    }
                    for item in algo_result["logs"]
                ],
            }

        audit_json = {
            "project": "PrimeGuard",
            "report_type": "probabilistic_primality_audit",
            "number_decimal": str(val),
            "bit_length": bit_len,
            "decimal_digits": digit_len,
            "rounds": audit_k,
            "deterministic_64_reference": deterministic_reference,
            "deterministic_reference_scope": "n < 2**64",
            "results": json_results,
        }
        st.download_button(
            label="⬇ To'liq hisobotni JSON formatida yuklab olish",
            data=json.dumps(audit_json, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"primeguard_report_{bit_len}bit.json",
            mime="application/json",
            width="stretch",
        )


# ==============================================================================
# KARMAYKL — SONNI TEKSHIRISH BO'LIMIDAGI O'QUV TAJRIBASI
# ==============================================================================
with tab1:
    st.divider()
    st.markdown("#### 🧪 Karmaykl sonlari: Fermat testining cheklovi")
    st.caption(
        "Ixtiyoriy matematik tajriba: 561, 8911 va boshqa kichik sonlarda "
        "Fermat, Solovay–Strassen va Miller–Rabin natijalarini solishtiring."
    )
    if st.toggle(
        "Karmaykl tajribasini ochish",
        key="primeguard_show_carmichael",
        value=False,
    ):
        st.markdown(r"""
        <div class="cyber-card" style="border-color: rgba(245, 158, 11, 0.4);">
            <div style="font-weight: 700; font-size: 1.15rem; color: #F3C77B; margin-bottom: 0.4rem;">
                ⚠️ Karmaykl sonlari va Korselt mezoni
            </div>
            <div style="font-size: 0.92rem; color: #ACBCCD; line-height: 1.5;">
                <b>Karmaykl sonlari</b> — Fermat testining cheklovini ko'rsatuvchi o'ziga xos murakkab sonlardir.
                Ular murakkab son bo'lishiga qaramay, o'zlari bilan o'zaro tub bo'lgan <i>barcha</i> <em>a</em> asoslar uchun
                <code>a<sup>n−1</sup> ≡ 1 (mod n)</code> tenglikni bajaradi. Quyidagi laboratoriyada Fermat testining aldanishini
                va boshqa algoritmlar murakkablikni qanday aniqlashini tekshiring.
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_select, col_custom = st.columns([1, 1])

        with col_select:
            carm_selected = st.selectbox(
                "Tayyor Karmaykl sonini tanlang:",
                options=CARMICHAEL_NUMBERS,
                index=CARMICHAEL_NUMBERS.index(8911) if 8911 in CARMICHAEL_NUMBERS else 0,
                key="carmichael_select",
                help="Fermat testining cheklovini ko'rsatadigan mashhur murakkab sonlar."
            )

        with col_custom:
            custom_carm = st.text_input(
                "Boshqa son kiritish (ixtiyoriy):",
                value="",
                placeholder="Masalan: 561, 8911, 1105...",
                help="Bo'sh qoldirsangiz, chapdagi tanlangan son tahlil qilinadi."
            )

        if st.button(
            "Karmaykl sonini tahlil qilish",
            type="primary",
            width="stretch",
            key="primeguard_start_carmichael",
        ):
            target_str = custom_carm.strip() if custom_carm.strip() else str(carm_selected)
            candidate, feedback, feedback_type = validate_number_input(target_str)
            if feedback_type == "error":
                st.session_state.pop("primeguard_last_carmichael", None)
                st.error(feedback)
            elif candidate > 1_000_000:
                st.session_state.pop("primeguard_last_carmichael", None)
                st.warning(
                    "Karmaykl tajribasi 1 000 000 gacha bo'lgan sonlar bilan cheklangan. "
                    "Katta sonlarni yuqoridagi asosiy tublik tekshiruvida sinang."
                )
            else:
                with st.spinner("Karmaykl soni Korselt mezoni bo'yicha tekshirilmoqda..."):
                    report = analyze_carmichael(candidate, global_k)
                st.session_state["primeguard_last_carmichael"] = {
                    "n": candidate,
                    "k": global_k,
                    "report": report,
                    "fermat": safe_extract_result(report["fermat"]),
                    "solovay_strassen": safe_extract_result(report["solovay_strassen"]),
                    "miller_rabin": safe_extract_result(report["miller_rabin"]),
                }

        last_carmichael = st.session_state.get("primeguard_last_carmichael")
        if last_carmichael is not None:
            n_carm = last_carmichael["n"]
            carm_report = last_carmichael["report"]
            c_f = last_carmichael["fermat"]
            c_ss = last_carmichael["solovay_strassen"]
            c_mr = last_carmichael["miller_rabin"]

            current_carm = custom_carm.strip() if custom_carm.strip() else str(carm_selected)
            if current_carm != str(n_carm) or global_k != last_carmichael["k"]:
                st.info(
                    "Quyidagi natija avvalgi Karmaykl tahliliga tegishli. "
                    "Yangi parametrlarni qo'llash uchun tahlil tugmasini qayta bosing."
                )

            st.markdown(f"### {n_carm} soni — algoritmlar natijasi")

            col_c1, col_c2, col_c3 = st.columns(3)

            # Fermat Card (Carmichael Trap)
            with col_c1:
                fermat_passed = c_f["is_prime"]
                is_fermat_fooled = fermat_passed and carm_report.get("is_carmichael") is True
                card_style = "kpi-card-warning" if is_fermat_fooled else ("kpi-card-prime" if fermat_passed else "kpi-card-composite")
                badge_style = "kpi-status-warning" if is_fermat_fooled else ("kpi-status-prime" if fermat_passed else "kpi-status-composite")
                title_status = "FERMATNING CHEKLOVI" if is_fermat_fooled else ("EHTIMOLIY TUB" if fermat_passed else "ANIQ MURAKKAB")
                fermat_summary = "Fermat sharti bajarildi, ammo son murakkab" if is_fermat_fooled else ("Bu raundlarda sinovdan o'tdi; bu isbot emas" if fermat_passed else "Fermat guvohi topildi")

                st.markdown(f"""
                <div class="kpi-card {card_style}">
                    <div class="kpi-algo-name">
                        <span>Fermat testi</span>
                        <span class="cyber-badge cyber-badge-amber">Zaif</span>
                    </div>
                    <div class="kpi-status-badge {badge_style}">
                        {title_status}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Xulosa:</span>
                        <span class="kpi-metric-val" style="color: {'#F3C77B' if is_fermat_fooled else '#FF8898'};">
                            {fermat_summary}
                        </span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{c_f['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Murakkablik guvohi (a):</span>
                        <span class="kpi-metric-val">{c_f['witness'] if c_f['witness'] else 'Mavjud emas'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Solovay-Strassen Card
            with col_c2:
                ss_passed = c_ss["is_prime"]
                card_style_ss = "kpi-card-prime" if ss_passed else "kpi-card-composite"
                badge_style_ss = "kpi-status-prime" if ss_passed else "kpi-status-composite"
                title_ss = "EHTIMOLIY TUB" if ss_passed else "ANIQ MURAKKAB"
                ss_summary = "Murakkablikni aniqladi" if not ss_passed else "Eyler–Yakobi sinovidan o'tdi"

                st.markdown(f"""
                <div class="kpi-card {card_style_ss}">
                    <div class="kpi-algo-name">
                        <span>Solovay–Strassen</span>
                        <span class="cyber-badge cyber-badge-green">Eyler–Yakobi mezoni</span>
                    </div>
                    <div class="kpi-status-badge {badge_style_ss}">
                        {title_ss}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Xulosa:</span>
                        <span class="kpi-metric-val" style="color: {'#75D9AF' if not ss_passed else '#F3C77B'};">
                            {ss_summary}
                        </span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{c_ss['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Eyler–Yakobi guvohi:</span>
                        <span class="kpi-metric-val" style="color: #FF8898;">{c_ss['witness'] if c_ss['witness'] else '—'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Miller-Rabin Card
            with col_c3:
                mr_passed = c_mr["is_prime"]
                card_style_mr = "kpi-card-prime" if mr_passed else "kpi-card-composite"
                badge_style_mr = "kpi-status-prime" if mr_passed else "kpi-status-composite"
                title_mr = "EHTIMOLIY TUB" if mr_passed else "ANIQ MURAKKAB"

                st.markdown(f"""
                <div class="kpi-card {card_style_mr}">
                    <div class="kpi-algo-name">
                        <span>Miller–Rabin</span>
                        <span class="cyber-badge cyber-badge-green">Kuchli tublik testi</span>
                    </div>
                    <div class="kpi-status-badge {badge_style_mr}">
                        {title_mr}
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Xulosa:</span>
                        <span class="kpi-metric-val" style="color: #75D9AF;">
                            {'Murakkablik aniqlandi' if not mr_passed else 'Ehtimoliy tub'}
                        </span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Bajarilish vaqti:</span>
                        <span class="kpi-metric-val">{c_mr['execution_time_ms']:.4f} ms</span>
                    </div>
                    <div class="kpi-metric-row">
                        <span class="kpi-metric-label">Murakkablik guvohi:</span>
                        <span class="kpi-metric-val" style="color: #FF8898;">{c_mr['witness'] if c_mr['witness'] else '—'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            render_round_explorer(
                n_carm,
                {
                    "Fermat": c_f,
                    "Solovay-Strassen": c_ss,
                    "Miller-Rabin": c_mr,
                },
                namespace="primeguard_carmichael",
            )

            # Chuqur Matematik Tahlil (Korselt Mezoni)
            st.markdown("### Korselt mezoni bo'yicha tekshiruv")

            factors_list = carm_report.get("factors", [])
            factorization_complete = carm_report.get("factorization_complete", False)
            factors_str = " × ".join(map(str, factors_list)) if factors_list else "To'liq ajratilmadi"
            korselt_sat = carm_report.get("korselt_satisfied")

            if not factorization_complete:
                st.warning("Sonning tub ko'paytuvchilarga ajratilishi hisoblash limiti ichida tugamadi. Korselt mezoni bo'yicha yakuniy xulosa berilmaydi.")
            elif korselt_sat is True:
                st.success("Korselt mezoni bajarildi: bu son Karmaykl soni.")
            else:
                st.info("Korselt mezoni bajarilmadi: bu son Karmaykl soni emas.")

            st.markdown(rf"""
            <div class="cyber-card">
                <div style="font-weight: 700; color: #69D6C5; font-size: 1rem; margin-bottom: 0.6rem;">
                    Tub ko'paytuvchilarga ajratish:
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; color: #F2F6FA; margin-bottom: 1rem;">
                    {n_carm} = {factors_str}
                </div>
                <div style="font-size: 0.92rem; color: #CBD8E4; line-height: 1.6;">
                    <b>Korselt mezoni (1899-yil):</b> Musbat murakkab toq son <em>n</em> faqat va faqat quyidagi shartlar
                    bajarilgandagina Karmaykl soni bo'ladi:
                    <ol style="margin-top: 0.4rem;">
                        <li><em>n</em> kvadratlardan xoli (square-free), ya'ni har bir tub bo'luvchi darajasi 1 ga teng.</li>
                        <li><em>n</em> ning har bir <em>p</em> tub bo'luvchisi uchun <code>(p − 1) | (n − 1)</code> bo'linish sharti qanoatlantiriladi.</li>
                    </ol>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if "korselt_details" in carm_report:
                with st.expander("🔍 Bo'linish shartlarini tekshirish:"):
                    for detail_line in carm_report["korselt_details"]:
                        st.markdown(f"- `{detail_line}`")

            st.markdown(r"""
            <div class="cyber-card" style="border-color: rgba(16, 185, 129, 0.3);">
                <div style="font-weight: 700; color: #75D9AF; font-size: 0.98rem; margin-bottom: 0.4rem;">
                    Miller–Rabin murakkablikni qanday aniqlaydi?
                </div>
                <div style="font-size: 0.9rem; color: #ACBCCD; line-height: 1.6;">
                    Karmaykl sonlari Fermat testidagi <code>a<sup>n−1</sup> ≡ 1 (mod n)</code>
                    tenglikning o'zi tublikni isbotlamasligini ko'rsatadi.
                    Miller–Rabin testi <code>n − 1 = 2<sup>s</sup> · d</code> orqali
                    <b>ketma-ket kvadratlash qoldiqlarini</b> tekshiradi. Agar guvoh topilsa,
                    son aniq murakkab. Biroq bitta tasodifiy raund hamma murakkab sonlarni
                    albatta aniqlaydi degan kafolat yo'q.
                </div>
            </div>
            """, unsafe_allow_html=True)




# ==============================================================================
# TAB 3: ALGORITMLAR TEZLIGINI TAQQOSLASH
# ==============================================================================
with tab3:
    st.markdown("""
    <div class="cyber-card">
        <div style="font-weight: 700; font-size: 1.15rem; color: #69D6C5; margin-bottom: 0.4rem;">
            Algoritmlar samaradorligi va bajarilish vaqti
        </div>
        <div style="font-size: 0.92rem; color: #ACBCCD; line-height: 1.5;">
            Bir xil sonlar ustida uch algoritmning bajarilish vaqtini taqqoslang.
            Tub son nomzodi va ikki tub son ko'paytmasidan iborat murakkab nomzod
            alohida ko'rsatiladi. <b>Median vaqt</b> asosiy taqqoslash mezonidir.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns([2, 1, 1])

    with col_b1:
        chosen_bits = st.multiselect(
            "Son uzunliklarini tanlang (bit):",
            options=[64, 128, 256, 512, 1024, 2048],
            default=[64, 128, 256],
            help="Katta sonlar ko'proq vaqt oladi. Dastlab 64–512 bit bilan sinab ko'ring."
        )

    with col_b2:
        bench_rounds = st.number_input(
            "Tekshiruv raundlari (k):",
            min_value=5,
            max_value=64,
            value=global_k,
            step=1
        )

    with col_b3:
        bench_trials = st.number_input(
            "Takrorlash soni:",
            min_value=3,
            max_value=30,
            value=10,
            step=1,
            help="Kamida 10 ta takrorlash tavsiya etiladi. Median natijaga asoslaning."
        )

    if st.button("Tezlik sinovini boshlash", type="primary", width="stretch"):
        if not chosen_bits:
            st.warning("Iltimos, kamida bitta bit uzunligini tanlang.")
        else:
            with st.spinner("Benchmark o'lchovlari bajarilmoqda..."):
                try:
                    measured = run_benchmark(
                        sorted(chosen_bits), int(bench_rounds), trials=int(bench_trials)
                    )
                except (ValueError, RuntimeError) as exc:
                    st.error(f"Tezlik sinovini bajarib bo'lmadi: {exc}")
                else:
                    st.session_state["primeguard_benchmark_data"] = measured
                    st.session_state["primeguard_benchmark_config"] = (
                        tuple(sorted(chosen_bits)), int(bench_rounds), int(bench_trials)
                    )

    # Persist benchmark output across Streamlit reruns (e.g., switching chart filters).
    df_bench = st.session_state.get("primeguard_benchmark_data")
    if df_bench is not None:
        saved_bits, saved_k, saved_trials = st.session_state["primeguard_benchmark_config"]
        st.markdown("### Grafik tahlillar")
        st.caption(
            f"Oxirgi sinov: {', '.join(map(str, saved_bits))} bit · "
            f"{saved_k} raund · {saved_trials} takrorlash. "
            "Bu haqiqiy o'lchovlar, matematik tezlik kafolati emas."
        )

        candidate_type = st.radio(
            "Taqqoslanadigan nomzod turi",
            options=("Tub nomzod", "Murakkab (semiprime)"),
            format_func=lambda value: (
                "Murakkab — ikki tub son ko'paytmasi"
                if value == "Murakkab (semiprime)" else value
            ),
            horizontal=True,
            key="primeguard_benchmark_candidate_type",
        )
        filtered = df_bench.loc[df_bench["Candidate_Type"] == candidate_type].copy()
        palette = {
            "Fermat": "#69D6C5",
            "Solovay-Strassen": "#F3C77B",
            "Miller-Rabin": "#75D9AF",
        }
        axis_labels = {
            "Bit_Length": "Bit uzunligi",
            "Median_Time_ms": "Median vaqt (ms)",
            "Algorithm": "Algoritm",
        }
        trend_tab, comparison_tab = st.tabs(
            ["Vaqt tendensiyasi", "Algoritmlarni taqqoslash"]
        )

        with trend_tab:
            trend_fig = px.line(
                filtered, x="Bit_Length", y="Median_Time_ms",
                color="Algorithm", markers=True, labels=axis_labels,
                template="plotly_dark", color_discrete_map=palette,
            )
            trend_fig.update_layout(
                height=440, margin=dict(l=38, r=22, t=55, b=45),
                paper_bgcolor="#0B1220", plot_bgcolor="#131F32",
                font=dict(family="Segoe UI, sans-serif", size=13),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="left", x=0),
                hovermode="x unified",
            )
            trend_fig.update_xaxes(type="category")
            st.plotly_chart(trend_fig, width="stretch", config={"displaylogo": False})

        with comparison_tab:
            comparison_fig = px.bar(
                filtered, x="Bit_Length", y="Median_Time_ms",
                color="Algorithm", barmode="group", labels=axis_labels,
                template="plotly_dark", color_discrete_map=palette,
            )
            comparison_fig.update_layout(
                height=440, margin=dict(l=38, r=22, t=55, b=45),
                paper_bgcolor="#0B1220", plot_bgcolor="#131F32",
                font=dict(family="Segoe UI, sans-serif", size=13),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="left", x=0),
            )
            comparison_fig.update_xaxes(type="category")
            st.plotly_chart(
                comparison_fig, width="stretch", config={"displaylogo": False}
            )

        st.markdown("### Natijalar jadvali")
        visible_columns = {
            "Bit_Length": "Bit",
            "Candidate_Type": "Nomzod turi",
            "Algorithm": "Algoritm",
            "Median_Time_ms": "Median (ms)",
            "Avg_Time_ms": "O'rtacha (ms)",
            "Std_Dev_ms": "Standart og'ish",
            "Avg_Rounds_Run": "O'rtacha raund",
            "Verdict": "Xulosa",
            "Verdict_Consistency": "Xulosalar mosligi",
        }
        friendly_table = df_bench[list(visible_columns)].rename(
            columns=visible_columns
        )
        friendly_table["Xulosa"] = friendly_table["Xulosa"].replace({
            "Probably Prime": "Ehtimoliy tub",
            "Prime": "Aniq tub",
            "Composite": "Murakkab",
            "Mixed": "Turlicha",
        })
        friendly_table["Xulosalar mosligi"] = friendly_table[
            "Xulosalar mosligi"
        ].replace({"Consistent": "Mos", "Mixed": "Turlicha"})
        st.dataframe(friendly_table, hide_index=True, width="stretch", height=420)
        st.caption(
            "Murakkab sonlarda algoritm guvoh topishi bilan to'xtaydi. "
            "Shu sabab bajarilgan raundlar va vaqt natijalari farqlanishi mumkin. "
            "CSV faylda barcha asl texnik ustunlar saqlanadi."
        )
        st.download_button(
            label="Benchmark jadvalini CSV formatida yuklab olish",
            data=df_bench.to_csv(index=False).encode("utf-8-sig"),
            file_name="primeguard_benchmark_results.csv",
            mime="text/csv",
            width="stretch",
        )


