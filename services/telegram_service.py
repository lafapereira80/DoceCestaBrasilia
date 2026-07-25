import requests
import streamlit as st

# =====================================================
# CONFIGURAÇÕES DO TELEGRAM (PUXANDO DO COFRE SEGURO)
# =====================================================
# Agora as chaves ficam escondidas no painel do Streamlit!
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID")

def enviar_notificacao_telegram(mensagem):
    """Envia uma mensagem para o seu Telegram via Bot API"""
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Aviso: Chaves do Telegram não configuradas no secrets.")
        return 
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar notificação no Telegram: {e}")
