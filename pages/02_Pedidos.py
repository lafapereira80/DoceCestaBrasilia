import streamlit as st
import pandas as pd

from services.pedido_service import (
    listar_pedidos_ativos,
    excluir_pedido_completo
)


st.set_page_config(
    page_title="Pedidos",
    page_icon="📋",
    layout="wide"
)


st.title("📋 Gestão de Pedidos")

st.write(
    "Pedidos em andamento do sistema."
)

st.divider()



# ==========================================================
# CARREGA PEDIDOS
# ==========================================================

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



df = pd.DataFrame(pedidos)



# ==========================================================
# ORDENAÇÃO
# ==========================================================

if "created_at" in df.columns:

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    df = df.sort_values(
        "created_at",
        ascending=False
    )



# ==========================================================
# PESQUISA
# ==========================================================

st.subheader("🔍 Pesquisar")


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



# ==========================================================
# MOSTRAR PEDIDOS
# ==========================================================

def mostrar_lista(
    titulo,
    status_filtro,
    permitir_exclusao=False
):


    st.subheader(titulo)



    pedidos_status = df[
        df["status"] == status_filtro
    ]



    if pedidos_status.empty:

        st.info(
            "Nenhum pedido encontrado."
        )

        return



    # Cabeçalho

    cab1, cab2, cab3, cab4, cab5, cab6, cab7 = st.columns(
        [3, 2, 2, 2, 1.5, 1.5, 2]
    )


    with cab1:
        st.write("**Cliente**")

    with cab2:
        st.write("**Telefone**")

    with cab3:
        st.write("**Cesta**")

    with cab4:
        st.write("**Entrega**")

    with cab5:
        st.write("**Status**")

    with cab6:
        st.write("**Valor**")

    with cab7:
        st.write("**Ações**")



    st.divider()



    for _, pedido in pedidos_status.iterrows():


        with st.container(border=True):


            col1, col2, col3, col4, col5, col6, col7 = st.columns(
                [3, 2, 2, 2, 1.5, 1.5, 2]
            )



            with col1:

                st.write(
                    pedido.get(
                        "cliente_nome",
                        "-"
                    )
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



        st.divider()



# ==========================================================
# STATUS
# ==========================================================

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
    permitir_exclusao=True
)



st.caption(
    f"Total de pedidos ativos: {len(df)}"
)
