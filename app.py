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
    inline_script = f"<script>\n{orgchart_js}\n</script>"

    if script_tag_pattern.search(html):
        return script_tag_pattern.sub(lambda _match: inline_script, html, count=1)

    # If the include does not exist, inject before </head>.
    head_close_pattern = re.compile(r"</head>", re.IGNORECASE)
    if head_close_pattern.search(html):
        return head_close_pattern.sub(lambda _match: inline_script + "\n</head>", html, count=1)

    return inline_script + "\n" + html


def _load_demo_html(demo_path: Path, orgchart_js: str) -> str:
    html = _read_text(demo_path)
    return _inject_js(html, orgchart_js)


def main() -> None:
    st.set_page_config(page_title="ChineseStrVisualizer", layout="wide")
    st.title("ChineseStrVisualizer on Streamlit")
    st.caption("Render existing OrgChart HTML demos directly in Streamlit.")

    if not DEMO_FILES:
        st.error("No demo HTML files found in this workspace.")
        return

    selected_name = st.sidebar.selectbox("Select demo", [p.name for p in DEMO_FILES], index=0)
    frame_height = st.sidebar.slider("Frame height", min_value=400, max_value=1200, value=760, step=20)
    show_source = st.sidebar.checkbox("Show HTML source", value=False)

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
