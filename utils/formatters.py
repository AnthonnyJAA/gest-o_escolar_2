import re
from datetime import datetime, date

def format_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_phone(phone):
    """Formata telefone brasileiro"""
    if not phone:
        return ""
    
    numbers = re.sub(r'\D', '', phone)
    
    if len(numbers) == 11:
        return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
    elif len(numbers) == 10:
        return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
    else:
        return phone

def validate_phone(phone):
    """Valida telefone brasileiro"""
    if not phone:
        return True  # Telefone é opcional
    
    numbers = re.sub(r'\D', '', phone)
    return len(numbers) in [10, 11]

def format_cpf(cpf):
    """Formata CPF brasileiro"""
    if not cpf:
        return ""
    
    numbers = re.sub(r'\D', '', cpf)
    
    if len(numbers) >= 11:
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:11]}"
    elif len(numbers) >= 9:
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"
    elif len(numbers) >= 6:
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:]}"
    elif len(numbers) >= 3:
        return f"{numbers[:3]}.{numbers[3:]}"
    else:
        return numbers

def validate_cpf(cpf):
    """Valida CPF brasileiro"""
    if not cpf:
        return True  # CPF é opcional
    
    # Remove formatação
    numbers = re.sub(r'\D', '', cpf)
    
    # Deve ter 11 dígitos
    if len(numbers) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if numbers == numbers[0] * 11:
        return False
    
    # Calcula primeiro dígito verificador
    sum1 = sum(int(numbers[i]) * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 == 10:
        digit1 = 0
    
    # Calcula segundo dígito verificador
    sum2 = sum(int(numbers[i]) * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 == 10:
        digit2 = 0
    
    # Verifica se os dígitos calculados conferem
    return int(numbers[9]) == digit1 and int(numbers[10]) == digit2

def format_date(date_input):
    """Formata data para DD/MM/YYYY"""
    if not date_input:
        return ""
    
    if isinstance(date_input, str):
        try:
            if len(date_input) == 10 and date_input[4] == '-':
                # Formato YYYY-MM-DD para DD/MM/YYYY
                parts = date_input.split('-')
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            else:
                return date_input
        except:
            return date_input
    
    if isinstance(date_input, (date, datetime)):
        return date_input.strftime('%d/%m/%Y')
    
    return str(date_input)

def parse_date(date_string):
    """Converte DD/MM/YYYY para YYYY-MM-DD"""
    if not date_string:
        return None
    
    try:
        if '/' in date_string:
            parts = date_string.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return date_string
    except:
        return date_string

def validate_date(date_string):
    """Valida formato de data DD/MM/YYYY"""
    if not date_string:
        return False
    
    try:
        if len(date_string) != 10 or date_string.count('/') != 2:
            return False
        
        day, month, year = date_string.split('/')
        datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
        return True
    except:
        return False

def calculate_age(birth_date):
    """Calcula idade baseada na data de nascimento"""
    if not birth_date:
        return 0
    
    try:
        if isinstance(birth_date, str):
            if '/' in birth_date:
                # DD/MM/YYYY
                day, month, year = birth_date.split('/')
                birth_date = date(int(year), int(month), int(day))
            elif '-' in birth_date:
                # YYYY-MM-DD
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return 0

# Função adicional para validar números (se necessário)
def validate_number(value):
    """Valida se é um número"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def format_number(value, decimals=2):
    """Formata número com casas decimais"""
    try:
        return f"{float(value):.{decimals}f}"
    except:
        return "0.00"
