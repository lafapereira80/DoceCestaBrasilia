import streamlit as st


from services.produto_service import (
    listar_produtos,
    cadastrar_produto,
    excluir_produto,
    listar_categorias,
    alterar_status_produto
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
    page_title="Produtos",
    page_icon="🛒",
    layout="wide"
)



# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()


usuario = st.session_state.usuario



# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>

.block-container{
    padding-top:1rem;
}


.stButton button{
    height:32px;
    border-radius:8px;
    font-size:13px;
}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# TÍTULO
# =====================================================

st.title("🛒 Produtos")

st.caption(
    "Gerenciamento de produtos por categoria"
)

st.divider()



# =====================================================
# CARREGAR CATEGORIAS
# =====================================================

try:

    categorias = listar_categorias()


except Exception as erro:

    st.error(
        f"Erro ao carregar categorias: {erro}"
    )

    categorias = []



# =====================================================
# CADASTRO
# =====================================================

if usuario["perfil"] == "Administrador":


    st.subheader(
        "➕ Novo Produto"
    )


    with st.form("novo_produto"):


        nome = st.text_input(
            "Nome do Produto"
        )


        descricao = st.text_area(
            "Descrição",
            height=70
        )


        categoria = st.selectbox(
            "Categoria",
            categorias,
            format_func=lambda x: x["nome"]
        )


        categoria_nome = (
            categoria["nome"]
            .strip()
            .lower()
        )


        if categoria_nome == "adicionais":


            tipo_preco = st.radio(
                "Tipo de preço",
                [
                    "Preço definido",
                    "Preço sob consulta"
                ],
                horizontal=True
            )


            if tipo_preco == "Preço sob consulta":

                preco = None

                st.info(
                    "O preço será informado posteriormente."
                )


            else:

                preco = st.number_input(
                    "Preço (R$)",
                    min_value=0.0,
                    step=0.50,
                    format="%.2f"
                )


        else:


            tipo_preco = "Incluso na cesta"

            preco = None

            st.info(
                "Produto incluso na composição da cesta."
            )


        ativo = st.checkbox(
            "Produto ativo",
            value=True
        )


        salvar = st.form_submit_button(
            "💾 Cadastrar Produto",
            use_container_width=True
        )
        # =====================================================
# SALVAR PRODUTO
# =====================================================

if salvar:


    if not nome.strip():

        st.error(
            "Informe o nome do produto."
        )

        st.stop()



    categoria_nome = (
        categoria["nome"]
        .strip()
        .lower()
    )



    if (

        categoria_nome == "adicionais"

        and

        tipo_preco == "Preço definido"

        and

        preco <= 0

    ):

        st.error(
            "Informe o valor do adicional."
        )

        st.stop()



    try:


        cadastrar_produto(

            categoria_id=categoria["id"],

            nome=nome.strip(),

            descricao=descricao.strip(),

            preco=preco,

            ativo=ativo,

            tipo_preco=tipo_preco

        )


        st.success(
            "Produto cadastrado com sucesso!"
        )


        st.rerun()



    except Exception as erro:


        st.error(
            f"Erro ao cadastrar produto: {erro}"
        )



else:


    if usuario["perfil"] != "Administrador":

        st.info(
            "Modo consulta. Apenas Administradores podem cadastrar produtos."
        )





# =====================================================
# FUNÇÃO EXIBIR PRODUTO
# =====================================================

