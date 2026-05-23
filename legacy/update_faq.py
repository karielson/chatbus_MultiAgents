import faiss
import numpy as np
import json
import time
from sentence_transformers import SentenceTransformer
from playwright.sync_api import sync_playwright

# Configurações
FAQ_URL = "https://www.sptrans.com.br/perguntas-e-respostas/"
FAQ_CACHE_FILE = "faq_data.json"
FAISS_INDEX_FILE = "faq_index.faiss"
EMBEDDINGS_FILE = "faq_embeddings.npy"

# Modelo de embeddings
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

def scrape_faq():
    """Raspa perguntas e respostas do FAQ da SPTrans usando Playwright"""
    faq_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FAQ_URL)
        
        # Aguarda o dropdown de categorias carregar
        page.wait_for_selector("#tipo_duvida")

        # Obtém as categorias disponíveis
        categories = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('#tipo_duvida option'))
                .map(option => ({
                    value: option.value,
                    text: option.text
                }))
                .filter(opt => opt.value);
        }''')

        for category in categories:
            page.select_option('#tipo_duvida', category['value'])
            time.sleep(2)  # Espera o carregamento

            # Extrai perguntas e respostas
            faq_items = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.panel'))
                    .map(panel => ({
                        question: panel.querySelector('.botao')?.textContent.trim(),
                        answer: panel.querySelector('.panel-body')?.textContent.trim()
                    }))
                    .filter(item => item.question && item.answer);
            }''')

            for item in faq_items:
                faq_data.append({
                    "category": category['text'],
                    "question": item['question'],
                    "answer": item['answer']
                })

        browser.close()

    return faq_data

def save_faq_data(faq_data):
    """Salva os dados coletados em JSON"""
    with open(FAQ_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(faq_data, f, ensure_ascii=False, indent=2)

def generate_faq_embeddings(faq_data):
    """Gera embeddings das perguntas e armazena no FAISS"""
    questions = [item["question"] for item in faq_data]
    embeddings = model.encode(questions)

    # Salva os embeddings em numpy para referência
    np.save(EMBEDDINGS_FILE, embeddings)

    # Configura FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype=np.float32))

    # Salva o índice FAISS
    faiss.write_index(index, FAISS_INDEX_FILE)

    return index

if __name__ == "__main__":
    print("📡 Extraindo FAQ...")
    faq_data = scrape_faq()
    save_faq_data(faq_data)

    print(f"✅ {len(faq_data)} perguntas e respostas extraídas.")

    print("🧠 Gerando embeddings e armazenando no FAISS...")
    generate_faq_embeddings(faq_data)
    print("✅ Embeddings armazenados!")

    print("🚀 Processo de indexação concluído! Agora, use `faq_rag.py` para buscar respostas.")
