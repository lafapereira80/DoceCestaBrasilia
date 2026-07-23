import streamlit as st
import urllib.parse

from datetime import datetime


from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido
)


from services.pedido_adicional_service import (
    listar_adicionais_pedido,
    atualizar_valor_adicional
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

    page_title="Detalhes do Pedido",

    page_icon="📋",

    layout="wide"

)



# =====================================================
# ACESSO
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
}

h2{
font-size:18px !important;
}

h3{
font-size:16px !important;
}


p,div,span,label{
font-size:13px;
}


.stButton button{

border-radius:8px;

}


</style>
""",

unsafe_allow_html=True

)





# =====================================================
# FUNÇÕES
# =====================================================


def formatar_data_br(data):


    if not data:

        return "-"



    try:


        return datetime.strptime(

            str(data)[:10],

            "%Y-%m-%d"

        ).strftime(

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





pedido_id = st.session_state["pedido_aberto"]





pedido = buscar_pedido(

    pedido_id

)





if not pedido:


    st.error(

        "Pedido não encontrado."

    )


    st.stop()





st.title(

"📋 Detalhes do Pedido"

)


st.caption(

f"Pedido #{pedido_id}"

)


st.divider()
# =====================================================
# DADOS DO CLIENTE
# =====================================================

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





st.divider()





# =====================================================
# ENTREGA
# =====================================================


st.subheader(

    "🚚 Informações da Entrega"

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


    try:


        data_valor = datetime.strptime(

            str(data_atual)[:10],

            "%Y-%m-%d"

        ).date()



    except:


        data_valor = datetime.today().date()



    nova_data = st.date_input(

        "Data de entrega",

        value=data_valor

    )








# -----------------------------
# PERÍODO
# -----------------------------


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








# -----------------------------
# HORÁRIO COMBINADO
# -----------------------------


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

    "💾 Salvar informações da entrega",

    type="primary"

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

            "Entrega atualizada com sucesso."

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


st.subheader(

    "🎁 Montagem do Pedido"

)



col1, col2 = st.columns(

    [1.5,1]

)





# =====================================================
# PRODUTOS DA CESTA
# =====================================================


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

            "Produtos",

            value=produtos,

            height=160,

            disabled=True,

            key="produtos_pedido"

        )



    else:


        st.info(

            "Nenhum produto cadastrado."

        )







# =====================================================
# ADICIONAIS
# =====================================================


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



            adicional_id = adicional.get(

                "id"

            )



            nome = adicional.get(

                "nome_produto",

                "-"

            )



            quantidade = adicional.get(

                "quantidade",

                1

            )



            valor = adicional.get(

                "valor",

                0

            )





            st.write(

                f"• {nome}"

            )



            st.caption(

                f"Quantidade: {quantidade}"

            )





            # ---------------------------------
            # SOB CONSULTA
            # ---------------------------------


            if adicional.get(

                "preco_consulta",

                False

            ):



                novo_valor = st.number_input(

                    "Valor",

                    min_value=0.0,

                    value=float(valor or 0),

                    step=1.0,

                    key=f"valor_adicional_{adicional_id}"

                )




                if st.button(

                    "💾 Salvar valor",

                    key=f"salvar_valor_{adicional_id}"

                ):



                    sucesso, mensagem = atualizar_valor_adicional(

                        adicional_id,

                        novo_valor

                    )



                    if sucesso:


                        st.success(

                            "Valor atualizado."

                        )


                        st.rerun()



                    else:


                        st.error(

                            mensagem

                        )




            else:


                if valor:


                    st.caption(

                        formatar_valor(valor)

                    )



    else:


        st.info(

            "Nenhum adicional."

        )





st.divider()
# =====================================================
# ENDEREÇO E MENSAGEM
# =====================================================


col1, col2 = st.columns(

    [1,1]

)





with col1:


    st.subheader(

        "📍 Endereço de entrega"

    )


    st.text_area(

        "Endereço",

        value=pedido.get(

            "endereco",

            "-"

        ),

        height=100,

        disabled=True,

        key="endereco_entrega"

    )







with col2:


    st.subheader(

        "💌 Mensagem da cesta"

    )



    st.text_area(

        "Mensagem",

        value=pedido.get(

            "mensagem",

            "-"

        ),

        height=100,

        disabled=True,

        key="mensagem_cesta"

    )






st.divider()





# =====================================================
# OBSERVAÇÃO ADMINISTRATIVA
# =====================================================


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

        "Ex: ligar antes da entrega, "

        "cliente pediu cuidado especial..."

    )

)





if st.button(

    "💾 Salvar observação",

    key="salvar_obs"

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


st.subheader(

    "💰 Resumo Financeiro"

)




col1, col2, col3, col4 = st.columns(

    [1,1,1,1]

)




with col1:


    st.metric(

        "Produtos",

        formatar_valor(

            pedido.get(

                "valor_produtos",

                0

            )

        )

    )






with col2:


    st.metric(

        "Frete",

        formatar_valor(

            pedido.get(

                "valor_frete",

                0

            )

        )

    )







with col3:


    st.metric(

        "Desconto",

        formatar_valor(

            pedido.get(

                "desconto",

                0

            )

        )

    )







with col4:


    st.metric(

        "Total",

        formatar_valor(

            pedido.get(

                "valor_total",

                0

            )

        )

    )






st.write(

    f"💳 Pagamento: **{pedido.get('pagamento','-')}**"

)



st.divider()
# =====================================================
# FECHAMENTO DO PEDIDO
# =====================================================


st.subheader(

    "✅ Fechamento do Pedido"

)



col1, col2 = st.columns(

    [1,2]

)




with col1:


    st.write(

        "**Status:**"

    )


    status = pedido.get(

        "status",

        "-"

    )



    if status == "Pago":


        st.success(

            status

        )


    elif status == "Recebido":


        st.warning(

            status

        )


    else:


        st.info(

            status

        )






with col2:


    st.write(

        "**Entrega combinada:**"

    )


    resumo_entrega = (

        f"{formatar_data_br(pedido.get('data_entrega'))}"

        f" - "

        f"{pedido.get('periodo_entrega','-')}"

    )



    if pedido.get(

        "horario_combinado"

    ):


        resumo_entrega += (

            f" às "

            f"{pedido.get('horario_combinado')}"

        )



    st.info(

        resumo_entrega

    )







st.divider()





# =====================================================
# WHATSAPP
# =====================================================


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


📅 Entrega:
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

    "Mensagem para copiar",

    mensagem_whatsapp,

    height=220

)





telefone = (

    str(

        pedido.get(

            "cliente_telefone",

            ""

        )

    )

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





st.divider()





# =====================================================
# VOLTAR
# =====================================================


if st.button(

    "⬅️ Voltar para pedidos",

    use_container_width=True

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
