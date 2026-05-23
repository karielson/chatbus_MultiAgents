import requests
from typing import Dict, Any, Optional
from config.settings import settings


class WhatsAppService:
    """
    Envio de mensagens via WhatsApp Cloud API.
    Espera que settings contenha:
      - WHATSAPP_API_URL (ex.: https://graph.facebook.com/v19.0/<PHONE_ID>/messages)
      - WHATSAPP_TOKEN
    """

    def __init__(self, session: Optional[requests.Session] = None):
        self.api_url = settings.WHATSAPP_API_URL
        self.token = settings.WHATSAPP_TOKEN
        self.session = session or requests.Session()

    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Envia uma mensagem de texto simples (limite ~4000 chars).
        """
        if not message:
            message = " "  # evita payload inválido

        # Corte de segurança: Cloud API geralmente aceita até ~4096 chars
        body = message.replace("\r\n", "\n")[:4000]

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": body},
        }

        resp = self.session.post(self.api_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()


whatsapp = WhatsAppService()
