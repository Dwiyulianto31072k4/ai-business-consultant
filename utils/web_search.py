# Fungsi-fungsi untuk pencarian web
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import logging

def search_internet_real(query, num_results=5):
    """
    Simulasi pencarian internet
    """
    st.info("🔍 Mencari di internet...")
    
    # Gunakan simulasi hasil pencarian
    return {
        "query": query,
        "results": [
            {
                "title": f"Hasil pencarian untuk '{query}' - #{i+1}",
                "link": f"https://example.com/search/{i+1}",
                "snippet": f"Ini adalah contoh hasil pencarian untuk {query}. "
                          f"Dalam implementasi sebenarnya, hasil ini akan diganti dengan "
                          f"hasil pencarian yang sesungguhnya dari internet."
            }
            for i in range(num_results)
        ]
    }

def search_and_summarize(query):
    """
    Mencari informasi dan merangkum hasil pencarian
    """
    search_results = search_internet_real(query)
    
    if not search_results["results"]:
        return f"Tidak ditemukan hasil untuk pencarian '{query}'."
    
    # Buat prompt untuk merangkum hasil pencarian
    results_text = "\n\n".join([
        f"Judul: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}"
        for result in search_results["results"]
    ])
    
    prompt = f"""
    Berikut adalah hasil pencarian web untuk "{query}":
    
    {results_text}
    
    Berdasarkan hasil pencarian di atas, berikan ringkasan yang komprehensif dan terstruktur.
    Fokus pada informasi yang paling relevan dengan bisnis dan perusahaan.
    Format respons dengan poin-poin dan struktur yang jelas.
    Sertakan informasi sumber (nama situs) saat menampilkan fakta penting.
    """
    
    try:
        if not st.session_state.get("llm"):
            return f"⚠️ Model AI belum diinisialisasi. Silakan masukkan API Key terlebih dahulu.", []
            
        from langchain.callbacks import get_openai_callback
        
        with get_openai_callback() as cb:
            result = st.session_state.llm.invoke(prompt)
            
            # Update token usage
            if "token_usage" not in st.session_state:
                st.session_state.token_usage = {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
                
            st.session_state.token_usage["prompt_tokens"] += cb.prompt_tokens
            st.session_state.token_usage["completion_tokens"] += cb.completion_tokens
            st.session_state.token_usage["total_tokens"] += cb.total_tokens
        
        # Tambahkan footer dengan sumber
        footer = "\n\n**Sumber Informasi:**\n" + "\n".join([
            f"- [{result['title']}]({result['link']})" 
            for result in search_results["results"]
        ])
        
        if hasattr(result, 'content'):
            return result.content + footer
        else:
            return str(result) + footer
            
    except Exception as e:
        logging.error(f"Error saat merangkum pencarian: {str(e)}")
        return f"⚠️ Terjadi kesalahan saat merangkum hasil pencarian: {str(e)}"
