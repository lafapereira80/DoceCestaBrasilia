from config.supabase import supabase

def salvar_pedido(dados):

    return supabase.table("pedidos").insert(dados).execute()
