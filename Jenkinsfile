pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        PYTHON_IMAGE = "python:3.11-slim"
        WORKDIR = "$WORKSPACE"
    }

    stages {

        stage('Checkout') {
            steps {
                cleanWs()
                checkout scm
            }
        }

        stage('Fix Permissions') {
            steps {
                sh '''
                    echo "Fixing workspace permissions..."
                    chmod -R a+rwX $WORKSPACE
                '''
            }
        }

        stage('Debug Workspace') {
            steps {
                sh '''
                    echo "=== HOST WORKSPACE ==="
                    pwd
                    ls -la

                    echo "=== IMPORTANT FILES CHECK ==="
                    test -f requirements.txt && echo "requirements OK" || exit 1
                    test -f main.py && echo "main.py OK" || echo "WARNING: no main.py"
                '''
            }
        }

        stage('Docker Sanity') {
            steps {
                sh '''
                    docker version
                '''
            }
        }

        stage('Install Dependencies (Docker)') {
            steps {
                sh '''
                    docker run --rm \
                        --user $(id -u):$(id -g) \
                        -v $WORKSPACE:$WORKSPACE \
                        -w $WORKSPACE \
                        $PYTHON_IMAGE bash -c "
                            set -e
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        "
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    docker run --rm \
                        --user $(id -u):$(id -g) \
                        -v $WORKSPACE:$WORKSPACE \
                        -w $WORKSPACE \
                        $PYTHON_IMAGE bash -c "
                            set -e
                            pip install flake8
                            flake8 src || true
                        "
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    docker run --rm \
                        --user $(id -u):$(id -g) \
                        -v $WORKSPACE:$WORKSPACE \
                        -w $WORKSPACE \
                        $PYTHON_IMAGE bash -c "
                            set -e
                            pip install bandit
                            bandit -r src || true
                        "
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    docker run --rm \
                        --user $(id -u):$(id -g) \
                        -v $WORKSPACE:$WORKSPACE \
                        -w $WORKSPACE \
                        $PYTHON_IMAGE bash -c "
                            set -e
                            pip install -r requirements.txt
                            pip install pytest
                            pytest -v
                        "
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker run --rm \
                        --user $(id -u):$(id -g) \
                        -v $WORKSPACE:$WORKSPACE \
                        -w $WORKSPACE \
                        $PYTHON_IMAGE bash -c "
                            set -e
                            python main.py --help || echo 'No CLI entrypoint'
                        "
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: '**/*', fingerprint: true
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline succeeded"
        }

        failure {
            echo "❌ Pipeline failed"
        }

        always {
            cleanWs()
        }
    }
}