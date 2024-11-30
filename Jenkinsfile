pipeline {
    agent any

    environment {
        BUILD_NUMBER = "${env.BUILD_NUMBER}"  // Variável de ambiente com o número do build
    }

    stages {
        stage('Git pull and build') {
            steps {
                script {
                    // Faz o checkout do repositório
                    git branch: "main", url:"https://github.com/Mantovi/TrabalhoDevOps_23.9470-8.git"
                    // Para e remove volumes e contêineres antigos
                    sh 'docker-compose down -v'
                    // Constrói as imagens com o Docker Compose
                    sh 'docker-compose build'
                }
            }
        }

        stage('Start Containers & Run Tests') {
            steps {
                script {
                    // Remove o contêiner antigo, se ele existir
                    sh 'docker ps -aq -f name=mariadb_container_${BUILD_NUMBER} | xargs --no-run-if-empty docker rm -f || true'
                    // Inicia os contêineres com Docker Compose, passando a variável BUILD_NUMBER
                    sh "docker-compose up -d --build --force-recreate mariadb flask_app test mysqld_exporter prometheus grafana"
                    // Espera 40 segundos para os contêineres estarem prontos
                    sh 'sleep 40' 

                    try {
                        // Executa os testes dentro do contêiner
                        sh 'docker-compose run --rm test'
                    } catch (Exception e) {
                        // Caso os testes falhem, marca o build como falho e interrompe
                        currentBuild.result = 'FAILURE'
                        error "Testes falharam. Pipeline interrompido."
                    }
                }
            }
        }

        stage('Keep Application Running') {
            steps {
                script {
                    // Reinicia os contêineres para manter a aplicação rodando
                    sh "docker-compose up -d mariadb flask_app test mysqld_exporter prometheus grafana"
                }
            }
        }
    }

    post {
        always {
            // Sempre limpa os contêineres e volumes após a execução
            sh 'docker-compose down -v'
        }
        failure {
            // Caso o pipeline falhe, ainda limpa os contêineres e volumes
            sh 'docker-compose down -v'
        }
    }
}
