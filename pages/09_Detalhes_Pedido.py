import streamlit as st
from datetime import datetime
import urllib.parse


from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido
)


from services.pedido_adicional_service import (
    listar_adicionais_pedido
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

    page_title="Detalhes do Pedido",

    page_icon="📋",

    layout="wide"

)





# =====================================================
# CONTROLE DE ACESSO
# =====================================================

configurar_pagina()

menu_lateral()

administrador_operador()





# =====================================================
# CSS ORGANIZADO
# =====================================================

st.markdown(

"""
<style>


h1{

    font-size:26px !important;

    margin-bottom:10px;

}


h2{

    font-size:19px !important;

}


h3{

    font-size:16px !important;

}


p, div, span{

    font-size:13px;

}


[data-testid="stVerticalBlockBorderWrapper"]{

    padding:12px;

    border-radius:10px;

}



.stButton button{

    border-radius:8px;

    padding:5px 14px;

}



textarea{

    font-size:13px !important;

}


</style>

""",

unsafe_allow_html=True

)








# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================


def formatar_data_br(data):


    if not data:

        return "-"



    try:


        if isinstance(data,str):


            data = data[:10]


            data = datetime.strptime(

                data,

                "%Y-%m-%d"

            )



        return data.strftime(

            "%d/%m/%Y"

        )


    except:


        return str(data)








def formatar_valor(valor):


    try:


        return (

            f"R$ {float(valor):,.2f}"

            .replace(",", "X")

            .replace(".", ",")

            .replace("X",".")

        )


    except:


        return "R$ 0,00"







# =====================================================
# CARREGA PEDIDO
# =====================================================


if "pedido_aberto" not in st.session_state:


    st.warning(

        "Nenhum pedido selecionado."

    )

    st.stop()





pedido_id = st.session_state[

    "pedido_aberto"

]




pedido = buscar_pedido(

    pedido_id

)





if not pedido:


    st.error(

        "Pedido não encontrado."

    )

    st.stop()





# =====================================================
# CABEÇALHO
# =====================================================


st.title(

    "📋 Detalhes do Pedido"

)



st.caption(

    f"Pedido #{pedido.get('id','-')}"

)
# =====================================================
# CLIENTE
# =====================================================

with st.container(border=True):


    st.subheader(
        "👤 Cliente"
    )



    col1, col2, col3 = st.columns(
        [3,2,2]
    )



    with col1:

        st.write(
            f"**{pedido.get('cliente_nome','-')}**"
        )



    with col2:

        st.write(
            f"CPF: {pedido.get('cliente_cpf','-')}"
        )



    with col3:

        st.write(
            f"☎ {pedido.get('cliente_telefone','-')}"
        )









# =====================================================
# ENTREGA
# =====================================================

with st.container(border=True):


    st.subheader(
        "🚚 Dados da Entrega"
    )



    col1, col2, col3 = st.columns(
        [2,2,2]
    )



    # -----------------------------
    # DATA
    # -----------------------------

    with col1:


        data_atual = pedido.get(

            "data_entrega",

            ""

        )



        if isinstance(data_atual,str):

            data_atual = data_atual[:10]




        try:


            valor_data = datetime.strptime(

                data_atual,

                "%Y-%m-%d"

            ).date()


        except:


            valor_data = datetime.today().date()




        nova_data = st.date_input(

            "📅 Data entrega",

            value=valor_data

        )





    # -----------------------------
    # PERÍODO
    # -----------------------------

    with col2:


        opcoes_periodo = [

            "Manhã",

            "Tarde",

            "Noite"

        ]



        periodo_atual = pedido.get(

            "periodo_entrega",

            "Tarde"

        )



        if periodo_atual not in opcoes_periodo:


            periodo_atual = "Tarde"




        novo_periodo = st.selectbox(

            "🕒 Período",

            opcoes_periodo,

            index=opcoes_periodo.index(

                periodo_atual

            )

        )






    # -----------------------------
    # HORÁRIO COMBINADO
    # -----------------------------

    with col3:


        novo_horario = st.text_input(

            "⏰ Horário combinado",

            value=pedido.get(

                "horario_combinado",

                ""

            ),

            placeholder="Ex: 15:30"

        )





    st.caption(

        "Este horário será enviado ao cliente pelo WhatsApp e aparecerá na impressão."

    )






    if st.button(

        "💾 Salvar entrega",

        type="primary",

        use_container_width=True

    ):



        dados = {


            "data_entrega": nova_data.strftime(

                "%Y-%m-%d"

            ),


            "periodo_entrega": novo_periodo,


            "horario_combinado": novo_horario


        }





        sucesso, mensagem = atualizar_pedido(

            pedido_id,

            dados

        )





        if sucesso:


            st.success(

                "Dados da entrega atualizados."

            )


            st.rerun()



        else:


            st.error(

                mensagem

            )
            # =====================================================
# MONTAGEM DO PEDIDO
# =====================================================

