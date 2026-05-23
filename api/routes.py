# routes.py
from __future__ import annotations

from flask import Flask, request, jsonify
from config.settings import settings
from services.whatsapp import whatsapp

# >>> NOVO: Coordenador (Agno Team)
from agents.coordenador import coordenador

import os
import traceback

app = Flask(__name__)


def _run_coordinator(message: str, user_id: str) -> str:
    """
    Executa o coordenador do Agno e retorna a resposta final como string.
    Usa streaming para juntar os pedaços da resposta.
    """
    chunks = []
    try:
        for rr in coordenador.run(message, stream=True, user_id=user_id):
            if getattr(rr, "content", None):
                chunks.append(str(rr.content))
        # fallback caso nada tenha vindo via stream
        if not chunks and getattr(coordenador, "run_response", None):
            content = getattr(coordenador.run_response, "content", "")
            if content:
                chunks.append(str(content))
    except Exception:
        traceback.print_exc()
    return ("".join(chunks)).strip() or "Desculpe, não consegui gerar uma resposta agora."


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Verificação do WhatsApp (GET)
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token != settings.VERIFY_TOKEN:
            return "Token inválido", 403
        return challenge, 200

    # Recepção de mensagens (POST)
    try:
        data = request.get_json(silent=True) or {}
        if not data or "entry" not in data:
            return "EVENT_RECEIVED", 200

        changes = data["entry"][0].get("changes", [])
        if not changes:
            return "EVENT_RECEIVED", 200

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return "EVENT_RECEIVED", 200

        # Percorre todas as mensagens recebidas
        for message in messages:
            phone_number = message.get("from")
            msg_type = message.get("type")

            # Garante que temos número e tipo
            if not phone_number or not msg_type:
                continue

            try:
                # === Texto ===
                if msg_type == "text":
                    user_text = (message.get("text", {}) or {}).get("body", "")
                    user_text = (user_text or "").strip()
                    if not user_text:
                        whatsapp.send_message(
                            phone_number,
                            "Não entendi a mensagem. Por favor, envie um texto. 🙏",
                        )
                        continue

                    # Chama o coordenador (Agno Team) com user_id = número
                    response_text = _run_coordinator(user_text, user_id=phone_number)
                    whatsapp.send_message(phone_number, response_text)

                # === Localização ===
                elif msg_type == "location":
                    loc = message.get("location", {}) or {}
                    lat = loc.get("latitude")
                    lng = loc.get("longitude")

                    if lat is None or lng is None:
                        whatsapp.send_message(
                            phone_number,
                            "Recebi uma localização inválida. Pode reenviar?",
                        )
                        continue

                    # Passa um enunciado natural para o coordenador.
                    # Os agentes (ex.: rota/chegada) podem usar isso como origem do trajeto.
                    prompt_loc = (
                        f"Minha localização é {lat},{lng}. "
                        f"Se eu pedir uma rota, use esse ponto como origem, a menos que eu informe outra."
                    )
                    response_text = _run_coordinator(prompt_loc, user_id=phone_number)
                    whatsapp.send_message(phone_number, response_text)

                # === Outros tipos (áudio, imagem, etc.) ===
                else:
                    whatsapp.send_message(
                        phone_number,
                        "No momento, consigo entender apenas texto ou localização. 🙏",
                    )

            except Exception as e:
                traceback.print_exc()
                whatsapp.send_message(
                    phone_number,
                    "Desculpe, tive um problema ao processar sua mensagem. Por favor, tente novamente.",
                )

        return "EVENT_RECEIVED", 200

    except Exception as e:
        traceback.print_exc()
        return "ERROR", 500


@app.route("/")
def home():
    return "Servidor de Transporte Público - Status: Online"
