from langchain.tools import tool
from services.maps import maps
from services.sptrans import sptrans
from scrapers.horarios import horarios_scraper
from legacy.faq_rag import search_faq

from urllib.parse import quote  # Para codificar a URL
from config.settings import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm_sugestao = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.3
)

# Prompt da ferramenta de sugestão contextual
prompt_sugestoes = ChatPromptTemplate.from_messages([
    ("system", """
Você é um assistente de transporte público de São Paulo.

Depois de responder a uma pergunta do usuário, seu objetivo é pensar em até 2 funcionalidades extras que o usuário pode querer usar, com base na pergunta e na resposta.

Funcionalidades disponíveis:
- Consultar horários de ônibus
- Ver previsão de chegada de um ônibus em uma parada
- Gerar trajeto entre dois pontos
- Ver localização dos ônibus no mapa (Olho Vivo)
- Fazer perguntas gerais sobre o sistema
- Ativar modo iniciante (ensinar como usar o transporte público)

Se não houver nada útil para sugerir, retorne uma string vazia.
"""),
    ("human", "Pergunta: {pergunta}\nResposta: {resposta}")
])

@tool
def sugestoes_contextuais_tool(pergunta: str, resposta: str) -> str:
    """
    Usa a LLM para sugerir funcionalidades complementares com base na pergunta do usuário e na resposta já dada.
    Retorna sugestões amigáveis e úteis, ou uma string vazia se nada for relevante.
    """
    chain = prompt_sugestoes | llm_sugestao
    return chain.invoke({
        "pergunta": pergunta,
        "resposta": resposta
    }).content


@tool
def quadro_de_horario_tool(linha: str, dia: str|None) -> str:
    """Informa os horários de partidas da linha de ônibus. sempre informar todos os horários e explicar que se refere a saída do terminal.
    Se o usuário solicitar informações do domingo o parametro dia deve ser 2, se sábado dia deve ser 1, se um dia útil dia deve ser 0, não informar nada dia recebe none"""
    linhas = sptrans.buscar_linha(linha)
    
    if not linhas:
        return "Nenhuma linha encontrada. Tente novamente."
        
    if len(linhas) > 1:
        return f"Encontrei várias linhas. Por favor, especifique uma: {', '.join(linhas)}"
        
    horarios = horarios_scraper.scrape(linhas[0], dia)
    if not horarios:
        return "Desculpe, não consegui encontrar os horários dessa linha."
        
    return f"Horários da linha {linhas[0]}:\n" + "\n".join(horarios)

@tool
def rota_tool(origem: str = None, destino: str = None, preferencia: str = None) -> str:
    """
    Informa o melhor trajeto entre uma origem e um destino.
    Importante: se origem e destino estiverem descritos como texto adicione ",são paulo, SP, Brasil". Se estiver em formato de latitude e longitudo não adicione nada.
    'preferencia' pode ser:
      - 'rapida' => rota mais curta em tempo
      - 'menos_baldeacoes' => rota com menos conexões de ônibus
      - 'menos_caminhada' => rota com menos caminhada, etc.
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
    if not rota:
        return "Desculpe, não consegui encontrar uma rota com as informações fornecidas."
        
    return rota


@tool
def faq_tool(pergunta: str) -> str:
    """Responde perguntas gerais """
    respostas = search_faq(pergunta)  # Retorna até 2 respostas relevantes

    if not respostas:
        return "❌ Desculpe, não encontrei uma resposta específica para sua pergunta no FAQ."

    resposta_formatada = "\n\n".join([
        f"🔹 **Pergunta:** {r['question']}\n✅ **Resposta:** {r['answer']}"
        for r in respostas
    ])
    
    return resposta_formatada



@tool
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

@tool
def previsao_chegada_tool(linha: str = None, parada: str = None) -> str:
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
