import streamlit as st
from uuid import uuid4
from config.supabase import supabase

def montar_url_publica(caminho):
    if not caminho:
        return ""
    try:
        # Puxa a URL do cofre para não usar a função nativa bugada do Supabase
        url_base = st.secrets["SUPABASE_URL"].rstrip("/")
        return f"{url_base}/storage/v1/object/public/pedido_fotos/{caminho}"
    except Exception:
        return ""

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
            if foto.get("arquivo"):
                foto["url"] = montar_url_publica(foto["arquivo"])
                fotos_validas.append(foto)

        return fotos_validas
        
    except Exception as e:
        # NOSSO ALARME: Se o erro for aqui, ele vai gritar essa mensagem nova!
        raise Exception(f"[ALERTA DE CÓDIGO NOVO] O erro agora é: {e}")
