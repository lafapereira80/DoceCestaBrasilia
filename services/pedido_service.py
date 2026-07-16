from config.supabase import supabase


def salvar_pedido(dados):

    resposta = supabase.table("pedidos").insert(dados).execute()

    try:
        pedido_id = resposta.data[0]["id"]
        return True, pedido_id

    except Exception as erro:
        return False, str(erro)


def listar_pedidos():

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return resposta.data


def buscar_pedido(pedido_id):

    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("id", pedido_id)
        .single()
        .execute()
    )

    return resposta.data
