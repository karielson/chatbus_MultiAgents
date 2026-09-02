# agents/agente_faq.py

from dotenv import load_dotenv
import os

load_dotenv()

from core.eval_trace import set_tool, set_agent
from config.settings import settings

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.json import JSONKnowledgeBase
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb, SearchType


# === Caminhos padronizados ===
FAQ_JSON = "data/faq_data.json"
VECTOR_DIR = "data/lancedb"
DB_FILE = "data/agent.db"


# === Base de conhecimento (JSON + LanceDB) ===
# Mantemos text_key="text" para casar com update_faq.py que cria o campo 'text' (question+answer).
knowledge = JSONKnowledgeBase(
    path=FAQ_JSON,
    text_key="text",
    vector_db=LanceDb(
        uri=VECTOR_DIR,
        table_name="faq_table",
        search_type=SearchType.hybrid,
        # Embedding maior para melhorar a semântica
        embedder=OpenAIEmbedder(id="text-embedding-3-large", dimensions=3072),
    ),
)


# === Armazenamento de sessões (SQLite) ===
storage = SqliteStorage(table_name="faq_sessions", db_file=DB_FILE)


class TracedFAQAgent(Agent):
    """
    Agent com rastreamento para avaliação.

    Não altera a lógica do FAQ/RAG.
    Apenas registra que o agente FAQ foi acionado durante a avaliação.
    """

    def run(self, *args, **kwargs):
        set_agent("agente_faq")
        set_tool("faq")
        return super().run(*args, **kwargs)

    def print_response(self, *args, **kwargs):
        set_agent("agente_faq")
        set_tool("faq")
        return super().print_response(*args, **kwargs)


# === Agente FAQ (apenas consulta) ===
faq_agent = TracedFAQAgent(
    name="Agente FAQ SPTrans",
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    search_knowledge=True,
    storage=storage,
    add_history_to_messages=True,
    monitoring=settings.monitor_enabled,
    num_history_runs=3,
    # ❌ REMOVIDO: knowledge_top_k (não é suportado nessa versão do Agno)
    instructions=[
        "Você é um assistente do transporte público de São Paulo.",
        "Use sua base de conhecimento (FAQ SPTrans) para responder.",
        "Se a informação não estiver na base, diga que não encontrou.",
        "Responda de forma clara, amigável e objetiva.",
        "seja fiel à resposta do FAQ, não invente informações, e dê a informação completa",
    ],
    markdown=True,
    debug_mode=settings.DEBUG_MODE,
)


if __name__ == "__main__":
    # Execução direta (consulta simples, sem reindexar)
    faq_agent.print_response("Quanto custa a 2ª via do Bilhete Único de Estudante?", stream=True)