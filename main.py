from __future__ import annotations

# import os
# from flask import Flask
# from services.whatsapp import whatsapp
from pyngrok import ngrok
from config.settings import settings

# Importa o app do módulo de rotas (que já registra /webhook e /)
# Ajuste o caminho abaixo se seu pacote de rotas for diferente.
from api.routes import app as api_app


def setup_ngrok():
    """
    Configura o túnel ngrok para desenvolvimento.
    - Usa NGROK_AUTHTOKEN (se existir)
    - Expõe a porta 5000
    - Imprime a URL pública e lembra o endpoint do webhook
    """
    if not settings.NGROK_AUTHTOKEN:
        print("⚠️  NGROK_AUTHTOKEN não configurado. Executando sem túnel público.")
        return None

    ngrok.set_auth_token(settings.NGROK_AUTHTOKEN)
    public_tunnel = ngrok.connect(5000, bind_tls=True)
    public_url = str(public_tunnel.public_url)
    print(f"✅ ngrok ativo: {public_url}")
    print(f"➡️  Configure o Webhook do WhatsApp com: {public_url}/webhook")
    print(f"🔐 VERIFY_TOKEN esperado: {settings.VERIFY_TOKEN}")
    return public_url


if __name__ == "__main__":
    # Em ambiente de dev, abrimos ngrok (se não estiver em produção)
    # Aqui mantemos sua lógica: se o token começar com 'prod_' entende-se produção.
    if not settings.WHATSAPP_TOKEN.startswith("prod_"):
        setup_ngrok()

    # Sobe o servidor Flask
    # Se quiser, pode usar settings.DEBUG para ativar o modo debug.
    api_app.run(host="0.0.0.0", port=5000, debug=getattr(settings, "DEBUG", False))
