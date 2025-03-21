import streamlit as st
from components.chat_interface import render_chat_interface
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant - Chat",
    page_icon="💬",
    layout="wide"
)

# Inisialisasi session state jika tidak ada
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "llm" not in st.session_state:
    st.session_state.llm = None
if "history" not in st.session_state:
    st.session_state.history = []

# Header
st.title("💬 AI Business Consultant Pro")
st.markdown("""
Konsultan bisnis AI yang dapat membantu Anda dengan strategi bisnis, 
analisis data, pemasaran, keuangan, dan rekomendasi berdasarkan dokumen yang Anda unggah.
""")

# Render chat interface
try:
    render_chat_interface()
except Exception as e:
    logger.error(f"Error rendering chat interface: {str(e)}")
    st.error(f"⚠️ Terjadi kesalahan saat menampilkan chat interface: {str(e)}")
    
    # Informasi debugging untuk admin
    with st.expander("Debug Info", expanded=False):
        st.write("Session State Variables:")
        for key, value in st.session_state.items():
            if key == "api_key" or "_api_key" in key:
                st.write(f"- {key}: {'[SET]' if value else '[NOT SET]'}")
            else:
                st.write(f"- {key}: {type(value)}")
