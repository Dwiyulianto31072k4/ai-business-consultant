import streamlit as st
import os
import logging
import json
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.file_upload import render_file_upload

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Fungsi untuk memuat konfigurasi dari file
def load_config_from_file(filepath=".streamlit/config.json"):
    """Memuat konfigurasi dari file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.warning(f"Gagal memuat konfigurasi: {str(e)}")
        return {}

# Inisialisasi session state
def init_session_state():
    """Inisialisasi variabel session state yang diperlukan"""
    # Coba muat konfigurasi dari file
    config = load_config_from_file()
    
    # Inisialisasi defaults
    defaults = {
        "api_key": None,
        "llm": None,
        "memory": None,
        "history": [],
        "current_provider": "openai",
        "current_model": "gpt-3.5-turbo",
        "session_id": None,
        "file_processed": False,
        "file_info": {},
        "retriever": None,
        "conversation": None,
        "token_usage": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0},
        "temperature": 0.7,
        "max_tokens": 1024,
        "chunk_size": 500,
        "chunk_overlap": 50,
        "theme": "light",
        "language": "id",
        "tts_enabled": False,
        "tts_voice": "alloy",
        "api_keys": {
            "openai": None,
            "anthropic": None,
            "groq": None,
            "huggingface": None
        }
    }
    
    # Update defaults dengan konfigurasi yang dimuat
    for key, value in config.items():
        if key != "api_keys":  # Skip api_keys karena tidak disimpan di file
            defaults[key] = value
    
    # Set session state
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi session state
init_session_state()

# Update API key utama berdasarkan provider yang dipilih
if "current_provider" in st.session_state and "api_keys" in st.session_state:
    provider = st.session_state.current_provider
    if provider in st.session_state.api_keys and st.session_state.api_keys[provider]:
        st.session_state.api_key = st.session_state.api_keys[provider]
        # Juga set key yang sesuai dengan format <provider>_api_key
        st.session_state[f"{provider}_api_key"] = st.session_state.api_keys[provider]

# Render sidebar
render_sidebar()

# Main content
st.title("💼 AI Business Consultant Pro")
st.markdown("""
Konsultan bisnis AI yang dapat membantu Anda dengan strategi bisnis, 
analisis data, pemasaran, keuangan, dan rekomendasi berdasarkan dokumen yang Anda unggah.
""")

# Cek apakah API key telah dikonfigurasi
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

# Cek apakah API key telah dikonfigurasi
if not st.session_state.get("api_key"):
    st.warning("""
    ⚠️ **API Key belum dikonfigurasi**
    
    Silakan konfigurasi API key di halaman **Konfigurasi** untuk menggunakan aplikasi ini.
    """)
    
    # Gunakan tombol dengan URL navigasi alih-alih experimental_rerun
    if st.button("⚙️ Pergi ke Halaman Konfigurasi"):
        # Arahkan ke halaman konfigurasi
        if os.path.exists("pages/01_Konfigurasi.py"):
            try:
                # Metode yang lebih aman untuk navigasi
                st.switch_page("pages/01_Konfigurasi.py")
            except Exception as e:
                logging.error(f"Error navigating to config page: {str(e)}")
                st.error(f"Gagal membuka halaman konfigurasi: {str(e)}")
                st.info("Silakan klik pada menu 'Konfigurasi' di sidebar")
else:
    # Buat tab untuk fitur-fitur utama
    tab1, tab2 = st.tabs(["💬 Chat", "📂 Upload File"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_file_upload()
