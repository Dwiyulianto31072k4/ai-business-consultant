# UI chat interface
import streamlit as st
from langchain.callbacks import get_openai_callback
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def format_response(text: str) -> str:
    """Memformat respons untuk tampilan yang lebih baik"""
    # Pastikan heading memiliki spasi setelah tanda #
    text = re.sub(r'(#{1,6})([^ #])', r'\1 \2', text)
    
    # Tambahkan penekanan pada poin-poin penting jika belum ada
    if "**" not in text and "*" not in text:
        # Cari frasa-frasa penting untuk diberi penekanan
        important_phrases = ["penting", "kunci", "utama", "strategi", "rekomendasi", "solusi"]
        for phrase in important_phrases:
            pattern = re.compile(r'(\w*' + phrase + r'\w*)', re.IGNORECASE)
            text = pattern.sub(r'**\1**', text)
    
    return text

def process_query(query: str):
    """Memproses kueri dan menangani output."""
    try:
        # Perbarui timestamp aktivitas terakhir
        from datetime import datetime
        
        # Pastikan LLM sudah diinisialisasi
        if not st.session_state.get("llm"):
            return "⚠️ Model AI belum diinisialisasi. Silakan masukkan API Key dan pilih model terlebih dahulu.", []
        
        # Deteksi jika ada permintaan pencarian web
        if any(keyword in query.lower() for keyword in ["cari di internet", "search online", "cari online"]):
            try:
                from utils.web_search import search_and_summarize
                return search_and_summarize(query), []
            except Exception as e:
                logging.error(f"Error pada pencarian web: {str(e)}")
                return f"⚠️ Gagal melakukan pencarian web: {str(e)}", []
        
        # Jika ada file yang diproses, gunakan ConversationalRetrievalChain
        if st.session_state.get("file_processed", False) and st.session_state.get("conversation"):
            try:
                with get_openai_callback() as cb:
                    result = st.session_state.conversation({"question": query})
                    
                    # Update token usage
                    if "token_usage" not in st.session_state:
