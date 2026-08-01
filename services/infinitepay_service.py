import requests
import streamlit as st
from utils.encurtador import encurtar_link  # <-- Importando a sua nova ferramenta!

def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    """
    Gera um link de pagamento oficial via Checkout Integrado da InfinitePay
    e retorna a versão encurtada automaticamente.
    """
    # =======================================================
    # BUSCA DE CHAVES SEGURAS (ST.SECRETS) COM FALLBACK
    # =======================================================
    handle_seguro = st.secrets.get("INFINITEPAY_HANDLE", "lafayette-improise")
    webhook_seguro = st.secrets.get("INFINITEPAY_WEBHOOK", "https://qtkcmwydongznncytncw.supabase.co/functions/v1/bright-action")

    # =======================================================
    # TRAVA DE VALOR MÍNIMO (Regra Comercial da InfinitePay)
    # =======================================================
    if valor_total < 1.00:
        st.warning("⚠️ A InfinitePay exige que o pedido tenha um valor mínimo de R$ 1,00 para gerar o link de pagamento.")
        return None

    # Valor em centavos para a API
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
        response = requests.post(url_api, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            dados = response.json()
            link_longo = dados.get("url") or dados.get("checkout_url")
            
            # =======================================================
            # A MÁGICA ACONTECE AQUI: Encurtando antes de devolver
            # =======================================================
            if link_longo:
                return encurtar_link(link_longo)
            return None
            
        else:
            st.error(f"Erro na API InfinitePay: {response.text}")
            return None
    except Exception as e:
        st.error(f"Falha de conexão com a InfinitePay: {e}")
        return None
