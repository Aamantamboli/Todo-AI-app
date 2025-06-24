You absolutely can\! Jenkins is a fantastic choice for a robust CI/CD pipeline, offering immense flexibility and a vast plugin ecosystem. The core application and Docker setup will remain the same, but we'll swap GitHub Actions for a Jenkins server and a `Jenkinsfile` (Pipeline script).

Here's the revised project, "Automated Web Application Deployment with CI/CD (End-to-End) using Jenkins":

-----

## Project: Automated Web Application Deployment with CI/CD (End-to-End) using Jenkins

**Goal:** Create a CI/CD pipeline using Jenkins to automatically build a Flask web application, containerize it with Docker, push the Docker image to Docker Hub, and then deploy it to an AWS EC2 instance whenever changes are pushed to the GitHub repository.

**Technologies Used:**

  * **Application Language:** Python (Flask)
  * **Version Control:** Git, GitHub
  * **Containerization:** Docker
  * **CI/CD Tool:** Jenkins
  * **Cloud Provider:** Amazon Web Services (AWS) - EC2
  * **Container Registry:** Docker Hub

-----

### Step 1: Set up the Flask Web Application (Same as before)

This part remains identical. If you already did this, great\! If not, follow these steps:

**1. Create Project Directory:**

```bash
mkdir flask-ci-cd-project-jenkins
cd flask-ci-cd-project-jenkins
```

**2. Create `app.py` (Flask Application):**

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask App! (Deployed via Jenkins CI/CD)"

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**3. Create `requirements.txt`:**

```
# requirements.txt
Flask==2.3.3
```

**4. Create `Dockerfile`:**

```dockerfile
# Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

**5. Create `.dockerignore`:**

```
# .dockerignore
__pycache__/
.venv/
*.pyc
*.git/
.gitignore
```

-----

### Step 2: Initialize Git and Push to GitHub (Same as before)

Follow these steps:

**1. Initialize Git:**

```bash
git init
```

**2. Create `.gitignore`:**

```
# .gitignore
*.pyc
.venv/
__pycache__/
.DS_Store
```

**3. Add, Commit, and Push to GitHub:**

```bash
git add .
git commit -m "Initial commit: Flask app and Dockerfile"
```

Now, go to GitHub, create a **new public repository** (e.g., `flask-ci-cd-project-jenkins`). Do **not** initialize with a README or license.

Then, link your local repository to the remote one and push:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/flask-ci-cd-project-jenkins.git
git branch -M main
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

-----

### Step 3: Set up AWS EC2 Instance for Application Deployment (Same as before)

This EC2 instance will run your Dockerized Flask application.

**1. Launch an EC2 Instance:**

  * Log in to AWS Management Console.
  * Navigate to **EC2** service.
  * Click **"Launch instance"**.
  * **Name:** `flask-app-server` (or similar)
  * **AMI:** **"Ubuntu Server 22.04 LTS (HVM), SSD Volume Type"**.
  * **Instance type:** `t2.micro` (Free tier eligible).
  * **Key pair (login):** Choose an existing key pair or create a new one. **Save the `.pem` file securely\!**
  * **Network settings (Security groups):**
      * **Allow SSH traffic:** From "My IP" or "Anywhere".
      * **Allow HTTP traffic:** From "Anywhere" (Crucial for your web app, port 80).
  * Click **"Launch instance"**.

**2. SSH into the EC2 Instance and Install Docker:**

```bash
chmod 400 /path/to/your-key-pair.pem
ssh -i /path/to/your-key-pair.pem ubuntu@YOUR_EC2_PUBLIC_IP_OR_DNS

