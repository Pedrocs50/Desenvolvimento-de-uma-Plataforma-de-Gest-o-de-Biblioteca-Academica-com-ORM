from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma-chave-secreta-para-o-projeto-do-ifsp'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from . import models
    from .routes import main as main_blueprint
    from . import auth_routes, user_routes, admin_routes

    app.register_blueprint(main_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.Usuario, int(user_id))

    return app
