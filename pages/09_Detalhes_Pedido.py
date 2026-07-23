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
# CSS COMPACTO
# =====================================================

st.markdown(
"""
<style>

.block-container{

    padding-top:0.7rem;

    padding-bottom:1rem;

    max-width:960px;

}


h1{

    font-size:24px !important;

    margin-bottom:0.2rem !important;

}


h2{

    font-size:18px !important;

    margin-bottom:0.2rem !important;

}


h3{

    font-size:15px !important;

    margin-bottom:0.2rem !important;

}


p{

    margin-bottom:0.15rem !important;

}


div[data-testid="stVerticalBlock"]{

    gap:0.35rem;

}


.stButton button{

    font-size:13px;

    padding:6px 10px;

    border-radius:10px;

}


.stTextInput input,
.stNumberInput input{

    font-size:13px;

}


.resumo-card{

    background:#fff8f2;

    padding:12px 15px;

    border-radius:12px;

    border:1px solid #ead8c7;

    line-height:1.2;

}


.info-card{

    background:#f8f8f8;

    padding:10px;

    border-radius:10px;

    border:1px solid #ddd;

}


.edit-card{

    background:#f7f7f7;

    padding:12px;

    border-radius:12px;

    border:1px solid #ddd;

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


    if st.button(
        "⬅ Voltar"
    ):


        st.switch_page(
            "pages/02_Pedidos.py"
        )


    st.stop()



pedido_id = st.session_state["pedido_aberto"]



# =====================================================
# BUSCAR PEDIDO
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
# BUSCAR ADICIONAIS
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
            .replace("X", ".")
        )


    except:


        return "R$ 0,00"



def limpar_telefone(numero):


    return (
        str(numero)
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
    )



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
                nome
            )


            if valor_manual:


                lista_adicionais.append(
                    f"• {nome} - {formatar_valor(valor_manual)}"
                )


            else:


                lista_adicionais.append(
                    f"• {nome} (sob consulta)"
                )
              # =====================================================
# CABEÇALHO COMPACTO
# =====================================================


col_titulo, col_status = st.columns(
    [3,1]
)


with col_titulo:

    st.title(
        "📋 Detalhes do Pedido"
    )


with col_status:

    status_atual = pedido.get(
        "status",
        "-"
    )

    st.markdown(
        f"""
        <div style="
            margin-top:25px;
            text-align:right;
            font-size:14px;
        ">
        🟢 <b>{status_atual}</b>
        </div>
        """,
        unsafe_allow_html=True
    )



st.caption(
    f"Pedido #{pedido.get('id')}"
)



# =====================================================
# BOTÕES PRINCIPAIS
# =====================================================


col1, col2 = st.columns(2)



with col1:


    if st.button(
        "✏️ Alterar Pedido",
        use_container_width=True
    ):


        st.session_state.editar_pedido = (
            not st.session_state.editar_pedido
        )



with col2:


    st.info(
        "💰 Finalize o valor para liberar WhatsApp."
    )




# =====================================================
# PAINEL CLIENTE + PEDIDO
# =====================================================


st.markdown(
    "### 👤 Pedido"
)



st.markdown(
"""
<div class="info-card">
""",
unsafe_allow_html=True
)



col1, col2, col3 = st.columns(3)



with col1:


    st.write(
        "**Nome**"
    )


    st.write(
        pedido.get(
            "cliente_nome",
            "-"
        )
    )



with col2:


    st.write(
        "**CPF**"
    )


    st.write(
        pedido.get(
            "cliente_cpf",
            "-"
        )
    )



with col3:


    st.write(
        "**Telefone**"
    )


    st.write(
        pedido.get(
            "cliente_telefone",
            "-"
        )
    )



col1, col2, col3, col4 = st.columns(4)



with col1:


    st.write(
        "**🎁 Cesta**"
    )


    st.write(
        pedido.get(
            "cesta_nome",
            "-"
        )
    )



with col2:


    st.write(
        "**💳 Pagamento**"
    )


    st.write(
        pedido.get(
            "pagamento",
            "-"
        )
    )



with col3:


    st.write(
        "**📅 Entrega**"
    )


    st.write(
        pedido.get(
            "data_entrega",
            "-"
        )
    )



with col4:


    st.write(
        "**⏰ Período**"
    )


    st.write(
        pedido.get(
            "periodo_entrega",
            "-"
        )
    )



st.markdown(
"""
</div>
""",
unsafe_allow_html=True
)
# =====================================================
# PRODUTOS E ADICIONAIS
# =====================================================


col1, col2 = st.columns(
    [1,1]
)



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


        lista_produtos = produtos.split(
            "\n"
        )


        texto_produtos = ""


        for item in lista_produtos:


            if item.strip():

                texto_produtos += (
                    f"• {item}<br>"
                )



        st.markdown(
            f"""
            <div class="info-card">

            {texto_produtos}

            </div>
            """,
            unsafe_allow_html=True
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



    lista_html = ""



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
            # VALOR FIXO
            # -----------------------------------------


            if valor is not None:


                valor = float(
                    valor
                )


                valor_adicionais += valor


                lista_html += (
                    f"• {nome} - "
                    f"{formatar_valor(valor)}<br>"
                )



            # -----------------------------------------
            # SOB CONSULTA
            # -----------------------------------------


            else:


                valor_salvo = float(
                    itens_consulta_salvos.get(
                        nome,
                        0
                    )
                    or 0
                )



                valor_digitado = st.number_input(

                    f"{nome}",

                    min_value=0.0,

                    value=valor_salvo,

                    step=1.0,

                    format="%.2f",

                    key=f"consulta_{nome}"

                )



                itens_consulta[nome] = valor_digitado



                if valor_digitado > 0:


                    valor_consulta += valor_digitado

                    valor_adicionais += valor_digitado


                    lista_html += (
                        f"• {nome} - "
                        f"{formatar_valor(valor_digitado)}<br>"
                    )


                else:


                    lista_html += (
                        f"• {nome} "
                        "(sob consulta)<br>"
                    )



        st.markdown(

            f"""
            <div class="info-card">

            {lista_html}

            </div>
            """,

            unsafe_allow_html=True

        )



    else:


        st.info(
            "Nenhum adicional selecionado."
        )





# =====================================================
# RESUMO DOS ADICIONAIS
# =====================================================


col1, col2 = st.columns(2)



with col1:


    st.caption(
        "🎀 Total adicionais"
    )


    st.success(
        formatar_valor(
            valor_adicionais
        )
    )



with col2:


    st.caption(
        "⚠️ Sob consulta"
    )


    st.info(
        formatar_valor(
            valor_consulta
        )
    )
  # =====================================================
# MENSAGEM E PEDIDO ESPECIAL
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

        height=60,

        key="mensagem_cliente"

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

        height=60,

        key="pedido_especial"

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

    key="endereco"

)






# =====================================================
# FOTOS POLAROID
# =====================================================


st.markdown(
    "### 📷 Fotos"
)



try:


    fotos = listar_fotos(
        pedido["id"]
    )



    if fotos:


        colunas = st.columns(
            5
        )


        for i, foto in enumerate(fotos):


            with colunas[i % 5]:


                st.image(

                    foto.get(
                        "url"
                    ),

                    caption=foto.get(
                        "nome_original",
                        "Foto"
                    ),

                    use_container_width=True

                )


    else:


        st.caption(
            "Nenhuma foto enviada."
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
    "Uso exclusivo da equipe."
)


anotacao_atual = pedido.get(
    "anotacoes_internas",
    ""
) or ""


anotacao = st.text_area(
    "Observações do atendimento",
    value=anotacao_atual,
    height=80,
    placeholder=(
        "Ex:\n"
        "- Cliente confirmou endereço\n"
        "- Aguardando pagamento\n"
        "- Alteração solicitada"
    ),
    key="campo_anotacao"
)



if st.button(
    "💾 Salvar Anotação",
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
    "Valores sob consulta entram no total após definição."
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
# RESUMO FINAL COMPACTO
# =====================================================


st.markdown(
    "### 🧮 Resumo do Pedido"
)



st.markdown(
f"""
<div class="resumo-card">

<div style="line-height:1.8;">

🎁 <b>Cesta:</b> {formatar_valor(valor_cesta)}<br>

🎀 <b>Adicionais:</b> {formatar_valor(valor_adicionais)}<br>

⚠️ <b>Sob consulta:</b> {formatar_valor(valor_consulta)}<br>

🚚 <b>Frete:</b> {formatar_valor(valor_frete)}<br>

🏷️ <b>Desconto:</b> {formatar_valor(desconto)}

<hr style="margin:8px 0;">

💰 <b>TOTAL FINAL:</b>

<h2 style="margin:5px 0;">
{formatar_valor(valor_total_calculado)}
</h2>


</div>

</div>
""",
unsafe_allow_html=True
)






# =====================================================
# WHATSAPP
# =====================================================


st.markdown(
    "### 📲 Atendimento WhatsApp"
)



link_whatsapp = gerar_whatsapp(

    pedido,

    adicionais_pedido,

    itens_consulta,

    valor_total_calculado

)



st.link_button(

    "📲 Enviar resumo pelo WhatsApp",

    link_whatsapp,

    use_container_width=True

)
# =====================================================
# SALVAR ATENDIMENTO
# =====================================================


st.divider()



if st.button(

    "💾 Salvar Atendimento",

    use_container_width=True,

    type="primary"

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



        supabase.table("pedidos").update(

            {

                "itens_consulta": itens_consulta

            }

        ).eq(

            "id",

            pedido["id"]

        ).execute()



        st.success(

            "✅ Atendimento salvo com sucesso!"

        )


        st.rerun()



    except Exception as erro:


        st.error(

            f"Erro ao salvar atendimento: {erro}"

        )
      # =====================================================
# VOLTAR
# =====================================================


st.markdown(
    "<br>",
    unsafe_allow_html=True
)



if st.button(

    "⬅ Voltar para Pedidos",

    use_container_width=True

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
