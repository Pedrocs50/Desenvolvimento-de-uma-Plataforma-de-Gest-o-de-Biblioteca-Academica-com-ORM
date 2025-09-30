# Plataforma de Gestão de Biblioteca Acadêmica - IFSP Jacareí

Este projeto foi desenvolvido para a disciplina de Banco de Dados 2 do curso de Análise e Desenvolvimento de Sistemas. O sistema consiste em uma plataforma web completa para gerenciar uma biblioteca universitária, implementado com Python, Flask e SQLAlchemy.

## Documentação do Projeto
* **[Modelo Relacional e Justificativas](docs/modelagem.md)**: Descrição detalhada de cada tabela, suas colunas e relacionamentos.
* **[Esquema Visual do Banco de Dados](docs/esquema_relacional.svg)**: Diagrama navegável do esquema do banco de dados.
* **[Comparativo ORM vs. SQL](docs/comparacao.md)**: Análise das diferentes abordagens de consulta utilizadas no projeto.

## Tecnologias Utilizadas
* **Backend:** Python, Flask, SQLAlchemy (ORM), Flask-Login, Jinja2(Templating Engine)
* **Frontend:** HTML, Tailwind CSS, JavaScript
* **Banco de Dados:** SQLite
* **Testes:** Pytest

## Como Executar o Projeto

### Pré-requisitos
* Python 3.8+
* Git

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Pedrocs50/Desenvolvimento-de-uma-Plataforma-de-Gest-o-de-Biblioteca-Academica-com-ORM](https://github.com/Pedrocs50/Desenvolvimento-de-uma-Plataforma-de-Gest-o-de-Biblioteca-Academica-com-ORM)
    cd Desenvolvimento-de-uma-Plataforma-de-Gest-o-de-Biblioteca-Academica-com-ORM
    ```

2.  **Crie e ative o ambiente virtual:**
    * **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    * **Linux/Mac:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    python run.py
    ```
    O servidor iniciará e estará acessível em `http://127.0.0.1:5000`.

---
## Como Usar a Aplicação

### Setup Inicial Automatizado
Na primeira vez que você executar o projeto (`python run.py`), o sistema irá automaticamente:
1.  Criar o arquivo de banco de dados (`biblioteca.db`).
2.  Criar um usuário **administrador** padrão.

### Credenciais de Acesso
* **Email do Admin:** `admin@ifsp.edu.br`
* **Senha do Admin:** `admin123`

### Explorando o Sistema
Após iniciar o servidor, siga estes passos para uma experiência completa:

1.  **Faça o Login:** Acesse `http://127.0.0.1:5000` e entre com as credenciais de administrador.
2.  **Cadastre os Primeiros Dados:** O sistema começará vazio. Use os painéis de gerenciamento para popular o banco:
    * Vá para **"Gerenciar Autores"** e adicione alguns autores.
    * Vá para **"Gerenciar Obras"** e use o botão `+ Nova Obra` para cadastrar livros e suas quantidades de exemplares.
    * Use a página de **Cadastro** (acessível após fazer logout) para criar contas de `aluno`.
3.  **Teste as Funcionalidades:** Com os dados cadastrados, explore o Dashboard, realize empréstimos, devolva livros e teste as permissões entre os tipos de usuário.