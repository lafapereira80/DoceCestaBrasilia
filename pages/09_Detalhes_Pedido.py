import streamlit as st
import urllib.parse

from datetime import datetime


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
# CSS
# =====================================================

st.markdown(

"""
<style>


h1{
    font-size:24px !important;
    margin-bottom:5px;
}


h2{
    font-size:18px !important;
}


h3{
    font-size:15px !important;
}


p,div,span,label{
    font-size:13px;
}


.stButton button{

    border-radius:8px;

    height:35px;

}


[data-testid="stVerticalBlockBorderWrapper"]{

    padding:10px;

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

            data = datetime.strptime(

                data[:10],

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








def limpar_telefone(numero):


    if not numero:

        return ""



    return (

        str(numero)

        .replace(

            "(",

            ""

        )

        .replace(

            ")",

            ""

        )

        .replace(

            "-",

            ""

        )

        .replace(

            " ",

            ""

        )

    )







# =====================================================
# BUSCA PEDIDO
# =====================================================


if "pedido_aberto" not in st.session_state:


    st.warning(

        "Nenhum pedido selecionado."

    )


    st.stop()






pedido_id = st.session_state["pedido_aberto"]





pedido = buscar_pedido(

    pedido_id

)





if not pedido:


    st.error(

        "Pedido não encontrado."

    )


    st.stop()





# =====================================================
# TÍTULO
# =====================================================


st.title(

    "📋 Detalhes do Pedido"

)



st.caption(

    f"Pedido #{pedido.get('id','-')}"

)



st.divider()
# =====================================================
# DADOS DO CLIENTE
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
# DADOS DA ENTREGA
# =====================================================

with st.container(border=True):


    st.subheader(

        "🚚 Dados da Entrega"

    )



    col1, col2, col3 = st.columns(

        [2,2,2]

    )





    # -------------------------------
    # DATA
    # -------------------------------

    with col1:


        data_atual = pedido.get(

            "data_entrega",

            ""

        )



        try:


            data_input = datetime.strptime(

                str(data_atual)[:10],

                "%Y-%m-%d"

            ).date()



        except:


            data_input = datetime.today().date()





        nova_data = st.date_input(

            "Data de entrega",

            value=data_input

        )







    # -------------------------------
    # PERÍODO
    # -------------------------------

    with col2:


        periodos = [

            "Manhã",

            "Tarde",

            "Noite"

        ]



        periodo_atual = pedido.get(

            "periodo_entrega",

            "Tarde"

        )



        if periodo_atual not in periodos:

            periodo_atual = "Tarde"





        novo_periodo = st.selectbox(

            "Período",

            periodos,

            index=periodos.index(

                periodo_atual

            )

        )







    # -------------------------------
    # HORÁRIO COMBINADO
    # -------------------------------

    with col3:


        novo_horario = st.text_input(

            "Horário combinado",

            value=pedido.get(

                "horario_combinado",

                ""

            ),

            placeholder="Ex: 15:30"

        )







    if st.button(

        "💾 Salvar entrega",

        type="primary",

        use_container_width=True

    ):



        dados = {


            "data_entrega":

                nova_data.strftime(

                    "%Y-%m-%d"

                ),



            "periodo_entrega":

                novo_periodo,



            "horario_combinado":

                novo_horario


        }



        sucesso, mensagem = atualizar_pedido(

            pedido_id,

            dados

        )



        if sucesso:


            st.success(

                "Entrega atualizada."

            )


            st.rerun()



        else:


            st.error(

                mensagem

            )



st.divider()
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

            "**🎁 Produtos da cesta**"

        )


        produtos = pedido.get(

            "produtos",

            ""

        )



        if produtos:


            st.text_area(

                "",

                value=produtos,

                height=150,

                disabled=True,

                key="produtos_cesta"

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

            "**➕ Adicionais**"

        )



        try:


            adicionais = listar_adicionais_pedido(

                pedido_id

            )


        except:


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

                    f"• {nome}"

                )


                st.caption(

                    f"Quantidade: {quantidade}"

                )



        else:


            st.info(

                "Nenhum adicional."

            )









# =====================================================
# ENDEREÇO E MENSAGEM
# =====================================================


with st.container(border=True):


    col1, col2 = st.columns(

        [1,1]

    )





    with col1:


        st.subheader(

            "📍 Endereço"

        )



        st.text_area(

            "",

            value=pedido.get(

                "endereco",

                "-"

            ),

            height=110,

            disabled=True,

            key="endereco"

        )






    with col2:


        st.subheader(

            "💌 Mensagem da Cesta"

        )


        st.text_area(

            "",

            value=pedido.get(

                "mensagem",

                "-"

            ),

            height=110,

            disabled=True,

            key="mensagem"

        )








# =====================================================
# OBSERVAÇÃO ADMINISTRATIVA
# =====================================================


with st.container(border=True):


    st.subheader(

        "📝 Observação Administrativa"

    )



    observacao_atual = pedido.get(

        "observacao_admin",

        ""

    )



    nova_observacao = st.text_area(

        "Uso interno (não enviado ao cliente)",

        value=observacao_atual,

        height=100,

        placeholder=(

            "Ex: Cliente pediu entrega após 15h, "

            "tocar campainha, ligar antes..."

        )

    )





    if st.button(

        "💾 Salvar observação",

        use_container_width=True

    ):



        sucesso, mensagem = atualizar_pedido(

            pedido_id,

            {

                "observacao_admin":

                    nova_observacao

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





st.divider()
# =====================================================
# RESUMO FINANCEIRO
# =====================================================

with st.container(border=True):


    st.subheader(

        "💰 Resumo Financeiro"

    )



    col1, col2, col3 = st.columns(

        [1,1,1]

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
# FECHAMENTO DO PEDIDO
# =====================================================

with st.container(border=True):


    st.subheader(

        "✅ Fechamento do Pedido"

    )



    col1, col2 = st.columns(

        [1,2]

    )



    with col1:


        st.write(

            "**Status atual:**"

        )


        st.success(

            pedido.get(

                "status",

                "-"

            )

        )





    with col2:


        st.write(

            "**Entrega combinada:**"

        )



        texto_entrega = (

            f"{formatar_data_br(pedido.get('data_entrega'))}"

            f" - "

            f"{pedido.get('periodo_entrega','-')}"

        )



        if pedido.get(

            "horario_combinado"

        ):


            texto_entrega += (

                f" às "

                f"{pedido.get('horario_combinado')}"

            )



        st.info(

            texto_entrega

        )









# =====================================================
# WHATSAPP
# =====================================================


with st.container(border=True):


    st.subheader(

        "📲 WhatsApp Cliente"

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
        "valor_total",
        0
    )
)}



Obrigado pela preferência! ❤️

"""





    st.text_area(

        "Mensagem",

        mensagem_whatsapp,

        height=220

    )





    telefone = limpar_telefone(

        pedido.get(

            "cliente_telefone",

            ""

        )

    )



    link_whatsapp = (

        "https://wa.me/55"

        +

        telefone

        +

        "?text="

        +

        urllib.parse.quote(

            mensagem_whatsapp

        )

    )





    st.link_button(

        "📲 Abrir WhatsApp",

        link_whatsapp,

        use_container_width=True

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
