import streamlit as st
import json
import urllib.parse


from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido,
    atualizar_anotacao_pedido
)


from services.pedido_adicional_service import (
    listar_adicionais_pedido
)


from services.foto_service import (
    listar_fotos
)


from services.cesta_service import (
    buscar_cesta,
    listar_cestas
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

configurar_pagina()

menu_lateral()

administrador_operador()


usuario = st.session_state.usuario



# =====================================================
# CSS PADRÃO VISUAL COM CARDS
# =====================================================

st.markdown(
"""
<style>


/* ==========================================
   CONFIGURAÇÃO GERAL
========================================== */

.block-container{

    padding-top:0.8rem !important;

    padding-bottom:1rem !important;

    max-width:1100px;

}



html,
body,
p,
span,
label,
div{

    font-family: Arial, sans-serif !important;

    font-size:12px !important;

}



/* ==========================================
   TÍTULOS
========================================== */

h1{

    font-size:24px !important;

    font-weight:700 !important;

    margin-bottom:4px !important;

}


h2{

    font-size:18px !important;

    font-weight:700 !important;

}


h3{

    font-size:16px !important;

    font-weight:700 !important;

}



/* ==========================================
   ESPAÇAMENTO
========================================== */

div[data-testid="stVerticalBlock"]{

    gap:0.35rem !important;

}



.element-container{

    margin-bottom:0.2rem !important;

}



/* ==========================================
   COLUNAS
========================================== */

div[data-testid="column"]{

    padding-left:0.25rem !important;

    padding-right:0.25rem !important;

}



/* ==========================================
   BOTÕES
========================================== */

.stButton button{

    font-size:14px !important;

    font-weight:600 !important;

    padding:8px 14px !important;

    border-radius:10px !important;

}



/* ==========================================
   INPUTS
========================================== */

input,
textarea,
select{

    font-size:14px !important;

}



/* ==========================================
   CARDS PADRÃO
========================================== */

.card{

    background:#ffffff;

    border:1px solid #dfcdbb;

    border-radius:16px;

    padding:14px 16px;

    margin-bottom:12px;

}



.card-title{

    font-size:16px;

    font-weight:700;

    margin-bottom:10px;

    color:#5a3b28;

}



/* CARD EDIÇÃO */

.edit-card{

    background:#faf7f3;

    border:1px solid #dcc8b7;

    border-radius:16px;

    padding:16px;

}



/* CARD RESUMO */

.resumo-card{

    background:#fff8ef;

    border:1px solid #e6d1bb;

    border-radius:16px;

    padding:16px;

}



.resumo-card table{

    width:100%;

}



.resumo-card td{

    padding:5px 0;

}



/* ==========================================
   TEXTOS INTERNOS
========================================== */

.info-label{

    font-weight:700;

    color:#555;

}



.info-value{

    margin-bottom:6px;

}



/* ==========================================
   DIVISOR
========================================== */

hr{

    margin-top:8px !important;

    margin-bottom:8px !important;

}



</style>
""",
unsafe_allow_html=True
)




# =====================================================
# VALIDA PEDIDO ABERTO
# =====================================================


if "pedido_aberto" not in st.session_state:


    st.error(
        "Nenhum pedido selecionado."
    )


    if st.button("⬅ Voltar"):


        st.switch_page(
            "pages/02_Pedidos.py"
        )


    st.stop()



pedido_id = st.session_state["pedido_aberto"]



# =====================================================
# BUSCA PEDIDO
# =====================================================

try:

    pedido = buscar_pedido(
        pedido_id
    )


except Exception as erro:

    st.error(
        f"Erro ao carregar pedido: {erro}"
    )

    st.stop()



if not pedido:

    st.error(
        "Pedido não encontrado."
    )

    st.stop()



# =====================================================
# BUSCA ADICIONAIS
# =====================================================

try:

    adicionais_pedido = listar_adicionais_pedido(
        pedido["id"]
    )


except:

    adicionais_pedido = []



# =====================================================
# CONTROLE DE EDIÇÃO
# =====================================================

if "editar_pedido" not in st.session_state:

    st.session_state.editar_pedido = False



# =====================================================
# VALORES SOB CONSULTA
# =====================================================

itens_consulta_salvos = pedido.get(
    "itens_consulta",
    {}
)



if isinstance(
    itens_consulta_salvos,
    str
):

    try:

        itens_consulta_salvos = json.loads(
            itens_consulta_salvos
        )

    except:

        itens_consulta_salvos = {}



if not isinstance(
    itens_consulta_salvos,
    dict
):

    itens_consulta_salvos = {}



# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================


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

    return (
        str(numero)
        .replace("(","")
        .replace(")","")
        .replace("-","")
        .replace(" ","")
    )



def formatar_data(data):

    if not data:

        return "-"


    try:

        ano,mes,dia = str(data)[:10].split("-")

        return f"{dia}/{mes}/{ano}"


    except:

        return str(data)
        # =====================================================
# GERA WHATSAPP
# =====================================================


def gerar_whatsapp(
    pedido,
    adicionais,
    valor_final
):


    itens_consulta = pedido.get(
        "itens_consulta",
        {}
    )


    if isinstance(
        itens_consulta,
        str
    ):

        try:

            itens_consulta = json.loads(
                itens_consulta
            )

        except:

            itens_consulta = {}



    lista_adicionais = []



    for item in adicionais:


        nome = item.get(
            "nome_produto",
            "-"
        )


        valor = item.get(
            "valor_unitario"
        )



        if valor is not None:


            lista_adicionais.append(
                f"• {nome} - {formatar_valor(valor)}"
            )


        else:


            valor_manual = itens_consulta.get(
                nome,
                0
            )


            if valor_manual:


                lista_adicionais.append(
                    f"• {nome} - {formatar_valor(valor_manual)}"
                )


            else:


                lista_adicionais.append(
                    f"• {nome} (sob consulta)"
                )



    texto = (

        f"🎁 *Doce Cesta Brasília*\n\n"

        f"Olá {pedido.get('cliente_nome','')}!\n\n"

        f"🎀 Cesta: {pedido.get('cesta_nome','-')}\n\n"

        f"🛒 Produtos:\n"

        f"{pedido.get('produtos','-')}\n\n"

        f"🎀 Adicionais:\n"

        f"{chr(10).join(lista_adicionais)}\n\n"

        f"📍 Entrega:\n"

        f"Data: {formatar_data(pedido.get('data_entrega'))}\n"

        f"Período: {pedido.get('periodo_entrega','-')}\n"

        f"Horário: {pedido.get('horario_combinado','-')}\n\n"

        f"💳 Pagamento: {pedido.get('pagamento','-')}\n"

        f"💰 Valor Final: {formatar_valor(valor_final)}\n\n"

        f"Obrigado! ❤️"

    )


    telefone = limpar_telefone(

        pedido.get(
            "cliente_telefone",
            ""
        )

    )


    return (

        f"https://wa.me/55{telefone}?text={urllib.parse.quote(texto)}"

    )



# =====================================================
# CABEÇALHO
# =====================================================


st.title(
    "📋 Detalhes do Pedido"
)



st.caption(

    f"Pedido #{pedido.get('id')} | Status: {pedido.get('status','-')}"

)



# =====================================================
# BOTÃO ALTERAR PEDIDO
# =====================================================


if st.button(

    "✏️ Alterar Pedido",

    use_container_width=True

):


    st.session_state.editar_pedido = (

        not st.session_state.editar_pedido

    )



# =====================================================
# CARD - EDIÇÃO DO PEDIDO
# =====================================================


if st.session_state.editar_pedido:


    st.markdown(
        '<div class="edit-card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">✏️ Editando Pedido</div>',
        unsafe_allow_html=True
    )



    novo_nome = st.text_input(

        "👤 Nome",

        value=pedido.get(
            "cliente_nome",
            ""
        )

    )



    novo_telefone = st.text_input(

        "📱 Telefone",

        value=pedido.get(
            "cliente_telefone",
            ""
        )

    )



    try:

        cestas = listar_cestas()


        nomes_cestas = [

            c.get(
                "nome",
                ""
            )

            for c in cestas

        ]


    except:


        nomes_cestas = []



    cesta_atual = pedido.get(
        "cesta_nome",
        ""
    )



    if nomes_cestas:


        if cesta_atual in nomes_cestas:

            indice_cesta = nomes_cestas.index(
                cesta_atual
            )

        else:

            indice_cesta = 0



        nova_cesta = st.selectbox(

            "🎁 Cesta",

            nomes_cestas,

            index=indice_cesta

        )


    else:

        nova_cesta = cesta_atual



    nova_mensagem = st.text_area(

        "💌 Mensagem",

        value=pedido.get(
            "mensagem",
            ""
        ),

        height=80

    )



    novo_especial = st.text_area(

        "✨ Pedido Especial",

        value=pedido.get(
            "pedido_especial",
            ""
        ),

        height=80

    )



    novo_endereco = st.text_area(

        "📍 Endereço",

        value=pedido.get(
            "endereco",
            ""
        ),

        height=100

    )



    col_salvar, col_cancelar = st.columns(2)



    with col_salvar:


        if st.button(

            "💾 Salvar Alterações",

            use_container_width=True,

            type="primary"

        ):


            dados = {

                "cliente_nome":
                    novo_nome,

                "cliente_telefone":
                    novo_telefone,

                "cesta_nome":
                    nova_cesta,

                "mensagem":
                    nova_mensagem,

                "pedido_especial":
                    novo_especial,

                "endereco":
                    novo_endereco

            }



            atualizar_pedido(

                pedido["id"],

                dados

            )


            st.success(
                "Pedido alterado com sucesso!"
            )


            st.session_state.editar_pedido = False


            st.rerun()



    with col_cancelar:


        if st.button(

            "❌ Cancelar",

            use_container_width=True

        ):


            st.session_state.editar_pedido = False


            st.rerun()



    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )




