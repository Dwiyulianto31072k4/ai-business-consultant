import streamlit as st
from components.file_upload import render_file_upload
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant - Document Analysis",
    page_icon="📄",
    layout="wide"
)

# Header
st.title("📄 Document Analysis")
st.markdown("""
Unggah dokumen bisnis Anda (PDF, CSV, TXT) untuk dianalisis oleh AI Business Consultant Pro.
AI akan memproses dokumen Anda dan memungkinkan Anda untuk bertanya tentang isinya.
""")

# Render file upload interface
try:
    render_file_upload()
except Exception as e:
    logger.error(f"Error rendering file upload interface: {str(e)}")
    st.error(f"⚠️ Terjadi kesalahan saat menampilkan antarmuka upload dokumen: {str(e)}")
    
    # Informasi debugging untuk admin
    with st.expander("Debug Info", expanded=False):
        st.write("Session State Variables:")
        for key, value in st.session_state.items():
            if key == "api_key" or "_api_key" in key:
                st.write(f"- {key}: {'[SET]' if value else '[NOT SET]'}")
            else:
                st.write(f"- {key}: {type(value)}")
