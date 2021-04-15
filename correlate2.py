import socket, json, traceback, collections, re, os, errno, time, netaddr
from datetime import datetime
import datetime as dt
from multiprocessing import Process, Queue
from pymisp import ExpandedPyMISP, PyMISP, MISPEvent, MISPAttribute, MISPSighting, MISPTag

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## DEFINITIONS ##

LOCAL_ORG = "8615364b-47b0-4603-82bf-2d76a9fe2b2f"
THRESHOLD = 5
FEEDHITSMULTIPLIER = 3

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

def score(event, feed, local, tags):
    if local == 0 and feed > 0:
        print("Email alert")
        return 1
    elif local == 0:
        return 0
    global FEEDHITSMULTIPLIER
    global THRESHOLD
    score = feed * FEEDHITSMULTIPLIER
    score /= local
    if score > THRESHOLD:
        print("Email alert")
    return score


def correlateEvent(event_id):
    print(f"Correlating {event_id}")
    global misp
    result = misp.search(controller="events", eventid=event_id, metadata=True)
    origin = result[0]['Event']['uuid']
    date = datetime.fromtimestamp(int(result[0]['Event']['timestamp']))
    related = result[0]['Event']['RelatedEvent']
    feedHits = 0
    localHits = 0
    recentHits = 0
    tags = set()
    # parse all related events
    for event in related:
        if event['Event']['Orgc']['uuid'] != LOCAL_ORG:
            feedHits += 1
            # get any tags from the feed hits
            hit = misp.search(controller="events", eventid=event['Event']['id'], metadata=True)
            if 'Tag' in hit[0]['Event'].keys():
                for tag in hit[0]['Event']['Tag']:
                    tags.add(json.dumps(tag))
            date2 = datetime.fromtimestamp(int(hit[0]['Event']['timestamp']))
            if date - date2 < dt.timedelta(days=40):
                print("RECENT!!")
            #print(datetime.date(int(date)))
            #print(datetime.date(int(date2)))
    # add each tag in this set to the MISPEvent
    for tag in tags:
        t = MISPTag()
        t.from_json(tag)
        misp.tag(origin, t)
    localHits = len(related) - feedHits
    return feedHits, localHits, tags


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
                attr = addAttribute(event, t, elem, category, netaddr.IPAddress(elem).is_private(), sighting)
                attr = addAttribute(event, 'ip-dst', elem, category, netaddr.IPAddress(elem).is_private(), sighting)
            continue
        elif type(data[key]) == list and key == "eventTime":
            for elem in data[key]:
                attr = addAttribute(event, t, elem, category, True, sighting)
            continue
        if key == "host" and re.search(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', data[key]):
            attr = addAttribute(event, 'ip-src', data[key], category, True, sighting)
        elif key == "host" and re.search(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}', data[key]):
            attr = addAttribute(event, 'ip-src|port', data[key], category, True, sighting)
        elif key == "host" and data[key].find('.') == -1:
            attr = addAttribute(event, t, data[key] + ".local", category, True, sighting)
        else:
            attr = addAttribute(event, t, data[key], category, False, sighting)
    return sighting, attr

def addAttribute(event, a_type, val, category, cor, sighting):
    global misp
    attr = MISPAttribute()
    attr.type = a_type
    attr.value = val
    attr.to_ids = False
    attr.disable_correlation = cor
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
    return e_id

def qPop(q):
    while True:
        # ignore an empty queue
        if q.empty():
            continue
        # try to read from queue
        try:
            contents = q.get().split("|")
            for e in contents:
                if len(e) > 0:
                    e_id = createEvent(json.loads(e))
                    feed, local, tags = correlateEvent(e_id)
                    print(f"EVENT {e_id} ({feed} FEED HITS AND {local} LOCAL HITS)")
                    s = score(e_id, feed, local, tags)
                    print(f"SCORE {s}")
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
