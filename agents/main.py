from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from config.settings import settings
from .tools import quadro_de_horario_tool, rota_tool, faq_tool, status_onibus_tool, previsao_chegada_tool, sugestoes_contextuais_tool

def create_agent():
    """Cria e configura o agente de chat."""
    # Define as ferramentas disponíveis
    tools = [quadro_de_horario_tool, rota_tool, faq_tool, status_onibus_tool, previsao_chegada_tool, sugestoes_contextuais_tool]
    # Configura o modelo de linguagem
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model_name="gpt-3.5-turbo",
        temperature=0
    )
    print(settings.OPENAI_API_KEY)
    
    # Define o template do prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um assistente especializado no transporte público de São Paulo. 
        Siga o padrão ReAct para resolver cada solicitação: 

        1️⃣ **Pense**: analise a pergunta e descreva seu raciocínio.  
        2️⃣ **Aja**: escolha a ferramenta mais adequada.  
        3️⃣ **Observe**: use o resultado da ferramenta.  
        4️⃣ **Responda**: formule a resposta final de forma simpática e clara.  
        5️⃣ **Sugira**: pense no que mais o usuário pode precisar e chame a ferramenta `sugestoes_contextuais_tool`.

        ⚠️ Nunca pule etapas. Se tiver dúvida, peça mais informações ao usuário.

         Após responder a dúvida do usuário, sempre pense no que mais ele pode querer e chame a ferramenta `sugestoes_contextuais_tool`, informando a pergunta original e sua resposta.
        
        Use as seguintes ferramentas de acordo com a necessidade:
        - faq_tool: Para responder perguntas gerais sobre o sistema
        - quadro_de_horario_tool: Para consultar horários específicos de linhas. 
        - rota_tool: Para fornecer informações sobre trajetos
        - status_onibus_tool: Para gerar o link do Olho Vivo com o mapa da linha de ônibus.
        - previsao_chegada_tool: Para informar o tempo de chegada do próximo ônibus em uma parada.
        - sugestoes_contextuais_tool: para sugerir mais ferramentas ao usuário.
         

         
        Mantenha suas respostas:
        1. Simpáticas e claras
        2. Focadas no contexto de transporte público
        3. Úteis e práticas para o usuário
        4. Seja bastante simpático, use emojis para mostrar simpatia de acordo com contexto.
        5. nunca invente respostar, basei-se nos dados.
        Se não tiver certeza sobre alguma informação, peça esclarecimentos.
        """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])
    
    # Cria o agente
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # Cria o executor do agente
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

# Cria uma instância do agente
agent_executor = create_agent()