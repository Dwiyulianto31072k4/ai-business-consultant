import os
import tempfile
import hashlib
import logging
import streamlit as st

def sanitize_filename(filename: str) -> str:
    return hashlib.md5(filename.encode()).hexdigest()

def get_secure_temp_file(uploaded_file):
    temp_dir = tempfile.gettempdir()
    secure_filename = sanitize_filename(uploaded_file.name)
    extension = os.path.splitext(uploaded_file.name)[1]
    temp_file_path = os.path.join(temp_dir, f"{secure_filename}{extension}")
    
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if "temp_files" not in st.session_state:
        st.session_state.temp_files = []
    st.session_state.temp_files.append(temp_file_path)
    
    return temp_file_path

def cleanup_temp_files():
    if "temp_files" in st.session_state:
        for file_path in st.session_state.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"File berhasil dihapus: {file_path}")
            except Exception as e:
                logging.error(f"Gagal menghapus file: {file_path} - {str(e)}")
        st.session_state.temp_files = []

def process_file(uploaded_file, chunk_size=500, chunk_overlap=50):
    try:
        return None
    except Exception as e:
        logging.error(f"Error memproses file: {str(e)}")
        st.error(f"❌ Gagal memproses file: {str(e)}")
        return None
