from flask import render_template, request, redirect, url_for, flash
from . import db, models
from flask_login import login_user, logout_user, login_required, current_user
from .routes import main

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        usuario = models.Usuario.query.filter_by(email=request.form.get('email')).first()
        if usuario and usuario.check_senha(request.form.get('senha')):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        if models.Usuario.query.filter_by(email=request.form.get('email')).first():
            flash('Este email já está cadastrado.', 'warning')
            return redirect(url_for('main.cadastro'))
        novo_usuario = models.Usuario(nome=request.form.get('nome'), email=request.form.get('email'), tipo='aluno')
        novo_usuario.set_senha(request.form.get('senha'))
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('cadastro.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('main.login'))