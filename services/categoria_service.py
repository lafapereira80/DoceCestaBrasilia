from config.supabase import supabase
import uuid

# =====================================================
# LISTAR CESTAS
# =====================================================
def listar_cestas():
    resposta = (
        supabase
        .table("cestas")
        .select("*")
        .order("ordem", desc=False)
        .order("nome", desc=False)
        .execute()
    )
    return resposta.data or []

# =====================================================
# UPLOAD IMAGEM DA CESTA
# =====================================================
def upload_imagem_cesta(arquivo):
    if arquivo is None:
        return None

    try:
        extensao = arquivo.name.split(".")[-1]
        nome_arquivo = f"{uuid.uuid4()}.{extensao}"
        caminho = f"cestas/{nome_arquivo}"

        supabase.storage.from_("cestas").upload(
            caminho,
            arquivo.getvalue(),
            {"content-type": arquivo.type}
        )

        url = (
            supabase.storage
            .from_("cestas")
            .get_public_url(caminho)
        )

        return url

    except Exception as erro:
        raise Exception(f"Erro no upload da imagem: {erro}")

# =====================================================
# CADASTRAR CESTA COM REORDENAÇÃO EM CASCATA
# =====================================================
def cadastrar_cesta(nome, descricao, preco, imagem=None, ordem=1, **kwargs):
    cestas_existentes = listar_cestas()
    
    for c in cestas_existentes:
        if c.get("ordem", 0) >= ordem:
            nova_ordem = c.get("ordem", 0) + 1
            supabase.table("cestas").update({"ordem": nova_ordem}).eq("id", c["id"]).execute()

    resposta = (
        supabase
        .table("cestas")
        .insert({
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "imagem": imagem,
            "ativa": True,
            "ordem": ordem
        })
        .execute()
    )
    return resposta.data

# =====================================================
# EXCLUIR CESTA
# =====================================================
def excluir_cesta(cesta_id):
    (
        supabase
        .table("cestas")
        .delete()
        .eq("id", cesta_id)
        .execute()
    )

# =====================================================
# ALTERAR STATUS
# =====================================================
def alterar_status_cesta(cesta_id, ativa):
    (
        supabase
        .table("cestas")
        .update({
            "ativa": ativa
        })
        .eq("id", cesta_id)
        .execute()
    )

# =====================================================
# BUSCAR CESTA
# =====================================================
def buscar_cesta(cesta_id):
    resposta = (
        supabase
        .table("cestas")
        .select("*")
        .eq("id", cesta_id)
        .single()
        .execute()
    )
    return resposta.data

# =====================================================
# ATUALIZAR CESTA COM REORDENAÇÃO (BLINDADO COM **kwargs)
# =====================================================
def atualizar_cesta(cesta_id, nome, descricao, preco, imagem, ativa, ordem=1, **kwargs):
    cestas_existentes = listar_cestas()
    for c in cestas_existentes:
        if c["id"] != cesta_id and c.get("ordem", 0) >= ordem:
            nova_ordem = c.get("ordem", 0) + 1
            supabase.table("cestas").update({"ordem": nova_ordem}).eq("id", c["id"]).execute()

    (
        supabase
        .table("cestas")
        .update({
            "nome": nome,
            "descricao": descricao,
            "preco": preco,
            "imagem": imagem,
            "ativa": ativa,
            "ordem": ordem
        })
        .eq("id", cesta_id)
        .execute()
    )

# =====================================================
# REMOVER IMAGEM DA CESTA
# =====================================================
def remover_imagem_cesta(cesta_id):
    (
        supabase
        .table("cestas")
        .update({
            "imagem": None
        })
        .eq("id", cesta_id)
        .execute()
    )
