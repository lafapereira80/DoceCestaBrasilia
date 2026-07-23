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
# CSS - COMPACTAR ESPAÇO VERTICAL
# =====================================================

st.markdown(
"""
<style>


/* Área principal */

.block-container{

    padding-top:0.8rem !important;

    padding-bottom:1rem !important;

    max-width:950px;

}


/* Mantém fontes originais */

h1{

    font-size:26px !important;

    margin-top:0 !important;

    margin-bottom:0.15rem !important;

}


h2{

    font-size:19px !important;

    margin-top:0.35rem !important;

    margin-bottom:0.15rem !important;

}


h3{

    font-size:16px !important;

    margin-top:0.25rem !important;

    margin-bottom:0.15rem !important;

}



/* Texto mantém tamanho */

p,
div,
span,
label{

    font-size:13px;

}



/* Reduz espaços automáticos do Streamlit */

.element-container{

    margin-bottom:0.15rem !important;

}



/* Reduz espaço dos blocos */

div[data-testid="stVerticalBlock"]{

    gap:0.35rem !important;

}



/* Colunas mais próximas */

div[data-testid="column"]{

    padding-left:0.25rem !important;

    padding-right:0.25rem !important;

}



/* Botões continuam com acabamento */

.stButton button{

    font-size:13px !important;

    padding:7px 12px !important;

    border-radius:10px !important;

}



/* Inputs */

.stTextInput,
.stTextArea,
.stSelectbox,
.stNumberInput{

    margin-bottom:0 !important;

}



/* Textareas sem exagero */

textarea{

    padding:8px !important;

}



/* Alertas menores sem perder estilo */

div[data-testid="stAlert"]{

    padding:8px 12px !important;

    margin:3px 0 !important;

}



/* Cards continuam iguais */

.resumo-card{

    background:#fff8f2;

    padding:14px;

    border-radius:15px;

    border:1px solid #ead8c7;

}



.edit-card{

    background:#f7f7f7;

    padding:12px;

    border-radius:15px;

    border:1px solid #ddd;

}



/* Divisores mais próximos */

hr{

    margin-top:6px !important;

    margin-bottom:6px !important;

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
# CONTROLE VALORES SOB CONSULTA
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


    if isinstance(itens_consulta,str):

        try:

            itens_consulta=json.loads(
                itens_consulta
            )

        except:

            itens_consulta={}



    lista_adicionais=[]



    for item in adicionais:


        nome=item.get(

            "nome_produto",

            "-"

        )


        valor=item.get(

            "valor_unitario"

        )



        if valor is not None:


            lista_adicionais.append(

                f"• {nome} - {formatar_valor(valor)}"

            )


        else:


            valor_manual=itens_consulta.get(

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



    texto=(

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



    telefone=limpar_telefone(

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

        "📲"

    )







# =====================================================
# MODO EDIÇÃO
# =====================================================


if st.session_state.editar_pedido:


    st.markdown(

        "### ✏️ Editando Pedido"

    )


    st.markdown(

        '<div class="edit-card">',

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






    col_salvar,col_cancelar = st.columns(2)





    with col_salvar:


        if st.button(

            "💾 Salvar Alterações",

            use_container_width=True,

            type="primary"

        ):


            dados={


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


            st.session_state.editar_pedido=False


            st.rerun()





    with col_cancelar:


        if st.button(

            "❌ Cancelar",

            use_container_width=True

        ):


            st.session_state.editar_pedido=False


            st.rerun()





    st.markdown(

        "</div>",

        unsafe_allow_html=True

    )






# =====================================================
# CLIENTE
# =====================================================


st.markdown(

    "### 👤 Cliente"

)



col1,col2,col3 = st.columns(3)



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
# INFORMAÇÕES PRINCIPAIS
# =====================================================


st.markdown(

    "### 🎁 Pedido"

)



col1,col2,col3,col4 = st.columns(4)



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

        formatar_data(

            pedido.get(

                "data_entrega"

            )

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


st.divider()


col1,col2 = st.columns(2)



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

                f"• {item}"

            )


    else:


        st.info(

            "Nenhum produto informado."

        )







with col2:


    st.markdown(

        "### 🎀 Adicionais"

    )



    valor_adicionais=0.0

    valor_consulta=0.0


    itens_consulta={}



    if adicionais_pedido:


        for adicional in adicionais_pedido:


            nome=adicional.get(

                "nome_produto",

                "-"

            )



            valor=adicional.get(

                "valor_unitario"

            )





            if valor is not None:


                valor=float(valor)


                valor_adicionais += valor


                st.write(

                    f"• {nome} - {formatar_valor(valor)}"

                )



            else:


                st.write(

                    f"• {nome}"

                )


                valor_salvo=float(

                    itens_consulta_salvos.get(

                        nome,

                        0

                    )

                    or 0

                )



                valor_digitado=st.number_input(

                    f"Definir valor {nome}",

                    min_value=0.0,

                    value=valor_salvo,

                    step=1.0,

                    key=f"consulta_{nome}"

                )



                itens_consulta[nome]=valor_digitado



                if valor_digitado>0:


                    valor_consulta += valor_digitado

                    valor_adicionais += valor_digitado



    else:


        st.info(

            "Nenhum adicional selecionado."

        )



st.divider()
# =====================================================
# RESUMO DOS ADICIONAIS
# =====================================================


col1,col2 = st.columns(2)



with col1:


    st.write(

        "🎀 Total Adicionais"

    )


    st.success(

        formatar_valor(

            valor_adicionais

        )

    )




with col2:


    st.write(

        "⚠️ Valores Sob Consulta"

    )


    st.info(

        formatar_valor(

            valor_consulta

        )

    )





# =====================================================
# MENSAGEM E PEDIDO ESPECIAL
# =====================================================


st.divider()



col1,col2 = st.columns(2)



with col1:


    st.markdown(

        "### 💌 Mensagem da Cesta"

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

        height=75,

        key="pedido_especial"

    )







# =====================================================
# ENDEREÇO DE ENTREGA
# =====================================================


st.markdown(

    "### 📍 Endereço de Entrega"

)



st.text_area(

    "",

    value=pedido.get(

        "endereco",

        ""

    ),

    disabled=True,

    height=75,

    key="endereco_entrega"

)







# =====================================================
# FOTOS POLAROID
# =====================================================


st.divider()



st.markdown(

    "### 📷 Fotos da Polaroid"

)



try:


    fotos = listar_fotos(

        pedido["id"]

    )



    if fotos:



        colunas = st.columns(5)



        for i,foto in enumerate(fotos):


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

    height=100,

    placeholder="""

Exemplos:

- Cliente confirmou endereço
- Aguardando pagamento
- Alteração solicitada
- Observação da montagem

""",

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



except:


    valor_cesta = 0.0





# =====================================================
# FRETE / DESCONTO / STATUS
# =====================================================


col1,col2,col3 = st.columns(3)





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
# HORÁRIO DE ENTREGA
# =====================================================


st.markdown(

    "### 🕒 Horário da Entrega"

)



horario_combinado = st.text_input(

    "Horário combinado",

    value=pedido.get(

        "horario_combinado",

        ""

    ),

    placeholder="Ex: 15:30"

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


st.markdown(

f"""

<div class="resumo-card">


<table style="width:100%">


<tr>

<td>🎁 Cesta</td>

<td align="right">

<b>{formatar_valor(valor_cesta)}</b>

</td>

</tr>


<tr>

<td>🎀 Adicionais</td>

<td align="right">

<b>{formatar_valor(valor_adicionais)}</b>

</td>

</tr>


<tr>

<td>⚠️ Sob consulta</td>

<td align="right">

<b>{formatar_valor(valor_consulta)}</b>

</td>

</tr>


<tr>

<td>🚚 Frete</td>

<td align="right">

<b>{formatar_valor(valor_frete)}</b>

</td>

</tr>


<tr>

<td>🏷️ Desconto</td>

<td align="right">

<b>{formatar_valor(desconto)}</b>

</td>

</tr>


<tr>

<td colspan="2">

<hr>

</td>

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
# =====================================================
# WHATSAPP
# =====================================================

st.divider()


st.markdown(

    "### 📲 Atendimento WhatsApp"

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



        dados = {


            "status":

                status,


            "valor_frete":

                valor_frete,


            "desconto":

                desconto,


            "valor_total":

                valor_total_calculado,


            "horario_combinado":

                horario_combinado,


            "itens_consulta":

                itens_consulta


        }




        atualizar_pedido(

            pedido["id"],

            dados

        )





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
