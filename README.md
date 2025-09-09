# Sistema de Gestão Escolar

Este projeto é um sistema de gestão escolar desenvolvido em Python. Ele permite o gerenciamento de alunos, turmas e aspectos financeiros de uma instituição de ensino.

## Estrutura do Projeto

O projeto é organizado da seguinte forma:

- **main.py**: Arquivo principal que inicia a aplicação.
- **database/**: Contém a lógica de conexão e modelos do banco de dados.
  - **connection.py**: Estabelece a conexão com o banco de dados SQLite.
  - **models.py**: Define as tabelas do banco de dados.
  - **escola.db**: Arquivo do banco de dados que será criado.
- **interface/**: Contém a interface gráfica da aplicação.
  - **main_window.py**: Define a janela principal da aplicação.
  - **dashboard.py**: Tela do dashboard com resumo das informações.
  - **turmas.py**: Tela para gerenciamento de turmas.
  - **alunos.py**: Tela para gerenciamento de alunos.
  - **financeiro.py**: Tela para gerenciamento financeiro.
- **services/**: Contém a lógica de negócios do sistema.
  - **turma_service.py**: Lógica relacionada às turmas.
  - **aluno_service.py**: Lógica relacionada aos alunos.
  - **financeiro_service.py**: Lógica financeira.
- **utils/**: Contém funções utilitárias.
  - **validators.py**: Funções de validação de dados.
  - **formatters.py**: Funções para formatação de dados.
- **requirements.txt**: Lista de dependências do projeto.

## Instalação

Para instalar as dependências do projeto, execute o seguinte comando:

```
pip install -r requirements.txt
```

## Uso

Para iniciar o sistema, execute o arquivo `main.py`:

```
python main.py
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo LICENSE para mais detalhes.