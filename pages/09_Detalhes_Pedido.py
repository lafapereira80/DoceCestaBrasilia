import streamlit as st
import json


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

h1 {
    font-size:26px !important;
}

h2 {
    font-size:18px !important;
}

h3 {
    font-size:15px !important;
}

p, div, span {
    font-size:13px;
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
# BUSCA ADICIONAIS DO PEDIDO
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
# NORMALIZA ITENS SOB CONSULTA
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





# =====================================================
# PRODUTOS DA CESTA
# =====================================================


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







# =====================================================
# ADICIONAIS DO PEDIDO
# =====================================================


with col2:


    st.markdown(

        "### 🎀 Adicionais"

    )


    if adicionais_pedido:


        for adicional in adicionais_pedido:


            nome = adicional.get(

                "nome_produto",

                "-"

            )


            valor = adicional.get(

                "valor_unitario"

            )



            if valor is None:


                st.write(

                    f"• {nome} (Preço sob consulta)"

                )


            else:


                valor_formatado = (

                    f"R$ {float(valor):,.2f}"

                    .replace(",", "X")

                    .replace(".", ",")

                    .replace("X",".")

                )


                st.write(

                    f"• {nome} - {valor_formatado}"

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

        height=80,

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

        height=80,

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

    height=80,

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
# FECHAMENTO FINANCEIRO
# =====================================================


st.divider()



st.markdown(

    "### 💰 Fechamento Financeiro"

)



st.caption(

    "Valores calculados automaticamente conforme cadastro dos produtos."

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






st.markdown(

    "#### 🎁 Cesta"

)





col1, col2 = st.columns(2)





with col1:


    st.write(

        pedido.get(

            "cesta_nome",

            "-"

        )

    )





with col2:


    st.write(

        f"R$ {valor_cesta:,.2f}"

        .replace(",", "X")

        .replace(".", ",")

        .replace("X",".")

    )







# =====================================================
# ADICIONAIS FINANCEIRO - CORRIGIDO
# =====================================================


st.markdown(

    "#### 🎀 Adicionais"

)





valor_adicionais = 0.0


valor_itens_consulta = 0.0


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





        # ---------------------------------------------
        # ADICIONAL COM VALOR DEFINIDO
        # ---------------------------------------------


        if valor is not None:



            valor = float(valor)



            valor_adicionais += valor



            valor_formatado = (

                f"R$ {valor:,.2f}"

                .replace(",", "X")

                .replace(".", ",")

                .replace("X",".")

            )



            st.write(

                f"• {nome} - {valor_formatado}"

            )

        # ---------------------------------------------
        # ADICIONAL PREÇO SOB CONSULTA
        # ---------------------------------------------


        else:


            valor_anterior = float(

                itens_consulta_salvos.get(

                    nome,

                    0

                )

                or 0

            )


            col_nome, col_valor = st.columns([3, 1])


            with col_nome:

                st.write(

                    f"• {nome} (Preço sob consulta) -"

                )


            with col_valor:

                valor_digitado = st.number_input(

                    "Valor",

                    min_value=0.0,

                    value=valor_anterior,

                    step=1.0,

                    key=f"consulta_{nome}",

                    label_visibility="collapsed"

                )


            itens_consulta[nome] = valor_digitado


            valor_itens_consulta += valor_digitado


            valor_adicionais += valor_digitado





else:


    st.info(

        "Nenhum adicional."

    )
# =====================================================
# FRETE / DESCONTO / STATUS
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

        step=1.0,

        key="valor_frete"

    )







with col2:


    desconto = st.number_input(

        "Desconto (R$)",

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
# CÁLCULO TOTAL
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
# RESUMO
# =====================================================


st.markdown(

    "### 🧮 Resumo"

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

        f"R$ {valor_itens_consulta:,.2f}"

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

    f"💰 Valor Total: R$ {valor_total_calculado:,.2f}"

    .replace(",", "X")

    .replace(".", ",")

    .replace("X",".")

)








# =====================================================
# SALVAR ATENDIMENTO
# =====================================================


if st.button(

    "💾 Salvar Atendimento",

    use_container_width=True

):


    try:



        atualizar_pedido(

            pedido["id"],

            status,

            valor_frete,

            valor_total_calculado,

            desconto

        )







        from config.supabase import supabase





        supabase.table("pedidos").update({

            "itens_consulta":

                itens_consulta

        }).eq(

            "id",

            pedido["id"]

        ).execute()






        st.success(

            "✅ Pedido atualizado com sucesso!"

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
