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

h1{
    font-size:26px !important;
}


h2{
    font-size:20px !important;
}


div[data-testid="stVerticalBlockBorderWrapper"]{

    border-radius:12px;

    padding:12px;

    margin-bottom:18px;

}


.stButton button{

    font-size:13px;

    padding:5px 10px;

}


p, span, div{

    font-size:13px;

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
    "🔍 Pesquisa"
)


pesquisa = st.text_input(

    "Nome do cliente",

    placeholder="Digite o nome do cliente..."

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
# FUNÇÃO LISTAGEM
# =====================================================

def mostrar_lista(
    titulo,
    status_filtro,
    permitir_exclusao=False
):


    st.markdown(
        f"## {titulo}"
    )


    pedidos_status = df[
        df["status"] == status_filtro
    ]



    if pedidos_status.empty:

        st.info(
            "Nenhum pedido encontrado."
        )

        return



    st.caption(
        f"{len(pedidos_status)} pedido(s)"
    )



    for _, pedido in pedidos_status.iterrows():



        with st.container(border=True):


            col1,col2,col3,col4 = st.columns(
                [3,2,2,2]
            )



            with col1:

                st.markdown(
                    f"**👤 {pedido.get('cliente_nome','-')}**"
                )

                st.write(
                    pedido.get(
                        "cliente_telefone",
                        "-"
                    )
                )



            with col2:

                st.markdown(
                    "**🎁 Cesta**"
                )

                st.write(
                    pedido.get(
                        "cesta_nome",
                        "-"
                    )
                )



            with col3:

                st.markdown(
                    "**📅 Entrega**"
                )

                st.write(
                    pedido.get(
                        "data_entrega",
                        "-"
                    )
                )



            with col4:


                valor = float(

                    pedido.get(
                        "valor_total",
                        0
                    )

                    or 0

                )


                st.markdown(
                    "**💰 Valor**"
                )


                st.write(

                    f"R$ {valor:,.2f}"

                    .replace(",", "X")

                    .replace(".", ",")

                    .replace("X",".")

                )



            st.divider()



            col1,col2,col3 = st.columns(
                [2,2,6]
            )



            with col1:

                st.markdown(
                    "**Status**"
                )

                if pedido["status"] == "Pago":

                    st.success(
                        "💰 Pago"
                    )

                elif pedido["status"] == "Recebido":

                    st.warning(
                        "📥 Recebido"
                    )

                else:

                    st.error(
                        pedido["status"]
                    )



            with col2:


                if st.button(

                    "👁️ Abrir Pedido",

                    key=f"abrir_{pedido['id']}",

                    use_container_width=True

                ):


                    st.session_state[
                        "pedido_aberto"
                    ] = pedido["id"]


                    st.switch_page(
                        "pages/09_Detalhes_Pedido.py"
                    )



            with col3:


                if permitir_exclusao:


                    if st.button(

                        "🗑️ Excluir Pedido",

                        key=f"excluir_{pedido['id']}",

                        use_container_width=True

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



        st.write("")



# =====================================================
# LISTAS POR STATUS
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



st.divider()


st.caption(

    f"Total de pedidos ativos: {len(df)}"

)