# Once SSHed into EC2:
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu # Add current user to docker group
newgrp docker # Apply group change immediately (or re-SSH)
docker version # Verify installation
```

You might need to log out and log back in (SSH again) for the `docker` group changes to take effect without `sudo`.

-----

### Step 4: Set up Jenkins Server on a separate AWS EC2 Instance

It's best practice to run Jenkins on a dedicated server.

**1. Launch a NEW EC2 Instance for Jenkins:**

  * Log in to AWS Management Console.
  * Navigate to **EC2** service.
  * Click **"Launch instance"**.
  * **Name:** `jenkins-server`
  * **AMI:** **"Ubuntu Server 22.04 LTS (HVM), SSD Volume Type"**.
  * **Instance type:** `t2.medium` (or `t2.small` if `t2.micro` is too slow for Jenkins, though `t2.medium` is recommended for better performance).
  * **Key pair (login):** Choose an existing key pair or create a **new one** specifically for the Jenkins server. **Save the `.pem` file securely\!**
  * **Network settings (Security groups):**
      * **Allow SSH traffic:** From "My IP" or "Anywhere".
      * **Allow HTTP traffic (Port 8080):** From "Anywhere" (Jenkins runs on port 8080 by default).
  * Click **"Launch instance"**.

**2. SSH into the Jenkins EC2 Instance and Install Jenkins:**

Once the Jenkins EC2 instance is running, SSH into it:

```bash
chmod 400 /path/to/your-jenkins-key-pair.pem
ssh -i /path/to/your-jenkins-key-pair.pem ubuntu@YOUR_JENKINS_EC2_PUBLIC_IP_OR_DNS
```

Now, install Java and Jenkins:

```bash
# Update package list
sudo apt update -y

# Install Java (Jenkins requires Java)
sudo apt install -y openjdk-11-jre

# Download and add Jenkins GPG key
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository to your sources list
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Update package list again to include Jenkins repo
sudo apt update -y

# Install Jenkins
sudo apt install -y jenkins

# Start and enable Jenkins service
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins # Check status
```

**3. Initial Jenkins Setup:**

  * Open your web browser and go to `http://YOUR_JENKINS_EC2_PUBLIC_IP_OR_DNS:8080`.
  * You'll see an "Unlock Jenkins" screen.
  * To get the initial admin password, SSH back into your Jenkins EC2 instance and run:
    ```bash
    sudo cat /var/lib/jenkins/secrets/initialAdminPassword
    ```
  * Copy the password, paste it into the Jenkins browser page, and click **"Continue"**.
  * Click **"Install suggested plugins"**.
  * Create an admin user (username and password).
  * You can set the Jenkins URL (usually the public IP/DNS), then click **"Save and Finish"**.
  * Click **"Start using Jenkins"**.

-----

### Step 5: Configure Jenkins Credentials

We need to tell Jenkins how to authenticate with GitHub (to pull code), Docker Hub (to push images), and the EC2 application server (to deploy).

**1. Install Required Jenkins Plugins:**
From the Jenkins dashboard:

  * Go to **"Manage Jenkins"** -\> **"Manage Plugins"**.
  * Go to the **"Available"** tab and search for and install these plugins:
      * **`Docker Pipeline`** (for integrating Docker commands in pipelines)
      * **`SSH Agent`** (for securely using SSH keys to connect to the remote EC2 server)
      * **`Git`** (usually installed by default, but double-check)
  * You can select "Install without restart" and then "Restart Jenkins when installation is complete and no jobs are running".

