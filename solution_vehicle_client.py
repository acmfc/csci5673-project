from driver_constants import *
import json
import socket
import sys
import time
import argparse

def main(lane, location, velocity):

    # if len(sys.argv) > 1:
    #     location = int(sys.argv[1])

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--lane', type=int, default=0)
    parser.add_argument('--loc', type=int, default=0)
    parser.add_argument('--vel', type=int, default=0)
    args = parser.parse_args()

    lane = args.lane
    location = args.loc
    velocity = args.vel

    main(lane, location, velocity)
