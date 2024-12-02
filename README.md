# TrabalhoDevOps_23.9470-8

## Aluno
- Leandro Mantovi de Andrade

## Como Executar o Projeto
1. Abra o Jenkins com a url localhost:8080
2. Crie uma nova tarefa do tipo pipeline.
3. Seleciona Git no SCM, e adicione o repositório https://github.com/Mantovi/TrabalhoDevOps_23.9470-8.git
4.  Clique em "Contruir Agora"
5.  Aguarde a execução

## Desenvolvimento
Foi criado na raiz do projeto o arquivo docker-compose, para configuração de containers
`docker-compose.yml`
Em seguida foi adicionado nele, o seguinte código:
```
version: '3.8'
services:
  mariadb:
    build:
      context: ./mariadb
      dockerfile: Dockerfile_mariadb
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: school_db
      MYSQL_USER: flask_user
      MYSQL_PASSWORD: flask_password
    networks:
      - prom-network  # Adicionando à rede personalizada

  flask:
    build:
      context: ./flask
      dockerfile: Dockerfile_flask
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql+pymysql://flask_user:flask_password@mariadb:3306/school_db
    depends_on:
      - mariadb
    networks:
      - prom-network  # Adicionando à rede personalizada

  test:
    build:
      context: ./flask
      dockerfile: Dockerfile_flask
    command: ["pytest", "/app/test_app.py"]
    depends_on:
      - mariadb
      - flask
    environment:
      - DATABASE_URL=mysql+pymysql://flask_user:flask_password@mariadb:3306/school_db
    networks:
      - prom-network  # Adicionando à rede personalizada

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - mysqld_exporter
    networks:
      - prom-network  # Adicionando à rede personalizada

  mysqld_exporter:
    image: prom/mysqld-exporter
    environment:
      - DATA_SOURCE_NAME=mysql://flask_user:flask_password@mariadb:3306/school_db
    ports:
      - "9104:9104"
    depends_on:
      - mariadb

  grafana:
    build:
      context: ./grafana
      dockerfile: Dockerfile_grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - prom-network  # Adicionando à rede personalizada

networks:
  prom-network:  # Rede personalizada para garantir a comunicação entre containers
    driver: bridge
```

O arquivo requirements.txt foi adicionado ao diretório flask para especificar as dependências:
```
Flask==1.1.4  # Compatível com Flask-AppBuilder
Flask-SQLAlchemy==2.4.4  # Extensão para integração do Flask com SQLAlchemy
PyMySQL==0.9.3  # Conexão do Python com o banco de dados MariaDB
Flask-AppBuilder==3.3.0  # Compatível com a versão 1.x do Flask
Werkzeug==1.0.1  # Versão do Werkzeug compatível, para evitar problemas de importação
MarkupSafe==2.0.1  # Compatível com Jinja2 e Flask
WTForms==2.3.3  # Versão compatível com Flask-AppBuilder, inclui o módulo 'compat'
prometheus-flask-exporter==0.18.3  # Exportador de métricas Prometheus para Flask
pytest==6.2.5  # Framework de testes para Python
pytest-flask==1.2.0  # Extensão do pytest para testar aplicações Flask
Flask-Testing==0.8.0  # Biblioteca para testes unitários com Flask
```

O Dockerfile_flask foi criado para determinar o ambiente de trabalho do Flask:
```
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/
COPY test_app.py /app/

CMD ["flask", "run", "--host=0.0.0.0"]
```

## Banco de Dados
Para o MariaDB, foi criada a pasta mariadb com o arquivo Dockerfile_mariadb:
```
FROM mariadb:10.5

ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=school_db
ENV MYSQL_USER=flask_user
ENV MYSQL_PASSWORD=flask_password

EXPOSE 3306
```
Depois os Containers foram iniciados com:
```
docker-compose up --build
```

Ao acessar http://localhost:5000, a aplicação estava funcional.
![Imagem da Aplicação Rodando]()