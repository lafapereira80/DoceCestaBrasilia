import requests
import urllib.parse
import streamlit as st

def encurtar_link(link_longo):
    """
    Recebe um link longo de pagamento e tenta encurtar usando serviços profissionais.
    Redirecionamento 100% direto, sem telas de espera ou propagandas.
    """
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    try:
        # ==========================================
        # TENTATIVA 1: CleanURI (Profissional e Limpo)
        # ==========================================
        url_clean = "https://cleanuri.com/api/v1/shorten"
        res_clean = requests.post(url_clean, data={'url': link_longo}, timeout=5)
        
        if res_clean.status_code == 200:
            dados = res_clean.json()
            if "result_url" in dados:
                return dados["result_url"]

        # ==========================================
        # TENTATIVA 2: Clck.ru (Rápido e sem frescuras)
        # ==========================================
        link_codificado = urllib.parse.quote(link_longo)
        url_clck = f"https://clck.ru/--?url={link_codificado}"
        res_clck = requests.get(url_clck, timeout=5)
        
        if res_clck.status_code == 200 and "clck.ru" in res_clck.text:
            return res_clck.text.strip()
            
        # Se os dois bloquearem por segurança, avisa o usuário sutilmente e devolve o longo
        st.toast("⚠️ Os encurtadores de segurança recusaram o link. Usando o original para não travar a venda.")
        return link_longo
        
    except Exception as e:
        # Em caso de queda geral de internet
        return link_longo