**2. Add Docker Hub Credentials:**

  * From the Jenkins dashboard, go to **"Manage Jenkins"** -\> **"Manage Credentials"**.
  * Click on **"(global)"** -\> **"Add Credentials"**.
  * **Kind:** `Username with password`
  * **Scope:** `Global`
  * **Username:** Your Docker Hub username
  * **Password:** Your Docker Hub Access Token (generated from Docker Hub Security settings, same as in the GitHub Actions example).
  * **ID:** `dockerhub-credentials` (This ID is important; we'll use it in the `Jenkinsfile`).
  * **Description:** `Docker Hub credentials`
  * Click **"Create"**.

**3. Add GitHub Credentials (for Repository Checkout):**
If your GitHub repository is **public**, Jenkins can clone it without credentials. However, if it's private, or if you prefer explicit credentials:

  * Generate a **Personal Access Token (PAT)** on GitHub:
      * Go to GitHub -\> Your profile picture -\> **"Settings"** -\> **"Developer settings"** -\> **"Personal access tokens"** -\> **"Tokens (classic)"** -\> **"Generate new token"**.
      * Give it a descriptive name (e.g., `jenkins-repo-access`).
      * Grant `repo` scope permissions.
      * **Copy the generated token immediately\!**
  * In Jenkins, go to **"Manage Jenkins"** -\> **"Manage Credentials"** -\> **"(global)"** -\> **"Add Credentials"**.
  * **Kind:** `Secret text`
  * **Scope:** `Global`
  * **Secret:** Paste your GitHub PAT here.
  * **ID:** `github-pat` (or similar).
  * **Description:** `GitHub Personal Access Token for repository access`
  * Click **"Create"**.

**4. Add SSH Private Key for EC2 Deployment:**
This key will allow Jenkins to SSH into your `flask-app-server` EC2 instance and run Docker commands.

  * In Jenkins, go to **"Manage Jenkins"** -\> **"Manage Credentials"** -\> **"(global)"** -\> **"Add Credentials"**.
  * **Kind:** `SSH Username with Private Key`
  * **Scope:** `Global`
  * **ID:** `ec2-ssh-key` (This ID is important\!)
  * **Description:** `SSH key for EC2 app server deployment`
  * **Username:** `ubuntu` (or `ec2-user` if you're using Amazon Linux AMI).
  * **Private Key:** Select **"Enter directly"**.
  * **Paste your EC2 private key (`.pem` file content)** here (including `-----BEGIN ... PRIVATE KEY-----` and `-----END ... PRIVATE KEY-----`).
  * Click **"Create"**.

-----

### Step 6: Create the `Jenkinsfile` (Pipeline Script)

Create a file named `Jenkinsfile` (no extension) in the root of your `flask-ci-cd-project-jenkins` repository.

```groovy
// Jenkinsfile
pipeline {
    agent any // Jenkins will use any available agent/node to run this pipeline

    environment {
        // Docker Hub details
        DOCKER_HUB_USERNAME = credentials('dockerhub-credentials').username
        DOCKER_HUB_PASSWORD = credentials('dockerhub-credentials').password

        // EC2 deployment details
        EC2_HOST = 'YOUR_EC2_APP_SERVER_PUBLIC_IP_OR_DNS' // Replace with your flask-app-server's IP/DNS
        EC2_USER = 'ubuntu' // Or 'ec2-user' if you used Amazon Linux
        APP_NAME = 'flask-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url: 'https://github.com/YOUR_GITHUB_USERNAME/flask-ci-cd-project-jenkins.git'
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
```

**Important Replacements in `Jenkinsfile`:**

  * `YOUR_GITHUB_USERNAME`: Replace with your GitHub username.
  * `YOUR_EC2_APP_SERVER_PUBLIC_IP_OR_DNS`: Replace with the public IP address or DNS of your `flask-app-server` EC2 instance.

-----

### Step 7: Configure Jenkins Job

**1. Add the `Jenkinsfile` to your Git Repository:**

```bash
git add Jenkinsfile
git commit -m "Add Jenkins Pipeline script"
git push origin main
```

**2. Create a New Pipeline Job in Jenkins:**

  * From the Jenkins dashboard, click **"New Item"**.
  * **Enter an item name:** `Flask-App-CI-CD` (or similar).
  * Select **"Pipeline"**.
  * Click **"OK"**.

**3. Configure the Pipeline Job:**

  * **General:**
      * **"GitHub project"**: Check this box and enter your GitHub repo URL (e.g., `https://github.com/YOUR_GITHUB_USERNAME/flask-ci-cd-project-jenkins`).
  * **Build Triggers:**
      * **"GitHub hook trigger for GITScm polling"**: This is crucial. It sets up a webhook so GitHub notifies Jenkins of new pushes.
      * **(Optional but recommended for initial testing):** You can also check "Poll SCM" and set a schedule (e.g., `* * * * *` for every minute) to force Jenkins to check for changes if the webhook isn't immediately configured. Remember to remove or increase this interval for production.
  * **Pipeline:**
      * **Definition:** `Pipeline script from SCM`
      * **SCM:** `Git`
      * **Repository URL:** `https://github.com/YOUR_GITHUB_USERNAME/flask-ci-cd-project-jenkins.git`
      * **Credentials:** If your repo is private, select the `github-pat` credential you created. If it's public, select `- none -`.
      * **Branches to build:** `*/main` (or `*/master` if your default branch is `master`).
      * **Script Path:** `Jenkinsfile` (This is the default, so if you named your file `Jenkinsfile`, you're good).
  * Click **"Save"**.

-----

### Step 8: Configure GitHub Webhook

For automatic builds on every push, GitHub needs to tell Jenkins.

1.  Go to your GitHub repository (`flask-ci-cd-project-jenkins`).
2.  Click **"Settings"** -\> **"Webhooks"** -\> **"Add webhook"**.
3.  **Payload URL:** `http://YOUR_JENKINS_EC2_PUBLIC_IP_OR_DNS:8080/github-webhook/` (Make sure to include the trailing slash).
4.  **Content type:** `application/json`
5.  **Secret:** Leave blank for now (or generate one in Jenkins and add it here for security, but that's an advanced step for a first project).
6.  **"Which events would you like to trigger this webhook?"**: Select **"Just the push event"**.
7.  Ensure **"Active"** is checked.
8.  Click **"Add webhook"**.

**Important:** Ensure your Jenkins EC2 instance's security group allows inbound traffic on port `8080` from `Anywhere` (0.0.0.0/0) for GitHub to reach it.

-----

### Step 9: Trigger the CI/CD Pipeline

**1. Manual Trigger (Initial Test):**

  * Go to your Jenkins dashboard.
  * Click on your `Flask-App-CI-CD` job.
  * Click **"Build Now"** in the left menu.
  * Monitor the build in the "Build History" panel (click on the build number, then "Console Output" to see logs).

**2. Automatic Trigger (After Webhook Setup):**

  * Make a small change to your `app.py` locally.
  * Commit and push it to your GitHub `main` branch.
    ```bash
    # app.py
    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello from Flask App! Version 2.0 (Updated via Jenkins CI/CD)!" # Changed line

    @app.route('/health')
    def health_check():
        return "OK", 200

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
    ```
    ```bash
    git add app.py
    git commit -m "Update Flask app to version 2.0 (Jenkins)"
    git push origin main
    ```
  * Go to your Jenkins dashboard and observe a new build starting automatically.
  * Monitor the console output for success.

**3. Verify Deployment:**
Once the Jenkins pipeline completes successfully, open your web browser and navigate to:

`http://YOUR_EC2_APP_SERVER_PUBLIC_IP_OR_DNS`

You should see the updated message: "Hello from Flask App\! Version 2.0 (Updated via Jenkins CI/CD)\!"

-----

## What You've Achieved and LinkedIn Showcase

You've successfully implemented an end-to-end CI/CD pipeline using Jenkins, a cornerstone of many DevOps environments.

**You've demonstrated proficiency in:**

  * **Jenkins Setup & Administration:** Installing Jenkins, managing plugins, configuring jobs and credentials.
  * **Jenkins Pipelines (Jenkinsfile):** Writing Groovy scripts to define multi-stage CI/CD workflows.
  * **Credential Management:** Securely handling Docker Hub and SSH keys within Jenkins.
  * **Version Control Integration:** Connecting Jenkins to GitHub via webhooks for automated builds.
  * **Docker Integration:** Building, tagging, and pushing Docker images from Jenkins.
  * **Remote Deployment:** Using SSH to deploy containerized applications to a remote EC2 instance.
  * **Cloud Platform (AWS):** Utilizing EC2 instances for both the Jenkins server and the application deployment target.
  * **Scripting:** Employing Bash commands within the Jenkins pipeline for deployment logic.

**For your LinkedIn Profile:**

This project is a strong asset\! Use similar descriptive language as before, but emphasize Jenkins.

  * **Project Title:** End-to-End CI/CD Pipeline for Web App using Jenkins, Docker, and AWS
  * **Description:** "Designed and implemented a robust CI/CD pipeline leveraging Jenkins for continuous integration and delivery of a Python Flask web application. Orchestrated automated Docker image builds, pushes to Docker Hub, and seamless deployments to an AWS EC2 instance. Gained extensive hands-on experience with Jenkins Pipeline scripting, secure credential management, GitHub webhook integration, and remote server automation via SSH. This project significantly improved deployment efficiency and reliability from code commit to production."
  * **Links:** Link to your GitHub repository (with a clear `README.md` explaining the Jenkins setup, `Jenkinsfile` steps, etc.). Include screenshots of your Jenkins pipeline stages, Docker Hub image, and the deployed application.
  * **Skills:** Jenkins, Jenkins Pipeline, Groovy Scripting, Docker, Docker Hub, AWS EC2, CI/CD, Git, GitHub, SSH, Linux, Python, Automation.

This Jenkins-based project is highly valuable for demonstrating your practical DevOps skills to employers\!
