# UI chat interface
import streamlit as st
import re
import logging
from datetime import datetime
from langchain.callbacks import get_openai_callback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def build_prompt_with_history(query: str, history: list = None, max_history: int = 5):
    """
    Membuat prompt dengan konteks riwayat percakapan sebelumnya
    """
    # Siapkan konteks riwayat chat
    chat_history_text = ""
    if history and len(history) > 0:
        # Ambil beberapa pesan terakhir (tapi tidak terlalu banyak)
        recent_history = history[-min(max_history*2, len(history)):]
        
        for i, (role, message) in enumerate(recent_history):
            role_display = "User" if role == "user" else "AI"
            chat_history_text += f"{role_display}: {message}\n\n"
    
    # Buat prompt dengan konteks
    prompt = f"""
    Kamu adalah AI Business Consultant Pro yang profesional dan membantu.
    
    Nama kamu adalah "Business AI Pro" dan kamu memiliki pengalaman luas di bidang strategi bisnis,
    pemasaran, keuangan, manajemen, dan pengembangan produk.
    
    {"Berikut adalah konteks percakapan sebelumnya:\n\n" + chat_history_text if chat_history_text else ""}
    
    Pertanyaan pengguna saat ini: {query}
    
    Berikan jawaban yang komprehensif, terstruktur, dan bermanfaat.
    Pastikan kamu mengacu pada konteks percakapan sebelumnya ketika relevan.
    Format respons menggunakan Markdown untuk meningkatkan keterbacaan.
    """
    
    return prompt

