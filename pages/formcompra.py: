import requests  # Certifique-se de que requests está no seu requirements.txt

# 1. Campo de CEP com gatilho de busca
cep_input = st.text_input("CEP de Entrega (Apenas números)", max_chars=8, placeholder="Ex: 70000000")

# Inicializa variáveis do endereço no session_state se não existirem
if "end_rua" not in st.session_state: st.session_state.end_rua = ""
if "end_bairro" not in st.session_state: st.session_state.end_bairro = ""
if "end_cidade" not in st.session_state: st.session_state.end_cidade = ""

# Se o CEP tiver 8 dígitos, busca automaticamente na API da ViaCEP
if len(cep_input) == 8 and cep_input.isdigit():
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep_input}/json/")
        if response.status_code == 200:
            dados_cep = response.json()
            if "erro" not in dados_cep:
                # Atualiza os estados com os dados retornados pelo CEP
                st.session_state.end_rua = dados_cep.get("logradouro", "")
                st.session_state.end_bairro = dados_cep.get("bairro", "")
                st.session_state.end_cidade = f"{dados_cep.get('localidade', '')} - {dados_cep.get('uf', '')}"
    except Exception:
        pass

# 2. Exibe os campos de endereço (já preenchidos ou liberados para edição/complemento)
rua = st.text_input("Endereço (Rua, Quadra, Lote)", value=st.session_state.end_rua)
numero = st.text_input("Número / Complemento", placeholder="Ex: Bloco A, Apto 202")
bairro = st.text_input("Bairro", value=st.session_state.end_bairro)
cidade = st.text_input("Cidade - UF", value=st.session_state.end_cidade)

# Você pode juntar tudo em uma string final de endereço para salvar no seu banco (Supabase)
endereco_completo = f"{rua}, {numero} - {bairro}, {cidade} (CEP: {cep_input})"
