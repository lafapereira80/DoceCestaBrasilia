import requests
import streamlit as st

# Substitua pela sua InfiniteTag real (sem o @)
INFINITEPAY_HANDLE = "lafayette-improise" 

def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    """
    Gera um link de pagamento oficial via Checkout da InfinitePay.
    """
    if not INFINITEPAY_HANDLE or INFINITEPAY_HANDLE == "sua_ininitetag_aqui":
        st.error("Configure sua InfiniteTag no arquivo infinitepay_service.py")
        return None

    # A API da InfinitePay exige o valor em centavos
    valor_em_centavos = int(round(valor_total * 100))
    
    url_api = "https://api.infinitepay.io/v2/checkout"
    
    payload = {
        "handle": INFINITEPAY_HANDLE,
        "order_nsu": str(pedido_id),
        "amount": valor_em_centavos,
        "customer": {
            "name": cliente_nome,
            "phone": cliente_tel
        }
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
