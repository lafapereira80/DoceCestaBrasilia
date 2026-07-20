import streamlit as st
import pandas as pd


from services.pedido_service import (
    listar_pedidos_ativos,
    excluir_pedido_completo
)


from utils.menu import (
    configurar_pagina,
    menu_lateral
)


from utils.permissao import (
    administrador_operador
)



st.set_page_config(
    page_title="Pedidos",
    page_icon="📋",
    layout="wide"
)



# =====================================================
# CONFIGURAÇÕES
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
    font-size:18px !important;
}


p, div, span{
    font-size:13px;
}


.stButton button{

    font-size:12px;

    padding:4px 8px;

}



.card-recebido{

    background:#fff8dc;

    border-left:6px solid #e0b000;

    padding:12px;

    border-radius:10px;

    margin-bottom:12px;

}



.card-pago{

    background:#e9f7ef;

    border-left:6px solid #28a745;

    padding:12px;

    border-radius:10px;

    margin-bottom:12px;

}



.card-desistencia{

    background:#fdecea;

    border-left:6px solid #dc3545;

    padding:12px;

    border-radius:10px;

    margin-bottom:12px;

}


</style>
""",
unsafe_allow_html=True
)



# =====================================================
# TÍTULO
# =====================================================

st.title(
    "📋 Gestão de Pedidos"
)


st.caption(
    "Pedidos em andamento do sistema."
)


st.divider()



# =====================================================
# CARREGA PEDIDOS
# =====================================================

try:

    pedidos = listar_pedidos_ativos()


except Exception as erro:

    st.error(
        f"Erro ao carregar pedidos: {erro}"
    )

    st.stop()



if not pedidos:

    st.info(
        "Nenhum pedido em andamento."
    )

    st.stop()



df = pd.DataFrame(
    pedidos
)



# =====================================================
# ORDENAÇÃO
# =====================================================

if "created_at" in df.columns:


    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )


    df = df.sort_values(
        "created_at",
        ascending=False
    )



# =====================================================
# PESQUISA
# =====================================================

st.subheader(
    "🔍 Pesquisar"
)


pesquisa = st.text_input(

    "Nome do cliente",

    placeholder="Digite o nome..."

)



if pesquisa.strip():

    df = df[
        df["cliente_nome"]
        .fillna("")
        .str.contains(
            pesquisa,
            case=False
        )
    ]



# =====================================================
# LISTAGEM
# =====================================================

def mostrar_lista(
    titulo,
    status_filtro,
    permitir_exclusao=False
):


    st.subheader(
        titulo
    )



    pedidos_status = df[
        df["status"] == status_filtro
    ]



    if pedidos_status.empty:

        st.info(
            "Nenhum pedido encontrado."
        )

        return



    for _, pedido in pedidos_status.iterrows():



        if status_filtro == "Recebido":

            classe = "card-recebido"


        elif status_filtro == "Pago":

            classe = "card-pago"


        else:

            classe = "card-desistencia"




        st.markdown(

            f"<div class='{classe}'>",

            unsafe_allow_html=True

        )



        col1, col2, col3, col4, col5, col6, col7 = st.columns(
            [3,2,2,2,1.5,1.5,2]
        )



        with col1:

            st.write(
                f"**{pedido.get('cliente_nome','-')}**"
            )



        with col2:

            st.write(
                pedido.get(
                    "cliente_telefone",
                    "-"
                )
            )



        with col3:

            st.write(
                pedido.get(
                    "cesta_nome",
                    "-"
                )
            )



        with col4:

            st.write(
                pedido.get(
                    "data_entrega",
                    "-"
                )
            )



        with col5:

            st.write(
                pedido.get(
                    "status",
                    "-"
                )
            )



        with col6:


            valor = float(

                pedido.get(
                    "valor_total",
                    0
                )

                or 0

            )


            st.write(

                f"R$ {valor:,.2f}"

                .replace(",", "X")

                .replace(".", ",")

                .replace("X",".")

            )



        with col7:


            if st.button(

                "👁️",

                key=f"abrir_{pedido['id']}",

                help="Abrir pedido"

            ):


                st.session_state[
                    "pedido_aberto"
                ] = pedido["id"]


                st.switch_page(

                    "pages/09_Detalhes_Pedido.py"

                )




            if permitir_exclusao:


                if st.button(

                    "🗑️",

                    key=f"excluir_{pedido['id']}",

                    help="Excluir pedido"

                ):


                    sucesso, mensagem = (

                        excluir_pedido_completo(

                            pedido["id"]

                        )

                    )



                    if sucesso:


                        st.success(
                            mensagem
                        )

                        st.rerun()



                    else:

                        st.error(
                            mensagem
                        )



        st.markdown(

            "</div>",

            unsafe_allow_html=True

        )


        st.write("")



# =====================================================
# STATUS
# =====================================================


mostrar_lista(

    "📥 Pedidos Recebidos",

    "Recebido"

)



mostrar_lista(

    "💰 Pedidos Pagos",

    "Pago"

)



mostrar_lista(

    "❌ Desistências",

    "Desistência",

    permitir_exclusao=

    st.session_state.usuario["perfil"]

    ==

    "Administrador"

)



st.caption(

    f"Total de pedidos ativos: {len(df)}"

)
