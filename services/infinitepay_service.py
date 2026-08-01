import requests
import streamlit as st
from utils.encurtador import encurtar_link  # TEM QUE TER ESSA LINHA AQUI EM CIMA!

def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    # ... (código do handle, webhook, payload) ...
    
    try:
        response = requests.post(url_api, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            dados = response.json()
            link_longo = dados.get("url") or dados.get("checkout_url")
            
            # TEM QUE TER ESSE BLOCO AQUI NO FINAL:
            if link_longo:
                return encurtar_link(link_longo)
            return None
            
        else:
            st.error(f"Erro na API InfinitePay: {response.text}")
            return None
    except Exception as e:
        st.error(f"Falha de conexão com a InfinitePay: {e}")
        return None
