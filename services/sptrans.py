import requests
from config.settings import settings
from core.cache import cached
from typing import List, Optional

class SPTransService:
    def __init__(self):
        self.api_url = settings.API_BASE_URL
        self.token = settings.SPTRANS_API_TOKEN
        
    def _get_session(self) -> requests.Session:
        session = requests.Session()
        auth_url = f'{self.api_url}/Login/Autenticar?token={self.token}'
        session.post(auth_url)
        return session
        
    @cached(expire_hours=24)
    def buscar_linha(self, termo: str) -> Optional[List[str]]:
        session = self._get_session()
        response = session.get(f'{self.api_url}/Linha/Buscar?termosBusca={termo}')
        
        if response.status_code == 200:
            linhas = response.json()
            return list({f"{linha['lt']}-{linha['tl']}" for linha in linhas})
        return None
    
    @cached(expire_hours=24)
    def buscar_info_linhas(self, termo: str) -> Optional[List[str]]:
        session = self._get_session()
        response = session.get(f'{self.api_url}/Linha/Buscar?termosBusca={termo}')
        
        if response.status_code == 200:
            linha = response.json()
            
            return linha
        return None

    # @cached(expire_hours=24)
    # def buscar_codigo(self, termo: str) -> int:
    #     session = self._get_session()
    #     response = session.get(f'{self.api_url}/Linha/Buscar?termosBusca={termo}')
        
    #     if response.status_code == 200:
    #         linha = response.json()
    #         return linha[0]['cl']
    #     return None
    
    @cached(expire_hours=0.1)
    def buscar_parada(self, termos_busca: str) -> Optional[list]:
        """Busca paradas de ônibus com base no nome ou endereço."""
        session = self._get_session()
        response = session.get(f"{self.api_url}/Parada/Buscar?termosBusca={termos_busca}")
        if response.status_code == 200:
            return response.json()
        return None
    
    @cached(expire_hours=0.1)
    def buscar_paradas_linha(self, codigoLinha: int) -> Optional[list]:
        """Busca paradas de ônibus com base nona linha."""
        session = self._get_session()
        response = session.get(f"{self.api_url}/Parada/BuscarParadasPorLinha?codigoLinha={codigoLinha}")
        if response.status_code == 200:
            return response.json()
        return None

    @cached(expire_hours=0.1)
    def buscar_previsao_chegada(self, codigo_linha: int, codigo_parada: int) -> Optional[dict]:
        """Busca a previsão de chegada dos ônibus para uma linha e parada específicas."""
        session = self._get_session()
        url = f"{self.api_url}/Previsao?codigoParada={codigo_parada}&codigoLinha={codigo_linha}"
        response = session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar previsão de chegada: {response.status_code}")
            return None


sptrans = SPTransService()


