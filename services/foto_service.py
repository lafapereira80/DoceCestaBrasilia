from uuid import uuid4
from config.supabase import supabase


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
