import streamlit as st


from services.pedido_service import (
    buscar_pedido,
    atualizar_pedido,
    atualizar_anotacao_pedido
)


from services.foto_service import (
    listar_fotos
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
# AJUSTE VISUAL
# =====================================================

st.markdown(
"""
<style>


h1 {

font-size:26px !important;

margin-bottom:10px;

}


h2 {

font-size:18px !important;

margin-top:10px;

}


h3 {

font-size:15px !important;

}


p, div, span {

font-size:13px;

}


textarea {

font-size:13px !important;

}


.stButton button {

font-size:13px;

padding:5px 10px;

}


</style>
""",
unsafe_allow_html=True
)




# =====================================================
# VALIDA PEDIDO
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
        f"Erro ao buscar pedido: {erro}"
    )

    st.stop()



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
    f"Status atual: {pedido.get('status','-')}"
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
# PEDIDO
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


    st.write("**Data entrega**")


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



with col1:


    st.markdown(
        "### 🛒 Produtos"
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
            "Nenhum produto."
        )




with col2:


    st.markdown(
        "### 🎀 Adicionais"
    )


    adicionais = pedido.get(
        "adicionais",
        ""
    )


    if adicionais:


        st.write(
            adicionais
        )


    else:


        st.info(
            "Nenhum adicional."
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

        height=70,

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

        height=70,

        key="especial_view"

    )





# =====================================================
# ENDEREÇO
# =====================================================

st.markdown(
    "### 📍 Endereço"
)



st.text_area(

    "",

    value=pedido.get(
        "endereco",
        ""
    ),

    disabled=True,

    height=70,

    key="endereco_view"

)





# =====================================================
# FOTOS
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
    "Campo exclusivo para controle administrativo."
)



anotacao_atual = pedido.get(

    "anotacoes_internas",

    ""

) or ""



anotacao = st.text_area(

    "Observações do administrador",

    value=anotacao_atual,

    height=120,

    placeholder="""
Exemplos:

- Cliente confirmou entrega após 18h
- Aguardar pagamento
- Alteração solicitada pelo cliente
- Observação da montagem da cesta
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

            "✅ Anotação salva com sucesso!"

        )


        st.rerun()



    except Exception as erro:


        st.error(

            f"Erro ao salvar anotação: {erro}"

        )

# =====================================================
# ATENDIMENTO
# =====================================================

st.divider()


st.markdown(
    "### 🚚 Atendimento"
)



col1, col2, col3 = st.columns(3)



with col1:


    valor_frete = st.number_input(

        "Frete (R$)",

        min_value=0.0,

        value=float(

            pedido.get(

                "valor_frete",

                0

            )

            or 0

        ),

        step=1.0

    )




with col2:


    valor_total = st.number_input(

        "Valor Final (R$)",

        min_value=0.0,

        value=float(

            pedido.get(

                "valor_total",

                0

            )

            or 0

        ),

        step=1.0

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





if st.button(

    "💾 Salvar Atendimento",

    use_container_width=True

):


    try:


        atualizar_pedido(

            pedido["id"],

            status,

            valor_frete,

            valor_total

        )


        st.success(

            "✅ Pedido atualizado!"

        )


        st.rerun()



    except Exception as erro:


        st.error(

            f"Erro ao atualizar pedido: {erro}"

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
