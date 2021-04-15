import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#1
#connect to misp server using authkey of the api user
from pymisp import ExpandedPyMISP
misp_url = 'https://192.168.1.4' 
misp_key = "wyBPpYHVs7FCemnRDs94MPu47YTiOx6ksglge7jx" 
misp_verifycert = False  
# Init misp connector 
print("Connecting to MISP server...")
misp = ExpandedPyMISP(misp_url, misp_key, misp_verifycert)
with open("events.log",'r') as log:
    for line in log.readlines():
        try:
            misp.delete_event(line)
            print(f"Event {line} deleted!")
        except:
            print(f"Failed to delete event: {line}")

with open("events.log", "w") as log:
    pass

