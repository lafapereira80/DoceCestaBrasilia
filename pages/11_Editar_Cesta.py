import streamlit as st
from pathlib import Path
from datetime import datetime


from services.cesta_service import (
    buscar_cesta,
    atualizar_cesta
)


from config.supabase import supabase


from utils.menu import (
    configurar_pagina,
    menu_lateral
)


from utils.permissao import (
    administrador_operador
)





# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(

    page_title="Editar Cesta",

    page_icon="✏️",

    layout="wide"

)





# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()





# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>


.block-container{

    padding-top:1rem;

    padding-bottom:1rem;

}



h1{

    font-size:24px !important;

}



p, div, span{

    font-size:13px;

}



.stButton button{

    height:36px;

    font-size:13px;

    border-radius:8px;

}



input, textarea{

    font-size:13px !important;

}


</style>
""",
unsafe_allow_html=True
)





# =====================================================
# VALIDA CESTA
# =====================================================

if "cesta_editar" not in st.session_state:


    st.error(

        "Nenhuma cesta selecionada."

    )


    if st.button(

        "⬅ Voltar"

    ):


        st.switch_page(

            "pages/04_Cestas.py"

        )


    st.stop()





cesta_id = st.session_state["cesta_editar"]





# =====================================================
# BUSCA DADOS
# =====================================================

try:


    cesta = buscar_cesta(

        cesta_id

    )


except Exception as erro:


    st.error(

        f"Erro ao carregar cesta: {erro}"

    )


    st.stop()





imagem_atual = cesta.get(

    "imagem",

    ""

) or ""





# =====================================================
# TÍTULO
# =====================================================

st.title(

    "✏️ Editar Cesta"

)


st.caption(

    "Atualize os dados da cesta e substitua a imagem quando necessário."

)


st.divider()





# =====================================================
# CAMPOS DA CESTA
# =====================================================

col1, col2 = st.columns(2)



with col1:


    nome = st.text_input(

        "Nome da Cesta",

        value=cesta.get(

            "nome",

            ""

        )

    )



with col2:


    preco = st.number_input(

        "Preço (R$)",

        min_value=0.0,

        value=float(

            cesta.get(

                "preco",

                0

            )

        ),

        step=1.0

    )





descricao = st.text_area(

    "Descrição",

    value=cesta.get(

        "descricao",

        ""

    ) or "",

    height=90

)





ativa = st.checkbox(

    "Cesta ativa",

    value=cesta.get(

        "ativa",

        True

    )

)

# =====================================================
# IMAGEM DA CESTA
# =====================================================

st.divider()

st.subheader(
    "📷 Imagem da Cesta"
)



if imagem_atual:


    st.image(

        imagem_atual,

        width=220

    )


    st.caption(

        "Imagem atual"

    )


else:


    st.info(

        "Esta cesta ainda não possui imagem cadastrada."

    )





nova_foto = st.file_uploader(

    "Enviar nova foto da cesta",

    type=[

        "jpg",

        "jpeg",

        "png",

        "webp"

    ]

)





if nova_foto:


    st.image(

        nova_foto,

        width=220,

        caption="Nova imagem"

    )





st.divider()





# =====================================================
# BOTÕES
# =====================================================

col1, col2 = st.columns(2)



with col1:


    salvar = st.button(

        "💾 Salvar Alterações",

        use_container_width=True

    )



with col2:


    cancelar = st.button(

        "❌ Cancelar",

        use_container_width=True

    )





# =====================================================
# CANCELAR
# =====================================================

if cancelar:


    st.session_state.pop(

        "cesta_editar",

        None

    )


    st.switch_page(

        "pages/04_Cestas.py"

    )

# =====================================================
# SALVAR ALTERAÇÕES
# =====================================================

if salvar:



    if not nome.strip():


        st.error(

            "Informe o nome da cesta."

        )


        st.stop()





    imagem = imagem_atual





    # =================================================
    # ENVIA NOVA IMAGEM PARA O STORAGE
    # =================================================

    if nova_foto:



        try:



            extensao = Path(

                nova_foto.name

            ).suffix.lower()



            nome_arquivo = (

                f"{cesta_id}_"

                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"

                f"{extensao}"

            )



            caminho = nome_arquivo





            supabase.storage \

                .from_(

                    "cestas"

                ) \

                .upload(

                    caminho,

                    nova_foto.getvalue(),

                    {

                        "content-type":

                        nova_foto.type

                    }

                )





            imagem = (

                supabase.storage

                .from_(

                    "cestas"

                )

                .get_public_url(

                    caminho

                )

            )



        except Exception as erro:



            st.error(

                f"Erro ao enviar imagem: {erro}"

            )


            st.stop()





    # =================================================
    # ATUALIZA BANCO
    # =================================================

    try:



        atualizar_cesta(



            cesta_id,



            nome.strip(),



            descricao.strip(),



            preco,



            imagem,



            ativa



        )



        st.success(

            "Cesta atualizada com sucesso!"

        )



        st.session_state.pop(

            "cesta_editar",

            None

        )



        st.switch_page(

            "pages/04_Cestas.py"

        )





    except Exception as erro:



        st.error(

            f"Erro ao atualizar cesta: {erro}"

        )





# =====================================================
# RODAPÉ
# =====================================================

st.divider()



st.caption(

    "🎁 Edição de Cestas - Doce Cesta Brasília"

            )
