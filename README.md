# Desenvolvimento de uma Plataforma de Gestão de Biblioteca Acadêmica com ORM
O sistema deve permitir o cadastro de livros, dissertações, teses, autores, exemplares físicos, empréstimos, reservas e usuários (alunos, professores e funcionários)

## Modelo Relacional e Justificativas

[Modelo Relacional do Banco de Dados](docs/modelagem.md)

## Esquema do Banco de Dados

O esquema relacional do banco de dados foi projetado para atender aos requisitos do sistema de biblioteca.

![Esquema Relacional do Banco de Dados](docs/esquema_relacional.svg)

Este diagrama foi gerado utilizando DBML. O código-fonte do diagrama está disponível em [`docs/esquema.dbml`](docs/esquema.dbml) e pode ser visualizado na plataforma [dbdiagram.io](https://dbdiagram.io/d/68d842a1d2b621e422342762).

## Comparação entre Query com API do ORM vs. Query com SQL Nativo

[Comparação](docs/comparacao.md)

# Como rodar o projeto Biblioteca Acadêmica

## Pré-requisitos

- Python 3.8 ou superior
- Git

## Passos para rodar

### 1. Clone o repositório

```bash
git clone https://github.com/Pedrocs50/Desenvolvimento-de-uma-Plataforma-de-Gest-o-de-Biblioteca-Academica-com-ORM
cd seu-repo
```

### 2. Crie e ative o ambiente virtual

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o projeto

```bash
python run.py
```

O servidor estará disponível em [http://localhost:5000](http://localhost:5000).

---

## Observações

- O banco de dados será criado automaticamente na primeira execução.
- Um usuário admin padrão será criado:
  - **Email:** admin@ifsp.edu.br
  - **Senha:** admin123

---

## Problemas comuns

- Se aparecer "Erro ao carregar dados", verifique se há obras cadastradas no banco.
- Para adicionar obras de teste, use o Flask shell:

```bash
flask shell
```

```python
from app import db, models
obra = models.Obra(titulo="Livro Teste", ano_publicacao=2023, tipo_obra="livro")
db.session.add(obra)
db.session.commit()
```