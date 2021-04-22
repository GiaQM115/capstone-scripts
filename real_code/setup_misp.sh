#!/bin/bash

printf "Please make sure you are running with root privileges\n"

printf "Updating apt\n"
apt update

printf "Checking for git\n"
apt install git

printf "Fetching Docker dependencies\n"
apt install apt-transport-https ca-certificates curl software-properties-common lsb-release

printf "Adding Docker GPG key\n"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

printf "Setting up repository\n"
apt-add-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

printf "Updating apt (again)\n"
apt update

printf "Installing Docker\n"
apt install docker-ce
systemctl enable docker
systemctl start docker

printf "Removing old containers and directories\n"
rm -rf docker-misp
docker stop MISP
docker rm MISP
docker stop comparison-server
docker rm comparison-server
docker stop user-manager
docker rm user-manager
docker rmi harvarditsecurity/misp
docker rmi mattrayner/lamp

printf "Fetching MISP instance\n"
git clone https://github.com/harvard-itsecurity/docker-misp.git

echo -n "Set your MYSQL password:  "
read mysql

echo -n "Set your GPG password: "
read gpg

echo -n "Set the FQDN for your MISP instance: "
read fqdn

echo -n "Set your postfix relay, or press Enter for default (localhost): "
read postfix

echo -n "Set your MISP admin email, or press Enter for default (admin@localhost): "
read email

printf "Updating build files\n"
sed -i "s/MYSQL_MISP_PASSWORD=.*\\\/MYSQL_MISP_PASSWORD=$mysql \\\/" docker-misp/build.sh 
sed -i "s/MISP_GPG_PASSWORD=.*\\\/MISP_GPG_PASSWORD=$gpg \\\/" docker-misp/build.sh 
sed -i "s/MISP_FQDN=.*\\\/MISP_FQDN=$fqdn \\\/" docker-misp/build.sh 
if [ ! -z "${postfix}" ]; then
	sed -i "s/POSTFIX_RELAY_HOST=.*\\\/POSTFIX_RELAY_HOST=$postfix \\\/" docker-misp/build.sh 
fi
if [ ! -z "${email}" ]; then
	sed -i "s/MISP_EMAIL=.*\\\/MISP_EMAIL=$email \\\/" docker-misp/build.sh 
else
	email='admin@localhost'
fi

printf "Building MISP instance\n"
cd docker-misp
bash build.sh

printf "Creating DB directory at /etc/docker/misp-db\n"
mkdir -p /etc/docker/misp-db

printf "Starting MISP instance\n"
docker run -d --rm -v /etc/docker/misp-db:/var/lib/mysql harvarditsecurity/misp /init-db
docker run --name=MISP -d -p 443:443 -p 80:80 -p 3306:3306 -p 6666:6666 -v /etc/docker/misp-db:/var/lib/mysql harvarditsecurity/misp

printf "Server will be up momentarily. Please go to https://$fqdn and login with '$email', PW: 'admin'\n"

cd ../

echo -n "Server Listening Port: "
read port

echo -n "MSIP Org ID: "
read mid

echo -n "MISP auth key: "
read key

echo -n "Initial threshold (this can be tuned later): "
read threshold


cd scripts
cp client_sock_backup client_sock.py
cp correlate_backup correlate.py
cp fetch_backup fetch.py

printf "Preparing scripts"

sed -i "s/MISP_SERVER_PORT/$port/" client_sock.py

sed -i "s/MISP_ORG/$mid/" correlate.py
sed -i "s/ALERT_THRESHOLD/$threshold/" correlate.py
sed -i "s/MISP_FQDN/$fqdn/" correlate.py
sed -i "s/MISP_AUTH_KEY/$key/" correlate.py

sed -i "s/MISP_FQDN/$fqdn/" fetch.py
sed -i "s/MISP_AUTH_KEY/$key" fetch.py

printf "Building Docker image\n"
docker build -t correlation-base .
printf "Running container\n"
docker run --name=comparison-server -d -p $port:$port correlation-base
cd ../

mkdir -p user_manager/mysql

echo -n "User Manager MySQL admin password: "
read umpass

cd user_manager
cp site/config_template site/config.php
sed -i "s/MYSQL_ADMIN_PASS/$umpass/" site/config.php

printf "Starting user manager\n"
docker build -t usermgt .
docker run --name=user-manager -d \
	-p 3000:3306 -p 8080:80 \
	-e MYSQL_ADMIN_PASS="$umpass" \
	usermgt
cd ../

printf "Waiting for database initializing to return\n"
output=`docker logs user-manager 2>&1`
while [[ ${output} != *"mysqld entered RUNNING state, process has stayed up for > than 1 seconds"* ]]
do
	output=`docker logs user-manager 2>&1`
done

sleep 2

printf "Sourcing database\n"
$(docker exec user-manager mysql -uadmin -p$umpass -e 'source db.sql')

docker ps
