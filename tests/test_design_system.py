"""Design-system regression checks: semantics, contrast and native theme."""
import tomllib
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def _luminance(hex_color: str) -> float:
    rgb = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    components = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * components[0] + 0.7152 * components[1] + 0.0722 * components[2]


def contrast_ratio(foreground: str, background: str) -> float:
    light, dark = sorted([_luminance(foreground), _luminance(background)], reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_native_theme_has_matched_palette():
    theme = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8"))
    assert theme["theme"]["base"] == "dark"
    assert theme["client"]["toolbarMode"] == "viewer"
    assert theme["theme"]["primaryColor"] == "#69D6C5"
    assert theme["theme"]["backgroundColor"] == "#0B1220"
    assert theme["theme"]["secondaryBackgroundColor"] == "#131F32"
    assert theme["theme"]["sidebar"]["backgroundColor"] == "#0E192A"


def test_small_text_and_cta_meet_wcag_aa_contrast():
    pairs = [
        ("#F2F6FA", "#0B1220"),  # main copy
        ("#ACBCCD", "#131F32"),  # secondary copy
        ("#8C9FB3", "#131F32"),  # subdued labels
        ("#75D9AF", "#131F32"),  # success badge
        ("#FF8898", "#131F32"),  # composite badge
        ("#F3C77B", "#131F32"),  # educational notice
        ("#082524", "#69D6C5"),  # primary button label
    ]
    for foreground, background in pairs:
        assert contrast_ratio(foreground, background) >= 4.5, (
            foreground, background, contrast_ratio(foreground, background)
        )


def test_css_covers_core_blocks_and_responsive_accessibility():
    stylesheet = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    for selector in (".cyber-card", ".kpi-card", ".kpi-metric-row",
                     ".kpi-status-badge", ".cyber-alert", ".cyber-badge",
                     "button:focus-visible", "prefers-reduced-motion"):
        assert selector in stylesheet
    assert "@import" not in stylesheet
    assert stylesheet.count("PrimeGuard · Primality Research UI v2") == 1


def test_sample_carmichael_button_opens_educational_experiment():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25).run()
    assert not app.exception
    app.button(key="primeguard_sample_carmichael").click().run()
    assert not app.exception
    assert app.session_state["primeguard_show_carmichael"] is True
    assert app.session_state["tab1_text_area"] == "8911"
