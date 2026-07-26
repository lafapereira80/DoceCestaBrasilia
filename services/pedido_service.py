from config.supabase import supabase
# IMPORTAÇÃO CORRIGIDA PARA O NOME NOVO
from services.foto_service import listar_fotos

# =====================================================
# FUNÇÃO PRIVADA (APAGA FOTOS FÍSICAS DO BUCKET)
# =====================================================
def _apagar_fotos_fisicas_do_pedido(pedido_id):
    """
    Lista todas as fotos anexadas a um pedido (ex: Polaroid) 
    e deleta os arquivos reais de dentro do Storage (Bucket) do Supabase.
    """
    try:
        # CHAMADA CORRIGIDA PARA O NOME NOVO
        fotos = listar_fotos(pedido_id)
        if not fotos:
            return
            
        for foto in fotos:
            # O serviço novo retorna 'url' para a imagem
            url_foto = str(foto.get("url", ""))
            if "/public/" in url_foto:
                # Extrai apenas a parte "pasta/nome_arquivo" depois de "/public/"
                caminho_pos_public = url_foto.split("/public/")[1]
                partes = caminho_pos_public.split("/")
                
                # Assume que a primeira parte é o nome do bucket, e o resto é o caminho
                if len(partes) >= 2:
                    nome_bucket = partes[0]
                    caminho_arquivo = "/".join(partes[1:])
                    # Remove o arquivo físico diretamente
                    supabase.storage.from_(nome_bucket).remove([caminho_arquivo])
    except Exception as erro:
        print(f"Aviso - Erro ao limpar bucket: {erro}")


# =====================================================
# LISTAR TODOS OS PEDIDOS (ATIVOS = DENTRO DO FLUXO)
# =====================================================
def listar_pedidos_ativos():
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .neq("status", "Entregue")
        .order("created_at", desc=True)
        .execute()
    )
    return resposta.data or []


# =====================================================
# LISTAR PEDIDOS HISTÓRICOS (ENTREGUES)
# =====================================================
def listar_pedidos_historico():
    resposta = (
        supabase
        .table("pedidos")
        .select("*")
        .eq("status", "Entregue")
        .order("created_at", desc=True)
        .execute()
    )
    return resposta.data or []


# =====================================================
# SALVAR (CRIAR NOVO)
# =====================================================
def salvar_pedido(dados):
    resposta = (
        supabase
        .table("pedidos")
        .insert(dados)
        .execute()
    )
    
    if resposta.data:
        return True, resposta.data[0]["id"]
    return False, "Erro ao salvar"


# =====================================================
# BUSCAR PEDIDO POR ID
# =====================================================
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


# =====================================================
# ATUALIZAR STATUS (MUDANÇA DE ESTÁGIO)
# =====================================================
def atualizar_status(pedido_id, novo_status):
    """
    Se o novo status for 'Entregue', ele ativa o gatilho 
    para apagar as fotos pesadas dos clientes do Bucket 
    para economizar espaço, mantendo só o texto no histórico.
    """
    if str(novo_status).strip().capitalize() == "Entregue":
        _apagar_fotos_fisicas_do_pedido(pedido_id)

    (
        supabase
        .table("pedidos")
        .update({"status": novo_status})
        .eq("id", pedido_id)
        .execute()
    )


# =====================================================
# EXCLUIR PEDIDO COMPLETO (DESISTÊNCIAS)
# =====================================================
def excluir_pedido_completo(pedido_id):
    """
    Exclui um pedido que estava em 'Desistência'.
    Garante que os arquivos físicos sejam excluídos do 
    servidor antes de apagar os registros de texto!
    """
    try:
        # 1. Deleta os arquivos (imagens) pesados do servidor primeiro
        _apagar_fotos_fisicas_do_pedido(pedido_id)

        # 2. Deleta as referências das fotos no banco (NOME DA TABELA CORRIGIDO)
        supabase.table("pedido_fotos").delete().eq("pedido_id", pedido_id).execute()
        
        # 3. Deleta os adicionais no banco (NOME DA TABELA CORRIGIDO)
        supabase.table("pedido_adicionais").delete().eq("pedido_id", pedido_id).execute()
        
        # 4. Deleta o pedido em si (Tabela pedidos)
        supabase.table("pedidos").delete().eq("id", pedido_id).execute()
        
        return True, "Pedido e todas as fotos foram excluídos com sucesso."
    
    except Exception as e:
        return False, f"Erro ao excluir pedido: {str(e)}"
