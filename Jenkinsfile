pipeline {
    agent any // Use any available Jenkins agent/node

    environment {
        // Docker Hub credentials stored in Jenkins
        DOCKER_HUB_USERNAME = credentials('dockerhub-credentials').username
        DOCKER_HUB_PASSWORD = credentials('dockerhub-credentials').password

        // EC2 deployment details
        EC2_HOST = '13.204.85.165' // Replace with your EC2 server IP or DNS
        EC2_USER = 'ubuntu' // Or 'ec2-user' for Amazon Linux
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
                    docker.build("${DOCKER_HUB_USERNAME}/${APP_NAME}:latest", ".")
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        docker.image("${DOCKER_HUB_USERNAME}/${APP_NAME}:latest").push()
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

                            echo "${DOCKER_HUB_PASSWORD}" | sudo docker login --username ${DOCKER_HUB_USERNAME} --password-stdin

                            echo "Pulling latest Docker image: ${DOCKER_HUB_USERNAME}/${APP_NAME}:latest"
                            sudo docker pull ${DOCKER_HUB_USERNAME}/${APP_NAME}:latest

                            echo "Running new Docker container..."
                            sudo docker run -d --name ${APP_NAME}-container -p 5000:5000 ${DOCKER_HUB_USERNAME}/${APP_NAME}:latest

                            echo "Deployment complete!"
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
