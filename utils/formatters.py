from datetime import datetime, date

def format_currency(value):
    """Formata valor para moeda brasileira"""
    try:
        if value is None:
            return "R$ 0,00"
        
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

def format_date(date_value):
    """Formata data para DD/MM/AAAA"""
    try:
        if not date_value:
            return ""
        
        if isinstance(date_value, str):
            # Tentar diferentes formatos
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            return date_value
        
        elif isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
        
        elif isinstance(date_value, date):
            return date_value.strftime('%d/%m/%Y')
        
        return str(date_value)
        
    except:
        return ""

def calculate_age(birth_date):
    """Calcula idade baseada na data de nascimento"""
    try:
        if not birth_date:
            return 0
        
        if isinstance(birth_date, str):
            # Tentar diferentes formatos
            for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                try:
                    birth_dt = datetime.strptime(birth_date, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return 0
        elif isinstance(birth_date, datetime):
            birth_dt = birth_date.date()
        elif isinstance(birth_date, date):
            birth_dt = birth_date
        else:
            return 0
        
        today = date.today()
        age = today.year - birth_dt.year
        
        # Verificar se já fez aniversário este ano
        if today < date(today.year, birth_dt.month, birth_dt.day):
            age -= 1
        
        return age
        
    except:
        return 0

def parse_date(date_string):
    """Converte string de data DD/MM/AAAA para objeto date"""
    try:
        if not date_string or date_string == "DD/MM/AAAA":
            return None
        
        if '/' in date_string:
            parts = date_string.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return date(int(year), int(month), int(day))
        
        return None
        
    except:
        return None
