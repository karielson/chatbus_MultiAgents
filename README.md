# ChatBus — configuração multiagente

Implementação multiagente do ChatBus, protótipo de chatbot inteligente desenvolvido para centralizar informações sobre o transporte público urbano e disponibilizá-las em linguagem natural por meio do WhatsApp.

Este repositório integra os materiais da dissertação:

> FEITOSA, Karielson Medeiros. *ChatBus: protótipo de chatbot inteligente para a qualidade da informação e a eficiência técnica informacional no transporte público urbano*. Dissertação (Mestrado em Engenharia de Produção) — Universidade Federal do Rio Grande do Norte, Natal, 2026.

O protótipo foi aplicado ao sistema de ônibus do município de São Paulo. Seu objetivo é reunir informações operacionais e institucionais provenientes de fontes distintas, reduzindo a fragmentação informacional enfrentada pelos passageiros.

## Configuração multiagente

Nesta configuração, o processamento é distribuído entre um coordenador central e quatro agentes especializados. O coordenador interpreta a solicitação, identifica a intenção predominante e encaminha a tarefa ao agente responsável pelo domínio informacional correspondente.

A coordenação foi implementada com o framework Agno. O coordenador e os agentes utilizam o modelo GPT-4o-mini, com temperatura igual a zero.

```text
Usuário
   |
   v
WhatsApp Cloud API
   |
   v
Webhook Flask
   |
   v
Coordenador — Agno Team + GPT-4o-mini
   |
   +-- Agente de FAQ
   +-- Agente de horários
   +-- Agente de rotas
   +-- Agente de status
   |
   v
Resposta consolidada em linguagem natural
```

O fluxo de atendimento compreende recepção, análise da intenção, delegação, execução da ferramenta, geração da resposta e envio ao usuário. O contexto é compartilhado para preservar a continuidade das interações.

## Agentes e funcionalidades avaliadas

### Agente de FAQ

Responde a perguntas sobre regras, tarifas e procedimentos do transporte público. Utiliza Recuperação Aumentada por Geração (RAG), com busca semântica em uma base vetorial LanceDB construída a partir do FAQ oficial da SPTrans.

### Agente de horários

Consulta os horários oficiais de partida das linhas da SPTrans. A coleta considera o tipo de dia de operação: dia útil, sábado ou domingo/feriado.

### Agente de rotas

Obtém trajetos de transporte público entre uma origem e um destino por meio das APIs Directions e Geocoding do Google Maps. A resposta pode reunir duração estimada, distância, linhas utilizadas, baldeações, pontos de embarque e desembarque e etapas de caminhada.

### Agente de status

Gera o endereço do mapa oficial Olho Vivo para a linha e o sentido informados, permitindo ao usuário acessar a visualização disponibilizada pela SPTrans.

## Camadas funcionais

O ChatBus foi organizado em quatro camadas:

- **Interface:** WhatsApp Cloud API e webhook Flask para entrada e saída de mensagens.
- **Inteligência:** coordenador, agentes especializados, modelo de linguagem e mecanismo RAG.
- **Integração:** comunicação com SPTrans, Google Maps, OpenAI e LanceDB.
- **Dados:** armazenamento temporário em SQLite, base vetorial LanceDB e arquivo `faq_data.json`.

A decomposição por domínio permite incorporar novos agentes e substituir conectores ou fontes de dados, favorecendo manutenção, extensibilidade e adaptação a outros contextos urbanos.

## Tecnologias do ambiente experimental

| Tecnologia | Versão ou configuração | Função |
|---|---:|---|
| Python | 3.11 | Linguagem e ambiente de execução |
| GPT-4o-mini | temperatura 0 | Interpretação, coordenação e geração das respostas |
| Agno | 1.5.10 | Coordenação da configuração multiagente |
| OpenAI SDK | 1.55.3 | Integração com o modelo de linguagem |
| Flask | 3.0.3 | API e endpoint do webhook |
| LanceDB | 0.14.0 | Armazenamento e recuperação vetorial do FAQ |
| Playwright | 1.47.0 | Coleta automatizada de conteúdo web |
| Requests | 2.32.3 | Requisições aos serviços externos |
| python-dotenv | 1.0.1 | Carregamento das variáveis de ambiente |
| pyngrok | 7.2.3 | Exposição temporária do servidor local |
| WhatsApp Cloud API | Graph API | Interface de mensagens |

As versões completas das dependências estão registradas em `requirements.txt`.

## Fontes de informação

