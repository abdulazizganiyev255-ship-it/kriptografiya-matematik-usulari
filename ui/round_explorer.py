"""Interactive explanation of an already executed primality-test round."""
from collections.abc import Mapping

import streamlit as st

from analytics.round_explainer import ALGORITHMS, build_round_trace


def render_round_explorer(
    n: int,
    results: Mapping[str, dict],
    *,
    namespace: str = "primeguard",
) -> None:
    """Display algorithm, round and arithmetic-step navigation.

    Only recorded logs are used: interaction never reruns randomness or the
    algorithms, and therefore cannot quietly change a previous conclusion.
    """
    st.markdown("### 🧭 Algoritm qanday ishlaydi?")
    st.caption(
        "Algoritmni, bajarilgan raundni va qadamni tanlang. "
        "Har bir hisoblash aynan shu raundda tanlangan a asosidan qayta "
        "tekshiriladi; yangi tasodifiy asos tanlanmaydi."
    )

    algorithm = st.selectbox(
        "Algoritmni tanlang",
        options=list(ALGORITHMS),
        key=f"{namespace}_algorithm",
    )
    result = results[algorithm]
    logs = result["logs"]

    if not logs:
        st.info(
            "Bu son uchun tasodifiy tekshiruv o'tkazilmadi: "
            "dastlabki elak yoki maxsus holat natijani aniqlagan."
        )
        return

    round_numbers = [log.round_idx for log in logs]
    round_number = st.select_slider(
        "Raundni tanlang",
        options=round_numbers,
        key=f"{namespace}_round",
    )
    record = next(log for log in logs if log.round_idx == round_number)
    trace = build_round_trace(algorithm, n, record)

    st.caption(
        f"{round_number}-raund / {result['rounds']} ta bajarilgan raund"
        + (" · Murakkablik guvohi topilgan" if not record.passed
           else " · Ushbu raund sinovdan o'tgan")
    )

    context_key = f"{namespace}_trace_context"
    step_key = f"{namespace}_trace_step"
    context = (n, algorithm, round_number)
    if st.session_state.get(context_key) != context:
        st.session_state[context_key] = context
        st.session_state[step_key] = 0

    position = st.session_state[step_key]
    if not isinstance(position, int) or not 0 <= position < len(trace.steps):
        position = 0
        st.session_state[step_key] = position

    previous_col, next_col = st.columns(2)
    with previous_col:
        if st.button(
            "◀ Oldingi qadam",
            disabled=position == 0,
            width="stretch",
            key=f"{namespace}_previous",
        ):
            position -= 1
            st.session_state[step_key] = position
    with next_col:
        if st.button(
            "Keyingi qadam ▶",
            disabled=position >= len(trace.steps) - 1,
            width="stretch",
            key=f"{namespace}_next",
        ):
            position += 1
            st.session_state[step_key] = position

    step = trace.steps[position]
    st.progress((position + 1) / len(trace.steps))
    st.markdown(
        f"**{position + 1}/{len(trace.steps)} — {step.title}**"
    )
    st.latex(step.formula)
    st.code(step.value, language="text")
    if step.status == "fail":
        st.error(step.explanation)
    elif step.status == "pass":
        st.success(step.explanation)
    else:
        st.info(step.explanation)

    if not trace.matches_log:
        st.error(
            "Diqqat: qayta hisoblangan raund natijasi saqlangan log bilan mos emas. "
            "Ushbu natijaga tayanmang; matematik yadro tekshirilishi kerak."
        )
    if trace.truncated:
        st.warning(
            "Juda uzun kvadratlash zanjirining dastlabki 128 ta qadami "
            "ko'rsatilgan. Qolganlari hisoblab tekshirilgan."
        )

    with st.expander("Barcha qadamlar jadvalini ko'rish"):
        st.dataframe(
            [
                {
                    "Qadam": index,
                    "Nomi": item.title,
                    "Natija": item.value,
                    "Holat": item.status,
                }
                for index, item in enumerate(trace.steps, 1)
            ],
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "Jadval ushbu tanlangan raundga tegishli. "
            "Raundning butun son bo'yicha yakuniy tublik isboti emasligini "
            "unutmang."
        )
