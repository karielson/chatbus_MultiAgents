# agents/agente_status.py

from dotenv import load_dotenv
import os

load_dotenv()
from config.settings import settings

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from services.sptrans import sptrans
from urllib.parse import quote

# Tool oficial para gerar link do Olho Vivo
@tool(show_result=True, stop_after_tool_call=True)
def status_onibus_tool(linha: str = None, sentido: str = None) -> str:
    """
    Envia o link do mapa do Olho Vivo com a posição dos ônibus da linha especificada.
    Caso o sentido não seja informado, sugere as opções disponíveis.
    """
    if not linha:
        return "Por favor, informe o número ou nome da linha para que eu possa gerar o link."

    linhas = sptrans.buscar_linha(linha)
    
    if not linhas:
        return "Nenhuma linha encontrada. Tente novamente informando o número ou nome completo da linha."
    
    if len(linhas) > 1:
            return f"Encontrei várias linhas. Por favor, especifique uma: {', '.join(linhas)}"
    
    linhas = sptrans.buscar_info_linhas(linha)
    # Considera a primeira linha encontrada se houver apenas uma
    linha_info = linhas[0]
    cl = linha_info['cl']
    letreiro_completo = f"{linha_info['lt']}-{linha_info['tl']}"

    # Verifica se o sentido foi informado
    if not sentido:
        # Sugere os sentidos disponíveis
        sentidos_disponiveis = {
            "1": linha_info['tp'],  # Terminal Principal para Terminal Secundário
            "2": linha_info['ts']   # Terminal Secundário para Terminal Principal
        }
        
        return (
            f"A linha {letreiro_completo} possui os seguintes sentidos:\n"
            f"1️⃣ {linha_info['tp']}\n"
            f"2️⃣ {linha_info['ts']}\n"
            f"Por favor, informe o número do sentido desejado para que eu possa gerar o link."
        )
    
    # Determina a descrição do sentido com base na escolha do usuário
    if sentido == "1":
        sentido_desc = linha_info['tp']
    elif sentido == "2":
        sentido_desc = linha_info['ts']
    else:
        return "Sentido inválido. Por favor, informe 1 ou 2."

    # Codifica a descrição do sentido para a URL
    sentido_encoded = quote(sentido_desc)

    # Monta o link do Olho Vivo
    link = f"https://olhovivo.sptrans.com.br/#sp?cat=Mapa2&l={cl}&s={letreiro_completo}&sc={sentido_encoded}"
    
    return (
        f"Aqui está o link para acompanhar os ônibus da linha {letreiro_completo} ({sentido_desc}):\n"
        f"{link}"
    )

# Agente de status
agente_status = Agent(
    name="Agente de Status de Linhas",
    model=OpenAIChat(id="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[status_onibus_tool],
    instructions=[
        "Você é um agente que informa a posição dos ônibus em tempo real pelo link do Olho Vivo.",
        "Sempre que o usuário perguntar 'onde está o ônibus' ou 'mostrar no mapa', use a função `gerar_link_status`.",
        "Se o sentido não for informado, mostre as duas opções e peça para o usuário escolher 1 ou 2.",
        "Monte e retorne o link formatado com clareza.",
    ],
    markdown=True,
    debug_mode=settings.DEBUG_MODE
)

if __name__ == "__main__":
    pergunta = "Onde estão os ônibus da linha 6455-10? sentido 1"
    agente_status.print_response(pergunta, stream=True)
