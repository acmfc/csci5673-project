from driver_constants import *

import argparse
import json
import random
import random
import socket
import time

# NUM_SOLUTION_VEHICLES = 0
BROADCAST_RANGE = 15 # The range of broadcast messages in cells.

def make_road(num_lanes, length):
    '''Returns a 2d array representing a road with num_lanes lanes and length
    cells in each lane.'''
    # TODO Use a sparse representation of a road, like a linked list of cars
    # for each lane.
    return [[None for _ in range(length)] for _ in range(num_lanes)]

def space_ahead(road, lane, location):
    '''Returns the number of free cells in front of the current location.
    If there are more than MAX_VELOCITY cells, returns MAX_VELOCITY.'''
    ret = 0
    def get_wrapped_location(offset):
        return (location + offset) % ROAD_LENGTH

    while (ret < MAX_VELOCITY and
            road[lane][get_wrapped_location(ret + 1)] is None):
        ret += 1

    return ret

class Car():
    def __init__(self, road, lane, location, velocity, vel_tracker=None):
        if road[lane][location] is not None:
            raise ValueError('Requested location is already occupied')

        self.lane = lane
        self.location = location
        self.velocity = velocity
        self.road = road
        if vel_tracker is None:
            self.vel_tracker = []
        else:
            self.vel_tracker = vel_tracker

        road[lane][location] = self

    def update_velocity(self):
        self.accelerate()
        self.decelerate()
        self.randomize()

    def accelerate(self):
        if self.velocity < MAX_VELOCITY:
            self.velocity += 1

    def decelerate(self):
        space = space_ahead(self.road, self.lane, self.location)
        if space < self.velocity:
            self.velocity = space

    def randomize(self):
        if self.velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
            self.velocity -= 1

    def move(self):
        self.location = (self.location + self.velocity) % ROAD_LENGTH

    def notify(self, msg, command):
        '''Deliver a broadcast message. Non-solution vehicles can ignore
        these.'''
        pass

class PseudoSolutionCar(Car):
    def randomize(self):
        if self.velocity >= 1 and random.uniform(0, 1) < 0.16:
            self.velocity -= 1

def step(road, cars):
    '''Run one step in the Nagel-Schreckenberg model.'''
    for car in cars:
        car.update_velocity()
    for car in cars:
        lane = road[car.lane]
        lane[car.location % len(lane)] = None
        car.move()
        lane = road[car.lane]
        lane[car.location % len(lane)] = car
        car.vel_tracker.append(car.velocity)

def print_road(road, carnames):
    for i,lane in enumerate(road):
        print('lane{} '.format(i) + ' '.join(
            carnames[car] if car is not None else '_' for car in lane))
    print('')

class SolutionVehicle():
    '''Interface for networked solution vehicles.'''

    def __init__(self, socket, road):
        self.socket = socket

        msg = self.receive_msg('init')
        self.lane = msg['lane']
        self.location = msg['location']
        self.velocity = msg['velocity']
        self.vel_tracker = []

        if road[self.lane][self.location] is not None:
            raise ValueError('Requested location is already occupied')

        road[self.lane][self.location] = self
        self.road = road

    def receive_msg(self, command):
        # TODO Ensure the entire message was received.
        try:
            if command is not 'pass':
                self.socket.sendall(command.encode('utf-8'))

            msg = self.socket.recv(1024)
            return json.loads(msg.decode('utf-8'))
        except ConnectionResetError:
            print('Lost connection to SV at {}'.format(self.socket))

    def notify(self, msg, command):
        '''Delivers a broadcast message that the solution would have received -
        one that was sent by another vehicle in range.'''
        try:
            self.socket.sendall(command.encode('utf-8'))
            if command is 'velocity':
                self.socket.recv(1024).decode('utf-8')
                self.socket.sendall(bytes(json.dumps(msg), 'utf-8'))
        except ConnectionResetError:
            print('Lost connection to SV at {}'.format(self.socket))

    def update_velocity(self):
        msg = self.receive_msg('rec_vel')
        self.velocity = msg['velocity']

    def move(self):
        self.location = (self.location + self.velocity) % ROAD_LENGTH


