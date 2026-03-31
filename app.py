from __future__ import annotations

from pathlib import Path
import re

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
DEMO_FILES = sorted(ROOT.glob("[1-4][ab].html"))
JS_CANDIDATES = [ROOT / "orgchart.js", ROOT / "package" / "orgchart.js"]


def _read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp949", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"Cannot decode {path}")


def _load_orgchart_js() -> str:
    for candidate in JS_CANDIDATES:
        if candidate.exists():
            return _read_text(candidate)
    raise FileNotFoundError("orgchart.js was not found in project root or package/")


def _inject_js(html: str, orgchart_js: str) -> str:
    # Replace external OrgChart script include with inline script for Streamlit iframe rendering.
    script_tag_pattern = re.compile(
        r'<script\s+src=["\'](?:\./)?(?:OrgChart|orgchart)\.js["\']\s*></script>',
        re.IGNORECASE,
    )
    layout_style = """
<style>
#tree { position: relative; }
div[data-id="search"],
div[id="search"] {
    position: absolute !important;
    top: 6px !important;
    right: 12px !important;
    left: auto !important;
    margin: 0 !important;
    transform: none !important;
    z-index: 30;
}
div[data-id="search-icon"],
div[id="search-icon"] {
    position: absolute !important;
    top: 6px !important;
    right: 320px !important;
    left: auto !important;
    margin: 0 !important;
    transform: none !important;
    z-index: 31;
}
</style>
"""
    inline_script = f"<script>\n{orgchart_js}\n</script>"
    position_fix_script = """
<script>
(function () {
    function pinSearchControls() {
        var search = document.querySelector('div[data-id="search"], div[id="search"]');
        var icon = document.querySelector('div[data-id="search-icon"], div[id="search-icon"]');
        if (!search && !icon) return;

        var tree = document.getElementById('tree') || document.body;
        var wrapper = icon ? icon.parentElement : (search ? search.parentElement : null);

        if (wrapper && tree.contains(wrapper)) {
            wrapper.style.position = 'absolute';
            wrapper.style.top = '6px';
            wrapper.style.right = '12px';
            wrapper.style.left = 'auto';
            wrapper.style.margin = '0';
            wrapper.style.zIndex = '40';
            wrapper.style.width = 'auto';
            wrapper.style.height = 'auto';
        }

        if (search) {
            search.style.position = 'absolute';
            search.style.top = '0';
            search.style.right = '0';
            search.style.left = 'auto';
            search.style.margin = '0';
            search.style.transform = 'none';
        }

        if (icon) {
            icon.style.position = 'absolute';
            icon.style.top = '0';
            icon.style.right = '308px';
            icon.style.left = 'auto';
            icon.style.margin = '0';
            icon.style.transform = 'none';
        }
    }

    var observer = new MutationObserver(pinSearchControls);
    observer.observe(document.documentElement, { childList: true, subtree: true });

    window.addEventListener('load', function () {
        setTimeout(pinSearchControls, 10);
        setTimeout(pinSearchControls, 150);
        setTimeout(pinSearchControls, 500);
    });
})();
</script>
"""
    injection = layout_style + "\n" + inline_script + "\n" + position_fix_script

    if script_tag_pattern.search(html):
        return script_tag_pattern.sub(lambda _match: injection, html, count=1)

    # If the include does not exist, inject before </head>.
    head_close_pattern = re.compile(r"</head>", re.IGNORECASE)
    if head_close_pattern.search(html):
        return head_close_pattern.sub(lambda _match: injection + "\n</head>", html, count=1)

    return injection + "\n" + html


def _load_demo_html(demo_path: Path, orgchart_js: str) -> str:
    html = _read_text(demo_path)
    return _inject_js(html, orgchart_js)


def main() -> None:
    st.set_page_config(page_title="ChineseStrVisualizer", layout="wide")
    st.title("중국어 문장 구조 시각화 App")
    st.markdown(
        "중국어 문법 교육에 반응형 웹페이지(html5) 적용 <br> - 추상적인 문장 구조 시각화 <br> - 자극-반응을 통한 학습효과 극대화",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] .csv-footer {
            position: fixed;
            bottom: 1rem;
            left: 1rem;
            right: 1rem;
            font-size: 0.8rem;
            color: #6b7280;
            line-height: 1.4;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not DEMO_FILES:
        st.error("No demo HTML files found in this workspace.")
        return

    selected_name = st.sidebar.selectbox("예문 선택", [p.name for p in DEMO_FILES], index=0)
    frame_height = st.sidebar.slider("카드 크기 변경", min_value=400, max_value=1200, value=760, step=20)
    show_source = st.sidebar.checkbox("Show HTML source", value=False)
    st.sidebar.markdown(
        '<div class="csv-footer">ChineseStrVisualizer v.0.1<br/>Copyright © MJ Park</div>',
        unsafe_allow_html=True,
    )

    selected_path = ROOT / selected_name

    try:
        orgchart_js = _load_orgchart_js()
        html = _load_demo_html(selected_path, orgchart_js)
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)
        return

    components.html(html, height=frame_height, scrolling=True)

    if show_source:
        st.subheader("Loaded HTML")
        st.code(html, language="html")


if __name__ == "__main__":
    main()
