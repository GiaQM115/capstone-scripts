echo -n "What is your Fetch key? "
read api

sed -i "s/misp_key = .*$/misp_key = '$api'/" fetch.py

docker cp fetch.py comparison-server:/fetch.py
