import requests
import urllib.parse
import streamlit as st

def encurtar_link_direto(link_longo):
    """
    Função embutida para garantir 100% de execução sem problemas de importação.
    Usa encurtadores limpos e sem propagandas.
    """
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    try:
        # TENTATIVA 1: Spoo.me (Sem propagandas, direto ao ponto)
        headers = {'Accept': 'application/json'}
        data = {'url': link_longo}
        res = requests.post("https://spoo.me/", data=data, headers=headers, timeout=5)
        
        if res.status_code in [200, 201]:
            link_curto = res.json().get("short_url")
            if link_curto:
                st.toast("✅ Link curto gerado com sucesso (Spoo.me)!", icon="🔗")
                return link_curto
                
        # TENTATIVA 2: Is.gd (Backup oficial)
        url_isgd = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(link_longo)}"
        res2 = requests.get(url_isgd, timeout=5)
        
        if res2.status_code == 200 and "is.gd" in res2.text:
            st.toast("✅ Link curto gerado com sucesso (Is.gd)!", icon="🔗")
            return res2.text.strip()
            
        st.toast("⚠️ Encurtadores fora do ar. Usando link longo original.", icon="⚠️")
        return link_longo
        
    except Exception as e:
        print(f"Erro ao encurtar: {e}")
        return link_longo


def gerar_link_checkout_infinitepay(pedido_id: str, valor_total: float, cliente_nome: str, cliente_tel: str):
    """
    Gera um link de pagamento oficial via Checkout Integrado da InfinitePay
    e encurta o link imediatamente usando a função embutida.
    """
    handle_seguro = st.secrets.get("INFINITEPAY_HANDLE", "lafayette-improise")
    webhook_seguro = st.secrets.get("INFINITEPAY_WEBHOOK", "https://qtkcmwydongznncytncw.supabase.co/functions/v1/bright-action")

    if valor_total < 1.00:
        st.warning("⚠️ A InfinitePay exige que o pedido tenha um valor mínimo de R$ 1,00 para gerar o link de pagamento.")
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
        response = requests.post(url_api, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            dados = response.json()
            link_longo = dados.get("url") or dados.get("checkout_url")
            
            if link_longo:
                # Chama a função embutida para encurtar
                return encurtar_link_direto(link_longo)
            return None
            
        else:
            st.error(f"Erro na API InfinitePay: {response.text}")
            return None
    except Exception as e:
        st.error(f"Falha de conexão com a InfinitePay: {e}")
        return None
