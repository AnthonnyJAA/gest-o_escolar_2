"""
Tema claro para o Sistema de Gestão Escolar
"""

# Cores principais do tema claro
LIGHT_THEME = {
    # Cores de fundo
    'bg_primary': '#ffffff',        # Fundo principal branco
    'bg_secondary': '#f8f9fa',      # Fundo secundário cinza claro
    'bg_tertiary': '#e9ecef',       # Fundo terciário
    'bg_hover': '#dee2e6',          # Hover states
    'bg_selected': '#e7f3ff',       # Selecionado azul claro
    
    # Cores de texto
    'text_primary': '#212529',       # Texto principal preto
    'text_secondary': '#6c757d',     # Texto secundário cinza
    'text_disabled': '#adb5bd',      # Texto desabilitado
    
    # Cores de destaque
    'accent_blue': '#0d6efd',        # Azul principal
    'accent_green': '#198754',       # Verde sucesso
    'accent_red': '#dc3545',         # Vermelho erro
    'accent_orange': '#fd7e14',      # Laranja aviso
    'accent_purple': '#6f42c1',      # Roxo
    
    # Cores do menu
    'menu_bg': '#343a40',
    'menu_hover': '#495057',
    'menu_active': '#0d6efd',
    
    # Cores de borda
    'border_primary': '#dee2e6',
    'border_secondary': '#ced4da',
    
    # Cores especiais
    'success': '#198754',
    'warning': '#ffc107',
    'error': '#dc3545',
    'info': '#0dcaf0'
}

def apply_light_theme_to_widget(widget, widget_type="default"):
    """Aplica tema claro a um widget específico"""
    theme = LIGHT_THEME
    
    try:
        if widget_type == "frame":
            widget.configure(bg=theme['bg_primary'])
        
        elif widget_type == "label":
            widget.configure(
                bg=theme['bg_primary'],
                fg=theme['text_primary']
            )
        
        elif widget_type == "label_secondary":
            widget.configure(
                bg=theme['bg_primary'],
                fg=theme['text_secondary']
            )
        
        elif widget_type == "entry":
            widget.configure(
                bg='white',
                fg=theme['text_primary'],
                insertbackground=theme['text_primary'],
                relief='solid',
                bd=1,
                highlightbackground=theme['border_primary'],
                highlightcolor=theme['accent_blue'],
                highlightthickness=1
            )
        
        elif widget_type == "button_primary":
            widget.configure(
                bg=theme['accent_blue'],
                fg='white',
                relief='flat',
                bd=0,
                activebackground='#0b5ed7',
                activeforeground='white'
            )
        
        elif widget_type == "button_success":
            widget.configure(
                bg=theme['success'],
                fg='white',
                relief='flat',
                bd=0,
                activebackground='#157347',
                activeforeground='white'
            )
        
        elif widget_type == "button_danger":
            widget.configure(
                bg=theme['error'],
                fg='white',
                relief='flat',
                bd=0,
                activebackground='#bb2d3b',
                activeforeground='white'
            )
        
        elif widget_type == "button_secondary":
            widget.configure(
                bg=theme['bg_tertiary'],
                fg=theme['text_primary'],
                relief='flat',
                bd=0,
                activebackground=theme['bg_hover'],
                activeforeground=theme['text_primary']
            )
        
        elif widget_type == "menu_button":
            widget.configure(
                bg=theme['menu_bg'],
                fg='white',
                relief='flat',
                bd=0,
                activebackground=theme['menu_hover'],
                activeforeground='white'
            )
        
        elif widget_type == "menu_button_active":
            widget.configure(
                bg=theme['menu_active'],
                fg='white',
                relief='flat',
                bd=0
            )
        
        elif widget_type == "labelframe":
            widget.configure(
                bg=theme['bg_primary'],
                fg=theme['text_primary'],
                bd=1,
                relief='solid'
            )
        
    except Exception as e:
        print(f"Erro ao aplicar tema: {e}")

def get_rounded_button_style():
    """Retorna estilo para botões arredondados"""
    return {
        'relief': 'flat',
        'bd': 0,
        'padx': 20,
        'pady': 10,
        'font': ('Segoe UI', 10, 'bold'),
        'cursor': 'hand2'
    }

def get_modern_entry_style():
    """Retorna estilo para campos de entrada modernos"""
    return {
        'relief': 'solid',
        'bd': 1,
        'highlightthickness': 2,
        'font': ('Segoe UI', 10),
        'padx': 10,
        'pady': 8
    }
