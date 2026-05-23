from playwright.sync_api import sync_playwright
from typing import List, Optional

class HorariosScraper:
    def __init__(self):
        pass  # Nenhuma inicialização necessária sem cache
        
    def scrape(self, numero_linha: str, dia_operacional: Optional[str] = None) -> Optional[List[str]]:
        """
        dia_operacional:
          0 = Segunda a Sexta
          1 = Sábado
          2 = Domingo
        Caso dia_operacional seja None ou fora do intervalo [0,1,2], não filtra o dia no select.
        """
        url = f"https://www.sptrans.com.br/itinerarios/linha/?numero={numero_linha}"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(url)
                
                if dia_operacional in ("0", "1", "2"):
                    page.select_option("#sel_tipodia", str(dia_operacional))
                    page.wait_for_timeout(2000)  # tempo para recarregar os horários
                
                page.wait_for_selector(".partidas span", timeout=5000)
                horarios = page.locator(".partidas span")
                result = [h.text_content() for h in horarios.element_handles()]
                
                return result if result else None
                
            except Exception as e:
                print(f"Erro ao buscar horários: {e}")
                return None
                
            finally:
                browser.close()

# Instância global
horarios_scraper = HorariosScraper()
