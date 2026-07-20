import streamlit as st


from config.supabase import supabase


from utils.menu import (
    configurar_pagina,
    menu_lateral
)


from utils.permissao import (
    administrador_operador
)



st.set_page_config(
    page_title="Clientes",
    page_icon="👥",
    layout="wide"
)



# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "👥 Clientes"
)


st.write(
    "Clientes que já concluíram pelo menos um pedido."
)


st.divider()



# =====================================================
# BUSCA PEDIDOS ENTREGUES
# =====================================================

try:


    resposta = (

        supabase

        .table("pedidos")

        .select("*")

        .eq(
            "status",
            "Entregue"
        )

        .order(
            "cliente_nome"
        )

        .execute()

    )


    pedidos = resposta.data or []



except Exception as erro:


    st.error(
        f"Erro ao carregar clientes: {erro}"
    )


    st.stop()



# =====================================================
# SEM CLIENTES
# =====================================================

if not pedidos:


    st.info(
        "Nenhum cliente encontrado."
    )


    st.stop()



# =====================================================
# AGRUPA POR CPF
# =====================================================

clientes = {}



for pedido in pedidos:


    cpf = pedido["cliente_cpf"]



    if cpf not in clientes:


        clientes[cpf] = {


            "nome":

            pedido["cliente_nome"],


            "cpf":

            cpf,


            "telefone":

            pedido["cliente_telefone"],


            "quantidade":

            0


        }



    clientes[cpf]["quantidade"] += 1



# =====================================================
# LISTAGEM
# =====================================================

st.subheader(
    "📋 Clientes"
)



cab1, cab2, cab3, cab4, cab5 = st.columns(
    [3,2,2,1,1]
)


with cab1:

    st.write(
        "**Nome**"
    )


with cab2:

    st.write(
        "**CPF**"
    )


with cab3:

    st.write(
        "**Telefone**"
    )


with cab4:

    st.write(
        "**Pedidos**"
    )


with cab5:

    st.write(
        "**Ação**"
    )



st.divider()



for cliente in clientes.values():


    with st.container(border=True):


        col1, col2, col3, col4, col5 = st.columns(
            [3,2,2,1,1]
        )



        with col1:

            st.write(
                cliente["nome"]
            )



        with col2:

            st.write(
                cliente["cpf"]
            )



        with col3:

            st.write(
                cliente["telefone"]
            )



        with col4:

            st.write(
                cliente["quantidade"]
            )



        with col5:


            if st.button(

                "📖",

                key=f"hist_{cliente['cpf']}",

                help="Histórico do Cliente"

            ):


                st.session_state[
                    "cliente_cpf"
                ] = cliente["cpf"]



                st.switch_page(

                    "pages/13_Historico_Cliente.py"

                )



st.divider()



st.caption(

    f"Total de clientes: {len(clientes)}"

)
