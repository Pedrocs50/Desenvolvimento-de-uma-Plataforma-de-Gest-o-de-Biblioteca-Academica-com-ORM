# app/__init__.py (versão final do Requisito 3)

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Adicionamos 'text' e 'func' para as queries avançadas
from sqlalchemy import or_, text, func

# Crie a instância do DB fora da função, sem ligar a nenhuma app
db = SQLAlchemy()

def create_app():
    # Cria a instância da aplicação Flask
    app = Flask(__name__, instance_relative_config=True)

    # Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Conecta a instância do DB com a aplicação
    db.init_app(app)

    # Dentro da fábrica, nós definimos as rotas
    with app.app_context():
        # Importe seus modelos AQUI
        from . import models

        # --- ROTA RAIZ (HOME) ---
        @app.route('/')
        def home():
            return "<h1>Bem-vindo à Biblioteca!</h1><p>Acesse /criar_dados para popular o banco, ou /buscar para pesquisar.</p>"

        @app.route('/criar_dados')
        def criar_dados():
            # ... (código da função criar_dados, sem alterações) ...
            db.drop_all()
            db.create_all()
            autor1 = models.Autor(nome='J.R.R. Tolkien', nacionalidade='Sul-africano')
            autor2 = models.Autor(nome='George Orwell', nacionalidade='Britânico')
            livro1 = models.Livro(titulo='O Hobbit', ano_publicacao=1937, isbn='978-0345339683', editora='Allen & Unwin')
            livro1.autores.append(autor1)
            tese1 = models.Tese(titulo='A Semântica dos Modelos de IA Generativa', ano_publicacao=2024, programa_pos='Ciência da Computação', orientador='Dr. Alan Turing')
            tese1.autores.append(autor1)
            usuario1 = models.Usuario(nome='Alice', email='alice@example.com', tipo='aluno')
            usuario2 = models.Usuario(nome='Bob', email='bob@example.com', tipo='professor')
            exemplar1_hobbit = models.Exemplar(codigo_exemplar='HB01', status='disponivel', obra=livro1)
            exemplar2_hobbit = models.Exemplar(codigo_exemplar='HB02', status='disponivel', obra=livro1)
            exemplar1_tese = models.Exemplar(codigo_exemplar='TS01', status='disponivel', obra=tese1)
            emprestimo1 = models.Emprestimo(data_emprestimo=datetime(2025, 8, 1), data_prevista_devolucao=datetime(2025, 8, 15), usuario=usuario1, exemplar=exemplar1_hobbit)
            emprestimo2 = models.Emprestimo(data_emprestimo=datetime(2025, 9, 5), data_prevista_devolucao=datetime(2025, 9, 20), usuario=usuario2, exemplar=exemplar1_tese)
            emprestimo3 = models.Emprestimo(data_emprestimo=datetime(2025, 9, 15), data_prevista_devolucao=datetime(2025, 9, 30), usuario=usuario1, exemplar=exemplar2_hobbit)
            db.session.add_all([
                autor1, autor2, livro1, tese1, usuario1, usuario2,
                exemplar1_hobbit, exemplar2_hobbit, exemplar1_tese,
                emprestimo1, emprestimo2, emprestimo3
            ])
            db.session.commit()
            return "<h1>Dados de teste (incluindo empréstimos) foram criados com sucesso!</h1>"

        # --- ROTA DE BUSCA ---
        @app.route('/buscar')
        def buscar():
            # ... (código da função buscar, sem alterações) ...
            termo_busca = request.args.get('termo')
            tipo_obra = request.args.get('tipo')
            nome_autor = request.args.get('autor')
            query = models.Obra.query
            if termo_busca:
                try:
                    ano = int(termo_busca)
                    query = query.filter(or_(
                        models.Obra.ano_publicacao == ano,
                        models.Obra.titulo.ilike(f'%{termo_busca}%')
                    ))
                except ValueError:
                    query = query.filter(models.Obra.titulo.ilike(f'%{termo_busca}%'))
            if tipo_obra:
                query = query.filter(models.Obra.tipo_obra == tipo_obra.lower())
            if nome_autor:
                query = query.join(models.Obra.autores).filter(models.Autor.nome.ilike(f'%{nome_autor}%'))
            resultados = query.all()
            output = "<h2>Resultados da busca:</h2>"
            if not resultados:
                return output + "<p>Nenhum resultado encontrado.</p>"
            for obra in resultados:
                autores = ', '.join([autor.nome for autor in obra.autores])
                output += f"<p><b>{obra.titulo}</b> ({obra.ano_publicacao}) - Autores: {autores} [Tipo: {obra.tipo_obra}]</p>"
            return output

        # --- ROTA DE RELATÓRIO COM ORM ---
        @app.route('/relatorio/mais_emprestados')
        def relatorio_mais_emprestados():
            # ... (código da função de relatório ORM, sem alterações) ...
            obras_mais_emprestadas = db.session.query(
                models.Obra.titulo,
                func.count(models.Emprestimo.id).label('total_emprestimos')
            ).select_from(models.Obra).join(models.Exemplar).join(models.Emprestimo).group_by(models.Obra.id).order_by(func.count(models.Emprestimo.id).desc()).all()
            output = "<h2>Relatório: Obras Mais Emprestadas</h2>"
            if not obras_mais_emprestadas:
                return output + "<p>Nenhum empréstimo encontrado.</p>"
            output += "<ol>"
            for obra in obras_mais_emprestadas:
                output += f"<li><b>{obra.titulo}</b> - {obra.total_emprestimos} empréstimos</li>"
            output += "</ol>"
            return output

        # --- NOVA ROTA COM SQL NATIVO ADICIONADA ---
        @app.route('/relatorio/mais_emprestados_sql')
        def relatorio_mais_emprestados_sql():
            query_sql = text("""
                SELECT
                    o.titulo,
                    COUNT(e.id) AS total_emprestimos
                FROM obra AS o
                JOIN exemplar AS ex ON o.id = ex.id_obra
                JOIN emprestimo AS e ON ex.id = e.id_exemplar
                GROUP BY o.id
                ORDER BY total_emprestimos DESC;
            """)
            
            resultado = db.session.execute(query_sql)
            
            output = "<h2>Relatório com SQL Puro: Obras Mais Emprestadas</h2>"
            output += "<ol>"
            for linha in resultado:
                output += f"<li><b>{linha.titulo}</b> - {linha.total_emprestimos} empréstimos</li>"
            output += "</ol>"

            return output

    return app