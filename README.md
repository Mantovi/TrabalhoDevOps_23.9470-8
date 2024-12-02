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
` version: '3.8'

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
    driver: bridge `



