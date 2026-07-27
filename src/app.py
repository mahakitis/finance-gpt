import os
import requests
import streamlit as st

# ------------------ Config ------------------ #
BASE_URL = os.getenv("FINANCEGPT_API_URL", "http://localhost:8000")
UPLOAD_URL = f"{BASE_URL}/upload/document"
QUERY_URL = f"{BASE_URL}/query"
SESSION_CREATE_URL = f"{BASE_URL}/session/create"

st.set_page_config(page_title="FinanceGPT", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 900px; }
    [data-testid="stChatMessage"] { border-radius: 12px; }
    .fg-header {
        display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.2rem;
    }
    .fg-subtitle { color: #8a8f98; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .fg-empty {
        text-align: center; color: #8a8f98; padding: 3rem 1rem;
        border: 1px dashed #3a3f4b; border-radius: 12px;
    }
    .stStatusWidget { display: none; }
</style>
""", unsafe_allow_html=True)


# ------------------ Session bootstrap ------------------ #
def create_session() -> str | None:
    try:
        res = requests.post(SESSION_CREATE_URL, timeout=15)
        res.raise_for_status()
        return res.json().get("session_id")
    except requests.RequestException as e:
        st.error(f"Couldn't reach the backend to start a session: {e}")
        return None


def fetch_history(session_id: str) -> list[dict]:
    try:
        res = requests.get(f"{BASE_URL}/session/{session_id}/history", timeout=15)
        if res.status_code == 200:
            return res.json().get("history", [])
        return []
    except requests.RequestException:
        return []


# Restore session_id from the URL if present (survives page refresh),
# otherwise mint a new one and store it in the URL.
query_params = st.query_params
if "session_id" not in st.session_state:
    sid_from_url = query_params.get("session_id")
    if sid_from_url:
        st.session_state.session_id = sid_from_url
        st.session_state.messages = fetch_history(sid_from_url)
    else:
        new_sid = create_session()
        if new_sid:
            st.session_state.session_id = new_sid
            st.session_state.messages = []
            st.query_params["session_id"] = new_sid

if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------ Sidebar ------------------ #
with st.sidebar:
    st.markdown("### 📊 FinanceGPT")
    st.caption("Ask questions about your uploaded financial documents, or general finance/market questions.")

    st.divider()

    if st.button("🔁 New conversation", use_container_width=True):
        new_sid = create_session()
        if new_sid:
            st.session_state.session_id = new_sid
            st.session_state.messages = []
            st.query_params["session_id"] = new_sid
            st.rerun()

    st.divider()
    st.markdown("#### 📁 Upload a document")
    uploaded_file = st.file_uploader(
        "PDF, DOCX, or TXT", type=["pdf", "docx", "txt"], label_visibility="collapsed"
    )
    if uploaded_file is not None:
        if st.session_state.get("last_uploaded") != uploaded_file.name:
            with st.spinner("Processing & generating embeddings..."):
                try:
                    response = requests.post(
                        UPLOAD_URL,
                        files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                        timeout=120,
                    )
                    if response.status_code == 200:
                        st.session_state.last_uploaded = uploaded_file.name
                        st.success(f"✅ '{uploaded_file.name}' indexed. Ask about it below.")
                    else:
                        detail = response.json().get("detail", response.text)
                        st.error(f"Upload failed: {detail}")
                except requests.RequestException as e:
                    st.error(f"Upload error: {e}")

    st.divider()
    with st.expander("Session details"):
        st.code(st.session_state.get("session_id", "—"), language=None)


# ------------------ Main chat area ------------------ #
st.markdown('<div class="fg-header"><h2>💬 FinanceGPT</h2></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fg-subtitle">Powered by your uploaded documents + live web search for market data.</div>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        '<div class="fg-empty">No messages yet — upload a document from the sidebar, '
        'or just ask a finance question below to get started.</div>',
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.messages:
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):
            st.markdown(msg["answer"])

user_input = st.chat_input("Ask a finance question...")

if user_input:
    if not st.session_state.get("session_id"):
        st.error("No active session — click 'New conversation' in the sidebar.")
    else:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = requests.post(
                        QUERY_URL,
                        json={"session_id": st.session_state.session_id, "query": user_input},
                        timeout=60,
                    )
                    if res.status_code == 200:
                        answer = res.json().get("answer", "⚠️ No answer from server")
                    else:
                        answer = f"⚠️ Error: {res.json().get('detail', res.text)}"
                except requests.RequestException as e:
                    answer = f"⚠️ Couldn't reach the backend: {e}"
                st.markdown(answer)

        st.session_state.messages.append({"question": user_input, "answer": answer})
        st.rerun()