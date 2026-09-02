# agents/agente_horarios.py



from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from services.sptrans import sptrans
from scrapers.horarios import horarios_scraper
from dotenv import load_dotenv
import os
from agno.models.openai import OpenAIChat
from agno.tools import tool
from core.eval_trace import set_tool, set_agent


from config.settings import settings

load_dotenv()  # Carrega as variáveis do .env
# Função local que será usada pelo agente
@tool(show_result=True, stop_after_tool_call=True)
def consultar_horarios(linha: str, dia: str = None) -> str:
    """Informa os horários de partidas da linha de ônibus. sempre informar todos os horários do dia e explicar que se refere a saída do terminal.
    Se o usuário solicitar informações do domingo o parametro dia deve ser 2, se sábado dia deve ser 1, se um dia útil dia deve ser 0, não informar nada dia recebe none.
    Se usuário não informar o dia da semana não use nenhum parametro de entrada no dia da semana e informe na resposta 'são os horários de hoje'
    SEMPRE INFORME TODOS OS HORÁRIOS DA LISTA DE HORÁRIOS"""
    set_agent("agente_horarios")
    set_tool("consultar_horarios")   
    linhas = sptrans.buscar_linha(linha)

    if not linhas:
        return "Nenhuma linha encontrada. Tente novamente."
    if len(linhas) > 1:
        return f"Encontrei várias linhas. Especifique uma: {', '.join(linhas)}"
    
    horarios = horarios_scraper.scrape(linhas[0], dia)
    if not horarios:
        return "Desculpe, não encontrei os horários dessa linha."

    return f"Horários da linha {linhas[0]}:\n" + "\n".join(horarios)


openai_api_key = os.getenv("OPENAI_API_KEY")
# Definindo o agente Agno
agente_horarios = Agent(
    name="Agente de Horários de Ônibus",
    model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),  # passa a chave
    tools=[consultar_horarios],
    instructions=[
        "Você é um especialista em transporte público de São Paulo.",
        "Se o usuário solicitar informações do domingo o parametro dia deve ser 2, se sábado dia deve ser 1, se um dia útil dia deve ser 0, não informar nada dia recebe none",
        "Use a função `consultar_horarios(linha, dia)` para retornar os horários.",
        "Se houver múltiplas linhas, peça ao usuário para especificar.",
        "Se usuário não informar o dia da semana não use nenhum parametro de entrada no dia da semana e informe na resposta 'são os horários de hoje'",
        "sempre informar todos os horários do dia",
        "SEMPRE INFORME TODOS OS HORÁRIOS DA LISTA DE HORÁRIOS",
        
    ],
    markdown=True,
    debug_mode=settings.DEBUG_MODE
)

if __name__ == "__main__":
    pergunta = "Quais os horários da linha 6455-10 no sábado?"

    # Inicia a conversa com o agente passando a pergunta
    agente_horarios.print_response(pergunta, stream=True)
