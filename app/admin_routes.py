from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from . import db, models
from flask_login import login_required, current_user
from .routes import main
from sqlalchemy import func, or_
from datetime import datetime, timedelta, UTC
from itertools import chain

# --- ROTAS DO PAINEL DE ADMIN ---

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.tipo != 'admin': abort(403)
    
    stats = {
        'total_obras': db.session.query(models.Obra).count(),
        'total_alunos': db.session.query(models.Usuario).filter_by(tipo='aluno').count(),
        'emprestimos_ativos': models.Emprestimo.query.filter(models.Emprestimo.data_real_devolucao.is_(None)).count(),
        'emprestimos_atrasados': models.Emprestimo.query.filter(
            models.Emprestimo.data_real_devolucao.is_(None),
            models.Emprestimo.data_prevista_devolucao < datetime.utcnow()
        ).count()
    }
    top_obras = db.session.query(
        models.Obra.titulo, func.count(models.Emprestimo.id).label('total')
    ).select_from(models.Obra).join(models.Exemplar).join(models.Emprestimo).group_by(models.Obra.id).order_by(func.count(models.Emprestimo.id).desc()).limit(5).all()
    top_usuarios = db.session.query(
        models.Usuario.nome, func.count(models.Emprestimo.id).label('total')
    ).select_from(models.Usuario).join(models.Emprestimo).group_by(models.Usuario.id).order_by(func.count(models.Emprestimo.id).desc()).limit(5).all()
    ultimos_emprestimos = models.Emprestimo.query.order_by(models.Emprestimo.data_emprestimo.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           stats=stats, 
                           top_obras=top_obras, 
                           top_usuarios=top_usuarios,
                           ultimos_emprestimos=ultimos_emprestimos)

@main.route('/admin/usuarios')
@login_required
def listar_usuarios():
    if current_user.tipo != 'admin': abort(403)
    usuarios = models.Usuario.query.order_by(models.Usuario.nome).all()
    return render_template('usuarios.html', usuarios=usuarios)

@main.route('/admin/obras')
@login_required
def listar_obras_admin():
    if current_user.tipo != 'admin':
        abort(403)

    livros = models.Livro.query.all()
    teses = models.Tese.query.all()
    # se tiver dissertação como classe separada
    dissertacoes = models.Dissertacao.query.all()  

    obras = list(chain(livros, teses, dissertacoes))
    obras.sort(key=lambda o: o.titulo.lower() if o.titulo else '')

    return render_template('obras.html', obras=obras)

@main.route('/admin/autores', methods=['GET'])
@login_required
def listar_autores():
    if current_user.tipo != 'admin':
        abort(403)

    # Pega o parâmetro de filtro da URL
    nacionalidade_filtro = request.args.get('nacionalidade')
    
    # Busca todas as nacionalidades distintas para popular o dropdown do filtro
    nacionalidades = db.session.query(models.Autor.nacionalidade).distinct().order_by(models.Autor.nacionalidade).all()

    query = models.Autor.query
    if nacionalidade_filtro:
        query = query.filter_by(nacionalidade=nacionalidade_filtro)
    
    autores = query.order_by(models.Autor.nome).all()
    
    return render_template('autores.html', 
                           autores=autores, 
                           nacionalidades=nacionalidades, 
                           filtro_ativo=nacionalidade_filtro)

@main.route('/admin/autores/add', methods=['GET', 'POST'])
@login_required
def add_autor():
    if current_user.tipo != 'admin':
        abort(403)
    if request.method == 'POST':
        nome = request.form.get('nome')
        nacionalidade = request.form.get('nacionalidade')
        
        if models.Autor.query.filter_by(nome=nome).first():
            flash('Este autor já está cadastrado.', 'danger')
        else:
            novo_autor = models.Autor(nome=nome, nacionalidade=nacionalidade)
            db.session.add(novo_autor)
            db.session.commit()
            flash('Autor adicionado com sucesso!', 'success')
            return redirect(url_for('main.listar_autores'))

    return render_template('add_autor.html')

@main.route('/autor/<int:id>/delete', methods=['POST'])
@login_required
def delete_autor(id):
    if current_user.tipo != 'admin':
        abort(403)
    
    autor = db.get_or_404(models.Autor, id)
    
    # REGRA DE NEGÓCIO: Não permite remover autor com obras associadas.
    if autor.obras:
        flash(f'Erro: Não é possível remover o autor "{autor.nome}" pois ele possui obras cadastradas.', 'danger')
    else:
        db.session.delete(autor)
        db.session.commit()
        flash(f'Autor "{autor.nome}" removido com sucesso.', 'success')
        
    return redirect(url_for('main.listar_autores'))

@main.route('/admin/emprestimos')
@login_required
def listar_emprestimos_admin():
    if current_user.tipo != 'admin': abort(403)
    emprestimos = models.Emprestimo.query.order_by(models.Emprestimo.data_emprestimo.desc()).all()
    return render_template('emprestimos.html', emprestimos=emprestimos, now=datetime.utcnow())

