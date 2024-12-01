pipeline {
    agent any

    stages {
        stage('Prepare Environment') {
            steps {
                sh 'mkdir -p $WORKSPACE/prometheus'
                sh 'touch $WORKSPACE/prometheus/prometheus.yml'
            }
        }
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
