import streamlit as st


from services.cesta_service import (
    buscar_cesta,
    atualizar_cesta,
    upload_imagem_cesta
)


from utils.menu import (
    configurar_pagina,
    menu_lateral
)


from utils.permissao import (
    administrador_operador
)




# =====================================================
# CONFIGURAÇÃO
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
# VERIFICA CESTA
# =====================================================

if "cesta_editar" not in st.session_state:


    st.warning(
        "Nenhuma cesta selecionada."
    )


    if st.button("⬅ Voltar"):

        st.switch_page(
            "pages/04_Cestas.py"
        )


    st.stop()



cesta_id = st.session_state["cesta_editar"]




# =====================================================
# BUSCA CESTA
# =====================================================

try:

    cesta = buscar_cesta(
        cesta_id
    )


    if not cesta:

        st.error(
            "Cesta não encontrada."
        )

        st.stop()


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
    "Atualize os dados da cesta."
)

st.divider()




# =====================================================
# CAMPOS
# =====================================================

col1, col2 = st.columns(2)


with col1:

    nome = st.text_input(
        "Nome da Cesta",
        value=cesta.get("nome","")
    )


with col2:

    preco = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        value=float(
            cesta.get("preco",0)
        ),
        step=1.0
    )



descricao = st.text_area(
    "Descrição",
    value=cesta.get("descricao","") or "",
    height=100
)



ativa = st.checkbox(
    "Cesta ativa",
    value=cesta.get("ativa",True)
)




# =====================================================
# IMAGEM
# =====================================================

st.divider()

st.subheader(
    "📷 Imagem da Cesta"
)


imagem_atual = cesta.get(
    "imagem",
    ""
)


if imagem_atual:

    st.image(
        imagem_atual,
        width=220
    )

else:

    st.info(
        "Sem imagem cadastrada."
    )



nova_imagem = st.file_uploader(
    "Trocar imagem",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp"
    ]
)



if nova_imagem:

    st.image(
        nova_imagem,
        width=220,
        caption="Nova imagem"
    )




# =====================================================
# BOTÕES
# =====================================================

st.divider()


col1, col2 = st.columns(2)



with col1:

    salvar = st.button(
        "💾 Salvar",
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
# SALVAR
# =====================================================

if salvar:


    if not nome.strip():

        st.error(
            "Informe o nome da cesta."
        )

        st.stop()



    imagem = imagem_atual



    # NOVA IMAGEM

    if nova_imagem:


        try:

            imagem = upload_imagem_cesta(
                nova_imagem
            )


        except Exception as erro:


            st.error(
                f"Erro no upload: {erro}"
            )

            st.stop()




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
