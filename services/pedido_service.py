from config.supabase import supabase


def salvar_pedido(dados):
    """
    Salva um pedido na tabela pedidos.
    Retorna:
        (True, id_do_pedido)
    ou
        (False, mensagem_erro)
    """

    try:

        resposta = (
            supabase
            .table("pedidos")
            .insert(dados)
            .execute()
        )

        pedido = resposta.data[0]

        return True, pedido["id"]

    except Exception as erro:

        return False, str(erro)
