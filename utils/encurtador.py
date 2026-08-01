import requests
import urllib.parse
import streamlit as st

def encurtar_link(link_longo):
    """
    Encurtador Premium Spoo.me (Focado em Devs, sem anúncios, redirecionamento direto).
    """
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    try:
        # TENTATIVA 1: Spoo.me API (Muito estável e não bloqueia links de pagamento)
        headers = {'Accept': 'application/json'}
        data = {'url': link_longo}
        
        res = requests.post("https://spoo.me/", data=data, headers=headers, timeout=5)
        
        if res.status_code in [200, 201]:
            link_curto = res.json().get("short_url")
            if link_curto:
                st.toast("✅ Link encurtado com sucesso!")
                return link_curto
                
        # TENTATIVA 2: Is.gd formatado 
        url_isgd = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(link_longo)}"
        res2 = requests.get(url_isgd, timeout=5)
        
        if res2.status_code == 200 and "is.gd" in res2.text:
            st.toast("✅ Link encurtado (Alternativo)!")
            return res2.text.strip()
            
        st.toast("⚠️ Encurtador indisponível no momento. Usando link original.")
        return link_longo
        
    except Exception as e:
        print(f"Erro no encurtador: {e}")
        return link_longo
