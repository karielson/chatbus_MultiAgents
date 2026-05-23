# agents/agente_rota.py

from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()
from config.settings import settings

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from services.maps import maps

# Tool oficial para consulta de rotas
@tool(show_result=True, stop_after_tool_call=True)
def consultar_rota(origem: str, destino: str, preferencia: str = None) -> str:
    """
    Informa o melhor trajeto entre uma origem e um destino.
    Importante: se origem e destino estiverem descritos como texto adicione ",são paulo, SP, Brasil". Se estiver em formato de latitude e longitudo não adicione nada.
    'preferencia' pode ser:
      - 'rapida' => rota mais curta em tempo
      - 'menos_baldeacoes' => rota com menos conexões de ônibus
      - 'menos_caminhada' => rota com menos caminhada, etc.
      obs.: se o usuário não informar a preferencia coloque 'rapida'
    """
    if not destino:
        return "Por favor, informe o endereço de destino ou compartilhe sua localização."

    if not origem:
        # Caso o usuário só forneça o destino, pedimos a origem (endereço ou localização).
        return (
            "Entendi que você quer ir para: {destino}.\n"
            "Para prosseguir, preciso saber sua origem. "
            "Poderia me dizer o endereço de onde você está saindo, "
            "ou compartilhar sua localização? 📍"
        )

    # Se origem e destino foram fornecidos, chama a API do Google Maps
    rota = maps.get_directions(origem, destino, preferencia=preferencia)
    print(rota)
    if not rota:
        return "Desculpe, não consegui encontrar uma rota com as informações fornecidas."
        
    return rota

# Criação do agente de rota
agente_rota = Agent(
    name="Agente de Rotas SPTrans",
    model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[consultar_rota],
    instructions=[
        "Você é um especialista em trajetos de ônibus da cidade de São Paulo.",
        "Sempre que o usuário perguntar como ir de um ponto a outro, use a ferramenta `consultar_rota`.",
        "Se o usuário não informar origem ou destino, solicite educadamente.",
        "Se o usuário disser 'quero a mais rápida', use 'preferencia=rapida'.",
        "Se disser 'com menos baldeações' use 'menos_baldeacoes'.",
        "Se disser 'menos caminhada' use 'menos_caminhada'.",
        "obs.: se o usuário não informar a preferencia coloque 'rapida'",
        "Importante: se origem e destino estiverem descritos como texto adicione 'são paulo, SP, Brasil' Se estiver em formato de latitude e longitudo não adicione nada.",
    ],
    markdown=True,
    debug_mode=settings.DEBUG_MODE
)

if __name__ == "__main__":
    pergunta = "com ir de campo limpo para paraiso rapida?"
    agente_rota.print_response(pergunta, stream=True)
