import requests
import streamlit as st

# Substitua pela sua InfiniteTag real (aquela que aparece no app, mas SEM o símbolo $)
INFINITEPAY_HANDLE = "lafayette-improise" 

def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    """
    Gera um link de pagamento oficial via Checkout Integrado da InfinitePay.
    """
    if not INFINITEPAY_HANDLE or INFINITEPAY_HANDLE == "lafayette-improise":
        st.error("Configure sua InfiniteTag no arquivo infinitepay_service.py")
        return None

    # A API da InfinitePay exige o valor em centavos
    valor_em_centavos = int(round(valor_total * 100))
    id_curto = str(pedido_id).split('-')[0].upper()
    
    # Novo endpoint atualizado da InfinitePay
    url_api = "https://api.checkout.infinitepay.io/links"
    
    payload = {
        "handle": INFINITEPAY_HANDLE,
        # AQUI ESTÁ A MÁGICA: Sua URL do Supabase já está injetada no pedido!
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
        st.error(f"Falha de conexão: {e}")
        return None
