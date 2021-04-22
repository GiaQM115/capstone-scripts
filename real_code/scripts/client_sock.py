import socket, json, traceback, collections, re, time

## DEFINITIONS ##
PORT = 12345

def recvData():
    data = ""
    type_ = ""
    global tasks
    while data != "complete":
        data = clientsocket.recv(4096).decode()
        if data[0:4] == 'TYPE':
            type_ = data[6::]
        if data:
            if data != "complete" and data[0:4] != "TYPE" and data != "done" and len(data) > 0:
                try: 
                    tasks.append((json.loads(data), type_))
                except json.decoder.JSONDecodeError:
                    pass
            clientsocket.send("ok".encode())
    return


## EXECUTION BEGINS ##

# create data socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', PORT))
server.listen()

FIFO = "PYPIPE"

try:
    while True:
        tasks = list()
        print("Waiting for connection")
        (clientsocket, address) = server.accept()
        print("Connected!")
        if clientsocket.fileno() != -1:
            recvData()
            print("Complete received")
            clientsocket.send("done".encode())
            clientsocket.close
            print("Socket closed")
            print(f"I have {len(tasks)} tasks to complete")
            for task in tasks:
                try:
                    with open(FIFO, 'w') as fifo:
                        fifo.write(f"{json.dumps(task[0])}|")
                except:
                    traceback.print_exc()
                    break
except KeyboardInterrupt:
    server.close()
