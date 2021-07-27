#!/bin/sh

# Install Docker Engine: https://docs.docker.com/engine/install/ubuntu/
# Install Docker Compose: https://docs.docker.com/compose/install/

echo '---> Updating the apt package index and install packages to allow apt to use a repository over HTTPS'
sudo apt-get update  # To get the latest package lists
sudo apt-get install -y  \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

echo '---> Adding Dockers official GPG key'
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

echo '---> Verifying the fingerprint key'
sudo apt-key fingerprint 0EBFCD88

echo '---> Setting up the stable repository'
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

echo '---> Updating and Installing Docker Engine'
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo '---> Verifying Docker Engine is installed correctly'
sudo docker run hello-world

echo '---> Using Docker as a non-root user'
sudo usermod -aG docker $1

echo '---> Downloading current stable release of Docker Compose'
sudo curl -L "https://github.com/docker/compose/releases/download/1.28.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

echo '---> Applying executable permissions to the binary'
sudo chmod +x /usr/local/bin/docker-compose

echo '---> Creating a symbolic link'
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

echo '---> Verifying the installation'
docker-compose --version

echo '---> DONE !!!'
