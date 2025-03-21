import streamlit as st
import os
import logging
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.file_upload import render_file_upload

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Inisialisasi session state
def init_session_state():
    """Inisialisasi variabel session state yang diperlukan"""
    if "api_key" not in st.session_state:
        st.session_state.api_key = None
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "memory" not in st.session_state:
        st.session_state.memory = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = "openai"
    if "current_model" not in st.session_state:
        st.session_state.current_model = "gpt-3.5-turbo"
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False
    if "file_info" not in st.session_state:
        st.session_state.file_info = {}
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "token_usage" not in st.session_state:
        st.session_state.token_usage = {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi session state
init_session_state()

# Render sidebar
render_sidebar()

# Main content
st.title("💼 AI Business Consultant Pro")
st.markdown("""
Konsultan bisnis AI yang dapat membantu Anda dengan strategi bisnis, 
analisis data, pemasaran, keuangan, dan rekomendasi berdasarkan dokumen yang Anda unggah.
""")

# Buat tab untuk fitur-fitur utama
tab1, tab2 = st.tabs(["💬 Chat", "📂 Upload File"])

with tab1:
    render_chat_interface()

with tab2:
    render_file_upload()
