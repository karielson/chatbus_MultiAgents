# Extrator de Horários de Partida com Playwright

Este projeto utiliza o Playwright para acessar páginas da web e capturar dados visuais, como horários de partidas de linhas de ônibus. O script acessa a página da linha de ônibus especificada no site da SPTrans, aguarda o carregamento dos dados e extrai os horários de partidas da seção correspondente.

## Pré-requisitos

Antes de rodar o código, você precisará garantir que as seguintes dependências estejam instaladas em seu ambiente:

- Python 3.7 ou superior
- Playwright

## Instalação

1. **Instale todas as dependências**

   ```bash
   pip install -r requirements.txt
   ```

2. **Instale o Playwright:**

   Primeiro, instale o Playwright utilizando o `pip`:

   ```bash
   pip install playwright
   ```

   Após instalar o Playwright, você deve instalar os navegadores com o seguinte comando:

   ```bash
   playwright install
   ```

3. **Instalar Libs**

   algumas libs que precisei instalar depois do comando item 1

   ```bash
   pip install flask pyngrok python-dotenv requests agno openai sqlalchemy playwright pip lancedb tantivy fastapi uvicorn

   ```
