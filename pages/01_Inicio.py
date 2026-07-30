import streamlit as st
import pandas as pd
import requests
import re
import uuid
from datetime import datetime, date
from config.supabase import supabase
from services.cesta_service import listar_cestas
from services.pedido_service import salvar_pedido
from utils.menu import configurar_pagina

st.set_page_config(page_title="Doce Cesta Brasília", page_icon="🧺", layout="centered")
configurar_pagina()

# ==========================================
# CSS PREMIUM (CATÁLOGO E FORMULÁRIO)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Dancing+Script:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; color: #4a2e1b !important; }

.header-loja { background: linear-gradient(135deg, #ffffff 0%, #fdfbf8 100%); padding: 30px; border-radius: 20px; border: 1px solid #e8ddd3; text-align: center; margin-bottom: 25px;}
.loja-title { font-family: 'Dancing Script', cursive !important; font-size: 52px !important; color: #c5721f; margin: 0; line-height: 1.1; }
.loja-sub { font-size: 16px; color: #775a46; font-weight: 600; margin-top: 5px; }

.box-etapa { background: #ffffff; border: 1px solid #e8ddd3; border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
.box-title { font-size: 20px; font-weight: 800; color: #c5721f; border-bottom: 2px dashed #f5eee6; padding-bottom: 10px; margin-bottom: 15px; }

.cesta-desc-box { background: #fffcf8; border-left: 4px solid #c5721f; padding: 15px; margin-top: 10px; border-radius: 0 8px 8px 0; font-size: 14px; color: #5a3b28;}

.polaroid-box { background: #fff8f8; border: 2px dashed #ffb6c1; border-radius: 12px; padding: 15px; margin-top: 15px;}

div[data-testid="stButton"] button[kind="primary"] { border-radius: 12px !important; font-weight: 800 !important; background: linear-gradient(135deg, #c5721f 0%, #a65d14) !important; color: white !important; border: none !important; padding: 10px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-loja">
    <h1 class="loja-title">Monte sua Cesta</h1>
    <p class="loja-sub">Personalize seu presente com amor e agende a entrega ❤️</p>
</div>
""", unsafe_allow_html=True)

# FUNÇÕES
def tratar_preco(valor):
    if valor is None or str(valor).strip() == "": return 0.0
    try: return float(str(valor).replace(",", "."))
    except: return 0.0

def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def buscar_cep_api(cep_str):
    cep_limpo = re.sub(r'\D', '', cep_str)
    if len(cep_limpo) != 8: return False, "CEP inválido."
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        if r.status_code == 200:
            dados = r.json()
            if "erro" in dados: return False, "CEP não encontrado."
            return True, dados
    except: pass
    return False, "Erro na busca."

@st.cache_data(ttl=60)
def carregar_dados_loja():
    cestas = sorted([c for c in listar_cestas() if c.get("ativa", True)], key=lambda x: x.get("nome", ""))
    try:
        res = supabase.table("produtos").select("*").execute()
        todos_produtos = [p for p in (res.data or []) if p.get("ativo", True)]
        adicionais = [p for p in todos_produtos if "adicional" in p.get("categoria", "").strip().lower()]
        return cestas, adicionais, todos_produtos
    except: return cestas, [], []

cestas_disp, adicionais_disp, todos_produtos = carregar_dados_loja()

# Sessões do CEP do Cliente
for key in ["cli_cep", "cli_rua", "cli_num", "cli_comp", "cli_bairro", "cli_cid", "cli_uf"]:
    if key not in st.session_state: st.session_state[key] = ""

# 1. ESCOLHA A CESTA
st.markdown('<div class="box-etapa"><div class="box-title">1️⃣ Escolha o Pacote Principal</div>', unsafe_allow_html=True)
cesta_sel = st.selectbox("Selecione a cesta que deseja presentear:", [None] + cestas_disp, format_func=lambda x: f"{x['nome']} (R$ {tratar_preco(x.get('preco')):.2f})" if x else "Clique aqui para escolher...")

opcoes_selecionadas = []
preco_cesta = 0.0

if cesta_sel:
    preco_cesta = tratar_preco(cesta_sel.get("preco"))
    # Exibe a DESCRIÇÃO DA CESTA (A correção principal solicitada!)
    st.markdown(f"""
    <div class="cesta-desc-box">
        <b>O que vem nesta cesta?</b><br>
        {cesta_sel.get('descricao', 'Descrição não informada.')}
    </div>
    """, unsafe_allow_html=True)
    
    # Verifica se a cesta tem opções selecionáveis
    itens_vinculados = [p for p in todos_produtos if p.get("cesta_id") == cesta_sel["id"]]
    if itens_vinculados:
        st.markdown("<div style='margin-top: 15px; font-weight: 700; color: #c5721f;'>Opções de Personalização da sua Cesta:</div>", unsafe_allow_html=True)
        opcoes_selecionadas = st.multiselect("Selecione os sabores/itens desejados:", itens_vinculados, format_func=lambda x: x["nome"])
st.markdown('</div>', unsafe_allow_html=True)

# 2. ADICIONAIS GLOBAIS
st.markdown('<div class="box-etapa"><div class="box-title">2️⃣ Incremente seu Presente (Opcional)</div>', unsafe_allow_html=True)
adicionais_selecionados = st.multiselect(
    "Adicione chocolates, balões, pelúcias:", 
    adicionais_disp, 
    format_func=lambda x: f"{x['nome']} (+ R$ {tratar_preco(x.get('preco')):.2f})"
)

# 3. UPLOAD DE FOTOS E MENSAGEM
st.markdown('<div class="box-etapa"><div class="box-title">3️⃣ Emoção e Mensagem</div>', unsafe_allow_html=True)
mensagem = st.text_area("Mensagem do Cartão (Enviada impressa junto ao presente):", placeholder="Escreva aqui tudo o que o seu coração mandar...")

tem_polaroid = any("polaroid" in adc["nome"].lower() or "foto" in adc["nome"].lower() for adc in adicionais_selecionados)
fotos_enviadas = []
if tem_polaroid:
    st.markdown("""
    <div class="polaroid-box">
        <h4 style="color: #d1476a; margin-top: 0;">📸 Envie suas Fotos Polaroid</h4>
        <p style="font-size: 13px; color: #5a3b28;">Você adicionou fotos ao pedido! Faça o upload das imagens que deseja revelar.</p>
    </div>
    """, unsafe_allow_html=True)
    fotos_enviadas = st.file_uploader("Selecione as fotos do seu dispositivo", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

st.markdown('</div>', unsafe_allow_html=True)

# 4. ENDEREÇO E LOGÍSTICA
st.markdown('<div class="box-etapa"><div class="box-title">4️⃣ Entrega e Destinatário</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 2])
with c1:
    cep_input = st.text_input("CEP de Entrega", value=st.session_state.cli_cep)
with c2:
    st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
    if st.button("Buscar Endereço"):
        ok, dados = buscar_cep_api(cep_input)
        if ok:
            st.session_state.cli_cep = cep_input
            st.session_state.cli_rua = dados.get("logradouro", "")
            st.session_state.cli_bairro = dados.get("bairro", "")
            st.session_state.cli_cid = dados.get("localidade", "")
            st.session_state.cli_uf = dados.get("uf", "")
            st.rerun()

col_end1, col_end2, col_end3 = st.columns([3, 1, 2])
rua = col_end1.text_input("Rua", value=st.session_state.cli_rua)
num = col_end2.text_input("Número")
comp = col_end3.text_input("Complemento")
bairro = st.text_input("Bairro", value=st.session_state.cli_bairro)

st.write("")
col_ent1, col_ent2 = st.columns(2)
with col_ent1:
    data_entrega = st.date_input("Qual a Data da Entrega?", value=date.today(), format="DD/MM/YYYY")
with col_ent2:
    horario = st.text_input("Horário Desejado", placeholder="Ex: Entre 08h e 10h")

dest_nome = st.text_input("Nome da Pessoa que vai Receber *", placeholder="Ex: Ana Souza")
dest_tel = st.text_input("Telefone de Contato de Quem vai Receber", placeholder="Ex: (61) 99999-9999")
st.markdown('</div>', unsafe_allow_html=True)

# 5. DADOS DO COMPRADOR E FINALIZAÇÃO
st.markdown('<div class="box-etapa"><div class="box-title">5️⃣ Seus Dados e Pagamento</div>', unsafe_allow_html=True)

comprador_nome = st.text_input("Seu Nome Completo *")
comprador_tel = st.text_input("Seu WhatsApp *")
forma_pagamento = st.selectbox("Forma de Pagamento Desejada", ["Pix", "Cartão de Crédito"])

# CÁLCULOS
soma_adicionais = sum(tratar_preco(a.get("preco")) for a in adicionais_selecionados)
taxa_frete_fixa = 15.0 # Taxa padrão da loja (Pode ajustar no banco depois)
total_final = preco_cesta + soma_adicionais + taxa_frete_fixa

st.markdown(f"""
<div style="background: #fffcf8; border: 2px solid #c5721f; border-radius: 12px; padding: 20px; text-align: center; margin-top: 20px;">
    <span style="font-size: 16px; font-weight: 700; color: #775a46;">VALOR TOTAL (Com Frete de Entrega Incluso): </span><br>
    <span style="font-size: 32px; font-weight: 800; color: #137333;">R$ {formatar_moeda(total_final)}</span>
</div>
""", unsafe_allow_html=True)

st.write("")
if st.button("🚀 ENVIAR MEU PEDIDO AGORA", type="primary", use_container_width=True):
    if not cesta_sel: st.error("Por favor, selecione uma cesta no Passo 1."); st.stop()
    if not dest_nome: st.error("Informe quem vai receber o presente."); st.stop()
    if not rua or not num: st.error("Preencha o endereço completo de entrega."); st.stop()
    if not comprador_nome or not comprador_tel: st.error("Preencha seus dados de contato."); st.stop()

    with st.spinner("Preparando o seu pedido mágico..."):
        # UPLOAD DE POLAROIDS NO SUPABASE
        links_polaroid = []
        if tem_polaroid and fotos_enviadas:
            for foto in fotos_enviadas:
                ext = foto.name.split('.')[-1]
                file_name = f"polaroid_{uuid.uuid4().hex}.{ext}"
                try:
                    supabase.storage.from_("polaroids").upload(file_name, foto.read(), {"content-type": foto.type})
                    url = supabase.storage.from_("polaroids").get_public_url(file_name)
                    links_polaroid.append(url)
                except Exception as e:
                    pass

        # MONTAGEM DA STRING DE PRODUTOS
        desc_cesta_bd = cesta_sel['descricao']
        if opcoes_selecionadas:
            desc_cesta_bd += f" | Opções escolhidas: {', '.join([o['nome'] for o in opcoes_selecionadas])}"
        
        produto_txt = f"1x {cesta_sel['nome']} (R$ {formatar_moeda(preco_cesta)})"
        
        adicionais_txt = "Nenhum adicional."
        if adicionais_selecionados:
            adicionais_txt = "ADICIONAIS:\n" + "\n".join([f"1x {a['nome']} (R$ {formatar_moeda(tratar_preco(a.get('preco')))})" for a in adicionais_selecionados])

        if links_polaroid:
            adicionais_txt += "\n\n📸 LINKS FOTOS POLAROID:\n" + "\n".join(links_polaroid)

        endereco_completo = f"{rua}, {num} - {comp} - {bairro}, {st.session_state.cli_cid}-{st.session_state.cli_uf}"

        dados_cliente = {
            "cliente_nome": comprador_nome.strip(),
            "cliente_telefone": comprador_tel.strip(),
            "cliente_cpf": "00000000000",
            "destinatario_nome": dest_nome.strip(),
            "destinatario_telefone": dest_tel.strip(),
            "motivo_homenagem": "Site",
            "cesta_id": cesta_sel['id'],
            "cesta_nome": cesta_sel['nome'],
            "produtos": produto_txt,
            "adicionais": adicionais_txt,
            "pagamento": forma_pagamento,
            "mensagem": mensagem.strip(),
            "endereco": endereco_completo,
            "data_entrega": data_entrega.strftime("%Y-%m-%d"),
            "periodo_entrega": horario.strip() or "A combinar",
            "status": "Recebido",
            "valor_frete": taxa_frete_fixa,
            "valor_total": total_final,
            "cesta_montada": False
        }
        
        sucesso, p_id = salvar_pedido(dados_cliente)
        
        if sucesso:
            st.success("🎉 Seu pedido foi enviado com sucesso para a nossa equipe!")
            st.balloons()
            st.info("Nós entraremos em contato via WhatsApp rapidamente para confirmar os detalhes e a forma de pagamento.")
        else:
            st.error("Poxa, tivemos um erro ao enviar seu pedido. Tente nos contatar pelo WhatsApp direto.")

st.markdown('</div>', unsafe_allow_html=True)
