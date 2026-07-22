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
    buscar_cesta
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
# CSS
# =====================================================

st.markdown(
"""
<style>


.block-container{

    padding-top:1rem;

}


h1{

    font-size:26px !important;

}


h2{

    font-size:18px !important;

}


h3{

    font-size:15px !important;

}


p, div, span{

    font-size:13px;

}



.stButton button{

    font-size:13px;

    padding:6px 10px;

}



div[data-testid="stNumberInput"]{

    margin-top:-10px;

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
# MODO ALTERAÇÃO
# =====================================================

if "modo_edicao_pedido" not in st.session_state:

    st.session_state.modo_edicao_pedido = False





modo_edicao = st.session_state.modo_edicao_pedido





# =====================================================
# BUSCA PEDIDO
# =====================================================

try:


    pedido = buscar_pedido(

        pedido_id

    )


except Exception as erro:


    st.error(

        f"Erro ao buscar pedido: {erro}"

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


except Exception as erro:


    adicionais_pedido = []


    st.warning(

        f"Erro ao carregar adicionais: {erro}"

    )





# =====================================================
# VALORES SOB CONSULTA SALVOS
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
# TÍTULO
# =====================================================

st.title(

    "📋 Detalhes do Pedido"

)



st.caption(

    f"Status atual: {pedido.get('status','-')}"

)





# =====================================================
# AÇÕES DO PEDIDO
# =====================================================

col1, col2, col3 = st.columns(3)





with col1:


    if not modo_edicao:


        if st.button(

            "✏️ Alterar Pedido",

            use_container_width=True

        ):


            st.session_state.modo_edicao_pedido = True

            st.rerun()



    else:


        st.info(

            "Modo alteração ativo"

        )





with col2:


    if st.button(

        "📲 WhatsApp",

        use_container_width=True

    ):


        st.session_state.gerar_whatsapp = True





with col3:


    if st.button(

        "⬅ Pedidos",

        use_container_width=True

    ):


        st.switch_page(

            "pages/02_Pedidos.py"

        )





# =====================================================
# PREPARAÇÃO WHATSAPP
# =====================================================

if st.session_state.get(

    "gerar_whatsapp",

    False

):


    telefone = pedido.get(

        "cliente_telefone",

        ""

    )


    mensagem = f"""

🎁 *DOCE CESTA BRASÍLIA*

Cliente:
{pedido.get('cliente_nome','')}


Cesta:
{pedido.get('cesta_nome','')}


Pagamento:
{pedido.get('pagamento','')}


Entrega:
{pedido.get('data_entrega','')} - {pedido.get('periodo_entrega','')}


Endereço:
{pedido.get('endereco','')}


💰 Valor final:
R$ {pedido.get('valor_total',0)}


Obrigado por escolher a Doce Cesta Brasília 💝

"""


    link = (

        "https://wa.me/"

        + "".join(

            filter(

                str.isdigit,

                telefone

            )

        )

        +

        "?text="

        +

        urllib.parse.quote(

            mensagem

        )

    )



    st.markdown(

        f"""

<a href="{link}" target="_blank">

<button style="
background:#25D366;
color:white;
border:none;
padding:10px;
border-radius:10px;
width:100%;
font-weight:bold;
">

Abrir WhatsApp

</button>

</a>

""",

        unsafe_allow_html=True

    )
  # =====================================================
# CLIENTE
# =====================================================

st.markdown(
"### 👤 Cliente"
)


col1, col2, col3 = st.columns(3)



with col1:

    st.write("**Nome**")

    st.write(
        pedido.get(
            "cliente_nome",
            "-"
        )
    )



with col2:

    st.write("**CPF**")

    st.write(
        pedido.get(
            "cliente_cpf",
            "-"
        )
    )



with col3:

    st.write("**Telefone**")

    st.write(
        pedido.get(
            "cliente_telefone",
            "-"
        )
    )





# =====================================================
# INFORMAÇÕES DO PEDIDO
# =====================================================

st.markdown(
"### 🎁 Pedido"
)



col1, col2, col3, col4 = st.columns(4)



with col1:

    st.write("**Cesta**")

    st.write(
        pedido.get(
            "cesta_nome",
            "-"
        )
    )



with col2:

    st.write("**Pagamento**")

    st.write(
        pedido.get(
            "pagamento",
            "-"
        )
    )



with col3:

    st.write("**Entrega**")

    st.write(
        pedido.get(
            "data_entrega",
            "-"
        )
    )



with col4:

    st.write("**Período**")

    st.write(
        pedido.get(
            "periodo_entrega",
            "-"
        )
    )







# =====================================================
# PRODUTOS E ADICIONAIS
# =====================================================

col1, col2 = st.columns(2)





# =====================================================
# PRODUTOS DA CESTA
# =====================================================

with col1:


    st.markdown(
        "### 🛒 Produtos da Cesta"
    )



    produtos = pedido.get(

        "produtos",

        ""

    )



    if produtos:


        for item in produtos.split("\n"):


            st.write(

                "• " + item

            )


    else:


        st.info(

            "Nenhum produto informado."

        )







# =====================================================
# ADICIONAIS
# =====================================================

with col2:


    st.markdown(
        "### 🎀 Adicionais"
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






            # -----------------------------------------
            # PRODUTO COM VALOR
            # -----------------------------------------

            if valor is not None:



                valor = float(valor)



                valor_adicionais += valor



                valor_formatado = (

                    f"R$ {valor:,.2f}"

                    .replace(",", "X")

                    .replace(".", ",")

                    .replace("X",".")

                )



                st.success(

                    f"✅ {nome}  |  {valor_formatado}"

                )






            # -----------------------------------------
            # PRODUTO SOB CONSULTA
            # -----------------------------------------

            else:



                st.warning(

                    f"⚠️ {nome}"

                )


                st.caption(

                    "Valor definido pelo administrador."

                )



                valor_anterior = float(

                    itens_consulta_salvos.get(

                        nome,

                        0

                    )

                    or 0

                )





                valor_digitado = st.number_input(



                    "Informe o valor",



                    min_value=0.0,



                    value=valor_anterior,



                    step=1.0,



                    key=f"consulta_{nome}"

                )





                itens_consulta[nome] = valor_digitado



                valor_consulta += valor_digitado



                valor_adicionais += valor_digitado





    else:



        st.info(

            "Nenhum adicional selecionado."

        )





# =====================================================
# RESUMO DOS ADICIONAIS
# =====================================================


st.divider()



col1, col2 = st.columns(2)




with col1:


    st.write(

        "🎀 Total adicionais"

    )


    st.write(

        f"R$ {valor_adicionais:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )





with col2:


    st.write(

        "⚠️ Valores sob consulta"

    )


    st.write(

        f"R$ {valor_consulta:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )
  # =====================================================
# TEXTOS DO CLIENTE
# =====================================================


col1, col2 = st.columns(2)



with col1:


    st.markdown(

        "### 💌 Mensagem"

    )


    st.text_area(

        "",

        value=pedido.get(

            "mensagem",

            ""

        ),


        disabled=True,


        height=90,


        key="mensagem_view"

    )





with col2:


    st.markdown(

        "### ✨ Pedido Especial"

    )


    st.text_area(

        "",


        value=pedido.get(

            "pedido_especial",

            ""

        ),


        disabled=True,


        height=90,


        key="pedido_especial_view"

    )







# =====================================================
# ENDEREÇO
# =====================================================


st.markdown(

    "### 📍 Endereço de entrega"

)



st.text_area(

    "",


    value=pedido.get(

        "endereco",

        ""

    ),


    disabled=True,


    height=90,


    key="endereco_view"

)







# =====================================================
# FOTOS POLAROID
# =====================================================


st.markdown(

    "### 📷 Fotos da Polaroid"

)



try:


    fotos = listar_fotos(

        pedido["id"]

    )



    if fotos:



        colunas = st.columns(4)



        for i, foto in enumerate(fotos):



            with colunas[i % 4]:


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

            "Nenhuma foto cadastrada."

        )





except Exception as erro:


    st.error(

        f"Erro ao carregar fotos: {erro}"

    )









# =====================================================
# ANOTAÇÕES INTERNAS
# =====================================================


st.divider()



st.markdown(

    "### 📝 Anotações Internas"

)



st.caption(

    "Campo exclusivo para administrador e operador."

)





anotacao_atual = pedido.get(

    "anotacoes_internas",

    ""

) or ""





anotacao = st.text_area(

    "Observações internas",


    value=anotacao_atual,


    height=120,


    placeholder="""

Exemplos:

- Cliente confirmou entrega
- Alteração solicitada
- Aguardar pagamento
- Observação da montagem

""",


    key="anotacao_interna"

)







if st.button(

    "💾 Salvar Anotações",

    use_container_width=True

):


    try:


        atualizar_anotacao_pedido(

            pedido["id"],

            anotacao

        )


        st.success(

            "✅ Anotação salva!"

        )


        st.rerun()



    except Exception as erro:


        st.error(

            f"Erro ao salvar anotação: {erro}"

        )
  # =====================================================
# FECHAMENTO FINANCEIRO
# =====================================================

st.divider()


st.markdown(

    "### 💰 Fechamento Financeiro"

)


st.caption(

    "Itens cadastrados como preço sob consulta precisam ter o valor informado."

)





# =====================================================
# VALOR DA CESTA
# =====================================================

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



except Exception:


    valor_cesta = 0.0







# =====================================================
# RECALCULA ADICIONAIS
# =====================================================

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





        # -----------------------------------------
        # VALOR NORMAL
        # -----------------------------------------

        if valor is not None:



            valor_adicionais += float(valor)





        # -----------------------------------------
        # SOB CONSULTA
        # -----------------------------------------

        else:



            valor_anterior = float(

                itens_consulta_salvos.get(

                    nome,

                    0

                )

                or 0

            )



            valor_digitado = st.number_input(

                f"💡 Valor {nome}",


                min_value=0.0,


                value=valor_anterior,


                step=1.0,


                key=f"financeiro_consulta_{nome}"

            )




            itens_consulta[nome] = valor_digitado



            valor_consulta += valor_digitado





            valor_adicionais += valor_digitado







# =====================================================
# FRETE / DESCONTO / STATUS
# =====================================================


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

        key="valor_frete"

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









# =====================================================
# TOTAL FINAL
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







# =====================================================
# RESUMO FINAL
# =====================================================


st.markdown(

    "### 🧮 Resumo do Pedido"

)





col1, col2 = st.columns(2)





with col1:


    st.write(

        "🎁 Cesta"

    )


    st.write(

        f"R$ {valor_cesta:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )



    st.write(

        "🎀 Adicionais"

    )


    st.write(

        f"R$ {valor_adicionais:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )







with col2:


    st.write(

        "⚠️ Sob consulta"

    )


    st.write(

        f"R$ {valor_consulta:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )



    st.write(

        "🚚 Frete"

    )


    st.write(

        f"R$ {valor_frete:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )






st.success(

    f"💰 Valor Final: R$ {valor_total_calculado:,.2f}"

    .replace(",", "X")

    .replace(".", ",")

    .replace("X",".")

)
  # =====================================================
# AÇÕES FINAIS DO PEDIDO
# =====================================================

st.divider()


st.markdown(

    "### 📲 Ações do Atendimento"

)



col1, col2 = st.columns(2)



# =====================================================
# WHATSAPP
# =====================================================

with col1:


    import urllib.parse


    resumo_whatsapp = f"""
Olá {pedido.get('cliente_nome','')}! 😊

Segue o resumo do seu pedido da Doce Cesta Brasília:

🎁 Cesta:
{pedido.get('cesta_nome','')}

🎀 Adicionais:
"""



    if adicionais_pedido:


        for adicional in adicionais_pedido:


            nome = adicional.get(
                "nome_produto",
                ""
            )


            valor = adicional.get(
                "valor_unitario"
            )


            if valor is None:


                valor = itens_consulta_salvos.get(
                    nome,
                    0
                )


            resumo_whatsapp += (
                f"- {nome}: "
                f"R$ {float(valor):,.2f}\n"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X",".")
            )


    else:


        resumo_whatsapp += "- Nenhum adicional\n"





resumo_whatsapp += f"""

🚚 Frete:
R$ {valor_frete:,.2f}

🏷️ Desconto:
R$ {desconto:,.2f}

💰 Valor final:
R$ {valor_total_calculado:,.2f}

📅 Entrega:
{pedido.get('data_entrega','')}

🕘 Período:
{pedido.get('periodo_entrega','')}


Obrigado por escolher a Doce Cesta Brasília! 💝
"""



    resumo_whatsapp = (
        resumo_whatsapp
        .replace(",", "X")
        .replace(".", ",")
        .replace("X",".")
    )



    numero = (
        pedido.get(
            "cliente_telefone",
            ""
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

        numero

        +

        "?text="

        +

        urllib.parse.quote(

            resumo_whatsapp

        )

    )



    st.link_button(

        "📲 Enviar resumo pelo WhatsApp",

        link_whatsapp,

        use_container_width=True

    )





# =====================================================
# ALTERAR PEDIDO
# =====================================================

with col2:



    if st.button(

        "✏️ Alterar Pedido",

        use_container_width=True

    ):


        st.session_state["editar_pedido"] = True


        st.success(

            "Modo alteração ativado."

        )


        st.info(

            """
A próxima etapa permitirá alterar:

✅ Cesta escolhida  
✅ Produtos da cesta  
✅ Adicionais  
✅ Dados de entrega  
✅ Mensagem do cliente  
✅ Valores

"""

        )






# =====================================================
# VOLTAR
# =====================================================


st.divider()



if st.button(

    "⬅ Voltar para Pedidos",

    use_container_width=True

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
