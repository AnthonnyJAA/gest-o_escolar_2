import csv
from datetime import datetime
from utils.formatters import format_currency, format_date

class ExportService:
    def __init__(self):
        pass
    
    def exportar_mensalidades_csv(self, mensalidades, filename="mensalidades.csv"):
        """Exporta mensalidades para CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'ID', 'Aluno', 'Turma', 'Mes_Ano', 'Valor_Original', 
                    'Desconto', 'Multa', 'Valor_Final', 'Data_Vencimento', 
                    'Data_Pagamento', 'Status', 'Responsavel', 'Telefone', 'Observacoes'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for m in mensalidades:
                    writer.writerow({
                        'ID': m.get('id', ''),
                        'Aluno': m.get('aluno_nome', ''),
                        'Turma': f"{m.get('turma_nome', '')} - {m.get('turma_serie', '')}",
                        'Mes_Ano': m.get('mes_referencia', ''),
                        'Valor_Original': m.get('valor_original', 0),
                        'Desconto': m.get('desconto_aplicado', 0),
                        'Multa': m.get('multa_aplicada', 0),
                        'Valor_Final': m.get('valor_final', 0),
                        'Data_Vencimento': format_date(m.get('data_vencimento', '')),
                        'Data_Pagamento': format_date(m.get('data_pagamento', '')) if m.get('data_pagamento') else '',
                        'Status': m.get('status', ''),
                        'Responsavel': m.get('responsavel_nome', ''),
                        'Telefone': m.get('responsavel_telefone', ''),
                        'Observacoes': m.get('observacoes', '')
                    })
            
            return {'success': True, 'filename': filename}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
