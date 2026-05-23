from datetime import datetime, timedelta
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from legacy.database import db

class ChatHistory:
    def __init__(self, session_timeout_hours: int = 24):
        self.session_timeout = session_timeout_hours
        
    def _get_session_id(self, phone_number: str) -> str:
        try:
            with db.get_connection() as conn:
                result = conn.execute("""
                    SELECT session_id, timestamp 
                    FROM chat_history 
                    WHERE phone_number = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (phone_number,)).fetchone()
                
                if result:
                    session_id, timestamp = result
                    last_time = datetime.fromisoformat(timestamp)
                    
                    if datetime.now() - last_time < timedelta(hours=self.session_timeout):
                        return session_id
                        
                return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{phone_number}"
        except Exception as e:
            print(f"Erro ao obter session_id: {e}")
            return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{phone_number}"
    
    def add_message(self, phone_number: str, message_type: str, content: str):
        try:
            session_id = self._get_session_id(phone_number)
            timestamp = datetime.now().isoformat()
            
            with db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO chat_history 
                    (phone_number, message_type, content, timestamp, session_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (phone_number, message_type, content, timestamp, session_id))
        except Exception as e:
            print(f"Erro ao adicionar mensagem: {e}")
    
    def get_recent_history(self, phone_number: str, limit: int = 10) -> List:
        try:
            session_id = self._get_session_id(phone_number)
            
            with db.get_connection() as conn:
                messages = conn.execute("""
                    SELECT message_type, content 
                    FROM chat_history 
                    WHERE phone_number = ? AND session_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (phone_number, session_id, limit)).fetchall()
                
                return [
                    HumanMessage(content=content) if msg_type == "human"
                    else SystemMessage(content=content)
                    for msg_type, content in reversed(messages)
                ]
        except Exception as e:
            print(f"Erro ao recuperar histórico: {e}")
            return []