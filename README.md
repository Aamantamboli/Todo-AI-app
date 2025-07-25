## Project: Automated Web Application Deployment with CI/CD (End-to-End) using Jenkins

**Goal:** Create a CI/CD pipeline using Jenkins to automatically build a Flask web application, containerize it with Docker, push the Docker image to Docker Hub, and then deploy it to an AWS EC2 instance whenever changes are pushed to the GitHub repository.

![CI/CD Architecture Diagram](images/ci-cd-architecture-daigram.png)

**Technologies Used:**

  * **Application Language:** Python (Flask)
  * **Version Control:** Git, GitHub
  * **Containerization:** Docker
  * **CI/CD Tool:** Jenkins
  * **Cloud Provider:** Amazon Web Services (AWS) - EC2
  * **Container Registry:** Docker Hub

-----

### Step 1: Set up the Flask Web Application 

This part remains identical. If you already did this, great\! If not, follow these steps:

**1. Create Project Directory:**

```bash
mkdir Todo-AI-app
cd Todo-AI-app
```

**2. Create `app.py` (Flask Application):**

```python
from flask import Flask, render_template, request, redirect
from textblob import TextBlob

app = Flask(__name__)

# In-memory task list
tasks = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("task")
        if content:
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
            tasks.append({
                "content": content,
                "completed": False,
                "sentiment": sentiment
            })
        return redirect("/")
    return render_template("index.html", tasks=tasks)

@app.route("/complete/<int:task_id>")
def complete(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]["completed"] = True
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    if 0 <= task_id < len(tasks):
        del tasks[task_id]
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

**3. Create `requirements.txt`:**

```
# requirements.txt
Flask
textblob
```

**4. Create `Dockerfile`:**

```dockerfile
# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first to leverage Docker cache if unchanged
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app code into container
COPY . .

# Expose the port your app runs on (adjust if needed)
EXPOSE 5000

# Command to run your app
CMD ["python3", "app.py"]
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

### Step 2: Initialize Git and Push to GitHub

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

Now, go to GitHub, create a **new public repository** (e.g., `Todo-AI-app`). Do **not** initialize with a README or license.

Then, link your local repository to the remote one and push:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Todo-AI-app.git
git branch -M main
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

-----

### Step 3: Set up AWS EC2 Instance for Application Deployment 

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
sudo apt update 

# Install Java (Jenkins requires Java)
sudo apt install openjdk-11-jre 

# Download and add Jenkins GPG key
curl -fsSL https://pkg.jenkins.io/debian/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository to your sources list
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install jenkins -y

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
![Jenkins Unlock Screen](images/jenkins-unlock.png)
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
  ![Add Docker Hub Credentials Jenkins](images/jenkins-dockerhub-credentials.png) 

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
                    docker.build("${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest", ".")
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
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
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} << EOF
                            echo "--- Starting deployment on EC2 ---"

                            sudo systemctl start docker

                            if sudo docker ps -a | grep ${APP_NAME}-container; then
                                echo "Stopping existing container..."
                                sudo docker stop ${APP_NAME}-container
                                sudo docker rm ${APP_NAME}-container
                            fi

                            echo "${env.DOCKER_CREDENTIALS_PSW}" | sudo docker login --username ${env.DOCKER_CREDENTIALS_USR} --password-stdin

                            echo "Pulling latest Docker image: ${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest"
                            sudo docker pull ${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest

                            echo "Running new Docker container..."
                            sudo docker run -d --name ${APP_NAME}-container -p 5000:5000 ${env.DOCKER_CREDENTIALS_USR}/${APP_NAME}:latest

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
  ![Jenkins Job Configuration General](images/jenkins-job-config-general.png)
  ![Jenkins Job Configuration Pipeline](images/jenkins-job-config-pipeline.png)

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
   ![GitHub Webhook Configuration](images/github-webhook-config.png)

**Important:** Ensure your Jenkins EC2 instance's security group allows inbound traffic on port `8080` from `Anywhere` (0.0.0.0/0) for GitHub to reach it.

-----

### Step 9: Trigger the CI/CD Pipeline

**1. Manual Trigger (Initial Test):**

  * Go to your Jenkins dashboard.
  * Click on your `Flask-App-CI-CD` job.
  * Click **"Build Now"** in the left menu.
  * Monitor the build in the "Build History" panel (click on the build number, then "Console Output" to see logs).
    ![Jenkins Build History Success](images/jenkins-build-history.png)
    ![Jenkins Console Output Example](images/jenkins-console-output.png)

**2. Automatic Trigger (After Webhook Setup):**

  * Make a small change to your `app.py` locally.
  * Commit and push it to your GitHub `main` branch.
    ```bash
    # Trigger Jenkins build automatically via GitHub webhook
    from flask import Flask, render_template, request, redirect
    from textblob import TextBlob
    app = Flask(__name__)
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

You should see the updated Version
![Deployed Flask App Screenshot](images/deployed-flask-app.png)
-----
