import os
from app import create_app, db, models
from datetime import datetime

app = create_app()

def seed_database():
    """Popula o banco de dados com dados iniciais se ele estiver vazio."""
    
    # Verifica se já existem obras. Se sim, não faz nada.
    if db.session.query(models.Obra).count() > 0:
        print("Banco de dados já populado. Nenhuma ação foi tomada.")
        return

    print("Banco de dados vazio. Populando com dados de teste manuais...")

    # --- Criação de Autores ---
    autor_tolkien = models.Autor(nome='J.R.R. Tolkien', nacionalidade='Sul-africano')
    autor_asimov = models.Autor(nome='Isaac Asimov', nacionalidade='Russo-Americano')
    autor_tardelli = models.Autor(nome='Tardelli Ronan Coelho Stekel', nacionalidade='Brasileiro') # Homenagem ao orientador
    db.session.add_all([autor_tolkien, autor_asimov, autor_tardelli])

    # --- Criação de Obras ---
    livro1 = models.Livro(titulo='O Hobbit', ano_publicacao=1937, genero='Fantasia', tipo_obra='livro')
    livro1.autores.append(autor_tolkien)

    livro2 = models.Livro(titulo='Eu, Robô', ano_publicacao=1950, genero='Ficção Científica', tipo_obra='livro')
    livro2.autores.append(autor_asimov)

    tese1 = models.Tese(
        titulo='Otimização de Consultas em Bancos de Dados Relacionais',
        ano_publicacao=2023,
        genero='Computação',
        tipo_obra='tese',
        programa_pos='Ciência da Computação',
        orientador='Prof. Dr. Lineu Mialaret'
    )
    tese1.autores.append(autor_tardelli)
    
    # Commit para que as Obras tenham IDs antes de criar os Exemplares
    db.session.add_all([livro1, livro2, tese1])
    db.session.commit()

    # --- Criação de Exemplares ---
    exemplares = [
        models.Exemplar(codigo_exemplar='HB01', status='disponivel', obra=livro1),
        models.Exemplar(codigo_exemplar='HB02', status='disponivel', obra=livro1),
        models.Exemplar(codigo_exemplar='ER01', status='disponivel', obra=livro2),
        models.Exemplar(codigo_exemplar='TS01', status='disponivel', obra=tese1)
    ]
    db.session.add_all(exemplares)
    
    db.session.commit()
    print("Dados de teste criados com sucesso!")


with app.app_context():
    # Cria a estrutura de tabelas se não existir
    db.create_all()

    # Cria o usuário admin padrão, somente se ele não existir
    if not models.Usuario.query.filter_by(email='admin@ifsp.edu.br').first():
        print("Criando usuário admin padrão...")
        admin = models.Usuario(nome='Admin', email='admin@ifsp.edu.br', tipo='admin', status='ativo')
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado.")
    
    # Chama a função para popular o banco de dados
    seed_database()
        
if __name__ == "__main__":
    app.run(debug=True)