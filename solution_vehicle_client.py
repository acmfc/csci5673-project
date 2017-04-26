import json
import socket
import sys
import time
import argparse
import random
from threading import *


from driver_constants import *
from message import *


LOCK = Lock()


def send_data(sock, vehicle_data):
    sock.send(Message(CMD_INITIALIZE, vehicle_data))

    while True:
        time.sleep(0.1)

        data = json.dumps(vehicle_data)

        sock.send(Message(CMD_BROADCAST, vehicle_data))


def update_vehicle_data(vehicle_data, env_data):
    velocity = vehicle_data["velocity"]
    road_index = vehicle_data["road_index"]
    road_lane = vehicle_data["road_lane"]

    '''
    if velocity < MAX_VELOCITY:
        velocity += 1

    if velocity > msg['space_ahead']:
        velocity_pred = max(min(msg['space_one_ahead'] - 1,
                                msg['velocity_ahead'], MAX_VELOCITY - 1), 0)
        velocity = min(velocity, velocity_pred + msg['space_ahead'],
                       msg['space_ahead'])

    if velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
        velocity -= 1

    '''

    pass


def recv_data(sock, vehicle_data, env_data):
    global LOCK

    while True:
        data = sock.recv(1024)

        with LOCK:
            env_json = json.loads(data)

            for key in env_data.keys():
                if key not in env_json.keys():
                    del env_data[key]
                else:
                    env_data[key] = env_json[key]

            update_vehicle_data(vehicle_data, env_data)


def main(address, port):
    vehicle_data = {"road_index": -1,
                    "road_lane": -1,
                    "velocity": -1}

    env_data = {"env_data": {}}

    sock = socket.create_connection((address, port), 500)

    send_thread = Thread(target=send_data, args=(sock, vehicle_data))
    send_thread.daemon = True
    send_thread.start()

    recv_thread = Thread(target=recv_data, args=(sock, vehicle_data, env_data))
    recv_thread.daemon = True
    recv_thread.start()

    '''
    while True:
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
                velocity = min(velocity, velocity_pred + msg['space_ahead'],
                    msg['space_ahead'])
            if velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
                velocity -= 1
        else:
            sock.sendall(bytes(json.dumps({'velocity': velocity}), 'utf-8'))

        location = (location + velocity) % ROAD_LENGTH
    '''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, default="localhost")
    parser.add_argument('--port', type=int, required=True)

    args = parser.parse_args()

    main(args.address, args.port)
