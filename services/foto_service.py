import streamlit as st
from uuid import uuid4
from config.supabase import supabase

def salvar_fotos(pedido_id, arquivos):
    """
    Faz o upload das fotos para o Storage e salva os dados na tabela pedido_fotos,
    incluindo a URL pública direta da imagem.
    """
    if not arquivos:
        return True, ""

    if not isinstance(arquivos, list):
        arquivos = [arquivos]
        
    erros = []
    url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")

    for arquivo in arquivos:
        try:
            extensao = arquivo.name.split(".")[-1]
            nome_arquivo = f"{pedido_id}/{uuid4()}.{extensao}"
            conteudo = arquivo.getvalue()

            # 1. Faz o upload para o Storage
            supabase.storage.from_("pedido_fotos").upload(
                nome_arquivo,
                conteudo,
                {"content-type": arquivo.type}
            )

            # 2. Gera o link público oficial
            url_publica = f"{url_base}/storage/v1/object/public/pedido_fotos/{nome_arquivo}"

            # 3. Insere na tabela utilizando todas as colunas corretas
            supabase.table("pedido_fotos").insert({
                "pedido_id": pedido_id,
                "arquivo": nome_arquivo,
                "nome_original": arquivo.name,
                "url": url_publica
            }).execute()
            
        except Exception as e:
            erros.append(f"Falha na foto {arquivo.name}: {str(e)}")
            
    if erros:
        return False, " | ".join(erros)
        
    return True, ""


def listar_fotos(pedido_id):
    """
    Busca as fotos de um pedido no banco de dados. 
    Possui sistema de fallback para montar a URL de fotos antigas.
    """
    try:
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pedido_id).order("created_at").execute()
        fotos = resposta.data or []
        
        url_base = st.secrets.get("SUPABASE_URL", "").rstrip("/")
        
        # Garante que todas as fotos tenham um link válido para exibição, mesmo as mais antigas
        for foto in fotos:
            if not foto.get("url") and foto.get("arquivo"):
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{foto['arquivo']}"
                
        return fotos
    except Exception as e:
        print(f"Erro ao listar fotos: {e}")
        return []


def deletar_foto(foto_id, caminho_arquivo):
    """
    Deleta o arquivo físico do Storage e o registro da tabela.
    """
    try:
        if caminho_arquivo:
            supabase.storage.from_("pedido_fotos").remove([caminho_arquivo])
            
        supabase.table("pedido_fotos").delete().eq("id", foto_id).execute()
        return True, ""
    except Exception as e:
        return False, f"Erro ao deletar: {str(e)}"
