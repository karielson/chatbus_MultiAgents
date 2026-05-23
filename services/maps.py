import requests
from config.settings import settings
from core.cache import cached
from typing import Dict, Optional

class MapsService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.api_url = settings.MAPS_API_URL


    @cached(expire_hours=1)
    def get_directions(
        self, 
        origin: str, 
        destination: str, 
        mode: str = 'transit', 
        transit_mode: str = 'bus',
        preferencia: str = None
    ) -> Optional[str]:
        # Adiciona "São Paulo, SP" aos endereços
        
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'transit_mode': transit_mode,
            'key': self.api_key
        }
        

        # Ajusta parâmetros conforme a preferência informada
        if preferencia == 'menos_baldeacoes':
            params['transit_routing_preference'] = 'fewer_transfers'
        elif preferencia == 'menos_caminhada':
            params['transit_routing_preference'] = 'less_walking'
        elif preferencia == 'rapida':
            # Uma forma é ativar rotas alternativas e depois filtrar a mais rápida
            params['alternatives'] = 'true'

        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            return self._format_directions(response.json(), preferencia)
        return None
        
    def _format_directions(self, data: Dict, preferencia: str = None) -> Optional[str]:
        if data['status'] != 'OK':
            return None

        routes = data['routes']
        
        if preferencia == 'rapida' and len(routes) > 1:
            # Ordenar pelas durações (em segundos)
            routes = sorted(routes, key=lambda r: r['legs'][0]['duration']['value'])

        # Então pega a primeira do array (que será a mais rápida, se preferencia == 'rapida')
        route = routes[0]
        formatted_route = []
        
        for leg in route['legs']:
            formatted_route.extend([
                f"Origem: {leg['start_address']}",
                f"Destino: {leg['end_address']}",
                f"Duração: {leg['duration']['text']}",
                f"Distância: {leg['distance']['text']}\n"
            ])
            
            for step in leg['steps']:
                formatted_route.extend([
                    f" - {step['html_instructions']} ({step['distance']['text']})",
                    f"   Duração: {step['duration']['text']}",
                    f"   Modo: {step['travel_mode']}"
                ])
                
                if step['travel_mode'] == 'TRANSIT':
                    transit = step['transit_details']
                    formatted_route.extend([
                        f"   Linha: {transit['line']['short_name']} - {transit['line']['name']}",
                        f"   De: {transit['departure_stop']['name']}",
                        f"   Para: {transit['arrival_stop']['name']}",
                        f"   Horário de saída: {transit['departure_time']['text']}",
                        f"   Horário de chegada: {transit['arrival_time']['text']}\n"
                    ])
                    
        return "\n".join(formatted_route)

maps = MapsService()