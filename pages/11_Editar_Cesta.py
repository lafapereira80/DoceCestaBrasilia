import streamlit as st


from services.cesta_service import (
    buscar_cesta,
    atualizar_cesta
)


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
# CSS COMPACTO
# =====================================================

st.markdown(
"""
<style>


h1 {

font-size:24px !important;

margin-bottom:5px;

}


h2 {

font-size:18px !important;

margin-top:8px;

margin-bottom:8px;

}


p, div, span {

font-size:13px;

}



label {

font-size:13px !important;

}



.stButton button {

height:34px;

font-size:13px;

padding:4px 10px;

}



input, textarea {

font-size:13px !important;

}



.block-container {

padding-top:1rem;

padding-bottom:1rem;

}



textarea {

min-height:70px !important;

}



</style>
""",
unsafe_allow_html=True
)



# =====================================================
# VERIFICA CESTA SELECIONADA
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
# CARREGA DADOS
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



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "✏️ Editar Cesta"
)


st.caption(
    "Atualize as informações da cesta cadastrada."
)


st.divider()



# =====================================================
# FORMULÁRIO
# =====================================================

with st.form(
    "form_editar_cesta"
):


    col1,col2 = st.columns(2)



    with col1:


        nome = st.text_input(

            "Nome da Cesta",

            value=cesta["nome"]

        )



    with col2:


        preco = st.number_input(

            "Preço (R$)",

            min_value=0.0,

            value=float(
                cesta["preco"]
            ),

            step=1.0

        )



    descricao = st.text_area(

        "Descrição",

        value=cesta.get(
            "descricao",
            ""
        )
        or "",

        height=80

    )



    imagem = st.text_input(

        "Imagem (URL)",

        value=cesta.get(
            "imagem",
            ""
        )
        or ""

    )



    ativa = st.checkbox(

        "Cesta ativa",

        value=cesta.get(
            "ativa",
            True
        )

    )



    st.divider()



    col1,col2 = st.columns(2)



    with col1:


        salvar = st.form_submit_button(

            "💾 Salvar",

            use_container_width=True

        )



    with col2:


        cancelar = st.form_submit_button(

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
# SALVAR
# =====================================================

if salvar:



    if nome.strip() == "":


        st.error(

            "Informe o nome da cesta."

        )


    else:


        try:



            atualizar_cesta(

                cesta_id,

                nome.strip(),

                descricao.strip(),

                preco,

                imagem.strip(),

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
