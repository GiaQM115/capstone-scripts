echo -n "What is your API key? "
read api

sed -i "s/misp_key = .*$/misp_key = '$api'/" correlate.py

docker cp correlate.py comparison-server:/correlate.py