def process_query(query: str):
    """Memproses kueri dan menangani output."""
    try:
        # Deteksi jika ada permintaan pencarian web
        if any(keyword in query.lower() for keyword in ["cari di internet", "search online", "cari online"]):
            try:
                from utils.web_search import search_and_summarize
                return search_and_summarize(query), []
            except Exception as e:
                logger.error(f"Error pada pencarian web: {str(e)}")
                return f"⚠️ Gagal melakukan pencarian web: {str(e)}", []
        
        # Jika ada file yang diproses, gunakan ConversationalRetrievalChain
        if st.session_state.get("file_processed", False) and st.session_state.get("conversation"):
            try:
                with get_openai_callback() as cb:
                    # Log untuk debugging
                    logger.info("Menggunakan ConversationalRetrievalChain dengan RAG")
                    
                    # Kirim pertanyaan dengan konteks
                    result = st.session_state.conversation({
                        "question": query, 
                        "chat_history": [(h[0], h[1]) for h in st.session_state.get("history", [])][-10:] if st.session_state.get("history") else []
                    })
                    
                    # Update token usage
                    if "token_usage" not in st.session_state:
                        st.session_state.token_usage = {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
                        
                    st.session_state.token_usage["prompt_tokens"] += cb.prompt_tokens
                    st.session_state.token_usage["completion_tokens"] += cb.completion_tokens
                    st.session_state.token_usage["total_tokens"] += cb.total_tokens
                    
                    response = result["answer"]
                    source_docs = result.get("source_documents", [])
                    
                    # Format respons dengan Markdown untuk meningkatkan keterbacaan
                    response = format_response(response)
                    
                    # Tambahkan informasi sumber
                    if source_docs:
                        sources = set()
                        for doc in source_docs:
                            if hasattr(doc, "metadata") and "source" in doc.metadata:
                                sources.add(doc.metadata["source"])
                        
                        if sources:
                            response += "\n\n**Sumber:**\n"
                            for source in sources:
                                response += f"- {source}\n"
                    
                    return response, source_docs
            except Exception as e:
                logger.error(f"Error saat menggunakan RAG: {str(e)}")
                return f"⚠️ Terjadi kesalahan saat menggunakan database dokumen: {str(e)}", []
                
        # Jika tidak ada file (mode chat biasa), gunakan LLM dengan konteks riwayat
        else:
            if not st.session_state.get("llm"):
                return "⚠️ Model AI belum diinisialisasi. Silakan masukkan API Key dan pilih model terlebih dahulu.", []
                
            with get_openai_callback() as cb:
                # Dapatkan riwayat chat
                history = st.session_state.get("history", [])
                
                # Buat prompt dengan konteks
                prompt = build_prompt_with_history(query, history)
                
                # Log untuk debugging
                logger.info(f"Menggunakan LLM langsung dengan {len(history)} riwayat chat")
                
                # Jalankan LLM
                result = st.session_state.llm.invoke(prompt)
                
                # Update token usage
                if "token_usage" not in st.session_state:
                    st.session_state.token_usage = {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
                    
                st.session_state.token_usage["prompt_tokens"] += cb.prompt_tokens
                st.session_state.token_usage["completion_tokens"] += cb.completion_tokens
                st.session_state.token_usage["total_tokens"] += cb.total_tokens
                
                # Format respons
                if hasattr(result, 'content'):
                    response = format_response(result.content)
                else:
                    response = format_response(str(result))
                
                return response, []
                
    except Exception as e:
        logger.error(f"Error saat memproses pertanyaan: {str(e)}")
        return f"⚠️ Terjadi kesalahan: {str(e)}", []

def render_chat_interface():
    """Render chat interface UI"""
    st.subheader("💬 Chat dengan AI Business Consultant")
    
    # Tampilkan status koneksi file
    if st.session_state.get("file_processed", False):
        st.success(f"📄 Dokumen terhubung: **{st.session_state.file_info['filename']}**")
        st.markdown("AI akan menjawab berdasarkan dokumen yang diunggah dan pengetahuan umumnya.")
    else:
        st.info("💡 AI akan menjawab berdasarkan pengetahuan umumnya. Unggah dokumen di tab 'Upload File' untuk mendapatkan jawaban yang spesifik.")
    
    # Chat container
    chat_container = st.container()
    
    # Tampilkan chat history
    with chat_container:
        if "history" in st.session_state:
            for i, (role, message) in enumerate(st.session_state.history):
                with st.chat_message(role):
                    st.markdown(message)
    
    # Disable chat input jika API key tidak tersedia
    if not st.session_state.get("api_key"):
        st.warning("⚠️ Silakan masukkan API Key di halaman Konfigurasi untuk memulai chat.")
        chat_input_disabled = True
    else:
        chat_input_disabled = False
        
        # Chat input
        user_input = st.chat_input("✏️ Ketik pesan atau pertanyaan Anda...", disabled=chat_input_disabled)
        
        if user_input:
            # Tampilkan pesan user
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Tambahkan ke history
            if "history" not in st.session_state:
                st.session_state.history = []
                
            st.session_state.history.append(("user", user_input))
            
            # Proses pertanyaan
            with st.spinner("🧠 AI sedang menganalisis..."):
                response, source_docs = process_query(user_input)
                
                # Tambahkan respons ke history
                st.session_state.history.append(("assistant", response))
                
                # Tampilkan respons
                with st.chat_message("assistant"):
                    st.markdown(response)
                    
                    # Add Text-to-Speech option
                    if "tts" not in st.session_state:
                        st.session_state.tts = False
                        
                    enable_tts = st.toggle("🔊 Text-to-Speech", value=st.session_state.tts)
                    
                    if enable_tts:
                        st.session_state.tts = True
                        try:
                            from utils.text_to_speech import generate_speech, display_audio_player
                            
                            # Sederhanakan teks untuk TTS (hapus markdown, batas karakter)
                            clean_text = re.sub(r'[*#\[\]()]', '', response)
                            if len(clean_text) > 4000:
                                clean_text = clean_text[:4000] + "... (teks terpotong untuk audio)"
                                
                            with st.spinner("🔊 Generating audio..."):
                                audio_b64, error = generate_speech(clean_text)
                                if audio_b64:
                                    display_audio_player(audio_b64)
                                else:
                                    st.error(f"Gagal menghasilkan audio: {error or 'Terjadi kesalahan'}")
                                    st.info("Pastikan API key OpenAI Anda valid dan memiliki akses ke layanan TTS")
                        except Exception as e:
                            st.error(f"Gagal menghasilkan audio: {str(e)}")
