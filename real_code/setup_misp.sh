#!/bin/bash

echo "Please make sure you are running with root privileges"

echo "Updating apt"
apt update

echo "Checking for git"
apt install git

echo "Checking for Docker"
apt install docker

echo "Fetching MISP instance"
git clone https://github.com/harvard-itsecurity/docker-misp.git
cd docker-misp

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

echo "Updating build files"
sed -i "s/MYSQL_MISP_PASSWORD=.*\\\/MYSQL_MISP_PASSWORD=$mysql \\\/" docker-misp/build.sh 
sed -i "s/MISP_GPG_PASSWORD=.*\\\/MISP_GPG_PASSWORD=$gpg \\\/" docker-misp/build.sh 
sed -i "s/MISP_FQDN=.*\\\/MISP_FQDN=$fqdn \\\/" docker-misp/build.sh 
if [ ! -z "${postfix}" ]; then
	sed -i "s/POSTFIX_RELAY_HOST=.*\\\/POSTFIX_RELAY_HOST=$postfix \\\/" docker-misp/build.sh 
fi
if [ ! -z "${email}" ]; then
	sed -i "s/MISP_EMAIL=.*\\\/MISP_MAIL=$email \\\/" docker-misp/build.sh 
else
	email='admin@admin.test'
fi

echo "Building MISP instance"
cat build.sh
bash build.sh

echo "Starting MISP instance"
docker run -it --rm -v /docker/misp-db:/var/lib/mysql harvditsecurity/misp /init-db
docker run --name=MISP -it -p 443:443 -p 80:80 -p 3306:3306 -p 6666:6666 -v /docker/misp-db:/var/lib/mysql harvarditsecurity/misp

echo "Server will be up momentarily. Please go to https://$fqdn and login with "
COMMENT
echo -n "Server Listening Port: "
read port

echo -n "MSIP Org ID: "
read mid

echo -n "MISP auth key: "
read key

echo -n "Initial threshold (this can be tuned later): "
read threshold

dir=`pwd`

cp $dir/client_sock_backup client_sock.py
cp $dir/correlate_backup correlate.py

echo "Preparing scripts"

sed -i "s/MISP_SERVER_PORT/$port/" client_sock.py
sed -i "s/MISP_ORG/$mid/" correlate.py
sed -i "s/ALERT_THRESHOLD/$threshold/" correlate.py
sed -i "s/MISP_FQDN/$fqdn/" correlate.py
sed -i "s/MISP_AUTH_KEY/$key/" correlate.py

echo -n "Scheduling watchdog"

crontab -l > cronlist > /dev/null
echo "0 * * * * bash $dir/watchdog.sh" >> cronlist
crontab cronlist > /dev/null
rm cronlist

echo -n "Building Docker image"
docker build -t correlation-base .
echo -n "Running container"
docker run --name=comparison-server -d -p $port:$port correlation-base
docker ps
