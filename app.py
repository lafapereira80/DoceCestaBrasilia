import streamlit as st
from pathlib import Path


from services.pedido_service import salvar_pedido
from services.foto_service import salvar_fotos

from services.cesta_service import listar_cestas
from services.configuracao_cesta_service import carregar_configuracao_cesta

from services.produto_service import (
    listar_produtos,
    listar_categorias
)



st.set_page_config(
    page_title="Doce Cesta Brasília",
    page_icon="🎁",
    layout="centered",
    initial_sidebar_state="collapsed"
)



# ==========================================================
# CSS - DESIGN CLIENTE
# ==========================================================

st.markdown(
"""
<style>


section[data-testid="stSidebar"]{
    display:none;
}


[data-testid="collapsedControl"]{
    display:none;
}


header{
    visibility:hidden;
}


footer{
    visibility:hidden;
}


#MainMenu{
    visibility:hidden;
}



.block-container{

    max-width:720px;

    padding-top:15px;

    padding-bottom:30px;

}



h1{

    font-size:26px !important;

}


h2{

    font-size:20px !important;

}


h3{

    font-size:17px !important;

    color:#8B5A2B;

}



p, label, div{

    font-size:14px;

}



/* CAMPOS */

div[data-baseweb="input"]{

    background:white;

    border-radius:10px;

    border:1px solid #c9b8a8;

}



div[data-baseweb="input"]:focus-within{

    border:2px solid #8B5A2B;

}



input{

    height:42px !important;

    font-size:15px !important;

}



textarea{

    font-size:15px !important;

    border-radius:10px !important;

}



/* SELECT */

div[data-baseweb="select"] > div{

    border-radius:10px;

    border:1px solid #c9b8a8;

}



/* RADIO */

div[role="radiogroup"]{

    gap:12px;

}



/* CHECKBOX */

div[data-testid="stCheckbox"]{

    background:#fffaf5;

    padding:8px;

    border-radius:8px;

}



/* BOTÃO */

.stButton button{

    background:#8B5A2B;

    color:white;

    border-radius:12px;

    height:52px;

    font-size:16px;

    font-weight:bold;

    width:100%;

}



.stButton button:hover{

    background:#6f451f;

}



</style>
""",
unsafe_allow_html=True
)



# ==========================================================
# LOGO
# ==========================================================


logo = Path(
    "assets/logo.webp"
)



if logo.exists():


    col1,col2,col3 = st.columns(
        [2,1,2]
    )


    with col2:

        st.image(
            str(logo),
            width=130
        )



st.markdown(
"""
<h1 style="
text-align:center;
color:#8B5A2B;
margin-bottom:0;
">
Doce Cesta Brasília
</h1>
""",
unsafe_allow_html=True
)



st.markdown(
"""
<p style="
text-align:center;
margin-top:5px;
">
Cestas personalizadas para momentos especiais 💝
</p>
""",
unsafe_allow_html=True
)



# ==========================================================
# FORMULÁRIO
# ==========================================================


st.markdown(
"### 📝 Faça seu pedido"
)



# ==========================================================
# CLIENTE
# ==========================================================


st.markdown(
"### 👤 Seus dados"
)



col1,col2 = st.columns(2)



with col1:

    nome = st.text_input(
        "Nome completo *",
        placeholder="Digite seu nome"
    )



with col2:

    telefone = st.text_input(
        "Telefone *",
        placeholder="(61) 99999-9999"
    )



cpf = st.text_input(
    "CPF *",
    placeholder="000.000.000-00"
)



# ==========================================================
# CESTAS
# ==========================================================


try:

    cestas = listar_cestas()


except Exception as erro:

    st.error(
        f"Erro ao carregar cestas: {erro}"
    )

    st.stop()



if not cestas:

    st.warning(
        "Nenhuma cesta cadastrada."
    )

    st.stop()



st.markdown(
"### 🎁 Escolha sua cesta"
)



cesta = st.selectbox(

    "Selecione a cesta",

    cestas,

    format_func=lambda c:
        c["nome"]

)