@main.route('/obra/<int:id_obra>/detalhes')
@login_required
def detalhes_obra(id_obra):
    if current_user.tipo != 'admin': abort(403)
    obra = db.get_or_404(models.Obra, id_obra)
    return render_template('detalhes_obra.html', obra=obra)

@main.route('/usuario/<int:id>/delete', methods=['POST'])
@login_required
def delete_usuario(id):
    if current_user.tipo != 'admin': abort(403)
    usuario = db.get_or_404(models.Usuario, id)
    if usuario.emprestimos:
        flash('Não é possível remover um usuário com histórico de empréstimos.', 'danger')
    else:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuário removido com sucesso!', 'success')
    return redirect(url_for('main.listar_usuarios'))

@main.route('/obras/add', methods=['GET', 'POST'])
@login_required
def add_obra():
    if current_user.tipo != 'admin': abort(403)
    if request.method == 'POST':
        autor, nova_obra = None, None
        id_autor = request.form.get('autor_id', type=int)
        novo_autor_nome = request.form.get('novo_autor_nome', '').strip()
        if novo_autor_nome:
            autor = models.Autor(nome=novo_autor_nome)
            db.session.add(autor)
        elif id_autor:
            autor = db.get_or_404(models.Autor, id_autor)
        else:
            flash('É necessário selecionar um autor existente ou adicionar um novo.', 'danger')
            return render_template('add_obra.html', autores=models.Autor.query.order_by(models.Autor.nome).all())

        tipo_obra = request.form.get('tipo_obra')
        dados_comuns = {'titulo': request.form.get('titulo'), 'ano_publicacao': request.form.get('ano_publicacao', type=int)}
        if tipo_obra == 'livro':
            nova_obra = models.Livro(**dados_comuns, isbn=request.form.get('isbn'), editora=request.form.get('editora'), tipo_obra='livro')
        elif tipo_obra in ['tese', 'dissertacao']:
            nova_obra = models.Tese(**dados_comuns, programa_pos=request.form.get('programa_pos'), orientador=request.form.get('orientador'), tipo_obra=tipo_obra)
        
        if nova_obra and autor:
            nova_obra.autores.append(autor)
            db.session.add(nova_obra)
            db.session.commit()
            quantidade = request.form.get('quantidade_exemplares', type=int, default=1)
            for i in range(quantidade):
                codigo = f"{nova_obra.titulo[:3].upper()}{nova_obra.id}-{i+1}"
                novo_exemplar = models.Exemplar(codigo_exemplar=codigo, status='disponivel', obra=nova_obra)
                db.session.add(novo_exemplar)
            db.session.commit()
            flash(f'Obra "{nova_obra.titulo}" e seus {quantidade} exemplares foram adicionados com sucesso!', 'success')
            return redirect(url_for('main.listar_obras_admin'))
    
    return render_template('add_obra.html', autores=models.Autor.query.order_by(models.Autor.nome).all())

@main.route('/admin/emprestimo/novo', methods=['GET', 'POST'])
@login_required
def add_emprestimo():
    if current_user.tipo != 'admin': abort(403)
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario', type=int)
        id_exemplar = request.form.get('id_exemplar', type=int)
        data_emprestimo = datetime.strptime(request.form.get('data_emprestimo'), '%Y-%m-%d')
        data_prevista_devolucao = datetime.strptime(request.form.get('data_prevista_devolucao'), '%Y-%m-%d')
        usuario = db.get_or_404(models.Usuario, id_usuario)
        exemplar = db.get_or_404(models.Exemplar, id_exemplar)
        if exemplar.status != 'disponivel':
            flash(f"Erro: O exemplar '{exemplar.obra.titulo}' não está mais disponível.", 'danger')
            return redirect(url_for('main.add_emprestimo'))
        exemplar.status = 'emprestado'
        novo_emprestimo = models.Emprestimo(usuario=usuario, exemplar=exemplar, data_emprestimo=data_emprestimo, data_prevista_devolucao=data_prevista_devolucao)
        db.session.add(novo_emprestimo)
        db.session.commit()
        flash(f"Empréstimo realizado com sucesso para {usuario.nome}!", 'success')
        return redirect(url_for('main.listar_emprestimos_admin'))

    usuarios = models.Usuario.query.filter_by(tipo='aluno').order_by(models.Usuario.nome).all()
    exemplares_disponiveis = models.Exemplar.query.filter_by(status='disponivel').join(models.Obra).order_by(models.Obra.titulo).all()
    hoje = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('add_emprestimo.html', usuarios=usuarios, exemplares=exemplares_disponiveis, hoje=hoje)