# =====================================================
# CARD - CLIENTE
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">👤 Cliente</div>',
unsafe_allow_html=True
)



col1, col2, col3 = st.columns(3)



with col1:

    st.markdown(
        f"""
        <div class="info-label">Nome</div>
        <div class="info-value">
        {pedido.get('cliente_nome','-')}
        </div>
        """,
        unsafe_allow_html=True
    )



with col2:

    st.markdown(
        f"""
        <div class="info-label">CPF</div>
        <div class="info-value">
        {pedido.get('cliente_cpf','-')}
        </div>
        """,
        unsafe_allow_html=True
    )



with col3:

    st.markdown(
        f"""
        <div class="info-label">Telefone</div>
        <div class="info-value">
        {pedido.get('cliente_telefone','-')}
        </div>
        """,
        unsafe_allow_html=True
    )



st.markdown(
"</div>",
unsafe_allow_html=True
)



# =====================================================
# CARD - INFORMAÇÕES DO PEDIDO
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">🎁 Pedido</div>',
unsafe_allow_html=True
)



col1, col2, col3, col4 = st.columns(4)



with col1:

    st.markdown(
        f"""
        <div class="info-label">Cesta</div>
        <div class="info-value">
        {pedido.get('cesta_nome','-')}
        </div>
        """,
        unsafe_allow_html=True
    )



