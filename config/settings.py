import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys e Tokens
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    NGROK_AUTHTOKEN = os.getenv('NGROK_AUTHTOKEN')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    SPTRANS_API_TOKEN = os.getenv('SPTRANS_API_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
       
    # Configurações de Cache
    CACHE_EXPIRE_HOURS = 24
    
    # Configurações da API
    API_BASE_URL = 'https://api.olhovivo.sptrans.com.br/v2.1'
    MAPS_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
    WHATSAPP_API_URL = 'https://graph.facebook.com/v21.0/458777567322293/messages'
    
    # === Monitoramento ===
    AGNO_MONITOR: str = os.getenv("AGNO_MONITOR", "true")  # 👈 já vem ativado

    # === Debug Global ===
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # Helper
    @property
    def monitor_enabled(self) -> bool:
        return self.AGNO_MONITOR.lower() == "true"

settings = Settings()
