from driver_constants import *
import json
import socket
import sys
import time
import argparse
import random

def main(lane, location, velocity):

    try:
        sock = socket.create_connection(('localhost', 9000), 500)
    except:
        sys.exit(0)

    while True:
        # This is a bad way to synchronize the client and server. Come up with a
        # better way to delimit messages.
        # time.sleep(0.1)
        try:
            server_req = sock.recv(1024).decode('utf-8')

            if server_req == 'location':
                # Broadcast current status.
                sock.sendall(bytes(json.dumps((lane, location)), 'utf-8'))

            elif server_req == 'velocity':
                # Receive other broadcast messages.
                # Acknowledge velocity request
                sock.sendall('ready to receive'.encode('utf-8'))
                msg = json.loads(sock.recv(1024).decode('utf-8'))
                sv_list = json.loads(msg['sv_list'])

                velocity_share = velocity
                velocity_pred = velocity

                if velocity < MAX_VELOCITY:
                    velocity += 1

                # Calculate lead SV velocity
                if sv_list:
                    lead_sv = sv_list[-1]
                    velocity_share = max(min(lead_sv['space_ahead_lsv'] - 1,
                        lead_sv['vel_ahead_lsv'], MAX_VELOCITY - 1), 0)

                    for _ in range(len(sv_list)-1):
                        velocity_share = max(velocity_share - 1, 0)

                # Make prediction for car immediately in front of you
                if velocity > msg['space_ahead']:
                    velocity_pred = max(min(msg['space_one_ahead'] - 1,
                        msg['velocity_ahead'] - 1, MAX_VELOCITY-1), 0)

                # Set new velocity
                velocity = min(velocity, velocity_pred + msg['space_ahead'], velocity_share + msg['space_ahead'])

                # Decrease velocity probabilistically
                if velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
                    velocity = max(velocity - 1, 0)

            elif server_req == 'kill':
                    sock.sendall(bytes(json.dumps('client exiting'),'utf-8'))
                    sock.close()
                    sys.exit(1)

            else:
                sock.sendall(bytes(json.dumps({'velocity': velocity}), 'utf-8'))

        except:
            sys.exit(0)

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
