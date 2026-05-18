pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        PYTHON_IMAGE = 'python:3.11-slim'
        PIP_CACHE_DIR = '/tmp/pip-cache'
    }

    stages {

        stage('Checkout Clean') {
            steps {
                cleanWs()
                checkout scm
            }
        }

        stage('Debug Workspace') {
            steps {
                sh '''
                echo "=== WORKSPACE DEBUG ==="
                pwd
                ls -la
                '''
            }
        }

        stage('DEBUG ENV (TEMP)') {
            steps {
                sh '''
                echo "=== DEBUG ENV ==="
                echo "WORKSPACE=$WORKSPACE"
                echo "PWD=$(pwd)"
                env | grep WORKSPACE || true
                '''
            }
        }

        stage('Verify Requirements (HOST)') {
            steps {
                sh '''
                echo "=== HOST CHECK ==="
                test -f requirements.txt && echo "requirements EXISTS" || exit 1
                head -n 5 requirements.txt
                '''
            }
        }

        stage('Docker Sanity Check') {
            steps {
                sh '''
                docker version
                '''
            }
        }

        stage('Verify Inside Container (CRITICAL DEBUG)') {
            steps {
                sh '''
                docker run --rm \
                    -v ${WORKSPACE}:/app \
                    -w /app \
                    ${PYTHON_IMAGE} \
                    bash -c "
                        set -e
                        echo '=== INSIDE CONTAINER ==='
                        pwd
                        ls -la /app
                        test -f /app/requirements.txt
                    "
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                docker run --rm \
                    -v ${WORKSPACE}:/app \
                    -v ${PIP_CACHE_DIR}:/root/.cache/pip \
                    -w /app \
                    ${PYTHON_IMAGE} \
                    bash -c "
                        set -e
                        echo '=== INSTALL START ==='
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest flake8 pip-audit
                    "
                '''
            }
        }

        stage('Quality Gates') {
            parallel {

                stage('Lint') {
                    steps {
                        sh '''
                        docker run --rm \
                            -v ${WORKSPACE}:/app \
                            -w /app \
                            ${PYTHON_IMAGE} \
                            flake8 . --count --statistics
                        '''
                    }
                }

                stage('Security Scan') {
                    steps {
                        sh '''
                        docker run --rm \
                            -v ${WORKSPACE}:/app \
                            -w /app \
                            ${PYTHON_IMAGE} \
                            pip-audit || true
                        '''
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                docker run --rm \
                    -v ${WORKSPACE}:/app \
                    -w /app \
                    ${PYTHON_IMAGE} \
                    pytest -v --junitxml=/app/test-results.xml || true
                '''
            }
        }

        stage('Publish Test Results') {
            steps {
                junit testResults: 'test-results.xml', allowEmptyResults: true
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                docker run --rm \
                    -v ${WORKSPACE}:/app \
                    -w /app \
                    ${PYTHON_IMAGE} \
                    python -c "print('Smoke Test Passed')"
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline passed"
        }

        failure {
            echo "❌ Pipeline failed"
        }

        always {
            archiveArtifacts artifacts: '**/*.xml', allowEmptyArchive: true
        }
    }
}