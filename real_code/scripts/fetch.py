from pymisp import ExpandedPyMISP
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

misp_url = 'https://localhost'
misp_key = 'MISP_AUTH_KEY'
misp_verifycert = False
relative_path = 'feeds/fetchfromallfeeds'
body = {}

misp = ExpandedPyMISP(misp_url, misp_key, misp_verifycert)
misp.direct_call(relative_path, body)
