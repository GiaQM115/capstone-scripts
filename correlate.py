import socket, json, traceback, collections, re, os, errno, time
from multiprocessing import Process, Queue
from pymisp import ExpandedPyMISP, PyMISP, MISPEvent, MISPAttribute, MISPSighting

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## DEFINITIONS ##

LOCAL_ORG = "8615364b-47b0-4603-82bf-2d76a9fe2b2f"
THRESHOLD = 5

# global misp object
misp_url = 'https://192.168.1.4'
misp_key = "wyBPpYHVs7FCemnRDs94MPu47YTiOx6ksglge7jx"
misp = ExpandedPyMISP(misp_url, misp_key, False)

def correlateEvent(event_id):
    print(f"Correlating {event_id}")
    global misp
    result = misp.search(controller="events", eventid=event_id, metadata=True)
    related = result[0]['Event']['RelatedEvent']
    print(json.dumps(related, indent=2))
    feedHits = 0
    localHits = 0
    for event in related:
        if event['Event']['Orgc']['uuid'] != LOCAL_ORG:
            feedHits += 1
    if feedHits > 0:
        localHits = len(related) - feedHits
    return feedHits, localHits


def qPop(q):
    while True:
        if q.empty():
            continue
        try:
            contents = q.get().split("|")
            for event in contents:
                if len(event) > 0:
                    event = event.rstrip()
                    feed, local = correlateEvent(event)
                print(f"EVENT: {event} || FEED HITS: {feed} || LOCAL HITS: {local}")
        except:
            traceback.print_exc()

## EXECUTION BEGINS ##

FIFO = 'MISPPIPE'

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
