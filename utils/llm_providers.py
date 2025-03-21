# Factory untuk berbagai provider AI
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
import logging

class AIProviderFactory:
    """Factory untuk membuat berbagai provider AI"""
    
    @staticmethod
    def get_provider(provider_name, api_key=None, model_name=None, temperature=0.7, max_tokens=1024):
        """
        Mendapatkan provider AI berdasarkan nama
        
        Args:
            provider_name: Nama provider (openai, anthropic, groq, huggingface)
            api_key: API key untuk provider tersebut
            model_name: Nama model yang akan digunakan
            temperature: Nilai temperature untuk generasi
            max_tokens: Token maksimum untuk output
            
        Returns:
            Provider AI yang sesuai
        """
        if provider_name == "openai":
            if not model_name:
                model_name = "gpt-3.5-turbo"
            return AIProviderFactory._get_openai_provider(api_key, model_name, temperature, max_tokens)
            
        elif provider_name == "anthropic":
            if not model_name:
                model_name = "claude-3-sonnet-20240229"
            return AIProviderFactory._get_anthropic_provider(api_key, model_name, temperature, max_tokens)
            
        elif provider_name == "groq":
            if not model_name:
                model_name = "llama3-8b-8192"  # Default model yang diperbarui
            return AIProviderFactory._get_groq_provider(api_key, model_name, temperature, max_tokens)
            
        elif provider_name == "huggingface":
            if not model_name:
                model_name = "mistralai/Mistral-7B-Instruct-v0.2"
            return AIProviderFactory._get_huggingface_provider(api_key, model_name, temperature)
        
        else:
            raise ValueError(f"Provider tidak didukung: {provider_name}")
    
    @staticmethod
    def _get_openai_provider(api_key, model_name, temperature, max_tokens):
        """Buat OpenAI provider"""        
        try:
            return ChatOpenAI(
                api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            st.error(f"Error saat membuat provider OpenAI: {str(e)}")
            return None
    
    @staticmethod
    def _get_anthropic_provider(api_key, model_name, temperature, max_tokens):
        """Buat Anthropic provider"""
        try:
            from langchain_anthropic import ChatAnthropic
            
            return ChatAnthropic(
                api_key=api_key,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            st.error(f"Error saat membuat provider Anthropic: {str(e)}")
            return None
    
    @staticmethod
    def _get_groq_provider(api_key, model_name, temperature, max_tokens):
        """Buat Groq provider dengan fallback jika model tidak tersedia"""
        try:
            from langchain_groq import ChatGroq
            
            # Coba inisialisasi dengan model yang dipilih
            try:
                provider = ChatGroq(
                    api_key=api_key,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Uji model dengan request kecil untuk memastikan model ada
                from groq import Groq
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                
                return provider
            except Exception as e:
                # Jika model tidak tersedia, coba model alternatif
                fallback_models = [
                    "llama3-8b-8192",     # Llama 3 8B (biasanya tersedia)
                    "mixtral-8x7b-32768", # Mixtral (biasanya tersedia)
                    "gemma-7b-it"         # Gemma (biasanya tersedia)
                ]
                
                # Jangan gunakan model yang sudah gagal
                if model_name in fallback_models:
                    fallback_models.remove(model_name)
                
                # Coba model-model alternatif
                for fallback_model in fallback_models:
                    try:
                        st.warning(f"Model {model_name} tidak tersedia, mencoba model {fallback_model}")
                        
                        # Test model terlebih dahulu
                        client = Groq(api_key=api_key)
                        client.chat.completions.create(
                            model=fallback_model,
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=5
                        )
                        
                        # Model berhasil, gunakan sebagai fallback
                        return ChatGroq(
                            api_key=api_key,
                            model_name=fallback_model,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    except Exception:
                        continue
                
                # Jika semua model gagal
                raise ValueError(f"Tidak ada model Groq yang tersedia. Error awal: {str(e)}")
        except Exception as e:
            st.error(f"Error saat membuat provider Groq: {str(e)}")
            return None
    
    @staticmethod
    def _get_huggingface_provider(api_key, model_name, temperature):
        """Buat HuggingFace provider"""
        try:
            # Coba menggunakan langchain_community terlebih dahulu
            from langchain_community.llms import HuggingFaceHub
            
            return HuggingFaceHub(
                huggingfacehub_api_token=api_key,
                repo_id=model_name,
                model_kwargs={"temperature": temperature}
            )
        except Exception as e:
            st.error(f"Error saat membuat provider HuggingFace: {str(e)}")
            return None

def init_memory(llm=None, max_token_limit=3000):
    """Inisialisasi memory dengan batasan token"""
    if not llm:
        return None
        
    return ConversationTokenBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
        max_token_limit=max_token_limit,
        llm=llm
    )
