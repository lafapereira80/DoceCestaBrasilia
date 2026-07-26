import streamlit as st
import requests

def enviar_notificacao_telegram(mensagem):
    try:
        # 1. Busca as chaves no cofre do Streamlit
        bot_token = st.secrets.get("TELEGRAM_BOT_TOKEN")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
        
        # Validação: Se não tiver chave, avisa no log do servidor
        if not bot_token or not chat_id:
            print("⚠️ ERRO: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não encontrados no st.secrets.")
            return False
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # 2. Monta o pacote de envio com parse_mode HTML (para os <b> funcionarem)
        payload = {
            "chat_id": chat_id,
            "text": mensagem,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        # 3. Dispara a mensagem
        resposta = requests.post(url, json=payload, timeout=10)
        
        # 4. Verifica se o Telegram aceitou
        if resposta.status_code != 200:
            print(f"⚠️ ERRO DO TELEGRAM (Código {resposta.status_code}): {resposta.text}")
            return False
            
        return True
        
    except Exception as e:
        print(f"⚠️ ERRO CRÍTICO NO SERVIÇO DO TELEGRAM: {e}")
        return False
