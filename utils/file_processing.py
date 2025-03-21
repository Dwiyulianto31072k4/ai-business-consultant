import streamlit as st
# Komentar impor yang bermasalah untuk sementara
# from utils.file_processing import process_file
# from components.sidebar import render_sidebar
# from components.chat_interface import render_chat_interface
# from components.file_upload import render_file_upload

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("💼 AI Business Consultant Pro")
st.markdown("""
Konsultan bisnis AI yang dapat membantu Anda dengan strategi bisnis, 
analisis data, pemasaran, keuangan, dan rekomendasi berdasarkan dokumen yang Anda unggah.
""")

st.write("Aplikasi sedang dalam pengembangan. Fitur akan segera tersedia.")
