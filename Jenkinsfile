pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')

        EC2_HOST = '13.204.85.165'
        EC2_USER = 'ubuntu'
        APP_NAME = 'flask-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url: 'https://github.com/Aamantamboli/Todo-AI-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    docker.build("${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.tag("${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:${env.BUILD_NUMBER}", "${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest")
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        docker.image("${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:${env.BUILD_NUMBER}").push()
                        docker.image("${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest").push()
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Deploying to EC2 instance...'
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'EOF'
                            echo "--- Starting deployment on EC2 ---"
                            sudo systemctl start docker

                            if sudo docker ps -a | grep ${APP_NAME}-container; then
                                echo "Stopping existing container..."
                                sudo docker stop ${APP_NAME}-container
                                sudo docker rm ${APP_NAME}-container
                            fi

                            echo "${env.DOCKER_CREDENTIALS_PSW}" | sudo docker login --username ${env.DOCKER_CREDENTIALS_USR} --password-stdin

                            sudo docker pull ${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest

                            sudo docker run -d \
                              --name ${APP_NAME}-container \
                              -p 80:5000 \
                              ${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest

                            echo "--- Deployment finished on EC2 ---"
                            exit
                        EOF
                    """
                }
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
            echo 'Pipeline failed!'
        }
    }
}
