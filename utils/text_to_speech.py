# Fungsi-fungsi untuk text-to-speech
import streamlit as st
import base64
import logging

def generate_speech(text, voice="alloy"):
    """
    Menggunakan OpenAI TTS untuk mengubah teks menjadi audio
    
    Args:
        text: Teks yang akan dikonversi ke audio
        voice: Jenis suara (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Base64 encoded audio string untuk HTML audio tag
    """
    try:
        # Batasi teks untuk TTS (untuk penghematan biaya)
        if len(text) > 4000:
            text = text[:4000] + "... (teks terpotong untuk audio)"
        
        # Inisialisasi client OpenAI
        from openai import OpenAI
        client = OpenAI(api_key=st.session_state.api_key)
        
        # Buat permintaan TTS
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Konversi ke base64 untuk ditampilkan di browser
        audio_data = response.content
        b64_audio = base64.b64encode(audio_data).decode('utf-8')
        
        return b64_audio
    except Exception as e:
        logging.error(f"Error TTS: {str(e)}")
        return None

def display_audio_player(audio_b64):
    """Menampilkan HTML audio player dengan data audio base64"""
    audio_html = f"""
    <audio controls autoplay=false style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        Browser Anda tidak mendukung tag audio.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# UI untuk text-to-speech
def add_tts_option_to_response(response):
    """Menambahkan opsi TTS ke respons AI"""
    with st.expander("🔊 Dengarkan respons ini"):
        voices = {
            "alloy": "Alloy (Netral)",
            "echo": "Echo (Dewasa Tua)",
            "fable": "Fable (Cerita)",
            "onyx": "Onyx (Formal)",
            "nova": "Nova (Wanita)",
            "shimmer": "Shimmer (Ramah)"
        }
        
        selected_voice = st.selectbox("Pilih suara:", list(voices.keys()), format_func=lambda x: voices[x])
        
        if st.button("🔊 Generate Audio"):
            with st.spinner("Menghasilkan audio..."):
                audio_b64 = generate_speech(response, selected_voice)
                
                if audio_b64:
                    display_audio_player(audio_b64)
                    
                    # Opsi download
                    st.download_button(
                        label="📥 Download Audio",
                        data=base64.b64decode(audio_b64),
                        file_name=f"ai_response_{selected_voice}.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("Gagal menghasilkan audio. Coba lagi nanti.")
