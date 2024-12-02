import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import app, db, Aluno  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_and_reset_db():
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        # Limpa os dados após cada teste
        yield
        db.session.query(Aluno).delete()
        db.session.commit()

def test_listar_alunos(client):
    response = client.get('/alunos')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_adicionar_aluno(client):
    novo_aluno = {
        "nome": "Teste",
        "sobrenome": "Exemplo",
        "turma": "A1",
        "disciplinas": "DevOps",
        "ra": "11.1111-1"
    }
    response = client.post('/alunos', json=novo_aluno)
    assert response.status_code == 201
    assert response.json['message'] == 'Aluno adicionado com sucesso!'
