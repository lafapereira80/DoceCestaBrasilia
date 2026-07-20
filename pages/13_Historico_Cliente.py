import streamlit as st


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

    page_title="Histórico do Cliente",

    page_icon="👤",

    layout="wide"

)



# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()



# =====================================================
# VERIFICA CLIENTE SELECIONADO
# =====================================================

if "cliente_cpf" not in st.session_state:


    st.error(
        "Nenhum cliente selecionado."
    )


    if st.button(
        "⬅ Voltar"
    ):


        st.switch_page(
            "pages/03_Clientes.py"
        )


    st.stop()



cpf = st.session_state["cliente_cpf"]



# =====================================================
# BUSCA PEDIDOS ENTREGUES
# =====================================================

try:


    resposta = (

        supabase

        .table("pedidos")

        .select("*")

        .eq(
            "cliente_cpf",
            cpf
        )

        .eq(
            "status",
            "Entregue"
        )

        .order(
            "created_at",
            desc=True
        )

        .execute()

    )


    pedidos = resposta.data or []



except Exception as erro:


    st.error(

        f"Erro ao carregar histórico: {erro}"

    )


    st.stop()



if not pedidos:


    st.warning(

        "Cliente sem pedidos entregues."

    )


    st.stop()



cliente = pedidos[0]



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "👤 Histórico do Cliente"
)


st.divider()



# =====================================================
# RESUMO CLIENTE
# =====================================================

total_pedidos = len(pedidos)



valor_total = sum(

    float(
        p.get(
            "valor_total"
        )
        or 0
    )

    for p in pedidos

)



ticket_medio = (

    valor_total / total_pedidos

    if total_pedidos > 0

    else 0

)



ultima_compra = pedidos[0].get(

    "data_entrega",

    "-"

)



st.subheader(
    "👤 Dados do Cliente"
)



col1,col2 = st.columns(2)



with col1:


    st.write("**Nome**")

    st.write(
        cliente.get(
            "cliente_nome",
            "-"
        )
    )


    st.write("**CPF**")

    st.write(
        cliente.get(
            "cliente_cpf",
            "-"
        )
    )



with col2:


    st.write("**Telefone**")

    st.write(
        cliente.get(
            "cliente_telefone",
            "-"
        )
    )



st.divider()



# =====================================================
# RESUMO FINANCEIRO
# =====================================================

st.subheader(
    "📊 Resumo"
)



c1,c2,c3,c4 = st.columns(4)



with c1:


    st.metric(

        "Pedidos",

        total_pedidos

    )



with c2:


    st.metric(

        "Valor Gasto",

        f"R$ {valor_total:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )



with c3:


    st.metric(

        "Ticket Médio",

        f"R$ {ticket_medio:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )



with c4:


    st.metric(

        "Última Compra",

        str(
            ultima_compra
        )

    )



st.divider()



# =====================================================
# HISTÓRICO
# =====================================================

st.subheader(
    "📋 Histórico de Compras"
)



st.info(

    f"Total de compras entregues encontradas: {len(pedidos)}"

)



for i,pedido in enumerate(pedidos):


    with st.container(border=True):


        st.markdown(

            f"## 🎁 {pedido.get('cesta_nome','-')}"

        )


        st.caption(

            f"Pedido {i+1}"

        )



        col1,col2,col3 = st.columns(3)



        with col1:


            st.write("**Data entrega**")

            st.write(

                pedido.get(
                    "data_entrega",
                    "-"
                )

            )



        with col2:


            st.write("**Status**")

            st.write(

                pedido.get(
                    "status",
                    "-"
                )

            )



        with col3:


            st.write("**Pagamento**")

            st.write(

                pedido.get(
                    "pagamento",
                    "-"
                )

            )



        st.divider()



        st.write(
            "### 📦 Produtos da Cesta"
        )


        produtos = pedido.get(
            "produtos",
            ""
        )


        if produtos:


            st.code(
                produtos
            )


        else:


            st.info(
                "Nenhum produto registrado."
            )



        st.write(
            "### 🎀 Adicionais"
        )



        adicionais = pedido.get(
            "adicionais",
            ""
        )



        if adicionais:


            st.success(
                adicionais
            )


        else:


            st.info(
                "Nenhum adicional."
            )



        st.write(
            "### 💌 Mensagem"
        )



        mensagem = pedido.get(
            "mensagem",
            ""
        )



        if mensagem:


            st.text_area(

                "",

                value=mensagem,

                disabled=True,

                height=90,

                key=f"msg_{pedido['id']}"

            )


        else:


            st.info(
                "Sem mensagem."
            )



        st.write(
            "### ✨ Pedido Especial"
        )



        especial = pedido.get(
            "pedido_especial",
            ""
        )



        if especial:


            st.text_area(

                "",

                value=especial,

                disabled=True,

                height=90,

                key=f"esp_{pedido['id']}"

            )


        else:


            st.info(
                "Nenhum pedido especial."
            )



        st.write(
            "### 📍 Endereço"
        )


        st.text_area(

            "",

            value=pedido.get(
                "endereco",
                ""
            ),

            disabled=True,

            height=90,

            key=f"end_{pedido['id']}"

        )



        col1,col2 = st.columns(2)



        with col1:


            st.metric(

                "Frete",

                f"R$ {float(pedido.get('valor_frete') or 0):,.2f}"

                .replace(",", "X")

                .replace(".", ",")

                .replace("X",".")

            )



        with col2:


            st.metric(

                "Valor Total",

                f"R$ {float(pedido.get('valor_total') or 0):,.2f}"

                .replace(",", "X")

                .replace(".", ",")

                .replace("X",".")

            )



        st.write(
            "### 📷 Fotos"
        )



        if pedido.get(
            "foto_excluida"
        ):


            st.success(

                "Fotos removidas automaticamente após conclusão do pedido."

            )


        else:


            st.info(

                "Fotos ainda disponíveis."

            )



    st.divider()



# =====================================================
# VOLTAR
# =====================================================

if st.button(

    "⬅ Voltar para Clientes",

    use_container_width=True,

    key="voltar_clientes"

):


    st.session_state.pop(

        "cliente_cpf",

        None

    )


    st.switch_page(

        "pages/03_Clientes.py"

    )
