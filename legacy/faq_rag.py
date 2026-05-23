import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

# Configurações
FAQ_CACHE_FILE = "faq_data.json"
FAISS_INDEX_FILE = "faq_index.faiss"
EMBEDDINGS_FILE = "faq_embeddings.npy"

# Carrega os dados e o modelo
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

with open(FAQ_CACHE_FILE, 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

# Carrega FAISS
index = faiss.read_index(FAISS_INDEX_FILE)
embeddings = np.load(EMBEDDINGS_FILE)

def search_faq(query, top_k=3):
    """Busca as perguntas mais relevantes no FAISS e retorna respostas"""
    query_embedding = model.encode([query])
    _, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)

    results = []
    for idx in indices[0]:
        if idx < len(faq_data):
            results.append({
                "question": faq_data[idx]["question"],
                "answer": faq_data[idx]["answer"]
            })

    return results

if __name__ == "__main__":
    while True:
        user_query = input("\n🔎 Pergunta: ")
        if user_query.lower() in ["sair", "exit"]:
            break
        
        results = search_faq(user_query)
        if results:
            print("\n🎯 Melhor resposta encontrada:\n", results[0]["answer"])
        else:
            print("\n❌ Desculpe, não encontrei uma resposta específica para essa pergunta.")
