# app/routes.py

from flask import render_template, request, Blueprint, redirect, url_for, flash
from datetime import datetime, timedelta, UTC
from sqlalchemy import or_, text, func
from . import db
from . import models

main = Blueprint('main', __name__)

# --- ROTAS DE VISUALIZAÇÃO (PÁGINAS HTML) ---

@main.route('/')
def home():
    """Renderiza a página inicial."""
    return render_template('index.html')

@main.route('/obras')
def listar_obras():
    """Busca e exibe todas as obras cadastradas."""
    obras = models.Obra.query.order_by(models.Obra.titulo).all()
    return render_template('obras.html', obras=obras)

@main.route('/usuarios')
def listar_usuarios():
    """Busca e exibe todos os usuários."""
    usuarios = models.Usuario.query.order_by(models.Usuario.nome).all()
    return render_template('usuarios.html', usuarios=usuarios)

@main.route('/emprestimos')
def listar_emprestimos():
    emprestimos = models.Emprestimo.query.order_by(models.Emprestimo.data_emprestimo.desc()).all()
    # Usamos utcnow() para criar uma data "naive" (sem fuso)
    return render_template('emprestimos.html', emprestimos=emprestimos, now=datetime.utcnow())

# --- ROTAS DE AÇÕES E FORMULÁRIOS (CRUD) ---

@main.route('/usuarios/add', methods=['GET', 'POST'])
def add_usuario():
    """Exibe o formulário para adicionar um usuário (GET) e processa os dados (POST)."""
    if request.method == 'POST':
        novo_usuario = models.Usuario(
            nome=request.form.get('nome'),
            email=request.form.get('email'),
            tipo=request.form.get('tipo'),
            status='ativo'
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário adicionado com sucesso!', 'success')
        return redirect(url_for('main.listar_usuarios'))
    return render_template('add_usuario.html')

@main.route('/usuario/<int:id>/delete', methods=['POST'])
def delete_usuario(id):
    """Remove um usuário do banco de dados."""
    usuario_para_deletar = db.get_or_404(models.Usuario, id)
    
    if usuario_para_deletar.emprestimos:
        flash('Não é possível remover um usuário com histórico de empréstimos.', 'danger')
        return redirect(url_for('main.listar_usuarios'))

    db.session.delete(usuario_para_deletar)
    db.session.commit()
    flash('Usuário removido com sucesso!', 'success')
    return redirect(url_for('main.listar_usuarios'))

@main.route('/obras/add', methods=['GET', 'POST'])
def add_obra():
    """Exibe o formulário para adicionar uma obra (GET) e processa os dados (POST)."""
    if request.method == 'POST':
        novo_livro = models.Livro(
            titulo=request.form.get('titulo'),
            ano_publicacao=request.form.get('ano_publicacao', type=int),
            isbn=request.form.get('isbn'),
            editora=request.form.get('editora'),
            tipo_obra='livro'
        )
        id_autor = request.form.get('autor', type=int)
        autor = db.get_or_404(models.Autor, id_autor)
        if autor:
            novo_livro.autores.append(autor)
        db.session.add(novo_livro)
        db.session.commit()
        flash('Obra adicionada com sucesso!', 'success')
        return redirect(url_for('main.listar_obras'))
    autores = models.Autor.query.order_by(models.Autor.nome).all()
    return render_template('add_obra.html', autores=autores)

@main.route('/emprestimo/<int:id>/devolver', methods=['POST'])
def devolver_emprestimo(id):
    """Marca um empréstimo como devolvido."""
    emprestimo = db.get_or_404(models.Emprestimo, id)
    
    if emprestimo.data_real_devolucao is None:
        emprestimo.data_real_devolucao = datetime.now(UTC)
        emprestimo.exemplar.status = 'disponivel'
        db.session.commit()
        flash(f"Livro '{emprestimo.exemplar.obra.titulo}' devolvido com sucesso!", 'success')
    else:
        flash('Este livro já foi devolvido.', 'info')

    return redirect(url_for('main.listar_emprestimos'))

# --- ROTA PARA POPULAR O BANCO DE DADOS ---

@main.route('/criar_dados')
def criar_dados():
    db.drop_all()
    db.create_all()
    autor1 = models.Autor(nome='J.R.R. Tolkien', nacionalidade='Sul-africano')
    autor2 = models.Autor(nome='George Orwell', nacionalidade='Britânico')
    livro1 = models.Livro(titulo='O Hobbit', ano_publicacao=1937, isbn='978-0345339683', editora='Allen & Unwin')
    livro1.autores.append(autor1)
    tese1 = models.Tese(titulo='A Semântica dos Modelos de IA Generativa', ano_publicacao=2024, programa_pos='Ciência da Computação', orientador='Dr. Alan Turing')
    tese1.autores.append(autor1)
    usuario1 = models.Usuario(nome='Alice', email='alice@example.com', tipo='aluno', status='ativo')
    usuario2 = models.Usuario(nome='Bob', email='bob@example.com', tipo='professor', status='ativo')
    exemplar1_hobbit = models.Exemplar(codigo_exemplar='HB01', status='disponivel', obra=livro1)
    exemplar2_hobbit = models.Exemplar(codigo_exemplar='HB02', status='disponivel', obra=livro1)
    exemplar1_tese = models.Exemplar(codigo_exemplar='TS01', status='disponivel', obra=tese1)
    emprestimo_atrasado = models.Emprestimo(data_emprestimo=datetime.now(UTC) - timedelta(days=20), data_prevista_devolucao=datetime.now(UTC) - timedelta(days=5), usuario=usuario2, exemplar=exemplar1_hobbit)
    emprestimo_normal = models.Emprestimo(data_emprestimo=datetime.now(UTC), data_prevista_devolucao=datetime.now(UTC) + timedelta(days=14), usuario=usuario1, exemplar=exemplar1_tese)
    reserva_antiga = models.Reserva(data_reserva=datetime.now(UTC) - timedelta(days=3), status='ativa', usuario=usuario1, obra=livro1)
    reserva_recente = models.Reserva(data_reserva=datetime.now(UTC), status='ativa', usuario=usuario2, obra=tese1)
    db.session.add_all([
        autor1, autor2, livro1, tese1, usuario1, usuario2, exemplar1_hobbit, exemplar2_hobbit,
        exemplar1_tese, emprestimo_atrasado, emprestimo_normal, reserva_antiga, reserva_recente
    ])
    db.session.commit()
    return "<h1>Dados de teste finais foram criados com sucesso!</h1><p><a href='/'>Voltar para o Início</a></p>"