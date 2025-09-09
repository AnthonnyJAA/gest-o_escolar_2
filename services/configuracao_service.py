from database.connection import db
import sqlite3
from datetime import datetime

class ConfiguracaoService:
    def __init__(self):
        self.db = db
        self.init_config_table()
    
    def init_config_table(self):
        """Inicializa tabela de configurações"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                descricao TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def obter_configuracao(self, chave, valor_padrao=None):
        """Obtém uma configuração"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else valor_padrao
    
    def salvar_configuracao(self, chave, valor, descricao=None):
        """Salva uma configuração"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO configuracoes (chave, valor, descricao, updated_at)
                VALUES (?, ?, ?, ?)
            """, (chave, str(valor), descricao, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return {'success': True}
        except sqlite3.Error as e:
            conn.close()
            return {'success': False, 'error': str(e)}
