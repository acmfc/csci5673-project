import argparse
import json
import sys

def is_lane(parts, num_empty_spots):
    '''Returns True if parts represents a lane with num_empty_spots empty
    spots.'''
    return parts.count('_') == num_empty_spots

def encode_lane(parts):
    road_length = len(parts)
    positions = {name: i for i,name in enumerate(parts) if name != '_'}
    return json.dumps({'road_length': road_length, 'positions': positions})

def parse_traffic_model(traffic_model, num_cars):
    '''Returns the parse of the first valid lane found.'''
    for line in traffic_model.split('\n'):
        parts = line.strip().split()
        if is_lane(parts, len(parts) - num_cars):
            return encode_lane(parts)
    return None

def main(num_cars, filename):
    while True:
        parsed = parse_traffic_model(sys.stdin.readline(), num_cars)
        if parsed:
            with open(filename, 'w') as f:
                f.write(parsed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_cars', type=int, default=0)
    parser.add_argument('--out_file', type=str, default='lane_state')
    # num_cars is only used to select the proper lane when multiple are read
    # over stdin. This program will check for any lanes with the proper number
    # of cars and serve the last lane seen over a socket. This only really
    # works if there's only one lane with the right number of cars.
    # TODO use more sophisticated way to figure out which lane we're interested
    # in.
    args = parser.parse_args()
    main(args.num_cars, args.out_file)

