import socket, json, traceback, collections, re, os, errno
from multiprocessing import Process, Queue
from pymisp import ExpandedPyMISP, PyMISP, MISPEvent, MISPAttribute, MISPSighting

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## DEFINITIONS ##

LOCAL_ORG = '8615364b-47b0-4603-82bf-2d76a9fe2b2f'
THRESHOLD = 5

# global misp object
misp_url = 'https://192.168.1.4'
misp_key = "wyBPpYHVs7FCemnRDs94MPu47YTiOx6ksglge7jx"
misp = ExpandedPyMISP(misp_url, misp_key, False)

tag_dict = {
        'host': ['Network activity', 'hostname'],
        'ipport': ['Network activity', 'ip-src|port'],
        'ips': ['Network activity', 'ip-src', 'ip-dst'], 
        'eventTime': ['Other', 'datetime'], 
        'dip': ['Network activity', 'ip-dst'], 
        'sip': ['Network activity', 'ip-src'],
        'event': ['Other', 'comment'],
        'error': ['Other', 'comment']
        }

def correlateEvent(event_id):
    print(f"Correlating {event_id}")
    global misp
    result = misp.search(controller="events", event_id=event_id)
    print(json.dumps(result, indent=2))
    input("fuck me i guess")
    related = result['Event']['RelatedEvent']
    feedHits = 0
    localHits = 0
    for event in related:
        if event['Org']['uuid'] != LOCAL_ORG:
            feedHits += 1
    if feedHits > 0:
        localHits = len(related) - feedHits
    return feedHits, localHits


def parse(data, event):
    global tag_dict
    sighting = MISPSighting()
    sighting.id = event
    sighting.value = data['date']
    for key in data.keys():
        if key == "type":
            continue
        if key == "date":
            # sighting
            continue
        if key in tag_dict.keys():
            category = tag_dict[key][0]
            t = tag_dict[key][1]
        else:
            continue
        if type(data[key]) == list and key == "ips":
            for elem in data[key]:
                attr = addAttribute(event, t, elem, category, sighting)
                attr = addAttribute(event, 'ip-dst', elem, category, sighting)
            continue
        elif type(data[key]) == list and key == "eventTime":
            for elem in data[key]:
                attr = addAttribute(event, t, elem, category, sighting)
            continue
        if key == "host" and re.search(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', data[key]):
            attr = addAttribute(event, 'ip-src', data[key], category, sighting)
        elif key == "host" and re.search(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}', data[key]):
            attr = addAttribute(event, 'ip-src|port', data[key], category, sighting)
        elif key == "host" and data[key].find('.') == -1:
            attr = addAttribute(event, t, data[key] + ".local", category, sighting)
        else:
            attr = addAttribute(event, t, data[key], category, sighting)
    return sighting, attr

def addAttribute(event, a_type, val, category, sighting):
    global misp
    attr = MISPAttribute()
    attr.type = a_type
    attr.value = val
    attr.to_ids = False
   # print(event)
    try:
        aid = misp.add_attribute(event, attr)
        misp.add_sighting(sighting=sighting, attribute=attr)
    except:
        traceback.print_exc()
    return attr

def createEvent(data):
    global misp
    o = MISPEvent()
    o.distribution = 1
    o.threat_level_id = 4
    o.analysis = 1
    o.info = f"{data['type']} {data['date']}"
    e_id = misp.add_event(o)['Event']['id']
    # parse out fields
    with open('events.log', 'a') as log:
        log.write(f"{e_id}\n")
    s, attr = parse(data, e_id)
    print(f"{e_id} {attr} {s}")
    feeds, local = correlateEvent(e_id)
    print(f"EVENT: {e_id}; FEED HITS: {feeds}; LOCAL HITS: {local}\n\n")
    return e_id

def qPop(q):
    while True:
        if q.empty():
            continue
        try:
            contents = q.get().split("|")
            for e in contents:
                if len(e) > 0:
                    eid = createEvent(json.loads(e))
        except:
            traceback.print_exc()

## EXECUTION BEGINS ##

FIFO = 'PYPIPE'

# create and start queue
QUEUE = Queue()
qproc = Process(target=qPop, args=(QUEUE,))
qproc.daemon = True
qproc.start()

try:
    while True:
        if not os.path.isfile(FIFO):
            try:
                os.mkfifo(FIFO)
            except OSError as oe:
                if oe.errno == errno.EEXIST:
                    pass
                else:
                    print(oe.errno)
                    print("Exiting")
                    os.remove(FIFO)
                    continue
        with open(FIFO, 'r') as fifo:
            while True:
                data = fifo.read()
                if len(data) == 0:
                    break
                QUEUE.put(f"{data}|")
except KeyboardInterrupt:
    exit()
finally:
    qproc.join()
