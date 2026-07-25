import streamlit as st
from uuid import uuid4
from config.supabase import supabase

def montar_url_publica(caminho):
    # Solução blindada: Montamos a URL na mão puxando a base direto do cofre.
    # Isso evita o bug interno ('format') da biblioteca do Supabase.
    url_base = st.secrets["SUPABASE_URL"].rstrip("/")
    
    return f"{url_base}/storage/v1/object/public/pedido_fotos/{caminho}"

def salvar_fotos(pedido_id, arquivos):
    if not arquivos:
        return

    for arquivo in arquivos:
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

def listar_fotos(pedido_id):
    resposta = (
        supabase
        .table("pedido_fotos")
        .select("*")
        .eq("pedido_id", pedido_id)
        .order("created_at")
        .execute()
    )

    fotos = resposta.data or []

    for foto in fotos:
        # A página 09_Detalhes_Pedido procura por "url" (e não "url_publica")
        foto["url"] = montar_url_publica(foto["arquivo"])

    return fotos
