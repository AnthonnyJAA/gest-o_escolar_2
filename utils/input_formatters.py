import tkinter as tk
import re

class InputFormatter:
    """Classe para formatação inteligente de campos de entrada"""
    
    @staticmethod
    def format_phone_smart(text):
        """Formata telefone: (11) 98765-4321"""
        # Remove tudo que não é número
        numbers = re.sub(r'\D', '', text)
        
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
            # Para números com 10 ou 11 dígitos
            if len(numbers) == 10:
                return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
            else:
                return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
    
    @staticmethod
    def format_cpf_smart(text):
        """Formata CPF: 123.456.789-01"""
        # Remove tudo que não é número
        numbers = re.sub(r'\D', '', text)
        
        # Limitar a 11 dígitos
        numbers = numbers[:11]
        
        if len(numbers) == 0:
            return ""
        elif len(numbers) <= 3:
            return numbers
        elif len(numbers) <= 6:
            return f"{numbers[:3]}.{numbers[3:]}"
        elif len(numbers) <= 9:
            return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:]}"
        else:
            return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"
    
    @staticmethod
    def format_date_smart(text):
        """Formata data: 01/12/1990"""
        # Remove tudo que não é número
        numbers = re.sub(r'\D', '', text)
        
        # Limitar a 8 dígitos
        numbers = numbers[:8]
        
        if len(numbers) == 0:
            return ""
        elif len(numbers) <= 2:
            return numbers
        elif len(numbers) <= 4:
            return f"{numbers[:2]}/{numbers[2:]}"
        else:
            return f"{numbers[:2]}/{numbers[2:4]}/{numbers[4:]}"
    
    @staticmethod
    def format_currency_smart(text):
        """Formata moeda: R$ 1.234,56"""
        # Remove tudo que não é número
        numbers = re.sub(r'\D', '', text)
        
        if len(numbers) == 0:
            return "0,00"
        
        # Converter para float (considerando centavos)
        value = int(numbers) / 100
        
        # Formatar como moeda brasileira
        return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def clean_phone(formatted_text):
        """Remove formatação do telefone"""
        return re.sub(r'\D', '', formatted_text)
    
    @staticmethod
    def clean_cpf(formatted_text):
        """Remove formatação do CPF"""
        return re.sub(r'\D', '', formatted_text)
    
    @staticmethod
    def clean_date(formatted_text):
        """Remove formatação da data"""
        return re.sub(r'\D', '', formatted_text)
    
    @staticmethod
    def clean_currency(formatted_text):
        """Remove formatação da moeda e retorna float"""
        numbers = re.sub(r'[^\d,]', '', formatted_text).replace(',', '.')
        try:
            return float(numbers) if numbers else 0.0
        except ValueError:
            return 0.0

