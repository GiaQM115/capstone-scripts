#!/bin/bash

procs=$(ps aux)

if [[ ${procs} != *"correlate.py"* ]]; then
	echo "WATCHDOG RESTARTING SCRIPT" >> watchdog.log
	python3 correlate.py > correlate.log&
fi

if [[ ${procs} != *"client_sock.py"* ]]; then
	echo "WATCHDOG RESTARTING SCRIPT" >> watchdog.log
	python3 client_sock.py > sock.log&
fi
