import streamlit as st
import pandas as pd


from services.pedido_service import (
    listar_pedidos_ativos,
    excluir_pedido_completo,
    buscar_pedido
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
    page_title="Pedidos",
    page_icon="📋",
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
# CSS COMPACTO
# =====================================================

st.markdown(
"""
<style>


h1{
    font-size:26px !important;
    margin-bottom:5px;
}


h2{
    font-size:18px !important;
}


h3{
    font-size:16px !important;
}


p, div, span{
    font-size:13px;
}


.stButton button{

    font-size:12px;

    padding:3px 8px;

}


[data-testid="stVerticalBlockBorderWrapper"]{

    padding:8px;

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
    "Controle dos pedidos em andamento."
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
    "🔍 Pesquisar cliente"
)



pesquisa = st.text_input(
    "",
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
# FUNÇÃO STATUS
# =====================================================

def status_visual(status):

    if status == "Pago":

        return "🟢 Pago"


    if status == "Recebido":

        return "🟡 Recebido"


    if status == "Desistência":

        return "🔴 Desistência"


    return status



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


        # =================================================
        # BUSCA VALOR ATUALIZADO DO PEDIDO
        # =================================================

        try:

            pedido_atualizado = buscar_pedido(
                pedido["id"]
            )


            if pedido_atualizado:

                pedido = pedido_atualizado


        except Exception:

            pass



        with st.container(border=True):


            col1, col2, col3, col4, col5 = st.columns(
                [3.5,2.5,1.8,1.5,1.2]
            )



            with col1:


                st.write(
                    f"**{pedido.get('cliente_nome','-')}**"
                )


                st.caption(
                    pedido.get(
                        "cliente_telefone",
                        "-"
                    )
                )



            with col2:


                st.write(
                    f"🎁 {pedido.get('cesta_nome','-')}"
                )


                st.caption(
                    f"Entrega: {pedido.get('data_entrega','-')}"
                )



            with col3:


                st.write(
                    status_visual(
                        pedido.get(
                            "status",
                            "-"
                        )
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


                valor_formatado = (

                    f"R$ {valor:,.2f}"

                    .replace(",", "X")

                    .replace(".", ",")

                    .replace("X",".")

                )


                st.write(

                    valor_formatado

                )



            with col5:



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
                          # =====================================================
# STATUS DOS PEDIDOS
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

    permitir_exclusao=(

        usuario["perfil"]

        ==

        "Administrador"

    )

)



# =====================================================
# TOTAL
# =====================================================


st.divider()


st.caption(

    f"Total de pedidos ativos: {len(df)}"

)
