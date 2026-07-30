import streamlit as st
import pandas as pd
from datetime import datetime, date
from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.pedido_service import salvar_pedido
from utils.menu import configurar_pagina, menu_lateral
from utils.permissao import administrador_operador

st.set_page_config(page_title="Novo Pedido Varejo (Manual)", page_icon="🛒", layout="wide")
configurar_pagina()
menu_lateral()
administrador_operador()

# ==========================================
# CSS PREMIUM
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b; }

.header-banner {
    background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 25px;
    border-radius: 20px; border: 1px solid #e8ddd3; box-shadow: 0 8px 24px rgba(90, 59, 40, 0.04);
    text-align: center; margin-bottom: 25px;
}
.header-title { font-family: 'Dancing Script', cursive !important; font-size: 42px; font-weight: 700; color: #c5721f; margin: 0; }
.header-sub { font-size: 14px; font-weight: 600; color: #775a46; }

.card-form { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1 class="header-title">Novo Pedido Manual (Varejo / PF)</h1>
    <p class="header-sub">Registre vendas realizadas via WhatsApp, Telefone ou Loja Física 🛒</p>
</div>
""", unsafe_allow_html=True)

# Função para blindar preços nulos
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

# Carrega Cestas e Produtos Adicionais
@st.cache_data(ttl=60, show_spinner=False)
def get_dados():
    cestas = [c for c in listar_cestas() if c.get("ativa", True)]
    try:
        res = supabase.table("produtos").select("*").execute()
        produtos = [p for p in (res.data or []) if p.get("ativo", True)]
    except:
        produtos = []
    return cestas, produtos

cestas_disp, produtos_disp = get_dados()

with st.container():
    st.markdown('<div class="card-form">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👤 Dados do Cliente (Comprador)")
        cliente_nome = st.text_input("Nome do Cliente *", placeholder="Ex: Maria da Silva")
        cliente_tel = st.text_input("Telefone / WhatsApp *", placeholder="Ex: (61) 98888-8888")
        cliente_cpf = st.text_input("CPF (Opcional)", placeholder="Apenas números")
        
    with col2:
        st.markdown("#### 🎁 Destinatário e Homenagem")
        dest_nome = st.text_input("Nome de Quem Vai Receber", placeholder="Ex: João Pedro (Se for a mesma pessoa, repita)")
        dest_tel = st.text_input("Telefone do Destinatário", placeholder="Ex: (61) 97777-7777")
        motivo = st.text_input("Motivo / Ocasião", placeholder="Ex: Aniversário, Dia das Mães, Declaração")

    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 📦 Escolha do Pacote / Cesta")
        cesta_escolhida = st.selectbox("Selecione a Cesta Principal", [None] + cestas_disp, format_func=lambda x: f"{x['nome']} - R$ {tratar_preco(x.get('preco')):.2f}" if x else "Selecione...")
        
        # Adicionais opcionais com proteção de preço
        adicionais_selecionados = st.multiselect(
            "Adicionais Extras para esta Cesta", 
            produtos_disp, 
            format_func=lambda x: f"{x['nome']} (+ R$ {tratar_preco(x.get('preco')):.2f})"
        )
        
    with col4:
        st.markdown("#### 💌 Mensagem do Cartão")
        mensagem_cartao = st.text_area("Texto que irá impresso no cartão", placeholder="Ex: Com todo meu amor, feliz aniversário! De: Carlos", height=128)

    st.markdown("<hr style='border-top: 1px dashed #e8ddd3; margin: 20px 0;'>", unsafe_allow_html=True)
    
    st.markdown("#### 📍 Logística e Pagamento")
    col5, col6, col7 = st.columns(3)
    with col5:
        data_entrega = st.date_input("Data da Entrega", value=date.today(), format="DD/MM/YYYY")
        periodo = st.selectbox("Período", ["Manhã (08h às 12h)", "Tarde (13h às 18h)", "Comercial", "Horário Marcado"])
    with col6:
        valor_frete = st.number_input("Taxa de Frete (R$)", min_value=0.0, step=5.0, value=15.0)
        forma_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Cartão de Crédito", "Dinheiro", "Link de Pagamento"])
    with col7:
        status_inicial = st.selectbox("Status Inicial do Pedido", ["Recebido", "Pago"])

    endereco = st.text_input("📍 Endereço Completo de Entrega", placeholder="SQS 202, Bloco C, Apto 204 - Asa Sul, Brasília - DF")

    # Cálculo do Valor Total Seguro
    preco_cesta = tratar_preco(cesta_escolhida.get("preco")) if cesta_escolhida else 0.0
    soma_adicionais = sum(tratar_preco(a.get("preco")) for a in adicionais_selecionados)
    valor_total_pedido = preco_cesta + soma_adicionais + valor_frete

    st.markdown(f"""
    <div style="background: #fdfbf8; border: 1px solid #e8ddd3; border-radius: 12px; padding: 15px; text-align: right; margin-top: 20px;">
        <span style="font-size: 14px; font-weight: 700; color: #775a46;">VALOR TOTAL DO PEDIDO: </span>
        <span style="font-size: 24px; font-weight: 800; color: #137333;">R$ {valor_total_pedido:,.2f}</span>
    </div>
    """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

    st.write("")
    if st.button("✅ REGISTRAR PEDIDO DE VAREJO", type="primary", use_container_width=True):
        if not cliente_nome: st.error("Informe o nome do cliente."); st.stop()
        if not cliente_tel: st.error("Informe o telefone do cliente."); st.stop()
        if not cesta_escolhida: st.error("Selecione ao menos uma cesta principal."); st.stop()
        if not endereco: st.error("Informe o endereço de entrega."); st.stop()

        lista_produtos = [f"1x {cesta_escolhida['nome']} (R$ {preco_cesta:.2f})"]
        lista_extras_txt = []
        for adc in adicionais_selecionados:
            lista_extras_txt.append(f"1x {adc['nome']} (R$ {tratar_preco(adc.get('preco')):.2f})")

        msg_adicionais = "Nenhum adicional."
        if lista_extras_txt:
            msg_adicionais = "ADICIONAIS:\n" + "\n".join(lista_extras_txt)

        dados_pedido = {
            "cliente_nome": cliente_nome.strip(),
            "cliente_telefone": cliente_tel.strip(),
            "cliente_cpf": cliente_cpf.strip() or "00000000000",
            "destinatario_nome": dest_nome.strip() or cliente_nome.strip(),
            "destinatario_telefone": dest_tel.strip() or cliente_tel.strip(),
            "motivo_homenagem": motivo.strip() or "Varejo",
            "cesta_id": cesta_escolhida['id'],
            "cesta_nome": cesta_escolhida['nome'],
            "produtos": "\n".join(lista_produtos),
            "adicionais": msg_adicionais,
            "pagamento": forma_pagamento,
            "mensagem": mensagem_cartao.strip(),
            "endereco": endereco.strip(),
            "data_entrega": data_entrega.strftime("%Y-%m-%d"),
            "periodo_entrega": periodo,
            "status": status_inicial,
            "valor_frete": valor_frete,
            "valor_total": valor_total_pedido,
            "cesta_montada": False
        }

        sucesso, p_id = salvar_pedido(dados_pedido)
        if sucesso:
            st.success(f"🎉 Pedido de varejo para **{cliente_nome}** cadastrado com sucesso e enviado para a produção!")
            st.balloons()
        else:
            st.error("Erro ao registrar o pedido no banco de dados.")

    st.markdown('</div>', unsafe_allow_html=True)
