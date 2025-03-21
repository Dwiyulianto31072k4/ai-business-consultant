import streamlit as st
from utils.file_processing import process_file
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.file_upload import render_file_upload

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom
with open('static/css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inisialisasi state
def initialize_app():
    """Inisialisasi aplikasi dan session state"""
    # Memastikan semua state tersedia
    state_vars = {
        "conversation": None,
        "retriever": None,
        "history": [],
        "file_processed": False,
        "file_info": {},
        "token_usage": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0},
        "llm": None,
        "memory": None,
        "current_model": "gpt-4",
        "current_provider": "openai",
        "chain": None,
        "temp_files": [],
        "api_key": None,
        "session_id": None,
    }
    
    for var, default in state_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default

# Main function
def main():
    initialize_app()
    
    # Render sidebar
    render_sidebar()
    
    # Judul utama
    st.title("💼 AI Business Consultant Pro")
    st.markdown("""
    Konsultan bisnis AI yang dapat membantu Anda dengan strategi bisnis, 
    analisis data, pemasaran, keuangan, dan rekomendasi berdasarkan dokumen yang Anda unggah.
    """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📂 Upload File", "ℹ️ Bantuan"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_file_upload()
    
    with tab3:
        st.subheader("📘 Panduan Penggunaan")
        st.markdown("""
        ### 🌟 Cara Menggunakan AI Business Consultant Pro

        #### 1️⃣ Persiapan
        - Masukkan API Key di sidebar (jika belum dikonfigurasi)
        - Pilih model AI yang ingin digunakan

        #### 2️⃣ Upload Dokumen (Opsional)
        - Unggah dokumen bisnis Anda (PDF, TXT, CSV)
        - Klik tombol "Proses File" untuk menganalisis dokumen
        - Dokumen akan dipecah dan dikonversi menjadi basis pengetahuan

        #### 3️⃣ Konsultasi dengan AI
        - Ajukan pertanyaan tentang bisnis Anda
        - AI akan menjawab berdasarkan pengetahuan umum atau dokumen yang diunggah
        - Untuk pencarian internet, tambahkan frasa "cari di internet" dalam pertanyaan Anda

        #### 📋 Contoh Pertanyaan untuk AI:
        - "Bagaimana strategi pemasaran yang efektif untuk startup teknologi?"
        - "Analisis SWOT untuk bisnis retail berdasarkan data yang saya unggah"
        - "Buat rencana bisnis untuk perusahaan jasa konsultasi"
        - "Cari di internet tentang tren e-commerce terbaru"
        """)
        
        st.info("💡 **Tip**: Untuk hasil terbaik, unggah dokumen yang berisi informasi spesifik tentang bisnis Anda.")

if __name__ == "__main__":
    main()
