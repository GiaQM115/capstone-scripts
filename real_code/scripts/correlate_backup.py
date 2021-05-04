"""
Creates the events utilizing the data from client_sock and then correlates and
determines a score on if the event should be alerted on
"""
import socket, json, traceback, re, os, errno, netaddr
from datetime import datetime
import datetime as dt
from multiprocessing import Process, Queue
from pymisp import ExpandedPyMISP, PyMISP, MISPEvent, MISPAttribute, MISPSighting, MISPTag

from send_emails import send_emails

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## DEFINITIONS ##

LOCAL_ORG = "MISP_ORG"
THRESHOLD = ALERT_THRESHOLD

# global misp object
misp_url = "https://MISP_FQDN"
misp_key = "MISP_AUTH_KEY"
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

def score(event, feed, local, tags, recent):
    """ Determines the score of the event and checks to see if it should
        be alerted

    Parameters
    ----------
    event: int
        Event ID that is being examined
    feed: int
        How many feed events are related to the current one being looked at
    local: int
        How many local events are related to the current one being looked at
    tags: dict
        Dictionary of tag names and descriptions
    recent: int
        How many recent events are related to current one being looked at
    Returns
    ----------
    score: int
        score that the event recieved
    """

    if local == 0 and feed > 0:
        print("Email alert")
        return 1
    elif local == 0:
        return 0
    global THRESHOLD
    score = feed + recent
    score /= local
    score *= 100
    if score > THRESHOLD:
        tag_list = []
        if len(tags) > 0:
            for tag in tags:
                tag_list.append(json.loads(tag)["name"])
        send_emails(event, tag_list)
    return score


def correlateEvent(event_id):
    """ Searches for related events to the one being examined and set tags based on
        relevent events 

    Parameters
    ----------
    event_id: int
        Int the can be used to search for the event
    Returns:
    ---------
    feedHits: int
        How many feed events are related to the current one being looked at
    localHits: int
        How many local events are related to the current one being looked at
    tags: dict
        Dictionary of tag names and descriptions
    recentHits: int
        How many recent events are related to the current one being looked at
    """

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
                recentHits += 1
            #print(datetime.date(int(date)))
            #print(datetime.date(int(date2)))
    # add each tag in this set to the MISPEvent
    for tag in tags:
        t = MISPTag()
        t.from_json(tag)
        misp.tag(origin, t)
    localHits = len(related) - feedHits
    return feedHits, localHits, tags, recentHits


def parse(data, event):
    """ Parses the information recieved from Security Onion to add attributes
        to an event

    Parameters
    ----------
    data: dict
        Dictionary of information sent from Security Onion
    event: int
        Int the can be used to search for the event
    Returns:
    ---------
    sighting: MISPSighting object
        Sighting of this event
    attr: MISPAttribute object
        Attribute added to the event
    """
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
                if elem == '0.0.0.0':
                    attr = addAttribute(event, t, elem, category, True, sighting)
                    attr = addAttribute(event, 'ip-dst', elem, category, True, sighting)
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
    """ Add attibute to an event

    Parameters
    ----------
    event: int
        Int the can be used to search for the event
    a_type: str
        type of attribute
    val: str
        The value to put in the attribute
    category: str
        The category to put the attirbute in
    cor: bool
        Determine if this attribute should be correlate on or not
    sighting: MISPSighting object
        Sighting of this event
    
    Returns:
    ---------
    attr: MISPAttribute object
        Attribute added to the event
    """

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
    """ Creates an event in MISP

    Parameters
    ----------
    data: dict
        Dictionary of information sent from Security Onion
    Returns:
    ---------
    e_id: int
        Int the can be used to search for the event
    """
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
    """ Checks to see if any data needs to be processed and then processes it

    Parameters
    ----------
    q: Queue
        Used to pass data from client_sock to this script
    Returns:
    ---------
    None
    """

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
                    feed, local, tags, recent = correlateEvent(e_id)
                    print(f"EVENT {e_id} ({feed} FEED HITS AND {local} LOCAL HITS)")
                    s = score(e_id, feed, local, tags, recent)
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
