# ==========================================================
# PASSO 6: RESUMO E FECHAMENTO
# ==========================================================
with st.container(border=True):
    renderizar_passo("6", "Pagamento e Resumo")
    
    pagamento = st.radio("Como você prefere pagar?", ["Pix (Aprovação Imediata)", "Cartão de Crédito"], horizontal=True, key="forma_pagamento_radio")

valor_base = float(cesta_obj.get("preco", 0)) if cesta_obj and cesta_obj.get("preco") is not None else 0
valor_adicionais = sum([float(item["preco"]) for item in adicionais_selecionados if item["preco"] is not None])
tem_consulta = any(item["preco"] is None for item in adicionais_selecionados)
total_estimado = valor_base + valor_adicionais

valor_base_fmt = f"R$ {valor_base:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
valor_adc_fmt = f"R$ {valor_adicionais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
total_fmt = f"R$ {total_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Lógica para ocultar a linha de Mimos se for R$ 0,00
linha_extras_html = ""
if valor_adicionais > 0:
    linha_extras_html = f'<div class="receipt-line"><span>🎀 Mimos Extras</span> <strong>{valor_adc_fmt}</strong></div>'

if cesta_obj:
    with st.container(border=True):
        st.markdown(f"""
        <div class="receipt-box">
            <div style="font-size: 16px; font-weight: 800; color: #5a3b28; margin-bottom: 15px; text-align: center;">RESUMO DO PEDIDO</div>
            
            <div class="receipt-line"><span>🎁 <b>{cesta_obj['nome']}</b></span> <strong>{valor_base_fmt}</strong></div>
            {linha_extras_html}
            <div class="receipt-line"><span>🚚 Taxa de Entrega</span> <strong>A calcular pelo WhatsApp</strong></div>
            
            <div class="receipt-total">
                <span>SUBTOTAL:</span> 
                <span>{total_fmt}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if tem_consulta:
            st.warning("⚠️ **Nota:** Você incluiu itens '*Sob Consulta*'. O valor exato será confirmado por nossa equipe.")
