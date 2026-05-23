# agents/agente_chegada.py

from dotenv import load_dotenv
import os

load_dotenv()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from config.settings import settings



from services.sptrans import sptrans

@tool(show_result=True, stop_after_tool_call=True)
def consultar_previsao_chegada(linha: str = None, parada: str = None) -> str:
    """
    Informa o tempo restante para o próximo ônibus de uma linha específica passar na parada informada.
    Caso alguma informação esteja faltando (linha ou parada), solicita os dados ao usuário.
    """

    # Verificação da Linha
    if not linha:
        return "Por favor, informe o número ou nome da linha para que eu possa verificar o tempo de chegada."

    linhas = sptrans.buscar_linha(linha)
    if not linhas:
        return "Nenhuma linha encontrada. Tente novamente informando o número ou nome completo da linha."

    if len(linhas) > 1:
            return f"Encontrei várias linhas. Por favor, especifique uma: {', '.join(linhas)}"

    linhas = sptrans.buscar_info_linhas(linha)
    linha_info = linhas[0]
    codigo_linha = linha_info['cl']
    print(linha_info)

    # Verificação da Parada
    if not parada:
        return "Por favor, informe o nome ou endereço da parada onde você deseja pegar o ônibus."

    paradas = sptrans.buscar_parada(parada)
    if not paradas:
        return "Não encontrei nenhuma parada com esse nome ou endereço. Tente novamente com mais detalhes."

    if len(paradas) > 1:
        opcoes_paradas = "\n".join([f"- {p['np']} ({p['ed']})" for p in paradas])
        return f"Encontrei várias paradas com esse nome. Por favor, escolha uma das opções:\n{opcoes_paradas}"

    parada_info = paradas[0]
    codigo_parada = parada_info['cp']

    # Busca da Previsão de Chegada
    previsao = sptrans.buscar_previsao_chegada(codigo_linha, codigo_parada)


    if not previsao or 'p' not in previsao or 'l' not in previsao['p']:
        return "Não foi possível encontrar informações sobre a previsão de chegada no momento."

    linha_previsao = previsao['p']['l'][0]
    veiculos = linha_previsao.get('vs', [])

    if not veiculos:
        return "Nenhum ônibus da linha está a caminho no momento."

    resposta = []
    for veiculo in veiculos:
        horario_previsto = veiculo['t']
        acessibilidade = "♿" if veiculo['a'] else "🚫"
        resposta.append(f"🚍 Ônibus prefixo {veiculo['p']} chegará às {horario_previsto}. Acessível: {acessibilidade}")

    return "\n".join(resposta)

# Agente de previsão de chegada
agente_chegada = Agent(
    name="Agente de Previsão de Chegada",
    model=OpenAIChat(id="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
    tools=[consultar_previsao_chegada],
    instructions=[
        "Você responde sobre o tempo de chegada de ônibus em pontos de São Paulo.",
        "Se o usuário não informar a linha ou o local da parada, solicite educadamente.",
        "Use a função `consultar_previsao_chegada` para buscar a previsão e formate a resposta com emojis.",
    ],
    markdown=True,
    debug_mode=settings.DEBUG_MODE
)

if __name__ == "__main__":
    pergunta = "Que horas o 6455-10 passa na Av. Paulista? parada 1"
    agente_chegada.print_response(pergunta, stream=True)
