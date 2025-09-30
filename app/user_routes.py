from flask import render_template, redirect, url_for, request, flash
from . import models, db
from flask_login import login_required, current_user
from .routes import main
from datetime import datetime

@main.route('/')
@login_required
def home():
    if current_user.tipo == 'admin':
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.perfil'))

@main.route('/perfil')
@login_required
def perfil():
    emprestimos = models.Emprestimo.query.filter_by(usuario=current_user, data_real_devolucao=None).order_by(models.Emprestimo.data_prevista_devolucao.asc()).all()
    return render_template('perfil.html', emprestimos=emprestimos, now=datetime.utcnow())

@main.route('/obras')
@login_required
def consultar_obras():
    obras = models.Obra.query.order_by(models.Obra.titulo).all()
    return render_template('obras.html', obras=obras)

@main.route('/reserva/<int:id_exemplar>/solicitar', methods=['POST'])
@login_required
def solicitar_reserva(id_exemplar):
    exemplar = db.get_or_404(models.Exemplar, id_exemplar)
    if exemplar.status != 'disponivel':
        flash('Este exemplar não está disponível para reserva.', 'danger')
        return redirect(request.referrer or url_for('main.consultar_obras'))

    # Verifica se o usuário já tem uma reserva pendente para este exemplar
    reserva_existente = models.Reserva.query.filter_by(
        id_usuario=current_user.id,
        id_obra=exemplar.obra.id,
        status='pendente'
    ).first()
    if reserva_existente:
        flash('Você já possui uma reserva pendente para este exemplar.', 'info')
        return redirect(request.referrer or url_for('main.consultar_obras'))

    nova_reserva = models.Reserva(
        usuario=current_user,
        obra=exemplar.obra,
        data_reserva=datetime.utcnow(),
        status='pendente'
    )
    db.session.add(nova_reserva)
    db.session.commit()
    flash(f'Reserva solicitada para "{exemplar.obra.titulo}". Aguarde aprovação do admin.', 'success')
    return redirect(request.referrer or url_for('main.consultar_obras'))