with col2:

    st.markdown(
        f"""
        <div class="info-label">Pagamento</div>
        <div class="info-value">
        {pedido.get('pagamento','-')}
        </div>
        """,
        unsafe_allow_html=True
    )



with col3:

    st.markdown(
        f"""
        <div class="info-label">Entrega</div>
        <div class="info-value">
        {formatar_data(pedido.get('data_entrega'))}
        </div>
        """,
        unsafe_allow_html=True
    )



with col4:

    st.markdown(
        f"""
        <div class="info-label">Período</div>
        <div class="info-value">
        {pedido.get('periodo_entrega','-')}
        </div>
        """,
        unsafe_allow_html=True
    )



st.markdown(
"</div>",
unsafe_allow_html=True
)
# =====================================================
# CARD - PRODUTOS E ADICIONAIS
# =====================================================


col1, col2 = st.columns(2)



# =====================================================
# CARD PRODUTOS
# =====================================================


with col1:


    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">🛒 Produtos da Cesta</div>',
        unsafe_allow_html=True
    )


    produtos = pedido.get(
        "produtos",
        ""
    )



    if produtos:


        for item in produtos.split("\n"):


            st.write(
                f"• {item}"
            )


    else:


        st.info(
            "Nenhum produto informado."
        )



    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )




# =====================================================
# CARD ADICIONAIS
# =====================================================


