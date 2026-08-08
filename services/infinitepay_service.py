import requests
import streamlit as st
from utils.encurtador import encurtar_link

def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    """
    Gera o link de pagamento na InfinitePay e passa pelo módulo encurtador.
    """
    handle_seguro = st.secrets.get("INFINITEPAY_HANDLE", "vanessa-hagen")
    webhook_seguro = st.secrets.get("INFINITEPAY_WEBHOOK", "https://qtkcmwydongznncytncw.supabase.co/functions/v1/bright-action")

    if valor_total < 1.00:
        st.warning("⚠️ O valor mínimo para gerar link é R$ 1,00.")
        return None

    valor_em_centavos = int(round(valor_total * 100))
    id_curto = str(pedido_id).split('-')[0].upper()
    
    url_api = "https://api.checkout.infinitepay.io/links"
    
    payload = {
        "handle": handle_seguro,
        "webhook_url": webhook_seguro,
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
        headers_inf = {'User-Agent': 'Mozilla/5.0'}
        response = requests.post(url_api, json=payload, headers=headers_inf, timeout=10)
        
        if response.status_code in [200, 201]:
            dados = response.json()
            link_longo = dados.get("url") or dados.get("checkout_url")
            
            if link_longo:
                # Chama a função importada do nosso arquivo utils/encurtador.py
                return encurtar_link(link_longo)
            return None
            
        else:
            st.error(f"Erro na InfinitePay: {response.text}")
            return None
    except Exception as e:
        st.error("Falha de conexão com a InfinitePay.")
        return None