@main.route('/emprestimo/<int:id>/devolver', methods=['POST'])
@login_required
def devolver_emprestimo(id):
    emprestimo = db.get_or_404(models.Emprestimo, id)
    if emprestimo.id_usuario != current_user.id and current_user.tipo != 'admin': abort(403)
    if emprestimo.data_real_devolucao is None:
        emprestimo.data_real_devolucao = datetime.now(UTC)
        emprestimo.exemplar.status = 'disponivel'
        db.session.commit()
        flash(f"Livro '{emprestimo.exemplar.obra.titulo}' devolvido com sucesso!", 'success')
    else:
        flash('Este livro já foi devolvido.', 'info')
    return redirect(request.referrer or url_for('main.home'))

@main.route('/exemplar/<int:id_exemplar>/toggle_status', methods=['POST'])
@login_required
def toggle_status_exemplar(id_exemplar):
    if current_user.tipo != 'admin': abort(403)
    exemplar = db.get_or_404(models.Exemplar, id_exemplar)
    id_obra_pai = exemplar.obra.id
    if exemplar.status == 'emprestado':
        flash(f'Ação negada: O exemplar {exemplar.codigo_exemplar} está atualmente emprestado.', 'danger')
    elif exemplar.status == 'disponivel':
        exemplar.status = 'desativado'
        flash(f'Exemplar {exemplar.codigo_exemplar} foi desativado.', 'success')
    elif exemplar.status == 'desativado':
        exemplar.status = 'disponivel'
        flash(f'Exemplar {exemplar.codigo_exemplar} foi reativado.', 'success')
    db.session.commit()
    return redirect(url_for('main.detalhes_obra', id_obra=id_obra_pai))

@main.route('/api/obras/search')
@login_required
def search_obras_api():
    termo = request.args.get('termo', '')
    tipo = request.args.get('tipo', '')

    query = models.Obra.query

    if termo:
        try:
            ano = int(termo)
            query = query.filter(models.Obra.ano_publicacao == ano)
        except ValueError:
            query = query.filter(or_(
                models.Obra.titulo.ilike(f'%{termo}%'),
                models.Obra.genero.ilike(f'%{termo}%')
            ))

    if tipo:
        query = query.filter(models.Obra.tipo_obra == tipo)

    obras = query.order_by(models.Obra.titulo).all()

    # Cria um dict para cada obra, incluindo o ID de um exemplar disponível
    def obra_to_dict(obra):
        exemplar_disponivel = next((ex for ex in obra.exemplares if ex.status == 'disponivel'), None)
        return {
            'id': obra.id,
            'titulo': obra.titulo,
            'genero': obra.genero,
            'ano_publicacao': obra.ano_publicacao,
            'tipo_obra': obra.tipo_obra,
            'tem_exemplares_disponiveis': exemplar_disponivel is not None,
            'id_exemplar': exemplar_disponivel.id if exemplar_disponivel else None
        }

    return jsonify([obra_to_dict(obra) for obra in obras])

@main.route('/admin/reservas')
@login_required
def listar_reservas():
    if current_user.tipo != 'admin': abort(403)
    reservas = models.Reserva.query.filter_by(status='pendente').order_by(models.Reserva.data_reserva.desc()).all()
    return render_template('reservas_admin.html', reservas=reservas)

@main.route('/admin/reserva/<int:id>/aprovar', methods=['POST'])
@login_required
def aprovar_reserva(id):
    if current_user.tipo != 'admin': abort(403)
    reserva = db.get_or_404(models.Reserva, id)
    # Pega um exemplar disponível da obra
    exemplar_disponivel = models.Exemplar.query.filter_by(obra_id=reserva.id_obra, status='disponivel').first()
    if not exemplar_disponivel:
        flash('Não há exemplares disponíveis para esta obra.', 'danger')
        return redirect(url_for('main.listar_reservas'))

    # Marca o exemplar como emprestado
    exemplar_disponivel.status = 'emprestado'

    # Cria o empréstimo
    novo_emprestimo = models.Emprestimo(
        usuario=reserva.usuario,
        exemplar=exemplar_disponivel,
        data_emprestimo=datetime.utcnow(),
        data_prevista_devolucao=datetime.utcnow() + timedelta(days=7)  # ou outro prazo
    )
    reserva.status = 'aprovada'
    db.session.add(novo_emprestimo)
    db.session.commit()
    flash(f'Reserva aprovada e empréstimo criado para "{reserva.obra.titulo}".', 'success')
    return redirect(url_for('main.listar_reservas'))

@main.route('/admin/reserva/<int:id>/rejeitar', methods=['POST'])
@login_required
def rejeitar_reserva(id):
    if current_user.tipo != 'admin': abort(403)
    reserva = db.get_or_404(models.Reserva, id)
    reserva.status = 'rejeitada'
    db.session.commit()
    flash(f'Reserva para "{reserva.obra.titulo}" foi rejeitada.', 'info')
    return redirect(url_for('main.listar_reservas'))