with col2:


    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">🎀 Adicionais</div>',
        unsafe_allow_html=True
    )



    valor_adicionais = 0.0

    valor_consulta = 0.0


    itens_consulta = {}





    if adicionais_pedido:



        for adicional in adicionais_pedido:


            nome = adicional.get(
                "nome_produto",
                "-"
            )


            valor = adicional.get(
                "valor_unitario"
            )



            if valor is not None:


                valor = float(valor)


                valor_adicionais += valor


                st.write(
                    f"• {nome} - {formatar_valor(valor)}"
                )



            else:


                st.write(
                    f"• {nome}"
                )



                valor_salvo = float(

                    itens_consulta_salvos.get(

                        nome,

                        0

                    )

                    or 0

                )



                valor_digitado = st.number_input(

                    "Definir valor",

                    min_value=0.0,

                    value=valor_salvo,

                    step=1.0,

                    key=f"consulta_{nome}"

                )



                itens_consulta[nome] = valor_digitado



                if valor_digitado > 0:


                    valor_consulta += valor_digitado


                    valor_adicionais += valor_digitado




    else:


        st.info(
            "Nenhum adicional selecionado."
        )



    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )





# =====================================================
# CARD TOTAIS ADICIONAIS
# =====================================================


col1, col2 = st.columns(2)



with col1:


    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">🎀 Total Adicionais</div>',
        unsafe_allow_html=True
    )


    st.success(

        formatar_valor(
            valor_adicionais
        )

    )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )




with col2:


    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">⚠️ Valores Sob Consulta</div>',
        unsafe_allow_html=True
    )


    st.info(

        formatar_valor(
            valor_consulta
        )

    )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )





# =====================================================
# CARD MENSAGEM E PEDIDO ESPECIAL
# =====================================================


col1, col2 = st.columns(2)




with col1:


    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">💌 Mensagem da Cesta</div>',
        unsafe_allow_html=True
    )



    st.text_area(

        "",

        value=pedido.get(
            "mensagem",
            ""
        ),

        disabled=True,

        height=70,

        key="mensagem_cliente"

    )



    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )




with col2:


    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="card-title">✨ Pedido Especial</div>',
        unsafe_allow_html=True
    )



    st.text_area(

        "",

        value=pedido.get(
            "pedido_especial",
            ""
        ),

        disabled=True,

        height=80,

        key="pedido_especial"

    )



    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )





# =====================================================
# CARD ENDEREÇO
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">📍 Endereço de Entrega</div>',
unsafe_allow_html=True
)



st.text_area(

    "",

    value=pedido.get(
        "endereco",
        ""
    ),

    disabled=True,

    height=80,

    key="endereco_entrega"

)



st.markdown(
'</div>',
unsafe_allow_html=True
)





# =====================================================
# CARD FOTOS POLAROID
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">📷 Fotos da Polaroid</div>',
unsafe_allow_html=True
)



try:


    fotos = listar_fotos(
        pedido["id"]
    )



    if fotos:


        colunas = st.columns(5)



        for i, foto in enumerate(fotos):


            with colunas[i % 5]:


                st.image(

                    foto.get("url"),

                    caption=foto.get(
                        "nome_original",
                        "Foto"
                    ),

                    use_container_width=True

                )



    else:


        st.info(
            "Nenhuma foto enviada."
        )



except Exception as erro:


    st.error(
        f"Erro ao carregar fotos: {erro}"
    )



st.markdown(
'</div>',
unsafe_allow_html=True
)
# =====================================================
# CARD ANOTAÇÕES INTERNAS
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">📝 Anotações Internas</div>',
unsafe_allow_html=True
)


st.caption(
    "Uso exclusivo da equipe."
)



anotacao = st.text_area(

    "Observações do atendimento",

    value=pedido.get(
        "anotacoes_internas",
        ""
    ) or "",

    height=100,

    key="campo_anotacao"

)



if st.button(

    "💾 Salvar Anotação",

    use_container_width=True

):


    atualizar_anotacao_pedido(

        pedido["id"],

        anotacao

    )


    st.success(
        "✅ Anotação salva!"
    )


    st.rerun()



st.markdown(
'</div>',
unsafe_allow_html=True
)





# =====================================================
# CARD FECHAMENTO FINANCEIRO
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">💰 Fechamento Financeiro</div>',
unsafe_allow_html=True
)


st.caption(
    "Valores sob consulta entram no total após definição."
)



valor_cesta = 0.0



try:


    if pedido.get("cesta_id"):


        cesta = buscar_cesta(
            pedido["cesta_id"]
        )


        if cesta:


            valor_cesta = float(

                cesta.get(
                    "preco",
                    0
                )

                or 0

            )


