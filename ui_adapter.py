import argparse
import json
import select
import socket
import sys

HOST = 'localhost'
PORT = 5050

def get_lane_number(parts):
    '''Returns the index of the lane represented by parts if parts is a valid
    lane or None otherwise.'''
    if len(parts) and parts[0][:4] == 'lane':
        return int(parts[0][4:])
    return None

def encode_lane(parts):
    road_length = len(parts)
    positions = {name: i for i,name in enumerate(parts) if name != '_'}
    return {'road_length': road_length, 'positions': positions}

# TODO deal with one line at a time.
def parse_traffic_model(traffic_model):
    '''Returns the parse of the first valid lane found.'''
    for line in traffic_model.split('\n'):
        parts = line.strip().split()
        laneidx = get_lane_number(parts)
        if laneidx is not None:
            return laneidx, encode_lane(parts[1:])
    return None, None

def get_avg_velocity_lane_number(parts):
    if len(parts) and parts[0][:3] == 'avg':
        return int(parts[0][3:])
    return None

def parse_avg_velocity(line):
    parts = line.strip().split()
    laneidx = get_avg_velocity_lane_number(parts)
    if laneidx is not None:
        return laneidx, float(parts[1])
    return None, None

def main(port):
    current_lane_descriptions = {}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        sources = [s, sys.stdin]
        while True:
            ready, _, _ = select.select(sources, [], [])
            for source in ready:
                if source == s:
                    conn, _ = s.accept()
                    conn.recv(4096)
                    conn.sendall(json.dumps(current_lane_descriptions).encode('utf-8'))
                elif source == sys.stdin:
                    line = sys.stdin.readline()
                    laneidx, lane = parse_traffic_model(line)
                    if laneidx is not None and lane is not None:
                        current_lane_descriptions[laneidx] = lane
                    else:
                        laneidx, avg_velocity = parse_avg_velocity(line)
                        if laneidx is not None and avg_velocity is not None:
                            current_lane_descriptions['avg' + str(laneidx)] = avg_velocity

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()
    main(args.port)

