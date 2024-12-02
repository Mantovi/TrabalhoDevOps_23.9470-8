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

Para realizar testes na aplicação, rode o comando:
```
docker-compose run --rm test
```
![Imagem dos testes funcionando](https://github.com/Mantovi/TrabalhoDevOps_23.9470-8/blob/main/imagens/Captura%20de%20tela%202024-12-02%20182541.png?raw=true)


Ao acessar http://localhost:5000, a aplicação estava funcional.
![Imagem da Aplicação Rodando](https://github.com/Mantovi/TrabalhoDevOps_23.9470-8/blob/main/imagens/Captura%20de%20tela%202024-12-02%20124941.png?raw=true)

## Grafana e Prometheus

Foi adicionada uma estrutura de pastas para configurar os serviços do Grafana e Prometheus.
Na pasta grafana, o arquivo Dockerfile_grafana é usado para criar uma imagem Docker personalizada do Grafana, onde são configurados ajustes específicos para o ambiente. Isso inclui configurações de dashboards, plugins e integrações necessárias. O código está assim:
```
FROM grafana/grafana:latest

USER root

RUN mkdir /var/lib/grafana/dashboards

COPY provisioning/datasource.yml /etc/grafana/provisioning/datasources/
COPY provisioning/dashboard.yml /etc/grafana/provisioning/dashboards/
COPY dashboards/mariadb_dashboard.json /var/lib/grafana/dashboards/

RUN chown -R 472:472 /etc/grafana/provisioning

USER grafana
```

Na pasta dashboards do Grafana, encontra-se um arquivo **mariadb_dashboard.json** destinado a um dashboard pré-configurado que descreve os painéis e as métricas específicas para acompanhar o desempenho de um banco de dados MariaDB. Ele detalha os painéis, as métricas observadas e a integração com as fontes de dados.

Na pasta provisioning, existem dois arquivos: **datasource.yml** e **dashboard.yml**, ambos projetados para automatizar a configuração de fontes de dados e dashboards. Essas automações eliminam a necessidade de realizar as configurações manualmente na interface do Grafana, aplicando-as automaticamente ao iniciar.

**datasource.yml:** Define fontes de dados, como Prometheus, MySQL ou Elasticsearch, utilizando arquivos no formato YML.
**dashboard.yml:** Especifica a localização dos arquivos JSON que contêm as definições dos dashboards para provisionamento automático.

**datasource.yml**
```
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: 5s
```

**dashboard.yml**
```
apiVersion: 1

providers:
  - name: "MariaDB Dashboards"
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
```

Na pasta prometheus, o arquivo prometheus.yml contém a configuração central do Prometheus, onde estão definidas:

Fontes de coleta de métricas (targets).
Parâmetros de coleta (frequência e regras de scrape).
Configuração de alertas (via Alertmanager).
Ajustes gerais de armazenamento e operação.

```
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "mysqld_exporter"
    static_configs:
      - targets: ["mysqld_exporter:9104"]
```

Arquivo **Jenkinsfile:**
```
pipeline {
    agent any

    stages {
        // stage('Prepare Environment') {
        //     steps {
        //         sh 'mkdir -p $WORKSPACE/prometheus'
        //         sh 'touch $WORKSPACE/prometheus/prometheus.yml'
        //     }
        // }
        stage('Git Pull & Build Containers') {
            steps {
                script {
                    git branch: "main", url: "https://github.com/Mantovi/TrabalhoDevOps_23.9470-8.git"
                    sh 'docker-compose down -v || true'
                    sh 'docker-compose build'
                }
            }
        }
        stage('Start Containers & Run Tests') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask mysqld_exporter prometheus grafana'
                    sh 'sleep 30' 
                    try {
                        sh 'docker-compose run --rm test'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Testes falharam. Pipeline interrompido."
                    }
                }
            }
        }
        stage('Keep Application Running') {
            steps {
                script {
                    sh 'docker-compose up -d'
                }
            }
        }
    }

    post {
        failure {
            sh 'docker-compose down -v || true'
        }
    }
}
```


Agora acessando o Grafana, na `localhost:3000`, faça o Login no Grafana, e clique em dashboards para vizualizar as métricas
Recomendo alterar a opção **time range** para 5 minutos
![Imagem dos Dashboards](https://github.com/Mantovi/TrabalhoDevOps_23.9470-8/blob/main/imagens/M%C3%A9tricas.png?raw=true)














>>>>>>> 0a7aa7cd890cfe0fd3427f2adee8b631f966faf4
