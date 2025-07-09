import streamlit as st
import requests
from session_utils import get_chat_history, add_chat_to_history, clear_chat_history

# ------------------ Backend URLs ------------------ #
BASE_URL = "http://localhost:8000"
UPLOAD_URL = f"{BASE_URL}/upload/document"
QUERY_URL = f"{BASE_URL}/query"
SESSION_URL = f"{BASE_URL}/session/create"

# ------------------ Config ------------------ #
st.set_page_config(page_title="FinanceGPT", layout="wide")

# ------------------ App State ------------------ #
if "view" not in st.session_state:
    st.session_state.view = "home"

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# ------------------ Home View ------------------ #
def render_home():
    st.title("📊 Welcome to FinanceGPT!")
    st.write("Ask questions about your financial documents powered by AI.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 Upload Document"):
            st.session_state.view = "upload"

    with col2:
        if st.button("💬 Start Conversation"):
            try:
                res = requests.post(SESSION_URL)
                if res.status_code == 200:
                    st.session_state.session_id = res.json().get("session_id")
                    clear_chat_history()
                    st.session_state.view = "chat"
                else:
                    st.error("Failed to start session.")
            except Exception as e:
                st.error(f"Error: {e}")

# ------------------ Upload View ------------------ #
def render_upload():
    st.header("📁 Upload a Financial Document")
    uploaded_file = st.file_uploader("Choose a file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file:
        with st.spinner("Processing and generating embeddings..."):
            try:
                response = requests.post(
                    UPLOAD_URL,
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                )
                if response.status_code == 200:
                    st.success("✅ Document uploaded and embeddings created!")
                    st.session_state.view = "home"
                    st.experimental_rerun()
                else:
                    st.error(f"Upload failed: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Upload error: {e}")

    if st.button("⬅️ Back to Home"):
        st.session_state.view = "home"

# ------------------ Chat View ------------------ #
def render_chat():
    st.header("💬 Chat with FinanceGPT")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Restart Conversation"):
            try:
                res = requests.post(SESSION_URL)
                if res.status_code == 200:
                    st.session_state.session_id = res.json().get("session_id")
                    clear_chat_history()
                    st.success("New session started!")
                else:
                    st.error("Failed to restart session.")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("⬅️ Back to Home"):
            st.session_state.view = "home"

    # Display chat history
    history = get_chat_history(st.session_state.session_id)
    for question, answer in history:
        with st.container():
            st.markdown(f"""
                <div style='background-color:#cfe9f1; padding:10px; border-radius:10px; margin-bottom:5px; text-align:right'>
                    {question}
                </div>
                <div style='background-color:#fde2e4; padding:10px; border-radius:10px; margin-bottom:15px; text-align:left'>
                    {answer}
                </div>
            """, unsafe_allow_html=True)

    user_input = st.chat_input("Ask a question...")

    if user_input:
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "session_id": st.session_state.session_id,
                    "query": user_input
                }
                res = requests.post(QUERY_URL, json=payload)
                if res.status_code == 200:
                    answer = res.json().get("answer", "⚠️ No answer from server")
                    add_chat_to_history(st.session_state.session_id, user_input, answer)
                    st.rerun()
                else:
                    st.error(f"Error: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Query error: {e}")


# ------------------ Render Based on View ------------------ #
if st.session_state.view == "home":
    render_home()
elif st.session_state.view == "upload":
    render_upload()
elif st.session_state.view == "chat":
    render_chat()
