from datetime import datetime, date
import re

def format_date(date_str):
    """Formata data para exibição"""
    if not date_str:
        return ""
    
    try:
        if isinstance(date_str, str):
            if '-' in date_str:  # Formato YYYY-MM-DD
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            elif '/' in date_str:  # Formato DD/MM/YYYY
                return date_str
        elif isinstance(date_str, date):
            return date_str.strftime('%d/%m/%Y')
        
        return str(date_str)
    except:
        return str(date_str)

def parse_date(date_str):
    """Converte data DD/MM/YYYY para YYYY-MM-DD"""
    if not date_str:
        return None
    
    try:
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1]:0>2}-{parts[0]:0>2}"
        return date_str
    except:
        return None

def validate_date(date_str):
    """Valida formato de data DD/MM/YYYY"""
    if not date_str:
        return False
    
    try:
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                date(year, month, day)
                return True
        return False
    except:
        return False

def calculate_age(birth_date):
    """Calcula idade baseada na data de nascimento"""
    if not birth_date:
        return 0
    
    try:
        if isinstance(birth_date, str):
            if '-' in birth_date:
                birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
            else:
                return 0
        elif isinstance(birth_date, date):
            birth = birth_date
        else:
            return 0
        
        today = date.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except:
        return 0

def format_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None:
        value = 0
    
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

def format_cpf(cpf):
    """Formata CPF"""
    if not cpf:
        return ""
    
    # Remove tudo que não é número
    numbers = re.sub(r'\D', '', cpf)
    
    # Limita a 11 dígitos
    numbers = numbers[:11]
    
    if len(numbers) <= 3:
        return numbers
    elif len(numbers) <= 6:
        return f"{numbers[:3]}.{numbers[3:]}"
    elif len(numbers) <= 9:
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:]}"
    else:
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"

def validate_cpf(cpf):
    """Valida CPF"""
    if not cpf:
        return False
    
    # Remove formatação
    numbers = re.sub(r'\D', '', cpf)
    
    # Deve ter 11 dígitos
    if len(numbers) != 11:
        return False
    
    # Verifica se não são todos iguais
    if len(set(numbers)) == 1:
        return False
    
    return True

def format_phone(phone):
    """Formata telefone"""
    if not phone:
        return ""
    
    # Remove tudo que não é número
    numbers = re.sub(r'\D', '', phone)
    
    # Limitar a 11 dígitos
    numbers = numbers[:11]
    
    if len(numbers) == 0:
        return ""
    elif len(numbers) <= 2:
        return f"({numbers}"
    elif len(numbers) <= 6:
        return f"({numbers[:2]}) {numbers[2:]}"
    elif len(numbers) <= 7:
        return f"({numbers[:2]}) {numbers[2:7]}"
    else:
        if len(numbers) == 10:
            return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
        else:
            return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"

def validate_phone(phone):
    """Valida telefone"""
    if not phone:
        return False
    
    numbers = re.sub(r'\D', '', phone)
    return len(numbers) >= 10
