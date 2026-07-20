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
# CARREGA PEDIDOS ATIVOS
# Não retorna Entregues
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
# ORDENAÇÃO POR DATA
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

st.subheader("🔍 Pesquisar Pedidos")


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
# FUNÇÃO PARA MOSTRAR CARDS
# ==========================================================

def mostrar_cards(
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



    for _, pedido in pedidos_status.iterrows():


        with st.container(border=True):


            col1, col2, col3, col4 = st.columns(
                [1, 3, 2, 2]
            )



            with col1:

                st.write(
                    f"### #{pedido['id']}"
                )



            with col2:

                st.write(
                    "**Cliente**"
                )

                st.write(
                    pedido.get(
                        "cliente_nome",
                        "-"
                    )
                )



            with col3:

                st.write(
                    "**Cesta**"
                )

                st.write(
                    pedido.get(
                        "cesta_nome",
                        "-"
                    )
                )



            with col4:

                st.write(
                    "**Entrega**"
                )

                st.write(
                    pedido.get(
                        "data_entrega",
                        "-"
                    )
                )



            st.divider()



            col1, col2, col3 = st.columns(3)



            with col1:

                st.write(
                    "📌 Status"
                )

                st.write(
                    pedido.get(
                        "status",
                        "-"
                    )
                )



            with col2:

                st.write(
                    "📞 Telefone"
                )

                st.write(
                    pedido.get(
                        "cliente_telefone",
                        "-"
                    )
                )



            with col3:

                valor = float(
                    pedido.get(
                        "valor_total",
                        0
                    )
                    or 0
                )

                st.write(
                    "💰 Valor"
                )

                st.write(
                    f"R$ {valor:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X",".")
                )



            st.divider()



            col1, col2 = st.columns(2)



            with col1:

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



            with col2:


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



        st.divider()



# ==========================================================
# CARDS DE STATUS
# ==========================================================


mostrar_cards(
    "📥 Pedidos Recebidos",
    "Recebido"
)



mostrar_cards(
    "💰 Pedidos Pagos",
    "Pago"
)



mostrar_cards(
    "❌ Desistências",
    "Desistência",
    permitir_exclusao=True
)



# ==========================================================
# RODAPÉ
# ==========================================================

st.caption(
    f"Total de pedidos ativos: {len(df)}"
)