def main(run_time):
    road = make_road(NUM_LANES, ROAD_LENGTH)

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('localhost', 8000))
    listener.listen()

    solution_vehicles = []
    for _ in range(NUM_SOLUTION_VEHICLES):
        sock, _ = listener.accept()
        solution_vehicles.append(SolutionVehicle(sock, road))


    car_count = round(ROAD_LENGTH * DENSITY)
    interval = round(ROAD_LENGTH / car_count)
    cars = [Car(road, 0, i, 5) for i in 
                range(NUM_SOLUTION_VEHICLES * interval, ROAD_LENGTH, interval)]
    # cars.append(Car(road, 1, 0, 5))
    cars.extend(solution_vehicles)

    cars.extend([PseudoSolutionCar(road, 1, i, 5) for i in
        range(NUM_SOLUTION_VEHICLES * interval, ROAD_LENGTH, interval)])

    #ids = (chr(i) for i in range(ord('0'), ord('~')))
    ids = (str(i) for i in range(ROAD_LENGTH))
    carnames = {car: next(ids) for car in cars}

    print_road(road, carnames)

    step_count = 0

    while step_count <= run_time:
        time.sleep(1)

        # Share broadcast messages with all other vehicles in range.

        to_notify = {(car.lane, car.location): [] for car in cars}
        print('to_notify: {}'.format(to_notify))
        # Start by collecting all messages that will be delivered to each
        # solution vehicle.
        for sv in solution_vehicles:
            try:
                msg = sv.receive_msg('location')
                # print('DBG Received broadcast:{}'.format(msg))
                for offset in range(1, BROADCAST_RANGE + 1):
                    for offset in (offset, -offset):
                        for lane in range(NUM_LANES):
                            location = (sv.location * 2 + offset) % len(road[lane])
                            if road[lane][location] is not None:
                                to_notify[(lane, location)].append(msg)
            except ValueError:
                # Remove the vehicle from car list and road
                index = cars.index(sv)
                cars.remove(sv)
                road[sv.lane][sv.location] = None

                # Create non-solution vehicle and insert it in same pos as
                # the old vehicle, with the same char id
                new_car = Car(road, sv.lane, sv.location, sv.velocity, sv.vel_tracker)
                cars.insert(index, new_car)
                carnames[new_car] = carnames[sv]
                solution_vehicles.remove(sv)

        # Deliver all collected messages along with the amount of free space
        # ahead.
        for coords in to_notify:
            car = road[coords[0]][coords[1]]
            space = space_ahead(road, car.lane, car.location)
            
            # Find the next vehicle ahead of the current
            location = (coords[1]+1) % ROAD_LENGTH
            while road[coords[0]][location] is None:
                location = (location + 1) % ROAD_LENGTH

            car_ahead = road[coords[0]][location]
            velocity_ahead = car_ahead.velocity
            space_one_ahead = space_ahead(road, car_ahead.lane, car_ahead.location)
            car.notify({'space_ahead': space, 'velocity_ahead': velocity_ahead, 
                'space_one_ahead': space_one_ahead, 'msgs': to_notify[coords]}, 'velocity')

        step(road, cars)
        step_count += 1
        print_road(road, carnames)
        for i in range(NUM_LANES):
            cars_in_lane = [car for car in cars if car.lane == i]
            total_distance = sum(sum(car.vel_tracker) for car in cars_in_lane)
            print('avg{} {}'.format(i, (total_distance / step_count) / len(cars_in_lane)))

    total_distance = 0
    for car in cars:
        print("{}: {}".format(carnames[car], car.vel_tracker))
        total_distance += sum(car.vel_tracker)
    highway_mean_velocity = (total_distance / step_count) / len(cars)

    print("Average freeway velocity: {}".format(highway_mean_velocity))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=int, default=15)
    parser.add_argument('--sv', type=int, default=0)
    args = parser.parse_args()

    run_time = args.run
    NUM_SOLUTION_VEHICLES = args.sv

    main(run_time)
