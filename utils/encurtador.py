import requests

def encurtar_link(link_longo):
    """
    Recebe um link longo (InfinitePay) e retorna uma versão curta via Is.gd.
    O Is.gd faz redirecionamento direto, SEM propagandas e SEM telas de espera.
    Em caso de falha de conexão, retorna o link original por segurança.
    """
    # Verifica se o link é válido antes de tentar encurtar
    if not link_longo or not str(link_longo).startswith("http"):
        return link_longo
        
    try:
        # API do Is.gd (format=simple retorna apenas o link em formato de texto)
        url_api = f"https://is.gd/create.php?format=simple&url={link_longo}"
        
        # Fazemos a requisição com limite de 5 segundos
        resposta = requests.get(url_api, timeout=5)
        
        # O Is.gd retorna HTTP 200 com o link curto direto no texto
        if resposta.status_code == 200 and "is.gd" in resposta.text:
            return resposta.text.strip()
            
        return link_longo
        
    except Exception as e:
        # Se a internet falhar ou o serviço cair, o sistema devolve o link longo (não quebra a venda)
        return link_longo
