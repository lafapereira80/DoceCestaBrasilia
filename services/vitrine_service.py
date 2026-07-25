from config.supabase import supabase

def obter_configuracao_vitrine():
    try:
        resposta = supabase.table("configuracao_vitrine").select("*").eq("id", 1).single().execute()
        if resposta.data: return resposta.data
    except: pass
    
    return {
        "cabecalho_titulo": "Doce Cesta Brasília",
        "cabecalho_subtitulo": "Cestas personalizadas para momentos inesquecíveis 💝",
        "boas_vindas_texto": "É uma alegria receber você aqui!...",
        "como_pedir_itens": ["✨ Defina através do nosso catálogo..."],
        "catalogo_titulo": "🎁 Catálogo de Cestas",
        "catalogo_subtitulo": "Escolha a cesta perfeita, confira os itens detalhados e personalize do seu jeito.",
        "adicionais_titulo": "🎀 Incremente seu presente com nossos Adicionais Especiais:",
        "rodape_titulo": "Fale Conosco",
        "rodape_texto": "Dúvidas sobre entregas, prazos ou encomendas corporativas?<br>📍 <b>Brasília - DF</b>",
        "rodape_whatsapp_numero": "5561999759079",
        "rodape_whatsapp_texto": "💬 (61) 99975-9079",
        "rodape_instagram_usuario": "docecestabrasilia",
        "rodape_instagram_texto": "📸 @docecestabrasilia",
        "ordem_layout": ["textos", "catalogo", "adicionais"],
        "mostrar_textos": True,
        "mostrar_catalogo": True,
        "mostrar_adicionais": True,
        "mostrar_rodape": True
    }

def atualizar_configuracao_vitrine(dados):
    try:
        supabase.table("configuracao_vitrine").update(dados).eq("id", 1).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar vitrine: {e}")
        return False
