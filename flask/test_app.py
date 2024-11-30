import pytest
from flask.testing import FlaskClient
from app import app, db, Aluno

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_db():
    with app.app_context():
        db.session.query(Aluno).delete() #Limpa o banco
        db.session.commit()

def test_listar_alunos(client: FlaskClient):
    response = client.get('/alunos')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 0


def test_adicionar_aluno(client: FlaskClient):
    novo_aluno = {
        "nome": "Aluno",
        "sobrenome": "Bobo",
        "turma": "D7",
        "disciplinas": "DevOps",
        "ra": "99.9999-9"
    }
    response = client.post('/alunos', json=novo_aluno)
    assert response.status_code == 201
    assert response.json['message'] == 'Aluno adicionado com sucesso!'
