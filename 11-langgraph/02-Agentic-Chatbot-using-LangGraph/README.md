# Agentic-Chatbot-APP-CICD-Deployment-with-Github-Actions-on-AWS

### Description: About the deployment

	1. Build docker image of the source code

	2. Push your docker image to docker hub

	3. Launch Your EC2 

	4. Pull Your image from docker hub in EC2

	5. Lauch your docker image in EC2

## 1. Login to AWS console.

## 2. Create IAM user for deployment

	#Policy:

	1. AmazonEC2FullAccess

	

## 3. Create EC2 machine (Ubuntu) 

## 4. Open EC2 and Install docker in EC2 Machine:
	
	
	#optinal

	sudo apt-get update -y

	sudo apt-get upgrade
	
	#Install Docker

	curl -fsSL https://get.docker.com -o get-docker.sh

	sudo sh get-docker.sh

	sudo usermod -aG docker ubuntu

	newgrp docker


### Note: Do the port mapping to this port:- 8501
	
# 5. Configure EC2 as self-hosted runner:

    setting>actions>runner>new self hosted runner> choose os> then run command one by one






# 6. How to add secret keys to GitHub Actions:


REGISTRY=docker.io

DOCKER_USERNAME=your-dockerhub-username

DOCKER_PASSWORD=your-dockerhub-access-token

IMAGE_NAME=agentic-chatbot

AWS_ACCESS_KEY_ID=your-aws-access-key

AWS_SECRET_ACCESS_KEY=your-aws-secret-key

AWS_REGION=us-east-1

OPENAI_API_KEY=your-openai-api-key

TAVILY_API_KEY=your-tavily-api-key

OPENWEATHER_API_KEY=your-openweather-api-key

GOOGLE_API_KEY=your-google-api-key

LANGSMITH_TRACING=true

LANGSMITH_ENDPOINT=https://api.smith.langchain.com

LANGSMITH_API_KEY=your-langsmith-api-key

LANGSMITH_PROJECT=agentic-chatbot-project