from __future__ import annotations

import html
import os
import re

import requests
import streamlit as st

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")


def api_post(path: str, payload: dict, timeout: int = 120):
    response = requests.post(
        f"{BACKEND_URL}{path}",
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response


def preview_html(text: str) -> str:
    safe = html.escape(text)
    blocks = []
    for block in re.split(r"\n\s*\n", safe):
        lines = block.splitlines()
        if not lines:
            continue
        first = lines[0].strip()
        if re.match(r"^\d+[\.\)]\s+", first) or (
            len(first) < 80 and first.isupper()
        ):
            blocks.append(f"<h3>{first}</h3>")
            rest = "<br>".join(lines[1:]).strip()
            if rest:
                blocks.append(f"<p>{rest}</p>")
        else:
            blocks.append(f"<p>{'<br>'.join(lines)}</p>")
    return "".join(blocks)


if "document" not in st.session_state:
    st.session_state.document = ""
if "model" not in st.session_state:
    st.session_state.model = ""

st.markdown(
    """
    <style>
    .hero { text-align:center; padding: 0.5rem 0 1rem 0; }
    .hero h1 { margin-bottom: 0.2rem; }
    .muted { color: #777; }
    .preview {
        background: #111827; color: #f3f4f6; padding: 24px;
        border-radius: 12px; max-height: 650px; overflow-y: auto;
        line-height: 1.65;
    }
    .preview h3 { color: #ffffff; margin-top: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>⚖️ LegalEase</h1>'
    '<div class="muted">AI-Powered Legal Document Generator</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Connection")
    st.caption(f"Backend: `{BACKEND_URL}`")
    if st.button("Check backend"):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=10)
            r.raise_for_status()
            info = r.json()
            st.success("Backend is online")
            st.json(info)
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")

    st.divider()
    st.caption(
        "LegalEase generates AI-assisted drafts. Always review generated content "
        "with a qualified legal professional before relying on it."
    )

left, right = st.columns(2)

with left:
    st.subheader("Document details")
    document_type = st.text_input(
        "Document Type",
        placeholder="Freelance Work Contract",
    )
    parties = st.text_area(
        "Parties Involved",
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=110,
    )
    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help="Separate clauses with semicolons or put each clause on a new line.",
    )
    dates = st.text_input(
        "Effective Date",
        placeholder="April 15, 2026",
    )
    language = st.selectbox(
        "Language",
        ["English", "Tamil", "Hindi", "Spanish", "French"],
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )

with right:
    st.subheader("Document preview")

    if generate:
        if not all(x.strip() for x in [document_type, parties, terms, dates]):
            st.warning("Please fill in document type, parties, terms, and effective date.")
        else:
            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "dates": dates,
                "language": language,
            }
            with st.spinner("Generating document..."):
                try:
                    response = api_post("/generate", payload)
                    data = response.json()
                    st.session_state.document = data["content"]
                    st.session_state.model = data["model"]
                    st.success(f"Generated using: {data['model']}")
                except requests.HTTPError as exc:
                    detail = exc.response.text if exc.response is not None else str(exc)
                    st.error(f"Generation failed: {detail}")
                except requests.RequestException as exc:
                    st.error(f"Cannot reach backend: {exc}")

    if st.session_state.document:
        st.markdown(
            f'<div class="preview">{preview_html(st.session_state.document)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Your generated document will appear here.")

st.divider()

if st.session_state.document:
    st.subheader("Edit Document")
    edited = st.text_area(
        "Editable document",
        value=st.session_state.document,
        height=520,
        label_visibility="collapsed",
    )
    st.session_state.document = edited

    st.subheader("Download")
    export_payload = {
        "document_type": document_type or "Legal Document",
        "content": st.session_state.document,
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Download TXT", use_container_width=True):
            try:
                r = api_post("/export/txt", export_payload)
                st.download_button(
                    "Save TXT file",
                    r.content,
                    "legalease_document.txt",
                    "text/plain",
                    use_container_width=True,
                )
            except Exception as exc:
                st.error(str(exc))

    with c2:
        if st.button("Download DOCX", use_container_width=True):
            try:
                r = api_post("/export/docx", export_payload)
                st.download_button(
                    "Save DOCX file",
                    r.content,
                    "legalease_document.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as exc:
                st.error(str(exc))

    with c3:
        if st.button("Download PDF", use_container_width=True):
            try:
                r = api_post("/export/pdf", export_payload)
                st.download_button(
                    "Save PDF file",
                    r.content,
                    "legalease_document.pdf",
                    "application/pdf",
                    use_container_width=True,
                )
            except Exception as exc:
                st.error(str(exc))
