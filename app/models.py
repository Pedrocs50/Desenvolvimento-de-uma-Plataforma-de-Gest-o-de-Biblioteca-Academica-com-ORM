# app/models.py

from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

obra_autor_association = db.Table('obra_autor',
    db.Column('id_obra', db.Integer, db.ForeignKey('obra.id'), primary_key=True),
    db.Column('id_autor', db.Integer, db.ForeignKey('autor.id'), primary_key=True)
)

class Usuario(db.Model, UserMixin): # <-- MUDANÇA 1: Herda de UserMixin
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    
    # MUDANÇA 2: Novo campo para a senha criptografada
    senha_hash = db.Column(db.String(256))

    tipo = db.Column(db.String(20), nullable=False) # 'aluno' ou 'admin'
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    
    emprestimos = db.relationship('Emprestimo', back_populates='usuario')
    reservas = db.relationship('Reserva', back_populates='usuario')

    # MUDANÇA 3: Novos métodos para gerenciar a senha
    def set_senha(self, senha):
        """Cria um hash seguro da senha e o armazena."""
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Obra(db.Model):
    __tablename__ = 'obra'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    ano_publicacao = db.Column(db.Integer)
    
    tipo_obra = db.Column(db.String(50), nullable=False)

    autores = db.relationship('Autor', secondary=obra_autor_association, back_populates='obras')
    exemplares = db.relationship('Exemplar', back_populates='obra')
    reservas = db.relationship('Reserva', back_populates='obra')

    __mapper_args__ = {
        'polymorphic_identity': 'obra',  
        'polymorphic_on': tipo_obra      
    }

    def __repr__(self):
        return f'<Obra {self.titulo}>'

class Livro(Obra):
    __tablename__ = 'livro'
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'), primary_key=True)
    isbn = db.Column(db.String(20))
    editora = db.Column(db.String(100))

    __mapper_args__ = {
        'polymorphic_identity': 'livro',
    }
    def __repr__(self):
        return f'<Livro {self.titulo}>'

class Tese(Obra):
    __tablename__ = 'tese'
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'), primary_key=True)
    programa_pos = db.Column(db.String(150))
    orientador = db.Column(db.String(150))

    __mapper_args__ = {
        'polymorphic_identity': 'tese',
    }
    def __repr__(self):
        return f'<Tese {self.titulo}>'

class Dissertacao(Obra):
    __tablename__ = 'dissertacao'
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'), primary_key=True)
    programa_pos = db.Column(db.String(150))
    orientador = db.Column(db.String(150))

    __mapper_args__ = {
        'polymorphic_identity': 'dissertacao',
    }
    def __repr__(self):
        return f'<Dissertacao {self.titulo}>'


class Autor(db.Model):
    __tablename__ = 'autor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    nacionalidade = db.Column(db.String(50))
    obras = db.relationship('Obra', secondary=obra_autor_association, back_populates='autores')
    def __repr__(self):
        return f'<Autor {self.nome}>'

class Exemplar(db.Model):
    __tablename__ = 'exemplar'
    id = db.Column(db.Integer, primary_key=True)
    codigo_exemplar = db.Column(db.String(20), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False)
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'), nullable=False)
    obra = db.relationship('Obra', back_populates='exemplares')
    emprestimos = db.relationship('Emprestimo', back_populates='exemplar')
    def __repr__(self):
        return f'<Exemplar Cód: {self.codigo_exemplar}>'

class Emprestimo(db.Model):
    __tablename__ = 'emprestimo'
    id = db.Column(db.Integer, primary_key=True)
    data_emprestimo = db.Column(db.DateTime, nullable=False)
    data_prevista_devolucao = db.Column(db.DateTime, nullable=False)
    data_real_devolucao = db.Column(db.DateTime)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_exemplar = db.Column(db.Integer, db.ForeignKey('exemplar.id'), nullable=False)
    usuario = db.relationship('Usuario', back_populates='emprestimos')
    exemplar = db.relationship('Exemplar', back_populates='emprestimos')
    def __repr__(self):
        return f'<Emprestimo ID: {self.id}>'

class Reserva(db.Model):
    __tablename__ = 'reserva'
    id = db.Column(db.Integer, primary_key=True)
    data_reserva = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_obra = db.Column(db.Integer, db.ForeignKey('obra.id'), nullable=False)
    usuario = db.relationship('Usuario', back_populates='reservas')
    obra = db.relationship('Obra', back_populates='reservas')
    def __repr__(self):
        return f'<Reserva ID: {self.id}>'