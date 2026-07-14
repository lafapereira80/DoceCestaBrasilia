from config.supabase import supabase


def salvar_pedido(dados):
    """
    Salva um pedido na tabela pedidos.
    Retorna (True, resposta) em caso de sucesso
    ou (False, erro) em caso de falha.
    """

    try:

        resposta = supabase.table("pedidos").insert(dados).execute()

        return True, resposta

    except Exception as erro:

        return False, str(erro)
