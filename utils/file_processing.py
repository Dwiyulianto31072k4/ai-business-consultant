import streamlit as st
import os
import tempfile
import time
import logging
from pathlib import Path
import shutil

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Variabel global
TEMP_DIR = Path(tempfile.gettempdir()) / "ai_business_consultant"

def get_secure_temp_file(uploaded_file):
    """
    Menyimpan file yang diunggah ke direktori sementara dengan aman
    
    Args:
        uploaded_file: File yang diunggah melalui st.file_uploader
        
    Returns:
        Path ke file sementara
    """
    try:
        # Pastikan direktori ada
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Buat path file dengan nama unik
        file_path = TEMP_DIR / uploaded_file.name
        
        # Tulis file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return str(file_path)
    except Exception as e:
        logging.error(f"Error menyimpan file sementara: {str(e)}")
        raise e

def process_file(uploaded_file, chunk_size=500, chunk_overlap=50):
    """
    Memproses file yang diunggah dan mengembalikan retriever
    
    Args:
        uploaded_file: File yang diunggah (PDF, TXT, CSV)
        chunk_size: Ukuran tiap potongan teks
        chunk_overlap: Jumlah overlap antar potongan
        
    Returns:
        Retriever yang dapat digunakan untuk RAG
    """
    try:
        start_time = time.time()
        file_path = get_secure_temp_file(uploaded_file)
        file_extension = Path(file_path).suffix.lower()
        
        # Import modul-modul yang diperlukan
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings
        
        # Inisialisasi data dan metainformation
        docs = []
        metadata = {
            "filename": uploaded_file.name,
            "size_mb": round(uploaded_file.size / (1024 * 1024), 2),
            "doc_count": 0,
            "chunk_count": 0,
            "processing_time": 0
        }
        
        # Proses berdasarkan tipe file
        if file_extension == ".pdf":
            from langchain.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            metadata["doc_count"] = len(docs)
            
        elif file_extension == ".txt":
            from langchain.document_loaders import TextLoader
            loader = TextLoader(file_path)
            docs = loader.load()
            metadata["doc_count"] = len(docs)
            
        elif file_extension == ".csv":
            from langchain.document_loaders.csv_loader import CSVLoader
            loader = CSVLoader(file_path)
            docs = loader.load()
            metadata["doc_count"] = len(docs)
            
        else:
            raise ValueError(f"Format file tidak didukung: {file_extension}")
        
        # Split dokumen menjadi chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = text_splitter.split_documents(docs)
        metadata["chunk_count"] = len(chunks)
        
        # Buat vectorstore dengan embeding OpenAI
        embeddings = OpenAIEmbeddings(api_key=st.session_state.api_key)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # Selesaikan metadata
        metadata["processing_time"] = round(time.time() - start_time, 2)
        st.session_state.file_info = metadata
        
        # Kembalikan retriever
        return vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
            
    except Exception as e:
        logging.error(f"Error memproses file: {str(e)}")
        st.error(f"❌ Gagal memproses file: {str(e)}")
        return None

def cleanup_temp_files():
    """Membersihkan file sementara"""
    try:
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
            logging.info("File sementara berhasil dibersihkan")
    except Exception as e:
        logging.error(f"Error saat membersihkan file: {str(e)}")