def exibir_produto(produto, categoria_nome):


    with st.container(border=True):


        col1, col2, col3, col4 = st.columns(
            [5, 2, 1.5, 2.5]
        )



        # ---------------------------------------------
        # NOME
        # ---------------------------------------------

        with col1:


            st.write(
                f"**{produto.get('nome','-')}**"
            )


            if produto.get("descricao"):


                st.caption(
                    produto["descricao"]
                )



        # ---------------------------------------------
        # PREÇO
        # ---------------------------------------------

        with col2:


            categoria = (
                categoria_nome
                .strip()
                .lower()
            )


            if categoria == "adicionais":


                tipo = produto.get(
                    "tipo_preco",
                    "Preço definido"
                )


                if tipo == "Preço sob consulta":


                    st.warning(
                        "⚠️ Sob consulta"
                    )


                else:


                    valor = produto.get(
                        "preco"
                    )


                    if valor is not None:


                        valor = float(valor)


                        texto = (

                            f"R$ {valor:,.2f}"

                            .replace(",", "X")

                            .replace(".", ",")

                            .replace("X",".")

                        )


                        st.write(texto)


            else:


                st.info(
                    "Incluso"
                )



        # ---------------------------------------------
        # STATUS
        # ---------------------------------------------

        with col3:


            if produto.get(
                "ativo",
                True
            ):


                st.success(
                    "🟢"
                )


            else:


                st.error(
                    "🔴"
                )



        # ---------------------------------------------
        # BOTÕES
        # ---------------------------------------------

        with col4:


            b1, b2, b3 = st.columns(3)



            with b1:

                editar = st.button(
                    "✏️",
                    key=f"editar_{produto['id']}"
                )



            with b2:

                status = st.button(
                    "🔴" if produto.get("ativo", True) else "🟢",
                    key=f"status_{produto['id']}"
                )



            with b3:

                excluir = st.button(
                    "🗑️",
                    key=f"excluir_{produto['id']}"
                )



        return editar, status, excluir
        # =====================================================
# LISTAGEM DOS PRODUTOS
# =====================================================

st.divider()


st.subheader(
    "📋 Produtos Cadastrados"
)



try:


    produtos = listar_produtos()



except Exception as erro:


    st.error(
        f"Erro ao carregar produtos: {erro}"
    )


    produtos = []





# =====================================================
# AGRUPAR POR CATEGORIA
# =====================================================

produtos_agrupados = {}



for produto in produtos:


    categoria = produto.get(
        "categorias"
    )


    if categoria:


        nome_categoria = categoria.get(
            "nome",
            "Sem Categoria"
        )


    else:


        nome_categoria = "Sem Categoria"



    if nome_categoria not in produtos_agrupados:


        produtos_agrupados[nome_categoria] = []



    produtos_agrupados[nome_categoria].append(
        produto
    )





# =====================================================
# EXIBIÇÃO
# =====================================================

if not produtos:


    st.info(
        "Nenhum produto cadastrado."
    )



else:


    for categoria_nome, lista_produtos in produtos_agrupados.items():


        st.markdown(
            f"""
            <div style="
                background:#8B5A2B;
                color:white;
                padding:8px 12px;
                border-radius:10px;
                margin-top:15px;
                font-weight:bold;
            ">
                📂 {categoria_nome}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.write("")



        for produto in lista_produtos:


            editar, status, excluir = exibir_produto(
                produto,
                categoria_nome
            )



            # =========================================
            # EDITAR
            # =========================================

            if editar:


                st.session_state["produto_editar"] = produto["id"]


                st.switch_page(
                    "pages/10_Editar_Produto.py"
                )



            # =========================================
            # STATUS
            # =========================================

            if status:


                novo_status = not produto.get(
                    "ativo",
                    True
                )


                try:


                    alterar_status_produto(

                        produto["id"],

                        novo_status

                    )


                    if novo_status:


                        st.success(
                            "Produto ativado."
                        )


                    else:


                        st.warning(
                            "Produto desativado."
                        )


                    st.rerun()



                except Exception as erro:


                    st.error(
                        f"Erro ao alterar status: {erro}"
                    )



            # =========================================
            # EXCLUIR
            # =========================================

            if excluir:


                try:


                    excluir_produto(
                        produto["id"]
                    )


                    st.success(
                        "Produto excluído com sucesso."
                    )


                    st.rerun()



                except Exception as erro:


                    st.error(
                        f"Erro ao excluir produto: {erro}"
                    )


            st.write("")
            # =====================================================
# RODAPÉ
# =====================================================

st.divider()


st.caption(
    "🛒 Cadastro de produtos - Doce Cesta Brasília"
)
