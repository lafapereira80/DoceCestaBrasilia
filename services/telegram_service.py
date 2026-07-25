import requests

# =====================================================
# CONFIGURAÇÕES DO TELEGRAM
# =====================================================
# Substitua pelas suas chaves reais (entre as aspas)
TELEGRAM_TOKEN = "8832158812:AAFYlXuZNKs7JAK8tVUvtEfUJ6g93MhgI5Q"
TELEGRAM_CHAT_ID = "603346115"

def enviar_notificacao_telegram(mensagem):
    """Envia uma mensagem para o seu Telegram via Bot API"""
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return # Se não tiver token, não faz nada
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML" # Permite usar negrito (<b>) e outros estilos
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar notificação no Telegram: {e}")
