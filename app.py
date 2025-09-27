from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Opcional: desativa warnings

db = SQLAlchemy(app)

# --- Rotas da Aplicação ---
@app.route('/')
def index():
    return "<h1>Aplicação Biblioteca ORM</h1><p>Configuração inicial funcionando!</p>"

# Garante que a aplicação só rode quando este arquivo for executado diretamente
if __name__ == '__main__':
    app.run(debug=True)