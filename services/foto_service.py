import streamlit as st
from uuid import uuid4
from config.supabase import supabase

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
        resposta = supabase.table("pedido_fotos").select("*").eq("pedido_id", pedido_id).order("created_at").execute()
        fotos = resposta.data or []
        
        fotos_validas = []
        url_base = st.secrets["SUPABASE_URL"].rstrip("/")
        
        for foto in fotos:
            caminho = foto.get("arquivo")
            # Só processa se o caminho existir (ignora fotos corrompidas)
            if caminho:
                foto["url"] = f"{url_base}/storage/v1/object/public/pedido_fotos/{caminho}"
                fotos_validas.append(foto)
                
        return fotos_validas
    except Exception as e:
        print(f"Erro ao listar fotos: {e}")
        return []
