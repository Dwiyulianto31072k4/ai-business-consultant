# Fungsi-fungsi untuk text-to-speech
import streamlit as st
import base64
import logging
import requests
import os
import tempfile
from pathlib import Path

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
        
        # Cek apakah API key tersedia
        api_key = st.session_state.get("api_key")
        if not api_key:
            return None, "API key tidak tersedia. Pastikan API key OpenAI telah dikonfigurasi."
        
        try:
            # Coba menggunakan OpenAI library versi baru
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Buat temporary file untuk menyimpan audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_path = temp_audio.name
            
            # Buat permintaan TTS
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Simpan ke file
            response.stream_to_file(temp_path)
            
            # Baca file dan konversi ke base64
            with open(temp_path, "rb") as audio_file:
                audio_data = audio_file.read()
                b64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            # Hapus file temporary
            os.remove(temp_path)
            
            return b64_audio, None
            
        except ImportError:
            # Fallback ke implementasi dengan requests jika OpenAI library tidak tersedia
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "tts-1",
                "voice": voice,
                "input": text
            }
            
            response = requests.post(
                "https://api.openai.com/v1/audio/speech",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                audio_data = response.content
                b64_audio = base64.b64encode(audio_data).decode('utf-8')
                return b64_audio, None
            else:
                error_message = f"Error TTS API: {response.status_code} - {response.text}"
                logging.error(error_message)
                return None, error_message
                
    except Exception as e:
        error_message = f"Error TTS: {str(e)}"
        logging.error(error_message)
        return None, error_message

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
                audio_b64, error = generate_speech(response, selected_voice)
                
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
                    st.error(f"Gagal menghasilkan audio: {error or 'Terjadi kesalahan'}")
                    st.info("Tips: Pastikan API key OpenAI Anda valid dan memiliki akses ke layanan TTS")
