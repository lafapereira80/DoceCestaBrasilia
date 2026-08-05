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
def cadastrar_cesta(dados: dict):
    """
    Cria uma cesta nova. Se a 'ordem' escolhida já existe (ou é menor que
    alguma existente), empurra as outras +1 em cascata para nunca haver
    duas cestas na mesma posição.
    """
    ordem = int(dados.get("ordem") or 1)
    cestas_existentes = listar_cestas()

    for c in cestas_existentes:
        if c.get("ordem", 0) >= ordem:
            supabase.table("cestas").update({"ordem": c.get("ordem", 0) + 1}).eq("id", c["id"]).execute()

    dados_finais = {**dados, "ordem": ordem}
    dados_finais.setdefault("ativa", True)

    resposta = supabase.table("cestas").insert(dados_finais).execute()
    return resposta.data


# =====================================================
# EXCLUIR CESTA
# =====================================================
def excluir_cesta(cesta_id):
    supabase.table("cestas").delete().eq("id", cesta_id).execute()


# =====================================================
# ALTERAR STATUS
# =====================================================
def alterar_status_cesta(cesta_id, ativa):
    supabase.table("cestas").update({"ativa": ativa}).eq("id", cesta_id).execute()


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


# Alias: algumas páginas (ex: 11_Editar_Cesta.py) importam com esse nome.
buscar_cesta_por_id = buscar_cesta


# =====================================================
# ATUALIZAR CESTA COM REORDENAÇÃO EM CASCATA
# =====================================================
def atualizar_cesta(cesta_id, dados: dict):
    """
    Atualiza os campos informados em 'dados'. Se 'ordem' fizer parte do
    dicionário, reordena em cascata as demais cestas para abrir espaço,
    sem nunca deixar duas cestas com a mesma posição.
    """
    ordem = dados.get("ordem")
    if ordem is not None:
        ordem = int(ordem)
        cestas_existentes = listar_cestas()
        for c in cestas_existentes:
            if c["id"] != cesta_id and c.get("ordem", 0) >= ordem:
                supabase.table("cestas").update({"ordem": c.get("ordem", 0) + 1}).eq("id", c["id"]).execute()
        dados = {**dados, "ordem": ordem}

    supabase.table("cestas").update(dados).eq("id", cesta_id).execute()
    return True


# =====================================================
# REMOVER IMAGEM DA CESTA (apaga o arquivo físico no bucket também)
# =====================================================
def remover_imagem_cesta(cesta_id, imagem_url=None):
    try:
        if imagem_url and "/public/cestas/" in str(imagem_url):
            caminho_arquivo = str(imagem_url).split("/public/cestas/", 1)[1]
            supabase.storage.from_("cestas").remove([caminho_arquivo])
    except Exception:
        pass  # segue removendo a referência no banco mesmo se o storage falhar

    supabase.table("cestas").update({"imagem": None}).eq("id", cesta_id).execute()
    return True


# Alias mais explícito, usado pelas páginas de gestão de cestas.
deletar_imagem_cesta = remover_imagem_cesta
