# Modelo Relacional e Justificativas

## Tabela: `Usuario`
* **Descrição:** Armazena os dados dos usuários que podem interagir com a biblioteca (alunos, professores, funcionários).
* **Colunas:**
    * `id` (INT, PK, AUTO_INCREMENT)
    * `nome` (VARCHAR(150), NOT NULL)
    * `email` (VARCHAR(150), NOT NULL, UNIQUE)
    * `tipo` (VARCHAR(20), NOT NULL)
    * `status` (VARCHAR(20), NOT NULL, DEFAULT 'Ativo')
* **Justificativa:** É a representação direta da entidade `Usuario`. O `id` como Chave Primária (PK) garante a identificação única. A restrição `UNIQUE` em `email` previne duplicidade de cadastros.

## Tabela: `Autor`
* **Descrição:** Armazena os autores das obras do acervo.
* **Colunas:**
    * `id` (INT, PK, AUTO_INCREMENT)
    * `nome` (VARCHAR(150), NOT NULL)
    * `nacionalidade` (VARCHAR(50))
* **Justificativa:** Conversão direta da entidade `Autor` para uma tabela normalizada.

## Tabela: `Obra`
* **Descrição:** Tabela base que contém os atributos comuns a todos os itens do acervo (livros, teses, etc.), implementando uma estratégia de herança.
* **Colunas:**
    * `id` (INT, PK, AUTO_INCREMENT)
    * `titulo` (VARCHAR(255), NOT NULL)
    * `ano_publicacao` (INT)
    * `tipo_obra` (VARCHAR(20), NOT NULL)
* **Justificativa:** Funciona como a classe-mãe no modelo de herança "Tabela por Hierarquia de Classe". A coluna `tipo_obra` é a "discriminadora", essencial para que o ORM saiba qual subtabela (`Livro`, `Tese`) deve ser associada a um registro de `Obra`.

## Tabela: `Livro`
* **Descrição:** Subtabela que armazena informações específicas de obras do tipo "Livro".
* **Colunas:**
    * `id_obra` (INT, PK, FK)
    * `isbn` (VARCHAR(20))
    * `editora` (VARCHAR(100))
* **Justificativa:** Especialização da tabela `Obra`. A chave `id_obra` é ao mesmo tempo Chave Primária e Chave Estrangeira (referenciando `Obra.id`), garantindo um relacionamento 1-para-1 e a integridade do modelo de herança.

## Tabela: `Tese`
* **Descrição:** Subtabela para informações específicas de obras do tipo "Tese".
* **Colunas:**
    * `id_obra` (INT, PK, FK)
    * `programa_pos` (VARCHAR(150))
    * `orientador` (VARCHAR(150))
* **Justificativa:** Semelhante à tabela `Livro`, especializa `Obra` para teses, mantendo o modelo organizado e normalizado.

## Tabela: `Dissertacao`
* **Descrição:** Subtabela para informações específicas de obras do tipo "Dissertação".
* **Colunas:**
    * `id_obra` (INT, PK, FK)
    * `programa_pos` (VARCHAR(150))
    * `orientador` (VARCHAR(150))
* **Justificativa:** Especialização da tabela `Obra` para dissertações.

## Tabela: `ObraAutor`
* **Descrição:** Tabela associativa para resolver o relacionamento Muitos-para-Muitos (N:N) entre `Obra` e `Autor`.
* **Colunas:**
    * `id_obra` (INT, FK)
    * `id_autor` (INT, FK)
* **Chave Primária Composta:** `(id_obra, id_autor)`
* **Justificativa:** Bancos de dados relacionais não suportam relacionamentos N:N diretamente. Esta tabela "conecta" as obras aos seus autores. A chave primária composta impede que o mesmo autor seja associado à mesma obra mais de uma vez.

## Tabela: `Exemplar`
* **Descrição:** Representa cada cópia física ou digital de uma obra que pode ser emprestada.
* **Colunas:**
    * `id` (INT, PK, AUTO_INCREMENT)
    * `codigo_exemplar` (VARCHAR(20), NOT NULL, UNIQUE)
    * `status` (VARCHAR(20), NOT NULL)
    * `id_obra` (INT, FK, NOT NULL)
* **Justificativa:** Implementa o lado "N" do relacionamento 1:N com `Obra`. A Chave Estrangeira `id_obra` garante que todo exemplar esteja obrigatoriamente ligado a uma obra existente, mantendo a integridade referencial.

## Tabela: `Emprestimo`
* **Descrição:** Registra a operação de empréstimo de um exemplar para um usuário.
* **Colunas:**
    * `id` (INT, PK, AUTO_INCREMENT)
    * `data_emprestimo` (DATETIME, NOT NULL)
    * `data_prevista_devolucao` (DATETIME, NOT NULL)
    * `data_real_devolucao` (DATETIME)
    * `id_usuario` (INT, FK, NOT NULL)
    * `id_exemplar` (INT, FK, NOT NULL)
* **Justificativa:** Tabela transacional que conecta `Usuario` e `Exemplar`. As Chaves Estrangeiras são essenciais para garantir que um empréstimo só possa ser registrado para um usuário e um exemplar que de fato existam.

## Tabela: `Reserva`
* **Descrição:** Registra o interesse de um usuário por uma obra que não está disponível no momento.
* **Colunas:**
    * `id` (INT, PK, AUTO_INCREMENT)
    * `data_reserva` (DATETIME, NOT NULL)
    * `status` (VARCHAR(20), NOT NULL)
    * `id_usuario` (INT, FK, NOT NULL)
    * `id_obra` (INT, FK, NOT NULL)
* **Justificativa:** Tabela transacional que conecta `Usuario` e `Obra`. A reserva é feita na obra (o conceito) e não no exemplar (a cópia física).