if cesta:


    col1,col2 = st.columns(
        [1,2]
    )


    with col1:

        if cesta.get("imagem"):

            st.image(
                cesta["imagem"],
                use_container_width=True
            )



    with col2:

        if cesta.get("descricao"):

            st.info(
                cesta["descricao"]
            )
            # ==========================================================
# PERSONALIZAÇÃO DA CESTA
# ==========================================================


st.markdown(
    "### 🍓 Personalize sua cesta"
)



configuracao = carregar_configuracao_cesta(
    cesta["id"]
)



selecoes_cliente = {}



if configuracao:


    for grupo in configuracao:


        categoria = grupo["categoria"]

        quantidade = grupo["quantidade"]

        produtos = grupo["produtos"]



        with st.container(border=True):


            st.markdown(
                f"**{categoria}**"
            )



            if quantidade == 1:


                escolhido = st.radio(

                    "",

                    produtos,

                    format_func=lambda p:
                        p["nome"],

                    key=f"radio_{categoria}"

                )


                selecoes_cliente[categoria] = [

                    escolhido

                ]



            else:


                escolhidos = st.multiselect(

                    f"Escolha até {quantidade}",

                    produtos,

                    format_func=lambda p:
                        p["nome"],

                    max_selections=quantidade,

                    key=f"multi_{categoria}"

                )


                selecoes_cliente[categoria] = escolhidos



else:


    st.info(
        "Esta cesta ainda não possui produtos configurados."
    )





# ==========================================================
# ADICIONAIS DINÂMICOS
# ==========================================================


st.markdown(
"### 🎀 Adicionais"
)



# Busca produtos e categorias

try:

    categorias = listar_categorias()

    produtos = listar_produtos()


except Exception as erro:


    st.error(
        f"Erro ao carregar adicionais: {erro}"
    )

    st.stop()



# Monta relação categoria -> nome

categorias_dict = {

    categoria["id"]: categoria["nome"]

    for categoria in categorias

}



# Filtra somente categoria Adicionais

lista_adicionais = []



for produto in produtos:


    nome_categoria = categorias_dict.get(

        produto["categoria_id"],

        ""

    )


    if nome_categoria == "Adicionais":


        lista_adicionais.append(
            produto
        )



adicionais_selecionados = []



with st.container(border=True):


    if not lista_adicionais:


        st.info(
            "Nenhum adicional cadastrado."
        )


    else:


        col1,col2 = st.columns(2)



        for i, adicional in enumerate(lista_adicionais):


            coluna = col1 if i % 2 == 0 else col2



            with coluna:


                escolhido = st.checkbox(

                    adicional["nome"],

                    key=f"adicional_{adicional['id']}"

                )



                if escolhido:


                    adicionais_selecionados.append(
                        adicional
                    )





# ==========================================================
# IDENTIFICA POLAROID
# ==========================================================


possui_polaroid = any(


    "polaroid"

    in

    adicional["nome"].lower()


    for adicional in adicionais_selecionados


)





# ==========================================================
# ENVIO DE FOTOS POLAROID
# ==========================================================


if possui_polaroid:


    st.markdown(
        "### 📷 Envie as fotos da Polaroid"
    )



    fotos = st.file_uploader(


        "Fotos para impressão",


        type=[


            "jpg",

            "jpeg",

            "png",

            "webp"


        ],


        accept_multiple_files=True


    )


else:


    fotos = []





# ==========================================================
# PAGAMENTO
# ==========================================================


st.markdown(
"### 💳 Pagamento"
)



with st.container(border=True):


    pagamento = st.radio(

        "",

        [

            "Pix",

            "Cartão de Crédito"

        ],

        horizontal=True

    )
    # ==========================================================
# MENSAGEM
# ==========================================================


st.markdown(
"### 💌 Mensagem"
)



mensagem = st.text_area(

    "Mensagem que acompanhará a cesta",

    height=100,

    placeholder="Digite uma mensagem especial..."

)





