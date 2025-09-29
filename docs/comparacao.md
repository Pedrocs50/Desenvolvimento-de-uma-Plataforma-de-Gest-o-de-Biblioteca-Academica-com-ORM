### Comparação: Query com API do ORM vs. Query com SQL Nativo

Para gerar o relatório de obras mais emprestadas, foram utilizadas duas abordagens distintas, permitindo uma comparação direta entre a API do SQLAlchemy (ORM) e uma query SQL nativa.

#### **Código Lado a Lado**

| Query com ORM (SQLAlchemy) | Query Nativa (SQL Puro) |
| :--- | :--- |
| ```python from sqlalchemy import func resultado = db.session.query( models.Obra.titulo, func.count(models.Emprestimo.id) ).\ select_from(models.Obra).\ join(models.Exemplar).\ join(models.Emprestimo).\ group_by(models.Obra.id).\ order_by(func.count(models.Emprestimo.id).desc()).\ all() ``` | ```sql SELECT o.titulo, COUNT(e.id) AS total_emprestimos FROM obra AS o JOIN exemplar AS ex ON o.id = ex.id_obra JOIN emprestimo AS e ON ex.id = e.id_exemplar GROUP BY o.id ORDER BY total_emprestimos DESC; ``` |

#### **Análise das Diferenças**

* **Nível de Abstração:** A principal diferença é o nível de abstração. Com o ORM, o desenvolvedor interage com **objetos Python** (`models.Obra`, `models.Emprestimo`), enquanto no SQL nativo, a interação é diretamente com **tabelas e colunas** do banco de dados (`obra`, `emprestimo`). O ORM esconde a complexidade das junções (`JOIN`) explícitas.

* **Sintaxe e Integração:** A query do ORM é escrita em Python, utilizando métodos encadeados (`.join()`, `.group_by()`). Isso permite uma integração fluida com o resto da aplicação, facilitando a construção de queries dinâmicas. O SQL, por sua vez, é uma linguagem separada que é embutida no código Python como uma string.

* **Segurança:** O ORM oferece uma camada de proteção nativa contra ataques de **SQL Injection**, pois ele parametriza e escapa os dados automaticamente. Ao usar SQL puro, o desenvolvedor assume a responsabilidade total pela segurança da consulta.

* **Portabilidade de Banco de Dados:** A query do ORM é, em grande parte, agnóstica ao banco de dados subjacente. O mesmo código Python poderia rodar em SQLite, PostgreSQL ou MySQL com mínimas alterações. A query SQL nativa pode precisar de ajustes de sintaxe dependendo do dialeto específico do banco de dados utilizado.

* **Produtividade vs. Controle:** Para a grande maioria das operações CRUD e consultas, o ORM aumenta significativamente a produtividade do desenvolvedor. Em cenários de otimização extrema ou queries muito complexas, o SQL nativo pode oferecer um controle mais granular e direto sobre o que o banco de dados executa.