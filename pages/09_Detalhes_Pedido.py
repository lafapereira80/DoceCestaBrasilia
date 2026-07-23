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

    padding-top:0.8rem;

    padding-bottom:1rem;

    max-width:1000px;

}



h1{

    font-size:24px !important;

    margin-bottom:5px;

}



h2{

    font-size:18px !important;

    margin-top:10px;

    margin-bottom:5px;

}



h3{

    font-size:15px !important;

    margin-top:8px;

    margin-bottom:4px;

}



p, div, span{

    font-size:13px;

}



.stButton button{

    font-size:13px;

    padding:5px 10px;

    border-radius:8px;

}



.stTextInput input,
.stTextArea textarea,
.stNumberInput input{

    font-size:13px;

}



[data-testid="stVerticalBlock"]{

    gap:0.4rem;

}



.resumo-card{

    background:#fff8f2;

    padding:10px 14px;

    border-radius:12px;

    border:1px solid #ead8c7;

}



.edit-card{

    background:#f7f7f7;

    padding:10px;

    border-radius:12px;

    border:1px solid #ddd;

}



.info-card{

    background:#fafafa;

    padding:8px 12px;

    border-radius:10px;

    border:1px solid #eee;

}



.small-caption{

    font-size:11px;

    color:#777;

}



</style>
""",
unsafe_allow_html=True
)





# =====================================================
# VALIDAR PEDIDO ABERTO
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
# CONTROLE EDIÇÃO
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
                    f"• {nome}"
                )



    if not lista_adicionais:


        lista_adicionais.append(
            "Nenhum adicional"
        )




    texto = (
        f"🎁 *Doce Cesta Brasília*\n"
        f"Olá {pedido.get('cliente_nome','')}!\n\n"
        f"*Resumo do pedido*\n\n"
        f"🎀 Cesta: {pedido.get('cesta_nome','-')}\n\n"
        f"🛒 Produtos:\n"
        f"{pedido.get('produtos','-')}\n\n"
        f"🎀 Adicionais:\n"
        f"{chr(10).join(lista_adicionais)}\n\n"
        f"📍 Entrega:\n"
        f"{pedido.get('data_entrega','-')} - "
        f"{pedido.get('periodo_entrega','-')}\n\n"
        f"💳 Pagamento: {pedido.get('pagamento','-')}\n"
        f"💰 Total: {formatar_valor(valor_final)}\n\n"
        f"Obrigado! ❤️"
    )



    telefone = limpar_telefone(
        pedido.get(
            "cliente_telefone",
            ""
        )
    )



    return (
        "https://wa.me/55"
        f"{telefone}?text="
        f"{urllib.parse.quote(texto)}"
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
        "📲 WhatsApp disponível após cálculo final."
    )







# =====================================================
# CLIENTE
# =====================================================


st.markdown(
    "### 👤 Cliente"
)



st.markdown(
"""
<div class="info-card">
""",
unsafe_allow_html=True
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



st.markdown(
"""
</div>
""",
unsafe_allow_html=True
)







# =====================================================
# INFORMAÇÕES DO PEDIDO
# =====================================================


st.markdown(
    "### 🎁 Pedido"
)



st.markdown(
"""
<div class="info-card">
""",
unsafe_allow_html=True
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



st.markdown(
"""
</div>
""",
unsafe_allow_html=True
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
                f"• {item}"
            )


    else:


        st.caption(
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
            # VALOR FIXO
            # -----------------------------------------


            if valor is not None:


                valor = float(valor)


                valor_adicionais += valor


                st.success(
                    f"✅ {nome} - {formatar_valor(valor)}"
                )






            # -----------------------------------------
            # SOB CONSULTA
            # -----------------------------------------


            else:


                st.warning(
                    f"⚠️ {nome}"
                )



                valor_salvo = float(
                    itens_consulta_salvos.get(
                        nome,
                        0
                    )
                    or 0
                )



                valor_digitado = st.number_input(


                    "Valor",


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





    else:


        st.caption(
            "Nenhum adicional selecionado."
        )







# =====================================================
# RESUMO ADICIONAIS
# =====================================================


st.markdown(
    "### 🎀 Totais dos Adicionais"
)



col1, col2 = st.columns(2)



with col1:


    st.success(
        f"Adicionais: {formatar_valor(valor_adicionais)}"
    )



with col2:


    st.info(
        f"Consulta: {formatar_valor(valor_consulta)}"
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
        height=70,
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
        height=70,
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
    "### 📷 Fotos Polaroid"
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
    "Observações",
    value=anotacao_atual,
    height=80,
    placeholder=(
        "Ex: cliente confirmou endereço, "
        "aguardando pagamento..."
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


st.markdown(
    "### 💰 Financeiro"
)



st.caption(
    "Valores sob consulta entram somente após definição."
)







# =====================================================
# VALOR DA CESTA
# =====================================================


valor_cesta = 0.0



try:


    if pedido.get(
        "cesta_id"
    ):


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
# RESUMO FINANCEIRO
# =====================================================


st.markdown(
    "### 🧮 Resumo do Pedido"
)



st.markdown(
f"""
<div class="resumo-card">

<table style="width:100%; border-collapse:collapse;">


