pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t bookstore:latest .'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh 'docker run --rm bookstore:latest python manage.py test store admin_panel'
            }
        }

        stage('Deploy (Placeholder)') {
            steps {
                echo 'Deploying application...'
                echo 'Actual deployment commands depend on the target server/platform.'
                script {
                    
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}