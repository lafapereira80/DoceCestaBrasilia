import requests
import streamlit as st

# Sua InfiniteTag real limpa
INFINITEPAY_HANDLE = "lafayette-improise" 

def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    """
    Gera um link de pagamento oficial via Checkout Integrado da InfinitePay.
    """
    # Valor em centavos para a API
    valor_em_centavos = int(round(valor_total * 100))
    id_curto = str(pedido_id).split('-')[0].upper()
    
    url_api = "https://api.checkout.infinitepay.io/links"
    
    payload = {
        "handle": INFINITEPAY_HANDLE,
        "webhook_url": "https://qtkcmwydongznncytncw.supabase.co/functions/v1/bright-action",
        "order_nsu": str(pedido_id),
        "items": [
            {
                "quantity": 1,
                "price": valor_em_centavos,
                "description": f"Pedido #{id_curto} - Doce Cesta"
            }
        ]
    }
    
    try:
        response = requests.post(url_api, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            dados = response.json()
            return dados.get("url") or dados.get("checkout_url")
        else:
            st.error(f"Erro na API InfinitePay: {response.text}")
            return None
    except Exception as e:
        st.error(f"Falha de conexão com a InfinitePay: {e}")
        return None