<tr>
<td>🎁 Cesta</td>
<td style="text-align:right">
<b>{formatar_valor(valor_cesta)}</b>
</td>
</tr>


<tr>
<td>🎀 Adicionais</td>
<td style="text-align:right">
<b>{formatar_valor(valor_adicionais)}</b>
</td>
</tr>


<tr>
<td>⚠️ Sob consulta</td>
<td style="text-align:right">
<b>{formatar_valor(valor_consulta)}</b>
</td>
</tr>


<tr>
<td>🚚 Frete</td>
<td style="text-align:right">
<b>{formatar_valor(valor_frete)}</b>
</td>
</tr>


<tr>
<td>🏷️ Desconto</td>
<td style="text-align:right">
<b>{formatar_valor(desconto)}</b>
</td>
</tr>


<tr>
<td colspan="2">
<hr style="margin:5px 0;">
</td>
</tr>


<tr>
<td>
<b>💰 TOTAL</b>
</td>

<td style="
text-align:right;
font-size:20px;
color:#2E7D32;
">

<b>
{formatar_valor(valor_total_calculado)}
</b>

</td>

</tr>


</table>

</div>
""",
unsafe_allow_html=True
)








# =====================================================
# WHATSAPP
# =====================================================


def gerar_whatsapp_atualizado():


    lista_adicionais = []



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





    for item in adicionais_pedido:


        nome = item.get(
            "nome_produto",
            "-"
        )


        valor = item.get(
            "valor_unitario"
        )



        if valor is not None:


            lista_adicionais.append(

                f"• {nome} - "
                f"{formatar_valor(valor)}"

            )



        else:


            valor_manual = itens_consulta.get(
                nome,
                0
            )



            if valor_manual > 0:


                lista_adicionais.append(

                    f"• {nome} - "
                    f"{formatar_valor(valor_manual)}"

                )


            else:


                lista_adicionais.append(

                    f"• {nome} (sob consulta)"

                )





    texto = (

        f"🎁 *Doce Cesta Brasília*\n"

        f"Olá {pedido.get('cliente_nome','')}!\n\n"

        f"*Resumo do pedido*\n"

        f"🎀 Cesta: {pedido.get('cesta_nome','-')}\n\n"

        f"🛒 Produtos:\n"
        f"{pedido.get('produtos','-')}\n\n"

        f"🎀 Adicionais:\n"
        f"{chr(10).join(lista_adicionais)}\n\n"

        f"📍 Entrega:\n"
        f"{pedido.get('data_entrega','-')} "
        f"- {pedido.get('periodo_entrega','-')}\n\n"

        f"💳 Pagamento: "
        f"{pedido.get('pagamento','-')}\n"

        f"💰 Total: "
        f"{formatar_valor(valor_total_calculado)}\n\n"

        f"Obrigado! ❤️"

    )



    telefone = limpar_telefone(
        pedido.get(
            "cliente_telefone",
            ""
        )
    )



    return (

        "https://wa.me/55"

        +

        telefone

        +

        "?text="

        +

        urllib.parse.quote(texto)

    )







# =====================================================
# BOTÃO WHATSAPP
# =====================================================


st.markdown(
    "### 📲 WhatsApp"
)



if valor_total_calculado > 0:


    st.link_button(

        "📲 Enviar resumo pelo WhatsApp",

        gerar_whatsapp_atualizado(),

        use_container_width=True

    )


else:


    st.info(
        "Defina o valor final para liberar o WhatsApp."
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


st.divider()



if st.button(

    "⬅ Voltar para Pedidos",

    use_container_width=True

):


    st.switch_page(

        "pages/02_Pedidos.py"

    )
# =====================================================
# CSS
# =====================================================

st.markdown(
"""
<style>


/* Área principal */

.block-container{

    padding-top:0.7rem;

    padding-bottom:1rem;

    max-width:950px;

}





/* Títulos */


h1{

    font-size:24px !important;

    margin-bottom:5px !important;

}


h2{

    font-size:17px !important;

    margin-top:12px !important;

    margin-bottom:5px !important;

}


h3{

    font-size:15px !important;

    margin-top:8px !important;

    margin-bottom:4px !important;

}





/* Texto geral */


p,
div,
span{

    font-size:13px;

}





/* Botões */


.stButton button{

    font-size:13px;

    padding:5px 10px;

    border-radius:8px;

}






/* Reduz espaço dos inputs */


div[data-baseweb="input"]{

    min-height:34px;

}



textarea{

    font-size:13px !important;

}





/* Cards informativos */


.info-card{


    background:#fafafa;

    padding:10px;

    border-radius:12px;

    border:1px solid #e5e5e5;

    margin-bottom:8px;


}





/* Card financeiro */


.resumo-card{


    background:#fff8f2;

    padding:10px;

    border-radius:12px;

    border:1px solid #ead8c7;


}





/* Card edição */


.edit-card{


    background:#f7f7f7;

    padding:10px;

    border-radius:12px;

    border:1px solid #ddd;


}





/* Remove espaços extras entre blocos */


.stMarkdown{

    margin-bottom:4px;

}





/* Divider menor */


hr{

    margin-top:8px;

    margin-bottom:8px;

}





</style>
""",
unsafe_allow_html=True
)
