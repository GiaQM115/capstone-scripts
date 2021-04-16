#!/bin/bash

echo "Please make sure you are running with root privileges"

<<COMMENT
echo "Updating apt"
apt update

echo "Checking for git"
apt install git

echo "Fetching MISP instance"
git clone https://github.com/harvard-itsecurity/docker-misp.git
cd docker-misp

echo -n "Set your MYSQL password:  "
read mysql

echo -n "Set your GPG password: "
read gpg
COMMENT
echo -n "Set the FQDN for your MISP instance: "
read fqdn
<<COMMENT
echo -n "Set your postfix relay, or press Enter for default (localhost): "
read postfix

echo -n "Set your MISP admin email, or press Enter for default (admin@localhost): "
read email

echo "Updating build files"
sed -i "s/MYSQL_MISP_PASSWORD=.*\\/MYSQL_MISP_PASSWORD=$mysql\\/" build.sh 
sed -i "s/MISP_GPG_PASSWORD=.*\\/MISP_GPG_PASSWORD=$gpg\\/" build.sh 
sed -i "s/MISP_FQDN=.*\\/MISP_FQDN=$fqdn\\/" build.sh 
if [ ! -z "${postfix}" ]; then
	sed -i "s/POSTFIX_RELAY_HOST=.*\\/POSTFIX_RELAY_HOST=$postfix\\/" build.sh 
fi
if [ ! -z "${email}" ]; then
	sed -i "s/MISP_EMAIL=.*\\/MISP_MAIL=$email\\/" build.sh 
fi

echo "Building MISP instance"
bash build.sh

echo "Starting MISP instance"
docker run -it --rm -v /docker/misp-db:/var/lib/mysql harvditsecurity/misp /init-db
docker run -it -p 443:443 -p 80:80 -p 3306:3306 -p 6666:6666 -v /docker/misp-db:/var/lib/mysql harvarditsecurity/misp

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
echo -n "Running container"
docker ps
