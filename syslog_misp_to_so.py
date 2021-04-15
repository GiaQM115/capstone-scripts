from datetime import datetime 
import time
import logging
import logging.handlers
from logging.handlers import SysLogHandler
import socket
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

interval = 3600

#1
#connect to misp server using authkey of the api user
from pymisp import ExpandedPyMISP
misp_url = 'https://192.168.1.4'
misp_key = "wyBPpYHVs7FCemnRDs94MPu47YTiOx6ksglge7jx"
misp_verifycert = False
# Init misp connector 
print("Connecting to MISP server...")
misp = ExpandedPyMISP(misp_url, misp_key, misp_verifycert)


logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

handler = SysLogHandler(facility=SysLogHandler.LOG_DAEMON, address=('192.168.1.3', 514), socktype=socket.SOCK_DGRAM)
logger.addHandler(handler)
#logger.info("foo")
#logger.critical("This is a problem")

print(json.dumps(misp.search(timestamp=(time.time()-interval)),indent=2))
