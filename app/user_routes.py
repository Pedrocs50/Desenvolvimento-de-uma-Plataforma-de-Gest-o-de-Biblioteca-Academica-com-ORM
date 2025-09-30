# app/user_routes.py
from flask import render_template, redirect, url_for
from . import models
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