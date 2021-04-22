#!/bin/bash
touch correlate.log
touch sock.log
python3 correlate.py > correlate.log&
python3 client_sock.py > sock.log&

bash schedule.sh

tail --follow correlate.log
