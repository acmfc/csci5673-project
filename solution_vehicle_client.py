from driver_constants import *
import json
import socket
import sys
import time

def main():
    # TODO Parse command line options to get an initial state.
    lane = 0
    location = 0
    velocity = 0

    if len(sys.argv) > 1:
        location = int(sys.argv[1])

    sock = socket.create_connection(('localhost', 8080), 500)
    sock.sendall(bytes(json.dumps(
        {'lane': lane, 'location': location, 'velocity': velocity}), 'utf-8'))

    while True:
        # This is a bad way to synchronize the client and server. Come up with a
        # better way to delimit messages.
        time.sleep(0.2)

        # Broadcast current status.
        sock.sendall(bytes(json.dumps((lane, location)), 'utf-8'))

        # Receive other broadcast messages.
        msg = json.loads(sock.recv(1024).decode('utf-8'))
        print('space_ahead: {}, msgs: {}'.format(msg['space_ahead'], msg['msgs']))

        if velocity < MAX_VELOCITY:
            velocity += 1

        if msg['space_ahead'] < velocity:
            velocity = msg['space_ahead']

        sock.sendall(bytes(json.dumps({'velocity': velocity}), 'utf-8'))
        location = (location + velocity) % ROAD_LENGTH

if __name__ == '__main__':
    main()