class SmartEntry:
    """Classe para criar campos de entrada com formatação inteligente"""
    
    def __init__(self, parent, textvariable, format_type, **kwargs):
        self.textvariable = textvariable
        self.format_type = format_type
        self.formatter = InputFormatter()
        
        # Criar entry normal
        self.entry = tk.Entry(parent, textvariable=textvariable, **kwargs)
        
        # Bind dos eventos
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Variável para controlar se estamos formatando
        self._formatting = False
    
    def _on_key_release(self, event=None):
        """Evento executado quando uma tecla é liberada"""
        if self._formatting:
            return
        
        self._formatting = True
        
        # Obter posição atual do cursor
        cursor_pos = self.entry.index(tk.INSERT)
        
        # Obter texto atual
        current_text = self.textvariable.get()
        
        # Aplicar formatação baseada no tipo
        if self.format_type == 'phone':
            formatted = self.formatter.format_phone_smart(current_text)
        elif self.format_type == 'cpf':
            formatted = self.formatter.format_cpf_smart(current_text)
        elif self.format_type == 'date':
            formatted = self.formatter.format_date_smart(current_text)
        elif self.format_type == 'currency':
            formatted = self.formatter.format_currency_smart(current_text)
        else:
            formatted = current_text
        
        # Atualizar apenas se mudou
        if formatted != current_text:
            self.textvariable.set(formatted)
            # Posicionar cursor no final
            self.entry.icursor(len(formatted))
        
        self._formatting = False
    
    def _on_focus_out(self, event=None):
        """Executado quando o campo perde o foco - formatação final"""
        self._on_key_release()
    
    def get_clean_value(self):
        """Retorna valor sem formatação"""
        formatted_text = self.textvariable.get()
        
        if self.format_type == 'phone':
            return self.formatter.clean_phone(formatted_text)
        elif self.format_type == 'cpf':
            return self.formatter.clean_cpf(formatted_text)
        elif self.format_type == 'date':
            return self.formatter.clean_date(formatted_text)
        elif self.format_type == 'currency':
            return self.formatter.clean_currency(formatted_text)
        else:
            return formatted_text
    
    def set_value(self, value):
        """Define valor com formatação automática"""
        self.textvariable.set(str(value))
        self._on_key_release()
    
    def pack(self, **kwargs):
        """Método pack para o entry"""
        return self.entry.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Método grid para o entry"""
        return self.entry.grid(**kwargs)
    
    def focus_set(self):
        """Define foco no entry"""
        return self.entry.focus_set()
    
    def bind(self, event, callback):
        """Bind de eventos para o entry"""
        return self.entry.bind(event, callback)

class NumberOnlyEntry:
    """Entry que aceita apenas números (sem formatação)"""
    
    def __init__(self, parent, textvariable, max_length=None, **kwargs):
        self.textvariable = textvariable
        self.max_length = max_length
        
        # Registrar validação
        vcmd = (parent.register(self._validate), '%P')
        
        self.entry = tk.Entry(
            parent, 
            textvariable=textvariable,
            validate='key',
            validatecommand=vcmd,
            **kwargs
        )
    
    def _validate(self, value):
        """Valida entrada - apenas números"""
        if value == "":
            return True
        
        try:
            int(value)
            if self.max_length and len(value) > self.max_length:
                return False
            return True
        except ValueError:
            return False
    
    def pack(self, **kwargs):
        return self.entry.pack(**kwargs)
    
    def grid(self, **kwargs):
        return self.entry.grid(**kwargs)
    
    def focus_set(self):
        return self.entry.focus_set()
    
    def bind(self, event, callback):
        return self.entry.bind(event, callback)

class CurrencyEntry:
    """Entry específico para valores monetários"""
    
    def __init__(self, parent, textvariable, **kwargs):
        self.textvariable = textvariable
        self.formatter = InputFormatter()
        
        # Frame para o R$ + Entry
        self.frame = tk.Frame(parent, bg=kwargs.get('bg', 'white'))
        
        # Label R$
        tk.Label(
            self.frame, text="R$", 
            font=kwargs.get('font', ('Arial', 11, 'bold')),
            bg=kwargs.get('bg', 'white')
        ).pack(side=tk.LEFT)
        
        # Entry para o valor
        self.entry = tk.Entry(
            self.frame,
            textvariable=textvariable,
            width=kwargs.get('width', 10),
            font=kwargs.get('font', ('Arial', 11)),
            relief=kwargs.get('relief', 'solid'),
            bd=kwargs.get('bd', 1)
        )
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Bind eventos
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Inicializar com 0,00
        if not textvariable.get():
            textvariable.set("0,00")
        
        self._formatting = False
    
    def _on_key_release(self, event=None):
        """Formatar valor monetário"""
        if self._formatting:
            return
        
        self._formatting = True
        
        current = self.textvariable.get()
        formatted = self.formatter.format_currency_smart(current)
        
        if formatted != current:
            self.textvariable.set(formatted)
            self.entry.icursor(len(formatted))
        
        self._formatting = False
    
    def _on_focus_out(self, event=None):
        """Formatação final ao perder foco"""
        self._on_key_release()
    
    def get_float_value(self):
        """Retorna valor como float"""
        return self.formatter.clean_currency(self.textvariable.get())
    
    def set_float_value(self, value):
        """Define valor a partir de um float"""
        formatted = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        self.textvariable.set(formatted)
    
    def pack(self, **kwargs):
        return self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        return self.frame.grid(**kwargs)
