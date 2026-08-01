import requests
import urllib.parse
import streamlit as st

def encurtar_link(link_longo):
    """
    Recebe um link longo, aplica o 'Disfarce' (User-Agent) para não ser 
    bloqueado como robô, e retorna a versão curta via Is.gd ou Clck.ru.
    """
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    # A máscara que engana a API fingindo ser o navegador Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
        
    try:
        # TENTATIVA 1: Is.gd (Sem anúncios, limpo)
        url_isgd = f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(link_longo)}"
        res = requests.get(url_isgd, headers=headers, timeout=5)
        
        if res.status_code == 200 and "is.gd" in res.text:
            return res.text.strip()
            
        # TENTATIVA 2: Clck.ru (Backup rápido)
        url_clck = f"https://clck.ru/--?url={urllib.parse.quote(link_longo)}"
        res2 = requests.get(url_clck, headers=headers, timeout=5)
        
        if res2.status_code == 200 and "clck" in res2.text:
            return res2.text.strip()
            
        return link_longo
        
    except Exception as e:
        return link_longo
