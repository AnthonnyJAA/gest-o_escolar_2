from database.connection import db
import sqlite3
from datetime import datetime, date, timedelta

class ConfigFinanceiraService:
    def __init__(self):
        self.db = db
    
    def obter_configuracoes(self):
        """Obtém configurações financeiras"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM config_financeiras ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'desconto_pontualidade': row[1],
                'dias_limite_desconto': row[2],
                'multa_por_dia': row[3],
                'dias_carencia_multa': row[4],
                'descricao': row[5],
                'updated_at': row[6]
            }
        else:
            # Retornar valores padrão
            return {
                'id': 1,
                'desconto_pontualidade': 10.0,
                'dias_limite_desconto': 5,
                'multa_por_dia': 2.0,
                'dias_carencia_multa': 30,
                'descricao': 'Configurações padrão',
                'updated_at': datetime.now().isoformat()
            }
    
    def salvar_configuracoes(self, config_data):
        """Salva configurações financeiras"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO config_financeiras 
                (id, desconto_pontualidade, dias_limite_desconto, multa_por_dia, 
                 dias_carencia_multa, descricao, updated_at)
                VALUES (1, ?, ?, ?, ?, ?, ?)
            """, (
                config_data['desconto_pontualidade'],
                config_data['dias_limite_desconto'],
                config_data['multa_por_dia'],
                config_data['dias_carencia_multa'],
                config_data.get('descricao', 'Configurações atualizadas'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return {'success': True}
            
        except sqlite3.Error as e:
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def calcular_valor_com_ajustes(self, valor_original, data_vencimento, data_pagamento, pode_receber_multa=True):
        """Calcula valor com desconto ou multa baseado nas datas"""
        config = self.obter_configuracoes()
        
        # Valores base
        valor_final = valor_original
        desconto_aplicado = 0
        multa_aplicada = 0
        
        if not data_pagamento:
            # Sem pagamento, retornar valor original
            return {
                'valor_final': valor_original,
                'desconto_aplicado': 0,
                'multa_aplicada': 0,
                'pode_ter_desconto': self._pode_ter_desconto(data_vencimento, date.today(), config),
                'dias_atraso': self._calcular_dias_atraso(data_vencimento, date.today()),
                'observacao': 'Aguardando pagamento'
            }
        
        try:
            # Converter datas
            if isinstance(data_vencimento, str):
                data_venc = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            else:
                data_venc = data_vencimento
            
            if isinstance(data_pagamento, str):
                data_pag = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
            else:
                data_pag = data_pagamento
            
            dias_diferenca = (data_pag - data_venc).days
            
            if dias_diferenca <= 0:
                # Pagamento antecipado ou no vencimento
                if abs(dias_diferenca) <= config['dias_limite_desconto']:
                    # Aplicar desconto por pontualidade
                    desconto_aplicado = config['desconto_pontualidade']
                    valor_final = valor_original - desconto_aplicado
                    observacao = f"Desconto por pontualidade aplicado (pago {abs(dias_diferenca)} dia(s) antes do vencimento)"
                else:
                    observacao = "Pago no vencimento"
            else:
                # Pagamento em atraso
                if pode_receber_multa and dias_diferenca > config['dias_carencia_multa']:
                    # Aplicar multa apenas após período de carência
                    dias_multa = dias_diferenca - config['dias_carencia_multa']
                    multa_aplicada = dias_multa * config['multa_por_dia']
                    valor_final = valor_original + multa_aplicada
                    observacao = f"Multa aplicada ({dias_multa} dias × R$ {config['multa_por_dia']:.2f})"
                else:
                    if not pode_receber_multa:
                        observacao = f"Pago com {dias_diferenca} dias de atraso (sem multa - matrícula anterior)"
                    else:
                        observacao = f"Pago com {dias_diferenca} dias de atraso (dentro do período de carência)"
            
            return {
                'valor_final': max(valor_final, 0),  # Nunca deixar valor negativo
                'desconto_aplicado': desconto_aplicado,
                'multa_aplicada': multa_aplicada,
                'dias_diferenca': dias_diferenca,
                'observacao': observacao
            }
            
        except Exception as e:
            return {
                'valor_final': valor_original,
                'desconto_aplicado': 0,
                'multa_aplicada': 0,
                'dias_diferenca': 0,
                'observacao': f'Erro no cálculo: {str(e)}'
            }
    
    def _pode_ter_desconto(self, data_vencimento, data_atual, config):
        """Verifica se ainda pode ter desconto"""
        try:
            if isinstance(data_vencimento, str):
                data_venc = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            else:
                data_venc = data_vencimento
            
            data_limite = data_venc - timedelta(days=config['dias_limite_desconto'])
            return data_atual <= data_limite
        except:
            return False
    
    def _calcular_dias_atraso(self, data_vencimento, data_atual):
        """Calcula dias de atraso"""
        try:
            if isinstance(data_vencimento, str):
                data_venc = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
            else:
                data_venc = data_vencimento
            
            diferenca = (data_atual - data_venc).days
            return max(diferenca, 0)
        except:
            return 0
    
    def calcular_preview_valores(self, valor_original, data_vencimento):
        """Calcula preview de valores para diferentes cenários"""
        config = self.obter_configuracoes()
        
        # Cenário 1: Pagamento antecipado (com desconto)
        data_antecipada = datetime.strptime(data_vencimento, '%Y-%m-%d').date() - timedelta(days=config['dias_limite_desconto'])
        cenario_desconto = self.calcular_valor_com_ajustes(valor_original, data_vencimento, data_antecipada.strftime('%Y-%m-%d'))
        
        # Cenário 2: Pagamento no vencimento
        cenario_normal = self.calcular_valor_com_ajustes(valor_original, data_vencimento, data_vencimento)
        
        # Cenário 3: Pagamento com atraso (após carência)
        data_atrasada = datetime.strptime(data_vencimento, '%Y-%m-%d').date() + timedelta(days=config['dias_carencia_multa'] + 10)
        cenario_multa = self.calcular_valor_com_ajustes(valor_original, data_vencimento, data_atrasada.strftime('%Y-%m-%d'))
        
        return {
            'config': config,
            'cenario_desconto': cenario_desconto,
            'cenario_normal': cenario_normal,
            'cenario_multa': cenario_multa,
            'data_limite_desconto': data_antecipada.strftime('%d/%m/%Y'),
            'data_inicio_multa': (datetime.strptime(data_vencimento, '%Y-%m-%d').date() + timedelta(days=config['dias_carencia_multa'])).strftime('%d/%m/%Y')
        }
