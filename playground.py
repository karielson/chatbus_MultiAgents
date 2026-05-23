# playground.py
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()

from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage

# === importe seus agentes e o team coordenador ===
from agents.coordenador import coordenador           # <- Team
from agents.agente_faq import faq_agent
from agents.agente_rota import agente_rota
from agents.agente_horarios import agente_horarios
from agents.agente_status import agente_status
from agents.agente_chegada import agente_chegada

# Armazenamento compartilhado (opcional, bom pra inspecionar tudo no mesmo DB)
shared_storage = SqliteStorage(table_name="playground_sessions", db_file="data/agent.db")

# Ajustes úteis na 1ª vez (opcional)
for ag in [faq_agent, agente_rota, agente_horarios, agente_status, agente_chegada]:
    ag.storage = ag.storage or shared_storage
    ag.debug_mode = True
    ag.show_tool_calls = True
    ag.markdown = True

# Para o Team (coordenador)
coordenador.storage = coordenador.storage or shared_storage
coordenador.debug_mode = True
coordenador.show_tool_calls = True
coordenador.show_members_responses = True
coordenador.markdown = True

# ✅ AQUI ESTÁ O PULO DO GATO:
# - O Team entra em `teams=[...]`
# - Os agentes individuais entram em `agents=[...]`
playground_app = Playground(
    agents=[agente_rota, agente_horarios, agente_status, agente_chegada],
    teams=[coordenador],  # coordenador já inclui o faq_agent
)

# FastAPI app
app = playground_app.get_app()

if __name__ == "__main__":
    # Sem reload para evitar loop monitorando venv/site-packages
    playground_app.serve("playground:app", host="0.0.0.0", port=7777, reload=False)

