# agents/coordenador.py

from dotenv import load_dotenv
import os
from config.settings import settings

load_dotenv()


from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.storage.sqlite import SqliteStorage

# Importa os agentes especialistas
from agents.agente_horarios import agente_horarios
from agents.agente_rota import agente_rota
from agents.agente_status import agente_status
from agents.agente_chegada import agente_chegada
from agents.agente_faq import faq_agent

# Storage compartilhado (opcional, mas recomendado)
team_storage = SqliteStorage(table_name="team_sessions", db_file="data/agent.db")

# Coordenador (Team) em modo "coordinate"
coordenador = Team(
    name="Coordenador ChatBus",
    mode="coordinate",  # o líder decide quem responde
    model=OpenAIChat(id="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
    members=[
        # ordem aqui importa quando o pedido parece ambíguo
        agente_rota,        # “como chegar”, origem/destino, “ir de X para Y”
        agente_chegada,     # “quando passa”, “previsão”, “chega em quanto tempo”
        agente_status,      # “onde está o ônibus”, “mapa”, “link do olho vivo”
        agente_horarios,    # “horário fixo de operação”, “tabela de horários”
        faq_agent,          # perguntas gerais, regras, bilhete único, etc.
    ],
    storage=team_storage,
    add_history_to_messages=True,
    num_history_runs=4,
    enable_agentic_context=True,     # compartilha contexto entre membros
    show_members_responses=True,     # útil para depuração
    show_tool_calls=True,
    markdown=False,
    monitoring=settings.monitor_enabled,  # 👈 ativa só para este agente
    instructions=[
        "Você é o coordenador do ChatBus (São Paulo).",
        "Analise a intenção do usuário e encaminhe para o AGENTE mais adequado:",
        "- ROTA: quando o usuário busca informações de rotas, pede 'como chegar', origem/destino.obs.: se o usuário não informar a preferencia coloque 'rapida'. Importante: se origem e destino estiverem descritos como texto adicione ',são paulo, SP, Brasil' em origem e destino nos parametros de entrada. Se estiver em formato de latitude e longitudo não adicione nada.",
        "- CHEGADA: quando o usuário pergunta 'quando passa', 'previsão de chegada' num ponto/parada.",
        "- STATUS/MAPA: quando pedir 'onde está o ônibus', 'mostrar no mapa', link do Olho Vivo.",
        "- HORÁRIOS: quando pedir a tabela de horários fixos da linha. Se usuário não informar o dia da semana não use nenhum parametro de entrada no dia da semana e informe na resposta 'são os horários de hoje'",
        "- FAQ: quando for uma pergunta geral (regras, bilhete único, animais, integrações, etc.).",
        "Se faltar informação (ex.: origem/destino, sentido, nome da parada), peça educadamente apenas o mínimo necessário e reencaminhe.",
        "Responda de forma clara, objetiva e amigável, em português do Brasil.",
        "Nunca peça dados redundantes: aproveite histórico quando presente.",
    ],
    success_criteria=(
        "O usuário recebe a melhor resposta possível para sua intenção, "
        "com dados corretos, passos claros e, quando aplicável, links do Olho Vivo."
    ),
    debug_mode=settings.DEBUG_MODE,
)

if __name__ == "__main__":
    # Exemplos de teste (rode um por vez ou comente/alterne)
    perguntas = [
        "Como vou da Av. Paulista até o Morumbi com menos caminhada?",
        "Onde estão os ônibus da 715M-10?",
        "Quais os horários da 6455-10 no domingo?",
        "Posso levar cachorro no ônibus?",
    ]
    for p in perguntas:
        print(f"\n👉 {p}")
        coordenador.print_response(p, stream=True)
