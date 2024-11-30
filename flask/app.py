import os
import time
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics

# Configurações iniciais
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'minha_chave_secreta_super_secreta')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'SQLALCHEMY_DATABASE_URI',
    'mysql+pymysql://root:root_password@mariadb/school_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização de extensões
db = SQLAlchemy(app)
metrics = PrometheusMetrics(app)
appbuilder = AppBuilder(app, db.session)

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de Aluno
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    sobrenome = db.Column(db.String(60), nullable=False)
    turma = db.Column(db.String(5), nullable=False)
    disciplinas = db.Column(db.String(100), nullable=False)
    ra = db.Column(db.String(9), nullable=False)

# Modelo de visão para o Aluno
class AlunoModelView(ModelView):
    datamodel = SQLAInterface(Aluno)
    list_columns = ['id', 'nome', 'sobrenome', 'turma', 'disciplinas', 'ra']

appbuilder.add_view(
    AlunoModelView,
    "Lista de Alunos",
    icon="fa-folder-open-o",
    category="Alunos",
)

# Rotas
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = Aluno.query.all()
    output = [{'id': aluno.id, 'nome': aluno.nome, 'sobrenome': aluno.sobrenome, 'turma': aluno.turma, 'disciplinas': aluno.disciplinas, 'ra': aluno.ra} for aluno in alunos]
    return jsonify(output)

@app.route('/alunos', methods=['POST'])
def adicionar_aluno():
    data = request.get_json()
    required_fields = ['nome', 'sobrenome', 'turma', 'disciplinas', 'ra']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltam campos obrigatórios!'}), 400

    novo_aluno = Aluno(**data)
    db.session.add(novo_aluno)
    db.session.commit()
    logger.info(f"Aluno {data['nome']} {data['sobrenome']} adicionado com sucesso!")
    return jsonify({'message': 'Aluno adicionado com sucesso!'}), 201

# Inicialização do banco
attempts = 5
for i in range(attempts):
    try:
        with app.app_context():
            db.create_all()
            logger.info("Banco de dados inicializado com sucesso.")
            break
    except OperationalError:
        if i < attempts - 1:
            logger.warning("Tentativa de conexão ao banco falhou. Tentando novamente em 5 segundos...")
            time.sleep(5)
        else:
            logger.error("Não foi possível conectar ao banco de dados após várias tentativas.")
            raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
