import streamlit as st


from services.cesta_service import listar_cestas
from services.cesta_produto_service import (
    listar_produtos_da_cesta
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

st.set_page_config(

    page_title="Configurar Cesta",

    page_icon="⚙️",

    layout="wide"

)



# =====================================================
# CONTROLE
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

h1{
font-size:26px !important;
}

h2{
font-size:20px !important;
}

[data-testid="stVerticalBlockBorderWrapper"]{

padding:15px;

background:#fffaf5;

border-radius:12px;

}

</style>
""",
unsafe_allow_html=True
)



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "⚙️ Configurar Cesta"
)


st.caption(
    "Defina quantos produtos o cliente poderá escolher dentro de cada categoria."
)


st.divider()



# =====================================================
# CARREGA CESTAS
# =====================================================

try:

    cestas = listar_cestas()


except Exception as erro:

    st.error(
        f"Erro ao carregar cestas: {erro}"
    )

    st.stop()



if not cestas:

    st.warning(
        "Nenhuma cesta cadastrada."
    )

    st.stop()



# =====================================================
# ESCOLHA DA CESTA
# =====================================================

cesta = st.selectbox(

    "Selecione a cesta",

    cestas,

    format_func=lambda x:
        x["nome"]

)



if not cesta:

    st.stop()



st.success(
    f"Cesta selecionada: {cesta['nome']}"
)



# =====================================================
# PRODUTOS DA CESTA
# =====================================================

try:

    produtos = listar_produtos_da_cesta(
        cesta["id"]
    )


except Exception as erro:

    st.error(
        f"Erro ao carregar produtos: {erro}"
    )

    st.stop()



if not produtos:

    st.warning(
        "Esta cesta ainda não possui produtos vinculados."
    )

    st.stop()



# =====================================================
# AGRUPA CATEGORIAS
# =====================================================

categorias = {}



for item in produtos:


    categoria = item.get(
        "categoria",
        "Sem categoria"
    )


    categorias.setdefault(
        categoria,
        []
    )


    categorias[categoria].append(
        item
    )



st.subheader(
    "📦 Configuração de escolha"
)



st.info(
"""
Defina a quantidade de produtos que o cliente poderá escolher.

Exemplo:

Bebidas → 2 opções  
Pães → 1 opção  
Espalháveis → 1 opção
"""
)



# =====================================================
# CONFIGURAÇÃO
# =====================================================

configuracoes = {}



for categoria, lista in categorias.items():


    with st.container(border=True):


        st.markdown(
            f"### 📦 {categoria}"
        )


        st.write(
            "Produtos disponíveis:"
        )


        for produto in lista:


            st.write(
                f"• {produto['nome']}"
            )


        quantidade = st.number_input(

            "Quantidade que o cliente pode escolher",

            min_value=1,

            max_value=len(lista),

            value=1,

            step=1,

            key=f"qtd_{categoria}"

        )


        configuracoes[categoria] = quantidade



# =====================================================
# SALVAR
# =====================================================

st.divider()



if st.button(

    "💾 Salvar Configuração",

    use_container_width=True

):


    st.success(
        "Configuração preparada."
    )


    st.json(
        configuracoes
    )
