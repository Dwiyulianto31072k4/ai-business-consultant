# UI sidebar
import streamlit as st
from utils.llm_providers import AIProviderFactory, init_memory
import uuid

def load_api_key(provider="openai"):
    """Load API key dari secrets atau input user"""
    key_name = f"{provider.upper()}_API_KEY"
    
    # Prioritaskan dari secrets
    if key_name in st.secrets:
        return st.secrets[key_name]
    
    # Jika tidak ada di secrets, minta dari user
    api_key = st.sidebar.text_input(f"🔑 {provider.capitalize()} API Key:", type="password", key=f"input_{key_name}")
    if not api_key:
        st.sidebar.warning(f"⚠️ Silakan masukkan API Key {provider.capitalize()} untuk memulai.")
    return api_key

def render_sidebar():
    """Render sidebar UI"""
    with st.sidebar:
        st.image("https://www.provincial.com/content/dam/public-web/global/images/micro-illustrations/bbva_manager_man_2.im1705594061549im.png?imwidth=320", width=100)
        st.title("💼 AI Business Consultant")
        
        # Provider selection
        provider_options = {
            "openai": "OpenAI (GPT)",
            "anthropic": "Anthropic (Claude)",
            "groq": "Groq (Fast)",
            "huggingface": "HuggingFace (Open Source)"
        }
        
        selected_provider = st.selectbox(
            "🤖 Pilih Provider:",
            options=list(provider_options.keys()),
            format_func=lambda x: provider_options[x],
            index=list(provider_options.keys()).index(st.session_state.get("current_provider", "openai"))
        )
        
        # Update provider in session state
        st.session_state.current_provider = selected_provider
        
        # Load API Key for selected provider
        st.session_state.api_key = load_api_key(selected_provider)
        
        # Model selection based on provider
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
            "🧠 Pilih Model:",
            options=list(available_models.keys()),
            format_func=lambda x: available_models[x],
            index=list(available_models.keys()).index(current_model) if current_model in available_models else 0
        )
        
        # Update model in session state
        st.session_state.current_model = selected_model
        
        # Advanced settings
        with st.expander("⚙️ Pengaturan Lanjutan"):
            temperature = st.slider("Temperature:", 0.0, 1.0, 0.7, 0.1, 
                                help="Nilai rendah: lebih fokus dan deterministik. Nilai tinggi: lebih kreatif dan bervariasi.")
            
            max_tokens = st.slider("Max Tokens Response:", 256, 4096, 1024, 128,
                                help="Batas maksimum token untuk respons AI.")
            
            chunk_size = st.slider("Chunk Size:", 100, 1000, 500, 50,
                                help="Ukuran potongan teks untuk pemrosesan dokumen.")
            
            chunk_overlap = st.slider("Chunk Overlap:", 0, 200, 50, 10,
                                help="Jumlah overlap antar potongan teks untuk mempertahankan konteks.")
        
        # Initialize LLM if API key is available
        if st.session_state.api_key and (st.session_state.llm is None or 
                                        selected_model != st.session_state.current_model or
                                        selected_provider != st.session_state.current_provider):
            with st.spinner("Initializing AI model..."):
                st.session_state.llm = AIProviderFactory.get_provider(
                    selected_provider,
                    st.session_state.api_key,
                    selected_model,
                    temperature,
                    max_tokens
                )
                
                # Reinitialize memory with new LLM
                if st.session_state.llm:
                    st.session_state.memory = init_memory(st.session_state.llm)
                    # Generate a session ID if not exists
                    if not st.session_state.session_id:
                        st.session_state.session_id = str(uuid.uuid4())
                    st.success(f"✅ Model {selected_model} siap digunakan!")
                else:
                    st.error("❌ Gagal menginisialisasi model AI. Periksa API key Anda.")
        
        # Token Usage Stats
        if "token_usage" in st.session_state and st.session_state.token_usage["total_tokens"] > 0:
            st.write("📊 **Token Usage**")
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
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Chat", key="reset"):
                st.session_state.history = []
                if st.session_state.llm:
                    st.session_state.memory = init_memory(st.session_state.llm)
                st.success("💡 Chat telah direset!")
        
        with col2:
            if st.button("🗑️ Clear Files", key="clear"):
                st.session_state.retriever = None
                st.session_state.file_processed = False
                st.session_state.file_info = {}
                from utils.file_processing import cleanup_temp_files
                cleanup_temp_files()
                st.success("🗑️ File telah dihapus!")
