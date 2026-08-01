import requests
import urllib.parse

def encurtar_link(link_longo):
    """
    Recebe um link longo, codifica os caracteres especiais e retorna a versão curta via Is.gd.
    """
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    try:
        # Codifica o link para que símbolos (como ? ou =) não quebrem a API
        link_codificado = urllib.parse.quote(link_longo)
        
        url_api = f"https://is.gd/create.php?format=simple&url={link_codificado}"
        
        resposta = requests.get(url_api, timeout=5)
        
        if resposta.status_code == 200 and "is.gd" in resposta.text:
            return resposta.text.strip()
            
        return link_longo
        
    except Exception as e:
        return link_longo
