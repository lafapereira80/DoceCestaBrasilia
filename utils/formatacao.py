import urllib.parse
import re
from datetime import datetime

# ==========================================
# DADOS GERAIS DA LOJA (Central de Controle)
# Altere aqui e mudará em todo o sistema!
# ==========================================
NOME_LOJA = "Doce Cesta Brasília"
NOME_LOJA_CURTO = "Doce Cesta"
TELEFONE_WHATSAPP = "5561999759079" # Apenas números (DDI + DDD + Número)
TELEFONE_EXIBICAO = "(61) 99975-9079"
INSTAGRAM_ARROBA = "@docecestabrasilia"
INSTAGRAM_URL = "https://instagram.com/docecestabrasilia"

# ==========================================
# FUNÇÕES GLOBAIS DE MATEMÁTICA E DATA
# ==========================================
def formatar_moeda(valor):
    """Garante que R$ 15.5 vire R$ 15,50"""
    try: 
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: 
        return "0,00"

def tratar_preco(valor):
    """Converte o texto digitado pelo usuário em número seguro para o banco"""
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_data_br(d_str):
    """Converte padrão americano do banco para DD/MM/YYYY"""
    if not d_str: return "-"
    try: return datetime.strptime(str(d_str)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return str(d_str)

def gerar_link_wpp(telefone, texto):
    """Gera um link clicável do WhatsApp blindado contra erros de digitação"""
    fone_limpo = re.sub(r'\D', '', str(telefone))
    if not fone_limpo: return "#"
    # Adiciona o 55 do Brasil se o usuário digitou apenas DDD+Número
    if len(fone_limpo) <= 11: fone_limpo = f"55{fone_limpo}"
    return f"https://wa.me/{fone_limpo}?text={urllib.parse.quote(texto)}"
