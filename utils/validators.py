def is_valid_cpf(cpf):
    if len(cpf) != 11 or not cpf.isdigit():
        return False

    # CPF validation logic
    def calculate_digit(cpf, factor):
        total = sum(int(digit) * factor for digit, factor in zip(cpf[:factor-1], range(factor, 1, -1)))
        remainder = total % 11
        return str(0 if remainder < 2 else 11 - remainder)

    first_digit = calculate_digit(cpf, 10)
    second_digit = calculate_digit(cpf, 11)

    return cpf[-2:] == first_digit + second_digit

def is_valid_email(email):
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_phone(phone):
    return len(phone) >= 10 and phone.isdigit()

def is_not_empty(value):
    return bool(value and value.strip())