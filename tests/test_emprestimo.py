import pytest
from app import create_app, db
from app.models import Usuario, Livro, Exemplar, Emprestimo
from datetime import datetime, timedelta, timezone

@pytest.fixture(scope='function')
def test_client():
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client

@pytest.fixture(scope='function')
def init_database():
    db.drop_all()
    db.create_all()

    usuario_ok = Usuario(id=1, nome='Usuario OK', email='ok@email.com', tipo='aluno', status='ativo')
    usuario_bloqueado = Usuario(id=2, nome='Usuario Bloqueado', email='bloqueado@email.com', tipo='aluno', status='bloqueado')
    usuario_com_atraso = Usuario(id=3, nome='Usuario Atrasado', email='atraso@email.com', tipo='aluno', status='ativo')

    livro1 = Livro(id=1, titulo='Livro de Teste', ano_publicacao=2025, tipo_obra='livro')

    exemplar_disponivel = Exemplar(id=1, codigo_exemplar='TESTE01', status='disponivel', obra=livro1)
    exemplar_emprestado = Exemplar(id=2, codigo_exemplar='TESTE02', status='emprestado', obra=livro1)
    exemplar_para_atraso = Exemplar(id=3, codigo_exemplar='TESTE03', status='emprestado', obra=livro1)

    emprestimo_atrasado = Emprestimo(
        data_emprestimo=datetime.now(timezone.utc) - timedelta(days=30),
        data_prevista_devolucao=datetime.now(timezone.utc) - timedelta(days=15),
        usuario=usuario_com_atraso,
        exemplar=exemplar_para_atraso
    )

    db.session.add_all([
        usuario_ok, usuario_bloqueado, usuario_com_atraso, livro1,
        exemplar_disponivel, exemplar_emprestado, exemplar_para_atraso,
        emprestimo_atrasado
    ])
    db.session.commit()

    yield

    db.session.remove()
    db.drop_all()

def test_emprestimo_sucesso(test_client, init_database):
    response = test_client.get('/emprestimo/realizar?id_usuario=1&id_exemplar=1')
    assert response.status_code == 200
    assert b'Empr\xc3\xa9stimo realizado com sucesso' in response.data

    exemplar = db.session.get(Exemplar, 1)
    assert exemplar.status == 'emprestado'
    emprestimo = Emprestimo.query.filter_by(id_exemplar=1).first()
    assert emprestimo is not None
    assert emprestimo.id_usuario == 1

def test_regra_exemplar_indisponivel(test_client, init_database):
    response = test_client.get('/emprestimo/realizar?id_usuario=1&id_exemplar=2')
    assert response.status_code == 400
    assert b'n\xc3\xa3o est\xc3\xa1 dispon\xc3\xadvel' in response.data

def test_regra_usuario_com_multa_atraso(test_client, init_database):
    response = test_client.get('/emprestimo/realizar?id_usuario=3&id_exemplar=1')
    assert response.status_code == 403
    assert b'possui empr\xc3\xa9stimos atrasados' in response.data