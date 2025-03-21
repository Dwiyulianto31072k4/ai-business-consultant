import streamlit as st
import json
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant - Konfigurasi",
    page_icon="⚙️",
    layout="wide"
)

# Inisialisasi session state jika belum ada
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {
        "openai": None,
        "anthropic": None,
        "groq": None,
        "huggingface": None
    }

# Judul halaman
st.title("⚙️ Konfigurasi API Key")
st.markdown("""
Gunakan halaman ini untuk mengatur API keys yang digunakan oleh AI Business Consultant Pro.
API keys disimpan hanya dalam session browser Anda untuk keamanan.
""")

# Header API Keys
st.header("🔑 Konfigurasi API Keys")

provider_info = {
    "openai": {
        "name": "OpenAI",
        "url": "https://platform.openai.com/account/api-keys",
        "models": ["GPT-3.5 Turbo", "GPT-4"],
        "info": "Diperlukan untuk menggunakan model GPT dan fitur embeddings."
    },
    "anthropic": {
        "name": "Anthropic",
        "url": "https://console.anthropic.com/account/keys",
        "models": ["Claude 3 Opus", "Claude 3 Sonnet", "Claude 3 Haiku"],
        "info": "Diperlukan untuk menggunakan model Claude AI."
    },
    "groq": {
        "name": "Groq",
        "url": "https://console.groq.com/keys",
        "models": ["Llama 2 70B", "Mixtral 8x7B"],
        "info": "Provider AI dengan latensi rendah dan throughput tinggi."
    },
    "huggingface": {
        "name": "HuggingFace",
        "url": "https://huggingface.co/settings/tokens",
        "models": ["Mistral 7B", "Phi-2"],
        "info": "Diperlukan untuk menggunakan model open source."
    }
}

# Tampilkan input untuk setiap provider
for provider, info in provider_info.items():
    st.subheader(f"{info['name']} API Key")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Tampilkan input API key
        api_key = st.text_input(
            f"{info['name']} API Key",
            type="password",
            value=st.session_state.api_keys.get(provider) or "",
            key=f"input_{provider}_key",
            help=f"{info['info']} [Dapatkan API key]({info['url']})"
        )
        
        # Update session state jika ada perubahan
        if api_key:
            st.session_state.api_keys[provider] = api_key
            # Juga simpan dengan format <provider>_api_key untuk kompatibilitas
            st.session_state[f"{provider}_api_key"] = api_key
            
            # Jika ini adalah provider yang aktif, update juga api_key utama
            if provider == st.session_state.get("current_provider", "openai"):
                st.session_state.api_key = api_key
        
        # Display models supported
        st.caption(f"**Model yang didukung:** {', '.join(info['models'])}")
    
    with col2:
        # Tambahkan tombol test koneksi
        if st.button(f"Test Koneksi", key=f"test_{provider}"):
            if not api_key:
                st.error("⚠️ API key tidak boleh kosong")
            else:
                try:
                    with st.spinner(f"Testing koneksi ke {info['name']}..."):
                        if provider == "openai":
                            try:
                                import openai
                                client = openai.OpenAI(api_key=api_key)
                                response = client.models.list(limit=1)
                                st.success(f"✅ Koneksi berhasil! Model tersedia: {response.data[0].id}")
                            except ImportError:
                                st.warning("Module openai tidak tersedia. Pastikan Anda telah menginstal package openai.")
                        elif provider == "anthropic":
                            try:
                                from anthropic import Anthropic
                                client = Anthropic(api_key=api_key)
                                response = client.messages.create(
                                    model="claude-3-haiku-20240307",
                                    max_tokens=10,
                                    messages=[{"role": "user", "content": "Hello"}]
                                )
                                st.success("✅ Koneksi ke Anthropic berhasil!")
                            except ImportError:
                                st.warning("Module anthropic tidak tersedia. Install dengan: pip install anthropic")
                        elif provider == "groq":
                            try:
                                from groq import Groq
                                client = Groq(api_key=api_key)
                                response = client.chat.completions.create(
                                    model="llama2-70b-4096",
                                    messages=[{"role": "user", "content": "Hello"}],
                                    max_tokens=10
                                )
                                st.success("✅ Koneksi ke Groq berhasil!")
                            except ImportError:
                                st.warning("Module groq tidak tersedia. Install dengan: pip install groq")
                        elif provider == "huggingface":
                            try:
                                from huggingface_hub import HfApi
                                api = HfApi(token=api_key)
                                user_info = api.whoami()
                                st.success(f"✅ Koneksi ke HuggingFace berhasil! User: {user_info['name']}")
                            except ImportError:
                                st.warning("Module huggingface_hub tidak tersedia. Install dengan: pip install huggingface_hub")
                except Exception as e:
                    st.error(f"❌ Gagal terhubung ke {info['name']}: {str(e)}")
                    logging.error(f"API connection error for {provider}: {str(e)}")
    
    st.divider()

# Provider & Model selection
st.header("🧠 Pengaturan Model AI")

# Provider selection
provider_options = {
    "openai": "OpenAI (GPT)",
    "anthropic": "Anthropic (Claude)",
    "groq": "Groq (Fast)",
    "huggingface": "HuggingFace (Open Source)"
}

default_provider = st.session_state.get("current_provider", "openai")

selected_provider = st.selectbox(
    "🤖 Provider AI Default:",
    options=list(provider_options.keys()),
    format_func=lambda x: provider_options[x],
    index=list(provider_options.keys()).index(default_provider) if default_provider in provider_options else 0
)

# Update provider in session state
st.session_state.current_provider = selected_provider

# Juga update API key utama jika provider berubah
if selected_provider in st.session_state.api_keys and st.session_state.api_keys[selected_provider]:
    st.session_state.api_key = st.session_state.api_keys[selected_provider]

# Model options based on provider
model_options = {
    "openai": {
        "gpt-4": "GPT-4 (Powerful & Accurate)",
        "gpt-3.5-turbo": "GPT-3.5 Turbo (Fast & Efficient)",
        "gpt-3.5-turbo-16k": "GPT-3.5 Turbo 16K (Extended Context)"
    },
    "anthropic": {
        "claude-3-opus-20240229": "Claude 3 Opus (Most Powerful)",
        "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
        "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)"
    },
    "groq": {
        "llama2-70b-4096": "Llama 2 70B",
        "mixtral-8x7b-32768": "Mixtral 8x7B"
    },
    "huggingface": {
        "mistralai/Mistral-7B-Instruct-v0.2": "Mistral 7B",
        "microsoft/phi-2": "Phi-2 (Lightweight)"
    }
}

available_models = model_options.get(selected_provider, {"none": "No models available"})

# Dapatkan model default untuk provider yang dipilih
default_model = list(available_models.keys())[0] if available_models else None
current_model = st.session_state.get("current_model", default_model)

# Pastikan current_model ada dalam available_models
if current_model not in available_models:
    current_model = default_model
    
selected_model = st.selectbox(
    "🧠 Model Default:",
    options=list(available_models.keys()),
    format_func=lambda x: available_models[x],
    index=list(available_models.keys()).index(current_model) if current_model in available_models else 0
)

# Update model in session state
st.session_state.current_model = selected_model

# Informasi tambahan
st.info("""
**Catatan Keamanan**: API key disimpan hanya dalam session browser Anda dan tidak dikirim ke server
kecuali saat berkomunikasi dengan provider AI yang sesuai. Kami sangat menyarankan untuk tidak
berbagi API key Anda dengan orang lain.
""")