with st.container(border=True):


    st.subheader(

        "🎁 Montagem do Pedido"

    )



    col1, col2 = st.columns(

        [2,1]

    )





    # =================================================
    # PRODUTOS DA CESTA
    # =================================================

    with col1:


        st.markdown(

            "**Produtos da cesta**"

        )


        produtos = pedido.get(

            "produtos",

            ""

        )



        if produtos:


            st.text_area(

                "Produtos",

                value=produtos,

                height=150,

                disabled=True,

                label_visibility="collapsed"

            )


        else:


            st.info(

                "Nenhum produto cadastrado."

            )







    # =================================================
    # ADICIONAIS
    # =================================================

    with col2:


        st.markdown(

            "**Adicionais**"

        )



        try:


            adicionais = listar_adicionais_pedido(

                pedido_id

            )


        except Exception:


            adicionais = []





        if adicionais:


            for adicional in adicionais:


                nome = adicional.get(

                    "nome_produto",

                    "-"

                )


                quantidade = adicional.get(

                    "quantidade",

                    1

                )



                st.write(

                    f"☐ {nome}"

                )


                st.caption(

                    f"Quantidade: {quantidade}"

                )



        else:


            st.info(

                "Nenhum adicional."

            )








# =====================================================
# DADOS DE ENTREGA
# =====================================================

with st.container(border=True):


    st.subheader(

        "📍 Informações da Entrega"

    )



    st.text_area(

        "Endereço",

        value=pedido.get(

            "endereco",

            "-"

        ),

        height=90,

        disabled=True

    )








# =====================================================
# MENSAGEM CLIENTE
# =====================================================

with st.container(border=True):


    st.subheader(

        "💌 Mensagem da Cesta"

    )


    st.text_area(

        "Mensagem",

        value=pedido.get(

            "mensagem",

            "-"

        ),

        height=90,

        disabled=True

    )









# =====================================================
# OBSERVAÇÃO ADMINISTRATIVA
# =====================================================

with st.container(border=True):


    st.subheader(

        "📝 Observação Administrativa"

    )



    st.caption(

        "Informação interna da equipe. Não enviada ao cliente."

    )



    observacao = st.text_area(

        "Observação",

        value=pedido.get(

            "observacao_admin",

            ""

        ),

        height=120,

        placeholder=(

            "Ex: Entregar após 15h, "

            "cliente pediu para avisar antes..."

        ),

        label_visibility="collapsed"

    )





    if st.button(

        "💾 Salvar observação",

        key="btn_salvar_observacao",

        use_container_width=True

    ):



        sucesso, mensagem = atualizar_pedido(

            pedido_id,

            {

                "observacao_admin": observacao

            }

        )




        if sucesso:


            st.success(

                "Observação salva."

            )


            st.rerun()



        else:


            st.error(

                mensagem

            )
            # =====================================================
# RESUMO FINANCEIRO
# =====================================================

with st.container(border=True):


    st.subheader(

        "💰 Resumo do Pedido"

    )



    col1, col2, col3 = st.columns(

        [2,2,2]

    )



    with col1:


        st.metric(

            "Frete",

            formatar_valor(

                pedido.get(

                    "valor_frete",

                    0

                )

            )

        )



    with col2:


        st.metric(

            "Valor Total",

            formatar_valor(

                pedido.get(

                    "valor_total",

                    0

                )

            )

        )



    with col3:


        st.metric(

            "Pagamento",

            pedido.get(

                "pagamento",

                "-"

            )

        )









# =====================================================
# WHATSAPP
# =====================================================

with st.container(border=True):


    st.subheader(

        "📲 Mensagem WhatsApp"

    )




    data_entrega = formatar_data_br(

        pedido.get(

            "data_entrega"

        )

    )



    periodo = pedido.get(

        "periodo_entrega",

        "-"

    )



    horario = pedido.get(

        "horario_combinado",

        ""

    )





    mensagem_whatsapp = f"""

Olá {pedido.get('cliente_nome','')}! 😊


Seu pedido está confirmado. ❤️


🎁 Cesta:
{pedido.get('cesta_nome','-')}



📅 Data de entrega:
{data_entrega}



🕒 Período:
{periodo}

"""



    if horario:


        mensagem_whatsapp += f"""

⏰ Horário combinado:
{horario}

"""



    mensagem_whatsapp += f"""

💰 Valor total:
{formatar_valor(
    pedido.get(
        'valor_total',
        0
    )
)}



Obrigado pela preferência! ❤️

"""





    st.text_area(

        "Mensagem para cliente",

        value=mensagem_whatsapp,

        height=220

    )







    link_whatsapp = (


        "https://wa.me/55"

        +

        str(

            pedido.get(

                "cliente_telefone",

                ""

            )

        )

        +

        "?text="

        +

        urllib.parse.quote(

            mensagem_whatsapp

        )

    )





    st.markdown(

        f"""

<a href="{link_whatsapp}" target="_blank">

<button style="

background:#25D366;

color:white;

border:none;

padding:10px 25px;

border-radius:10px;

font-size:15px;

">

📲 Abrir WhatsApp

</button>

</a>

""",

        unsafe_allow_html=True

    )









# =====================================================
# VOLTAR
# =====================================================

st.divider()



if st.button(

    "⬅️ Voltar para pedidos",

    use_container_width=True

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
