// Jenkinsfile
pipeline {
    agent any // Jenkins will use any available agent/node to run this pipeline

    environment {
        // Docker Hub details
        DOCKER_HUB_USERNAME = credentials('dockerhub-credentials').username
        DOCKER_HUB_PASSWORD = credentials('dockerhub-credentials').password

        // EC2 deployment details
        EC2_HOST = '13.204.85.165' // Replace with your flask-app-server's IP/DNS
        EC2_USER = 'ubuntu' // Or 'ec2-user' if you used Amazon Linux
        APP_NAME = 'flask-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url: 'https://github.com/Aamantamboli/Todo-AI-app.git'
                // If your repo is private, you would use:
                // git credentialsId: 'github-pat', branch: 'main', url: 'https://github.com/YOUR_GITHUB_USERNAME/flask-ci-cd-project-jenkins.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    // Build the Docker image from the Dockerfile in the current directory
                    // Tag it with 'latest' and also with the Jenkins BUILD_NUMBER for versioning
                    docker.build("${DOCKER_HUB_USERNAME}/${APP_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.tag("${DOCKER_HUB_USERNAME}/${APP_NAME}:${env.BUILD_NUMBER}", "${DOCKER_HUB_USERNAME}/${APP_NAME}:latest")
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                script {
                    // Use withRegistry to securely login to Docker Hub
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        docker.image("${DOCKER_HUB_USERNAME}/${APP_NAME}:${env.BUILD_NUMBER}").push()
                        docker.image("${DOCKER_HUB_USERNAME}/${APP_NAME}:latest").push()
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Deploying to EC2 instance...'
                // Use the sshagent plugin to securely provide the SSH key
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        # Connect to the EC2 instance and execute commands
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << 'EOF'
                            echo "--- Starting deployment on EC2 ---"
                            
                            # Ensure Docker is running
                            sudo systemctl start docker

                            # Stop and remove any existing container
                            if sudo docker ps -a | grep ${APP_NAME}-container; then
                                echo "Stopping existing container..."
                                sudo docker stop ${APP_NAME}-container
                                sudo docker rm ${APP_NAME}-container
                            fi

                            # Log in to Docker Hub on the EC2 instance
                            # Note: We are using a temporary login for the remote host.
                            # Best practice for production is to use more robust methods like AWS Secrets Manager
                            # or directly configure Docker daemon to use an AWS ECR login helper.
                            echo "${DOCKER_HUB_PASSWORD}" | sudo docker login --username ${DOCKER_HUB_USERNAME} --password-stdin
                            
                            # Pull the latest image
                            echo "Pulling latest Docker image: ${DOCKER_HUB_USERNAME}/${APP_NAME}:latest"
                            sudo docker pull ${DOCKER_HUB_USERNAME}/${APP_NAME}:latest

                            # Run the new container
                            echo "Running new Docker container..."
                            sudo docker run -d \
                              --name ${APP_NAME}-container \
                              -p 80:5000 \
                              ${DOCKER_HUB_USERNAME}/${APP_NAME}:latest
                            
                            echo "Deployment complete!"
                            echo "--- Deployment finished on EC2 ---"
                            exit # Exit the remote SSH session
                        EOF
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // You can add clean-up steps here, e.g., deleting old Docker images from the Jenkins server
            // sh 'docker rmi $(docker images -aq)' // Use with caution, deletes all local images
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
