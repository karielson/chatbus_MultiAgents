# update_faq.py
"""
Atualiza data/faq_data.json raspando o FAQ da SPTrans e, ao final,
recria o índice LanceDB usado pelo agente FAQ.

Uso:
  python update_faq.py                # raspa, salva JSON e recria índice
  python update_faq.py --no-reload    # só raspa e salva o JSON
  python update_faq.py --headful      # navegador visível (debug)
  python update_faq.py --limit 3      # limita categorias (debug)
"""

import argparse, json, os, sys, time
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright

FAQ_URL = "https://www.sptrans.com.br/perguntas-e-respostas/"
FAQ_JSON = "data/faq_data.json"
LOAD_DELAY_SEC = 2.2
WAIT_SELECTOR = "#tipo_duvida"
PANEL_SELECTOR = ".panel"
Q_SELECTOR = ".botao"
A_SELECTOR = ".panel-body"


def _dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen, out = set(), []
    for it in items:
        key = (
            (it.get("question") or "").strip().lower(),
            (it.get("answer") or "").strip().lower(),
        )
        if key not in seen and key[0] and key[1]:
            seen.add(key)
            out.append(it)
    return out


def scrape_faq(headless: bool = True, categories_limit: int | None = None) -> List[Dict[str, str]]:
    data: List[Dict[str, str]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(FAQ_URL, wait_until="domcontentloaded")
        page.wait_for_selector(WAIT_SELECTOR, timeout=20_000)

        categories = page.eval_on_selector_all(
            f"{WAIT_SELECTOR} option",
            "els => els.map(o => ({value:o.value, text:o.textContent?.trim()})).filter(o => o.value)"
        )
        if categories_limit:
            categories = categories[:categories_limit]

        for c in categories:
            page.select_option(WAIT_SELECTOR, c["value"])
            time.sleep(LOAD_DELAY_SEC)

            faq_items = page.evaluate(
                f"""
                () => Array.from(document.querySelectorAll('{PANEL_SELECTOR}')).map(panel => {{
                    const q = panel.querySelector('{Q_SELECTOR}');
                    const a = panel.querySelector('{A_SELECTOR}');
                    return {{
                        question: (q?.textContent || "").trim(),
                        answer: (a?.textContent || "").trim()
                    }};
                }}).filter(x => x.question && x.answer);
                """
            )
            for item in faq_items:
                q = (item["question"] or "").strip()
                a = (item["answer"] or "").strip()
                data.append({
                    "category": c["text"],
                    "question": q,
                    "answer": a,
                    "text": f"{q}\n\n{a}",  # <-- ADICIONE ESTE CAMPO
                })

        browser.close()
    return _dedupe(data)


def save_json_atomic(path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def reload_lancedb():
    """
    Recria o índice LanceDB usado pelo agente FAQ.
    Fazendo aqui, o agente fica apenas para consultas (sem latência de criação).
    """
    try:
        from agents.agente_faq import knowledge
        print("🔄 Recriando índices no LanceDB (knowledge.load(recreate=True))...")
        knowledge.load(recreate=True)
        print("✅ LanceDB recarregado com sucesso.")
    except Exception as e:
        print(f"⚠️  Não foi possível recarregar o LanceDB agora: {e}")
        print('    Dica: python -c "from agents.agente_faq import knowledge; knowledge.load(recreate=True)"')


def main():
    ap = argparse.ArgumentParser(description="Atualiza data/faq_data.json (FAQ SPTrans).")
    ap.add_argument("--no-reload", action="store_true", help="Não recarrega LanceDB.")
    ap.add_argument("--headful", action="store_true", help="Navegador visível (debug).")
    ap.add_argument("--limit", type=int, default=None, help="Limita categorias (debug).")
    args = ap.parse_args()

    print("📡 Extraindo FAQ da SPTrans...")
    items = scrape_faq(headless=not args.headful, categories_limit=args.limit)
    print(f"🧾 Coletados {len(items)} Q&A (após dedupe).")

    # JSON final sem o campo 'text' (o agente busca por 'question')
    print(f"💾 Salvando JSON em: {FAQ_JSON}")
    save_json_atomic(FAQ_JSON, items)
    print("✅ data/faq_data.json atualizado.")

    if not args.no_reload:
        reload_lancedb()
    else:
        print("ℹ️  Pulei o recarregamento do LanceDB (--no-reload).")


if __name__ == "__main__":
    sys.exit(main())
