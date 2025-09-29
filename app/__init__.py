# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Crie a instância do DB fora da função
db = SQLAlchemy()

def create_app():
    # Cria a instância da aplicação Flask
    app = Flask(__name__,
                instance_relative_config=True,
                static_folder='static',
                template_folder='templates')

    # Configuração do Banco de Dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Chave secreta para habilitar mensagens 'flash'
    app.config['SECRET_KEY'] = 'uma-chave-secreta-para-o-projeto-do-ifsp-jacarei'

    # Conecta a instância do DB com a aplicação
    db.init_app(app)

    with app.app_context():
        # Importe seus modelos para garantir que o SQLAlchemy os reconheça
        from . import models

        # Importa e registra o blueprint que contém todas as nossas rotas.
        # Esta é a linha que "conecta" tudo.
        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app