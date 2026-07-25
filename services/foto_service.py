import streamlit as st
from uuid import uuid4
from config.supabase import supabase

def montar_url_publica(caminho):
    # BLINDAGEM 1: Se o caminho estiver vazio (foto fantasma), retorna vazio sem travar
    if not caminho:
        return ""
        
    # BLINDAGEM 2 e 3: Puxa a URL base direto do cliente Supabase já conectado.
    # Isso evita totalmente o bug do .format() da função padrão do Supabase.
    url_base = supabase.supabase_url.rstrip("/")
    
    return f"{url_base}/storage/v1/object/public/pedido_fotos/{caminho}"

def salvar_fotos(pedido_id, arquivos):
    if not arquivos:
        return

    for arquivo in arquivos:
        try:
            extensao = arquivo.name.split(".")[-1]
            nome_arquivo = f"{pedido_id}/{uuid4()}.{extensao}"
            conteudo = arquivo.getvalue()

            supabase.storage.from_("pedido_fotos").upload(
                nome_arquivo,
                conteudo,
                {"content-type": arquivo.type}
            )

            supabase.table("pedido_fotos").insert({
                "pedido_id": pedido_id,
                "arquivo": nome_arquivo,
                "nome_original": arquivo.name
            }).execute()
        except Exception as e:
            print(f"Erro ao salvar foto: {e}")

def listar_fotos(pedido_id):
    try:
        resposta = (
            supabase
            .table("pedido_fotos")
            .select("*")
            .eq("pedido_id", pedido_id)
            .order("created_at")
            .execute()
        )

        fotos = resposta.data or []
        fotos_validas = []

        for foto in fotos:
            # Ignora fotos corrompidas ou sem arquivo salvo no banco
            if not foto.get("arquivo"):
                continue
                
            # A página 09_Detalhes_Pedido precisa que a chave se chame "url"
            foto["url"] = montar_url_publica(foto["arquivo"])
            fotos_validas.append(foto)

        return fotos_validas
        
    except Exception as e:
        # Retorna lista vazia em caso de qualquer outro erro bizarro, para não congelar a página
        print(f"Erro ao listar fotos: {e}")
        return []
