import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def enviar_email_cobranca(email_destino, cliente_nome, pedido_id, resumo_texto, link_pagamento):
    """
    Monta e dispara um e-mail em formato HTML profissional com o resumo do pedido.
    """
    # Busca as credenciais configuradas no secrets.toml
    remetente = st.secrets.get("EMAIL_SENDER", "")
    senha = st.secrets.get("EMAIL_PASSWORD", "")
    
    if not remetente or not senha:
        return False, "⚠️ E-mail ou Senha não configurados nos Secrets do sistema."
        
    assunto = f"Detalhes do seu Pedido #{pedido_id} - Doce Cesta"
    
    # Criando o contêiner do e-mail
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = f"Doce Cesta <{remetente}>"
    msg["To"] = email_destino
    
    # Adiciona o botão de pagamento apenas se o link existir
    html_botao = ""
    if link_pagamento:
        html_botao = f"""
        <div style="text-align: center; margin-top: 25px;">
            <a href="{link_pagamento}" style="background-color: #137333; color: white; padding: 14px 24px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💳 CLIQUE AQUI PARA PAGAR</a>
        </div>
        """
        
    # HTML do E-mail (O layout bonito que o cliente vai ver)
    html = f"""
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.5; background-color: #f8fafc; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            
            <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 1px;">🧺 Doce Cesta</h1>
            </div>
            
            <div style="padding: 30px;">
                <h3 style="color: #0F172A; font-size: 18px; margin-top: 0;">Olá, {cliente_nome}!</h3>
                <p style="color: #475569; font-size: 15px;">Aqui está o resumo oficial do seu pedido. Por favor, verifique os dados abaixo:</p>
                
                <div style="background: #F8FAFC; padding: 15px; border-left: 4px solid #C5721F; border-radius: 6px; font-family: monospace; font-size: 14px; color: #1E293B; white-space: pre-wrap;">{resumo_texto}</div>
                
                {html_botao}
            </div>
            
            <div style="background-color: #F1F5F9; padding: 20px; text-align: center; font-size: 12px; color: #64748B;">
                <p style="margin: 0;">Obrigado por escolher a Doce Cesta Brasília!</p>
                <p style="margin: 5px 0 0 0;">Se tiver dúvidas, responda a este e-mail.</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(resumo_texto, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    try:
        # Comunicação com o servidor do Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, email_destino, msg.as_string())
        server.quit()
        return True, "✅ E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Erro ao enviar: {e}"
