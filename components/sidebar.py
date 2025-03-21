# UI sidebar
import streamlit as st
from utils.llm_providers import AIProviderFactory, init_memory
import uuid

def render_sidebar():
    """Render sidebar UI"""
    with st.sidebar:
        st.image("https://www.provincial.com/content/dam/public-web/global/images/micro-illustrations/bbva_manager_man_2.im1705594061549im.png?imwidth=320", width=100)
        st.title("💼 AI Business Consultant")
        
        # Navigasi
        st.subheader("📑 Navigasi")
        
        # Opsi navigasi
        nav_options = {
            "home": "🏠 Beranda",
            "config": "⚙️ Konfigurasi",
            "chat": "💬 Chat",
            "upload": "📂 Upload File"
        }
        
        # Tampilkan opsi navigasi sebagai tombol
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏠 Beranda", use_container_width=True):
                # Kembali ke halaman utama
                if "nav" in st.session_state:
                    del st.session_state.nav
        
        with col2:
            if st.button("⚙️ Konfigurasi", use_container_width=True):
                # Navigasi ke halaman konfigurasi
                st.session_state.nav = "config"
                st.switch_page("pages/01_Konfigurasi.py")
        
        # Informasi model
        st.subheader("🤖 Model AI Aktif")
        
        # Provider dan model
        provider_display = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "groq": "Groq",
            "huggingface": "HuggingFace"
        }
        
        provider = st.session_state.get("current_provider", "openai")
        model = st.session_state.get("current_model", "gpt-3.5-turbo")
        
        # Tampilkan info model
        st.info(f"**Provider:** {provider_display.get(provider, provider)}\n\n**Model:** {model}")
        
        # API Key status
        api_key = st.session_state.get("api_key")
        if api_key:
            st.success("✅ API Key terkonfigurasi")
        else:
            st.error("❌ API Key belum dikonfigurasi")
            
            # Tampilkan tombol ke halaman konfigurasi
            if st.button("⚙️ Konfigurasi API Key"):
                st.switch_page("pages/01_Konfigurasi.py")
        
        # Initialize LLM if API key is available and not already initialized
        if st.session_state.api_key and (st.session_state.llm is None or 
                                        model != st.session_state.current_model or
                                        provider != st.session_state.current_provider):
            with st.spinner("Initializing AI model..."):
                try:
                    st.session_state.llm = AIProviderFactory.get_provider(
                        provider,
                        st.session_state.api_key,
                        model,
                        st.session_state.get("temperature", 0.7),
                        st.session_state.get("max_tokens", 1024)
                    )
                    
                    # Reinitialize memory with new LLM
                    if st.session_state.llm:
                        st.session_state.memory = init_memory(st.session_state.llm)
                        # Generate a session ID if not exists
                        if not st.session_state.session_id:
                            st.session_state.session_id = str(uuid.uuid4())
                        st.success(f"✅ Model {model} siap digunakan!")
                    else:
                        st.error("❌ Gagal menginisialisasi model AI. Periksa API key Anda.")
                except Exception as e:
                    st.error(f"❌ Error saat menginisialisasi model: {str(e)}")
                    # Clear the existing LLM if there was an error
                    st.session_state.llm = None
                    st.session_state.memory = None
        
        # Token Usage Stats
        if "token_usage" in st.session_state and st.session_state.token_usage["total_tokens"] > 0:
            st.subheader("📊 Token Usage")
            col1, col2 = st.columns(2)
            col1.metric("Total", f"{st.session_state.token_usage['total_tokens']:,}")
            col2.metric("Prompt", f"{st.session_state.token_usage['prompt_tokens']:,}")
            st.metric("Completion", f"{st.session_state.token_usage['completion_tokens']:,}")
            
            # Estimasi biaya (contoh harga, perlu disesuaikan)
            if "gpt-4" in st.session_state.current_model:
                prompt_cost = st.session_state.token_usage['prompt_tokens'] * 0.00003
                completion_cost = st.session_state.token_usage['completion_tokens'] * 0.00006
            else:  # gpt-3.5-turbo
                prompt_cost = st.session_state.token_usage['prompt_tokens'] * 0.0000015
                completion_cost = st.session_state.token_usage['completion_tokens'] * 0.000002
                
            total_cost = prompt_cost + completion_cost
            st.write(f"💰 **Estimasi Biaya:** ${total_cost:.4f}")
        
        # Control Buttons
        st.subheader("🔄 Kontrol")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Chat", key="reset", use_container_width=True):
                st.session_state.history = []
                if st.session_state.llm:
                    st.session_state.memory = init_memory(st.session_state.llm)
                st.success("💡 Chat telah direset!")
        
        with col2:
            if st.button("🗑️ Clear Files", key="clear", use_container_width=True):
                st.session_state.retriever = None
                st.session_state.file_processed = False
                st.session_state.file_info = {}
                from utils.file_processing import cleanup_temp_files
                cleanup_temp_files()
                st.success("🗑️ File telah dihapus!")