# ==========================================================
# PEDIDO ESPECIAL
# ==========================================================


st.markdown(
"### ✨ Pedido especial"
)



pedido_especial = st.text_area(

    "Alguma solicitação especial?",

    height=100,

    placeholder="Exemplo: entregar pela manhã..."

)





# ==========================================================
# ENTREGA
# ==========================================================


st.markdown(
"### 📍 Entrega"
)



endereco = st.text_area(

    "Endereço de entrega",

    height=100,

    placeholder="Informe o endereço completo..."

)



col1,col2 = st.columns(2)



with col1:


    data_entrega = st.date_input(

        "📅 Data"

    )



with col2:


    periodo_entrega = st.selectbox(

        "🕘 Período",

        [

            "Manhã",

            "Tarde",

            "Noite"

        ]

    )





# ==========================================================
# BOTÃO
# ==========================================================


st.divider()



enviar = st.button(

    "🎁 ENVIAR PEDIDO",

    use_container_width=True,

    type="primary"

)





# ==========================================================
# PROCESSAMENTO
# ==========================================================


if enviar:



    if not nome.strip():

        st.error(
            "Informe o nome do cliente."
        )

        st.stop()



    if not cpf.strip():

        st.error(
            "Informe o CPF."
        )

        st.stop()



    if not telefone.strip():

        st.error(
            "Informe o telefone."
        )

        st.stop()





    # ======================================================
    # ADICIONAIS SELECIONADOS
    # ======================================================


    adicionais = []



    for adicional in adicionais_selecionados:


        adicionais.append(

            adicional["nome"]

        )





    # ======================================================
    # PRODUTOS ESCOLHIDOS DA CESTA
    # ======================================================


    produtos_escolhidos = []



    for categoria,itens in selecoes_cliente.items():



        for item in itens:



            produtos_escolhidos.append(


                f"{categoria}: {item['nome']}"


            )





    # ======================================================
    # DADOS DO PEDIDO
    # ======================================================


    dados = {



        "cliente_nome":

            nome,



        "cliente_cpf":

            cpf,



        "cliente_telefone":

            telefone,



        "cesta_id":

            cesta["id"],



        "cesta_nome":

            cesta["nome"],



        "produtos":

            "\n".join(

                produtos_escolhidos

            ),



        "adicionais":

            ", ".join(

                adicionais

            ),



        "pagamento":

            pagamento,



        "mensagem":

            mensagem,



        "pedido_especial":

            pedido_especial,



        "endereco":

            endereco,



        "data_entrega":

            str(data_entrega),



        "periodo_entrega":

            periodo_entrega,



        "status":

            "Recebido",



        "valor_frete":

            0,



        "valor_total":

            0

    }





    sucesso,pedido_id = salvar_pedido(

        dados

    )





    if sucesso:




        # ==================================================
        # SALVA FOTOS POLAROID
        # ==================================================


        if possui_polaroid and fotos:



            try:


                salvar_fotos(

                    pedido_id,

                    fotos

                )



            except Exception as erro:



                st.warning(

                    f"Pedido salvo, mas houve erro nas fotos: {erro}"

                )





        st.success(

            "🎉 Pedido enviado com sucesso!"

        )



        st.info(

"""
❤️ Obrigado por escolher a **Doce Cesta Brasília**!

Recebemos seu pedido.

Nossa equipe entrará em contato para confirmar:

✅ Valor do frete  
✅ Valor final da cesta  
✅ Detalhes da entrega

"""

        )





    else:


        st.error(

            f"Erro ao salvar pedido: {pedido_id}"

        )





# ==========================================================
# RODAPÉ
# ==========================================================


st.divider()



st.markdown(

"""
<div style="
text-align:center;
font-size:12px;
padding:15px;
">

© 2026 Doce Cesta Brasília

</div>

""",

unsafe_allow_html=True

)



st.page_link(

    "pages/99_Admin.py",

    label="Área Administrativa",

    icon="🔒"

)
