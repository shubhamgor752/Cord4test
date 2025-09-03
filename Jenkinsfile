pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/shubhamgor752/Cord4test.git'
            }
        }
        stage('Build') {
            steps {
                echo 'Setting up virtual environment...'
                sh 'python3 -m venv ${VENV_DIR}'
                sh '. ${VENV_DIR}/bin/activate && pip install --upgrade pip'
                sh '. ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
                // Add build steps here, e.g. sh 'make'
            }
        }
        stage('Test') {
            steps {
                echo 'Running django tests...'
                sh '. ${VENV_DIR}/bin/activate && python manage.py test'
                // Add test steps here, e.g. sh 'make test'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying Django app locally...'

                // Run database migrations
                sh '. ${VENV_DIR}/bin/activate && python manage.py migrate'

                // Collect static files
                sh '. ${VENV_DIR}/bin/activate && python manage.py collectstatic --noinput'

                // Start the Django development server in the background
                sh 'nohup . ${VENV_DIR}/bin/activate && python manage.py runserver 0.0.0.0:8000 &'

                echo 'Local deployment finished.'
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}