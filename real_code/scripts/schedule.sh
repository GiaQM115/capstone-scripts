#!/bin/bash

crontab -l > cronlist > /dev/null
echo "0 * * * * bash watchdog.sh" >> cronlist
echo "0 0 * * * bash fetch.py" >> cronlist
crontab cronlist > /dev/null
rm cronlist
