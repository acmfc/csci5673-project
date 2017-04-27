from driver_constants import *
import json
import socket
import sys
import time
import argparse
import random

def main(lane, location, velocity):

    # if len(sys.argv) > 1:
    #     location = int(sys.argv[1])

    sock = socket.create_connection(('localhost', 8000), 500)
    init_req = sock.recv(1024).decode('utf-8')
    sock.sendall(bytes(json.dumps(
        {'lane': lane, 'location': location, 'velocity': velocity}), 'utf-8'))

    while True:
        # This is a bad way to synchronize the client and server. Come up with a
        # better way to delimit messages.
        # time.sleep(0.1)

        server_req = sock.recv(1024).decode('utf-8')

        if server_req == 'location':
            # Broadcast current status.
            sock.sendall(bytes(json.dumps((lane, location)), 'utf-8'))
        elif server_req == 'velocity':
            # Receive other broadcast messages.
            # Acknowledge velocity request
            sock.sendall('ready to receive'.encode('utf-8'))
            msg = json.loads(sock.recv(1024).decode('utf-8'))
            # print('space_ahead: {}, msgs: {}'.format(msg['space_ahead'], msg['msgs']))
            # Extended NS model
            if velocity < MAX_VELOCITY:
                velocity += 1
            if velocity > msg['space_ahead']:
                velocity_pred = max(min(msg['space_one_ahead'] - 1, 
                    msg['velocity_ahead'], MAX_VELOCITY-1), 0)
                print('velp: {}, velp+sa: {}, vel: {}'.format(velocity_pred, velocity_pred+msg['space_ahead'], velocity))
                velocity = min(velocity, velocity_pred + msg['space_ahead'])
            if velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
                velocity -= 1
        else:
            sock.sendall(bytes(json.dumps({'velocity': velocity}), 'utf-8'))

        location = (location + velocity) % ROAD_LENGTH

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lane', type=int, default=0)
    parser.add_argument('--loc', type=int, default=0)
    parser.add_argument('--vel', type=int, default=5)
    args = parser.parse_args()

    lane = args.lane
    location = args.loc
    velocity = args.vel

    main(lane, location, velocity)
