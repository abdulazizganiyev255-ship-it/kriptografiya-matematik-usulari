"""Regression checks for Streamlit UI compatibility and display contracts."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP_FILE = ROOT / "app.py"


def test_ui_uses_supported_width_and_pandas_apis():
    source = APP_FILE.read_text(encoding="utf-8")
    assert "use_container_width=" not in source
    assert "inplace=True" not in source
    assert 'width="stretch"' in source


def test_html_education_panels_have_no_literal_tex_delimiters():
    source = APP_FILE.read_text(encoding="utf-8")
    assert r"\(" not in source
    assert r"\)" not in source
    assert "a<sup>n−1</sup>" in source
    assert "φ(N)" in source


def test_benchmark_is_persistent_and_filters_are_present():
    source = APP_FILE.read_text(encoding="utf-8")
    assert 'st.session_state["primeguard_benchmark_data"]' in source
    assert 'key="primeguard_benchmark_candidate_type"' in source
    assert 'facet_col="candidate_type"' not in source
    assert "friendly_table" in source
    assert 'df_bench.to_csv(index=False)' in source


def test_app_initial_streamlit_render_has_no_exception():
    app = AppTest.from_file(str(APP_FILE), default_timeout=20).run()
    assert not app.exception
    assert len(app.tabs) >= 4
