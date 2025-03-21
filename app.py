import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Business Consultant Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main content
st.title("💼 AI Business Consultant Pro")
st.markdown("""
Konsultan bisnis AI yang dapat membantu Anda dengan strategi bisnis, 
analisis data, pemasaran, keuangan, dan rekomendasi berdasarkan dokumen yang Anda unggah.
""")

st.write("Aplikasi sedang dalam pengembangan. Fitur akan segera tersedia.")

# Inisialisasi sidebar sederhana
with st.sidebar:
    st.image("https://www.provincial.com/content/dam/public-web/global/images/micro-illustrations/bbva_manager_man_2.im1705594061549im.png?imwidth=320", width=100)
    st.title("💼 AI Business Consultant")
    
    # API Key input
    api_key = st.text_input("🔑 API Key:", type="password")
    
    # Model Selection
    model_options = {
        "gpt-4": "GPT-4 (Powerful)",
        "gpt-3.5-turbo": "GPT-3.5 (Fast)"
    }
    selected_model = st.selectbox(
        "🤖 Pilih Model:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x]
    )
