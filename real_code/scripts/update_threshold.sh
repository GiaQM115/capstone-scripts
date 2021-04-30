echo -n "What would you like to set the threshold too? "
read threshold

sed -i "s/THRESHOLD = .*$/THRESHOLD = $threshold/" correlate.py

docker cp correlate.py comparison-server:/correlate.py
