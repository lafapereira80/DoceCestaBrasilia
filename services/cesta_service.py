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

        .order("nome")

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


        # cria nome único

        extensao = arquivo.name.split(".")[-1]


        nome_arquivo = (

            f"{uuid.uuid4()}."

            f"{extensao}"

        )



        caminho = (

            f"cestas/{nome_arquivo}"

        )



        # upload para storage

        supabase.storage.from_(

            "cestas"

        ).upload(

            caminho,

            arquivo.getvalue(),

            {

                "content-type":

                arquivo.type

            }

        )



        # URL pública

        url = (

            supabase.storage

            .from_("cestas")

            .get_public_url(

                caminho

            )

        )



        return url



    except Exception as erro:


        raise Exception(

            f"Erro no upload da imagem: {erro}"

        )



# =====================================================
# CADASTRAR CESTA
# =====================================================

def cadastrar_cesta(

    nome,

    descricao,

    preco,

    imagem=None

):


    resposta = (

        supabase

        .table("cestas")

        .insert({

            "nome":

                nome,


            "descricao":

                descricao,


            "preco":

                preco,


            "imagem":

                imagem,


            "ativa":

                True

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

        .eq(

            "id",

            cesta_id

        )

        .execute()

    )



# =====================================================
# ALTERAR STATUS
# =====================================================

def alterar_status_cesta(

    cesta_id,

    ativa

):


    (

        supabase

        .table("cestas")

        .update({

            "ativa":

                ativa

        })

        .eq(

            "id",

            cesta_id

        )

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

        .eq(

            "id",

            cesta_id

        )

        .single()

        .execute()

    )


    return resposta.data



# =====================================================
# ATUALIZAR CESTA
# =====================================================

def atualizar_cesta(

    cesta_id,

    nome,

    descricao,

    preco,

    imagem,

    ativa

):


    (

        supabase

        .table("cestas")

        .update({

            "nome":

                nome,


            "descricao":

                descricao,


            "preco":

                preco,


            "imagem":

                imagem,


            "ativa":

                ativa

        })

        .eq(

            "id",

            cesta_id

        )

        .execute()

    )
