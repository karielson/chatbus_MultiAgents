# scripts/cli_chat.py
from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Garante que a raiz do projeto esteja no PYTHONPATH ao rodar como script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Importa o Coordenador (Team Agno) que orquestra os agentes especialistas
from agents.coordenador import coordenador  # noqa: E402


SEPARATOR = "-" * 50


def format_agent_response(response: str) -> str:
    """Formata a resposta do agente para melhor legibilidade."""
    return f"\n{SEPARATOR}\nResposta: {response}\n{SEPARATOR}\n"


def save_conversation(chat_history: list[dict]) -> str:
    """Salva o histórico da conversa em um arquivo .txt."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = ROOT / "conversas"
    outdir.mkdir(parents=True, exist_ok=True)
    filename = outdir / f"conversa_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("Histórico da Conversa (CLI ChatBus + Agno)\n")
        f.write("=" * 50 + "\n\n")
        for msg in chat_history:
            role = "Usuário" if msg.get("role") == "user" else "Agente"
            f.write(f"{role}: {msg.get('content','')}\n\n")

    return str(filename)


def run_coordinator(message: str) -> str:
    """
    Executa o coordenador do Agno e retorna a resposta final como string.
    Usa streaming para juntar os pedaços da resposta.
    """
    chunks = []
    # Coordenador (Team) expõe .run(stream=True) que rende RunResponse com .content
    for rr in coordenador.run(message, stream=True):
        if getattr(rr, "content", None):
            chunks.append(str(rr.content))
    # Se nada chegou via stream, tenta recuperar do objeto
    if not chunks and getattr(coordenador, "run_response", None):
        content = getattr(coordenador.run_response, "content", "")
        if content:
            chunks.append(str(content))
    return "".join(chunks).strip()


def main():
    print("\n=== ChatBus (Agno) - Modo Teste Local ===")
    print("Digite 'sair', 'exit' ou 'quit' para encerrar")
    print("Digite 'salvar' para salvar o histórico da conversa")
    print("=" * 50 + "\n")

    # Histórico simples só para salvar em arquivo (o estado real fica no storage do Agno)
    chat_history: list[dict] = []

    while True:
        try:
            user_question = input("\nVocê: ").strip()

            # Comandos especiais
            if user_question.lower() in {"sair", "exit", "quit"}:
                if chat_history:
                    save = input("\nDeseja salvar a conversa? (s/n): ").lower().strip()
                    if save == "s":
                        filename = save_conversation(chat_history)
                        print(f"\nConversa salva em: {filename}")
                print("\nEncerrando a conversa. Até logo!")
                break

            if user_question.lower() == "salvar":
                if chat_history:
                    filename = save_conversation(chat_history)
                    print(f"\nConversa salva em: {filename}")
                else:
                    print("Não há mensagens para salvar ainda.")
                continue

            if not user_question:
                print("Por favor, digite sua pergunta.")
                continue

            # Guarda no histórico local (para export .txt)
            chat_history.append({"role": "user", "content": user_question})

            # Chama o coordenador (que decide qual especialista usar)
            response = run_coordinator(user_question) or "Não obtive resposta do agente."

            print(format_agent_response(response))

            # Guarda a resposta no histórico local
            chat_history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print("\n\nOperação interrompida pelo usuário.")
            sys.exit(0)
        except Exception as e:
            print(f"\nErro ao processar a mensagem:")
            print(f"Tipo do erro: {type(e).__name__}")
            print(f"Descrição: {str(e)}")
            print("\nDetalhes técnicos:")
            traceback.print_exc()
            print("\nPor favor, tente novamente.")


if __name__ == "__main__":
    main()