- **SPTrans e Olho Vivo:** linhas, sentidos, informações operacionais e acesso ao mapa dos veículos.
- **Portal da SPTrans:** horários programados e FAQ institucional.
- **Google Maps:** planejamento de trajetos e geocodificação.
- **OpenAI:** processamento de linguagem natural e geração de embeddings.
- **LanceDB:** indexação e recuperação semântica do FAQ.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/karielson/chatbus_MultiAgents.git
cd chatbus_MultiAgents
```

Crie um ambiente virtual com Python 3.11.

Windows — PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux ou macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Instale as dependências e o navegador utilizado pelo Playwright:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```dotenv
OPENAI_API_KEY=sua_chave_openai
SPTRANS_API_TOKEN=seu_token_sptrans
GOOGLE_MAPS_API_KEY=sua_chave_google_maps
WHATSAPP_TOKEN=seu_token_whatsapp
VERIFY_TOKEN=seu_token_de_verificacao
NGROK_AUTHTOKEN=seu_token_ngrok
```

As credenciais, os arquivos com segredos e eventuais dados pessoais não fazem parte dos materiais públicos da pesquisa. Não publique o arquivo `.env`.

## Preparação da base institucional

O arquivo `update_faq.py` realiza a coleta do FAQ da SPTrans e prepara a base de conhecimento utilizada pela recuperação semântica:

```bash
python update_faq.py
```

Como o conteúdo de origem pode mudar, a data da coleta deve ser registrada ao executar uma nova avaliação.

## Execução

### Teste local

```bash
python cli_chat.py
```

### Integração com o WhatsApp

```bash
python main.py
```

O servidor Flask utiliza a porta `5000`. Durante o desenvolvimento, o ngrok pode disponibilizar uma URL HTTPS pública. O endpoint a ser configurado na WhatsApp Cloud API é:

```text
https://<endereco-ngrok>/webhook
```

O valor utilizado na validação do webhook deve corresponder a `VERIFY_TOKEN`.

## Avaliação experimental

A configuração multiagente foi avaliada com 200 consultas:

| Tipo de tarefa | Quantidade |
|---|---:|
| FAQ institucional | 50 |
| Horários programados | 50 |
| Planejamento de rotas | 50 |
| Status da linha | 50 |
| **Total** | **200** |

O mesmo conjunto de consultas foi aplicado à configuração monoagente, totalizando 400 respostas no experimento comparativo.

### Indicadores

- **Qualidade da Informação (QoI):** média das dimensões de acurácia, completude e atualidade.
- **Tempo de Resposta Médio (TRM):** tempo interno decorrido entre o início do processamento e a obtenção da resposta.
- **Precisão da Escolha da Ferramenta (PEF):** correspondência entre a ferramenta esperada e a ferramenta utilizada.

Acurácia, completude e atualidade foram atribuídas após comparação individual das respostas com os respectivos gabaritos. O QoI foi calculado com base nesses três escores revisados.

### Executar os conjuntos de consultas

```bash
python -m evaluation.run_evaluation --arquitetura multiagente --dataset evaluation/datasets/consultas_faq_50.csv
python -m evaluation.run_evaluation --arquitetura multiagente --dataset evaluation/datasets/consultas_horarios_50.csv
python -m evaluation.run_evaluation --arquitetura multiagente --dataset evaluation/datasets/consultas_rotas_50.csv
python -m evaluation.run_evaluation --arquitetura multiagente --dataset evaluation/datasets/consultas_status_50.csv
```

Os conjuntos de consultas estão em `evaluation/datasets/`. As respostas experimentais e os campos utilizados na avaliação estão em `evaluation/outputs/`.

### Resultado relatado na dissertação

| Indicador | Resultado multiagente |
|---|---:|
| QoI médio | 0,98080 |
| Tempo médio de resposta | 14,27 s |
| PEF | 1,0 |

As duas configurações apresentaram elevada Qualidade da Informação. No planejamento de rotas, o multiagente elevou o QoI em 0,01500 em relação ao monoagente, com acréscimo de 8,52 segundos no tempo médio dessa tarefa. Para o conjunto completo das funcionalidades avaliadas, a coordenação entre agentes aumentou a latência sem produzir ganho proporcional de qualidade geral.

## Reprodutibilidade e limitações

- Os resultados correspondem às condições, fontes, versões e datas do experimento descrito na dissertação.
- Horários, rotas e dados operacionais podem mudar após a coleta.
- Alterações nas APIs, nos modelos hospedados ou nas páginas consultadas podem produzir resultados diferentes.
- A avaliação foi realizada no sistema de ônibus de São Paulo.
- A replicabilidade foi projetada por meio da modularidade, mas não foi testada empiricamente em outro município.
- O protótipo é experimental e não substitui os canais oficiais de informação.

## Configuração relacionada

A implementação centralizada em um único agente está disponível em [chatbus_MonoAgent](https://github.com/karielson/chatbus_MonoAgent).

## Como citar

```bibtex
@mastersthesis{feitosa2026chatbus,
  author  = {Karielson Medeiros Feitosa},
  title   = {ChatBus: protótipo de chatbot inteligente para a qualidade da informação e a eficiência técnica informacional no transporte público urbano},
  school  = {Universidade Federal do Rio Grande do Norte},
  address = {Natal, RN},
  year    = {2026},
  type    = {Dissertação (Mestrado em Engenharia de Produção)}
}
```

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE).
