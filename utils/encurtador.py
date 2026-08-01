import requests

def encurtar_link(link_longo):
    """
    Recebe um link longo (InfinitePay) e retorna uma versão curta via TinyURL.
    Em caso de falha de conexão, retorna o link original por segurança.
    """
    # Verifica se o link é válido antes de tentar encurtar
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    try:
        url_api = f"http://tinyurl.com/api-create.php?url={link_longo}"
        
        # Fazemos a requisição com limite de 5 segundos para não travar o sistema
        resposta = requests.get(url_api, timeout=5)
        
        if resposta.status_code == 200:
            return resposta.text
            
        return link_longo
        
    except Exception as e:
        # Se a internet falhar ou a API do TinyURL cair, o sistema não quebra
        return link_longo