except:


    valor_cesta = 0.0





col1, col2, col3 = st.columns(3)



with col1:


    valor_frete = st.number_input(

        "🚚 Frete",

        min_value=0.0,

        value=float(

            pedido.get(
                "valor_frete",
                0
            )

            or 0

        ),

        step=1.0,

        key="frete"

    )




with col2:


    desconto = st.number_input(

        "🏷️ Desconto",

        min_value=0.0,

        value=float(

            pedido.get(
                "desconto",
                0
            )

            or 0

        ),

        step=1.0,

        key="desconto"

    )




with col3:


    status_opcoes = [

        "Recebido",

        "Pago",

        "Desistência",

        "Entregue"

    ]



    status_atual = pedido.get(

        "status",

        "Recebido"

    )



    if status_atual not in status_opcoes:

        status_atual = "Recebido"



    status = st.selectbox(

        "Status",

        status_opcoes,

        index=status_opcoes.index(
            status_atual
        )

    )





st.markdown(
'<div class="card-title">🕒 Horário da Entrega</div>',
unsafe_allow_html=True
)



horario_combinado = st.text_input(

    "Horário combinado",

    value=pedido.get(

        "horario_combinado",

        ""

    ),

    placeholder="Ex: 15:30"

)



st.markdown(
'</div>',
unsafe_allow_html=True
)





# =====================================================
# CARD RESUMO FINAL
# =====================================================


valor_total_calculado = (

    valor_cesta

    +

    valor_adicionais

    +

    valor_frete

    -

    desconto

)



if valor_total_calculado < 0:

    valor_total_calculado = 0




st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">🧮 Resumo do Pedido</div>',
unsafe_allow_html=True
)



st.markdown(

f"""

<div class="resumo-card">

<table>

<tr>
<td>🎁 Cesta</td>
<td align="right"><b>{formatar_valor(valor_cesta)}</b></td>
</tr>


<tr>
<td>🎀 Adicionais</td>
<td align="right"><b>{formatar_valor(valor_adicionais)}</b></td>
</tr>


<tr>
<td>⚠️ Sob consulta</td>
<td align="right"><b>{formatar_valor(valor_consulta)}</b></td>
</tr>


<tr>
<td>🚚 Frete</td>
<td align="right"><b>{formatar_valor(valor_frete)}</b></td>
</tr>


<tr>
<td>🏷️ Desconto</td>
<td align="right"><b>{formatar_valor(desconto)}</b></td>
</tr>


<tr>

<td>
<b>💰 TOTAL</b>
</td>

<td align="right">

<h3>
{formatar_valor(valor_total_calculado)}
</h3>

</td>

</tr>


</table>


</div>

""",

unsafe_allow_html=True

)



st.write(

f"💳 Pagamento: **{pedido.get('pagamento','-')}**"

)



st.markdown(
'</div>',
unsafe_allow_html=True
)





# =====================================================
# CARD WHATSAPP
# =====================================================


st.markdown(
'<div class="card">',
unsafe_allow_html=True
)


st.markdown(
'<div class="card-title">📲 Atendimento WhatsApp</div>',
unsafe_allow_html=True
)



if valor_total_calculado > 0:


    link_whatsapp = gerar_whatsapp(

        pedido,

        adicionais_pedido,

        valor_total_calculado

    )


    st.link_button(

        "📲 Enviar resumo pelo WhatsApp",

        link_whatsapp,

        use_container_width=True

    )



else:


    st.info(
        "Defina os valores para liberar o WhatsApp."
    )



st.markdown(
'</div>',
unsafe_allow_html=True
)





# =====================================================
# SALVAR ATENDIMENTO
# =====================================================


if st.button(

    "💾 Salvar Atendimento",

    use_container_width=True,

    type="primary"

):


    dados = {

        "status": status,

        "valor_frete": valor_frete,

        "desconto": desconto,

        "valor_total": valor_total_calculado,

        "horario_combinado": horario_combinado,

        "itens_consulta": itens_consulta

    }



    atualizar_pedido(

        pedido["id"],

        dados

    )


    st.success(
        "✅ Atendimento salvo com sucesso!"
    )


    st.rerun()





# =====================================================
# VOLTAR
# =====================================================


if st.button(

    "⬅ Voltar para Pedidos",

    use_container_width=True

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
