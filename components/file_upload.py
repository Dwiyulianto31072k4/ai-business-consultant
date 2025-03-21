import streamlit as st
import logging
import os
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from utils.file_processing import process_file, get_secure_temp_file

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

def init_chain(retriever):
    """Inisialisasi ConversationalRetrievalChain"""
    if not st.session_state.llm or not st.session_state.memory:
        return None
        
    template = """
    Kamu adalah AI Business Consultant yang profesional, cerdas, dan membantu.
    
    Nama kamu adalah "Business AI Pro" dan kamu memiliki pengalaman luas di bidang konsultasi bisnis.
    
    Konten berikut adalah informasi yang relevan yang ditemukan dari dokumen yang diunggah:
    {context}
    
    Riwayat Percakapan:
    {chat_history}
    
    Pertanyaan Pengguna: {question}
    
    Berikan jawaban yang komprehensif, akurat, dan bermanfaat berdasarkan informasi yang diberikan.
    Jika jawaban tidak ditemukan dalam informasi yang tersedia, katakan dengan jujur bahwa
    kamu tidak dapat menjawab berdasarkan dokumen yang diunggah.
    
    Berikan format yang rapi dengan poin-poin dan penekanan pada bagian penting.
    """

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=template
    )

    try:
        chain = ConversationalRetrievalChain.from_llm(
            llm=st.session_state.llm,
            retriever=retriever,
            memory=st.session_state.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=True
        )

        return chain

    except Exception as e:
        logging.error(f"Error inisialisasi chain: {str(e)}")
        st.error(f"❌ Gagal menginisialisasi chain: {str(e)}")
        return None

def render_file_upload():
    """Render file upload UI"""
    st.subheader("📂 Unggah Dokumen")
    
    uploaded_file = st.file_uploader(
        "📎 Unggah file (PDF, TXT, CSV) untuk analisis AI", 
        type=["pdf", "txt", "csv"],
        accept_multiple_files=False,
        help="Unggah dokumen untuk dianalisis oleh AI. Dokumen akan dipecah dan diubah menjadi basis pengetahuan."
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        process_button = st.button("✅ Proses File", type="primary", disabled=not uploaded_file)
    
    with col2:
        if uploaded_file:
            st.write(f"File dipilih: **{uploaded_file.name}**")
    
    if process_button and uploaded_file:
        # Proses file
        with st.spinner("🔍 Menganalisis dokumen... Mohon tunggu"):
            st.session_state.retriever = process_file(
                uploaded_file,
                chunk_size=st.session_state.get("chunk_size", 500),
                chunk_overlap=st.session_state.get("chunk_overlap", 50)
            )
            
            if st.session_state.retriever:
                st.session_state.file_processed = True
                # Initialize conversation chain
                st.session_state.conversation = init_chain(st.session_state.retriever)
                st.success("✅ Dokumen berhasil diproses dan siap digunakan untuk konsultasi!")
    
    # Tampilkan informasi file jika sudah diproses
    if st.session_state.get("file_processed", False) and st.session_state.get("file_info"):
        st.subheader("📊 Informasi Dokumen")
        info = st.session_state.file_info
        
        # Metric cards dalam 3 kolom
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Nama File", info["filename"])
            st.metric("📏 Ukuran", f"{info['size_mb']} MB")
        
        with col2:
            st.metric("📚 Jumlah Halaman/Baris", info["doc_count"])
            st.metric("🧩 Jumlah Chunks", info["chunk_count"])
            
        with col3:
            st.metric("⏱️ Waktu Proses", f"{info['processing_time']} detik")
            estimated_queries = info["chunk_count"] * 2
            st.metric("🔍 Estimasi Kapasitas Query", f"~{estimated_queries} pertanyaan")
            
        st.info("💡 Dokumen Anda telah dikonversi menjadi basis pengetahuan AI. Anda sekarang dapat mengajukan pertanyaan tentang isinya di tab Chat.")

        # Visualisasi jika file adalah CSV
        if info["filename"].lower().endswith('.csv'):
            import pandas as pd
            from utils.visualization import create_visualization
            
            st.subheader("📈 Visualisasi Data")
            
            try:
                # Load CSV file
                df = pd.read_csv(get_secure_temp_file(uploaded_file))
                
                # Display data sample
                st.write("Preview Data:")
                st.dataframe(df.head())
                
                # Create visualizations
                create_visualization(df)
            except Exception as e:
                st.error(f"Gagal memvisualisasikan data: {str(e)}")
