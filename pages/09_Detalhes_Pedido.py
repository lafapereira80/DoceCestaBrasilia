import streamlit as st
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
}

h2{
    font-size:18px !important;
}

p,div,span{
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
# FUNÇÕES AUXILIARES
# =====================================================


def formatar_data_br(data):

    """
    Converte datas para padrão brasileiro
    """

    if not data:

        return "-"



    try:

        if isinstance(data, str):

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
# BUSCA PEDIDO
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

st.subheader(

    "🚚 Dados da Entrega"

)



col1, col2, col3 = st.columns(

    [2,2,2]

)



with col1:


    data_atual = pedido.get(

        "data_entrega",

        ""

    )



    if isinstance(data_atual,str):

        data_atual = data_atual[:10]



    nova_data = st.date_input(

        "Data de entrega",

        value=(

            datetime.strptime(

                data_atual,

                "%Y-%m-%d"

            ).date()

            if data_atual

            else datetime.today().date()

        )

    )



with col2:


    periodo_atual = pedido.get(

        "periodo_entrega",

        ""

    )



    opcoes_periodo = [

        "Manhã",

        "Tarde",

        "Noite"

    ]



    if periodo_atual not in opcoes_periodo:

        periodo_atual = "Tarde"



    novo_periodo = st.selectbox(

        "Período",

        opcoes_periodo,

        index=opcoes_periodo.index(

            periodo_atual

        )

    )



with col3:


    horario_atual = pedido.get(

        "horario_combinado",

        ""

    )



    novo_horario = st.text_input(

        "Horário combinado",

        value=horario_atual,

        placeholder="Ex: 15:30"

    )







# =====================================================
# SALVAR ALTERAÇÃO ENTREGA
# =====================================================

if st.button(

    "💾 Salvar dados da entrega",

    type="primary"

):



    dados_atualizacao = {


        "data_entrega": nova_data.strftime(

            "%Y-%m-%d"

        ),


        "periodo_entrega": novo_periodo,


        "horario_combinado": novo_horario


    }



    sucesso, mensagem = atualizar_pedido(

        pedido_id,

        dados_atualizacao

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





st.divider()
# =====================================================
# PRODUTOS DA CESTA
# =====================================================

st.subheader(

    "🎁 Montagem do Pedido"

)



produtos = pedido.get(

    "produtos",

    ""

)



if produtos:


    st.text_area(

        "Produtos da cesta",

        value=produtos,

        height=120,

        disabled=True

    )


else:


    st.info(

        "Nenhum produto cadastrado."

    )





# =====================================================
# ADICIONAIS
# =====================================================

st.subheader(

    "➕ Adicionais"

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

            f"☐ {nome}  (Qtd: {quantidade})"

        )


else:


    st.info(

        "Nenhum adicional."

    )





st.divider()





# =====================================================
# ENDEREÇO
# =====================================================

st.subheader(

    "📍 Endereço de entrega"

)



st.text_area(

    "Endereço",

    value=pedido.get(

        "endereco",

        "-"

    ),

    height=80,

    disabled=True

)





# =====================================================
# MENSAGEM DO CLIENTE
# =====================================================

st.subheader(

    "💌 Mensagem da cesta"

)



st.text_area(

    "Mensagem",

    value=pedido.get(

        "mensagem",

        "-"

    ),

    height=80,

    disabled=True

)





# =====================================================
# OBSERVAÇÕES ADMINISTRATIVAS
# =====================================================

st.subheader(

    "📝 Observações administrativas"

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

        "Ex: Cliente pediu para tocar campainha, "

        "entregar somente após 15h..."

    )

)





if st.button(

    "💾 Salvar observações",

    key="salvar_observacao"

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

        "Total",

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





st.divider()





# =====================================================
# MENSAGEM WHATSAPP
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


Seu pedido está confirmado.


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
{formatar_valor(pedido.get('valor_total',0))}


Obrigado pela preferência! ❤️
"""





st.text_area(

    "Copiar mensagem",

    mensagem_whatsapp,

    height=250

)





# =====================================================
# BOTÃO WHATSAPP
# =====================================================

import urllib.parse



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

padding:8px 20px;

border-radius:8px;

font-size:14px;

">

📲 Abrir WhatsApp

</button>

</a>

""",

unsafe_allow_html=True

)





st.divider()





# =====================================================
# VOLTAR
# =====================================================

if st.button(

    "⬅️ Voltar para pedidos"

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
