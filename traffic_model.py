import socket
import time
import argparse
import random

from driver_constants import *
from standard_vehicle import StandardVehicle
from solution_vehicle import SolutionVehicle


BROADCAST_RANGE = 15


class BroadcastHandler:
    def __int__(self, dictionary):
        self.solution_vehicle_socket_dict = dictionary

    def handle_broadcast(self, source_vehicle, command):
        to_notify = []

        for sv in self.solution_vehicle_socket_dict.keys():


            if sv != source_vehicle:

                # sv.notify()

                pass


def initialize_vehicles(listener, num_solution_v, traffic_density):
    total_vehicle_count = round(ROAD_LENGTH * traffic_density)

    solution_vehicle_socket_dict = {}
    solution_vehicles = []
    for i in range(num_solution_v):
        sock, _ = listener.accept()
        sv = SolutionVehicle(sock)

        solution_vehicles.append(sv)

        solution_vehicle_socket_dict[sv] = sock

    broadcast_handler = BroadcastHandler(solution_vehicle_socket_dict)

    for sv in solution_vehicles:
        sv.set_broadcast_handler(broadcast_handler)

    vehicles = []
    for i in range(total_vehicle_count - num_solution_v):
        vehicles.append(StandardVehicle(5))

    vehicles.extend(solution_vehicles)

    random.shuffle(vehicles)

    return vehicles, solution_vehicles


# TODO: use a sparse representation of a road, like a linked list of cars for each lane.
def initialize_road(vehicles):
    interval = round(ROAD_LENGTH / len(vehicles))

    road = []
    for _ in range(NUM_LANES):
        road.append([None] * ROAD_LENGTH)

    road_index = 0
    for vehicle in vehicles:
        vehicle.set_location(0, road_index)
        road_index += interval

    return road


# returns the number of free cells in front of the current location.
# if there are more than MAX_VELOCITY cells, returns MAX_VELOCITY
def space_ahead(road, lane, location):
    ret = 0
    def get_wrapped_location(offset):
        return (location + offset) % ROAD_LENGTH

    while (ret < MAX_VELOCITY and
            road[lane][get_wrapped_location(ret + 1)] is None):
        ret += 1

    return ret


# run one step in the Nagel-Schreckenberg model
def step(road, cars):
    for car in cars:
        car.update_velocity()

    for car in cars:
        lane = road[car.road_lane]
        lane[car.road_index % len(lane)] = None
        car.move()
        lane = road[car.road_lane]
        lane[car.road_index % len(lane)] = car
        car.vel_tracker.append(car.velocity)


def print_road(road, carnames):
    for lane in road:
        print(' '.join(
            carnames[car] if car is not None else '_' for car in lane))

    print('')


def main(run_time, traffic_density, num_solution_v):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('localhost', 8000))
    listener.listen()

    vehicle_list, solution_vehicles = initialize_vehicles(listener,
                                                          num_solution_v,
                                                          traffic_density)

    road = initialize_road(vehicle_list)

    # TODO: change id / name assignment
    ids = (chr(i) for i in range(ord('0'), ord('~')))
    carnames = {car: next(ids) for car in vehicle_list}

    print_road(road, carnames)

    step_count = 0
    while step_count <= run_time:
        time.sleep(1)

        # share broadcast messages with all other vehicles in range
        to_notify = {(car.road_lane, car.road_index): [] for car in vehicle_list}
        print('to_notify: {}'.format(to_notify))

        # start by collecting all messages that will be delivered to each solution vehicle.
        for sv in solution_vehicles:
            try:
                msg = sv.receive_msg('location')
                # print('DBG Received broadcast:{}'.format(msg))
                for offset in range(1, BROADCAST_RANGE + 1):
                    for offset in (offset, -offset):
                        for lane in range(NUM_LANES):
                            location = (sv.road_index * 2 + offset) % len(road[lane])
                            if road[lane][location] is not None:
                                to_notify[(lane, location)].append(msg)
            except ValueError:
                # remove the vehicle from car list and road
                index = vehicle_list.index(sv)
                vehicle_list.remove(sv)
                road[sv.road_lane][sv.road_index] = None

                # create non-solution vehicle and insert it in same pos as the old vehicle, with the same char id
                new_car = StandardVehicle(road, sv.road_lane, sv.road_index, sv.velocity, sv.vel_tracker)
                solution_vehicles.insert(index, new_car)
                carnames[new_car] = carnames[sv]
                solution_vehicles.remove(sv)

        # deliver all collected messages along with the amount of free space ahead
        for coords in to_notify:
            car = road[coords[0]][coords[1]]
            space = space_ahead(road, car.road_lane, car.road_index)
            
            # find the next vehicle ahead of the current
            location = (coords[1]+1) % ROAD_LENGTH
            while road[coords[0]][location] is None:
                location = (location + 1) % ROAD_LENGTH

            car_ahead = road[coords[0]][location]
            velocity_ahead = car_ahead.velocity
            space_one_ahead = space_ahead(road, car_ahead.road_lane, car_ahead.road_index)
            car.notify({'space_ahead': space, 'velocity_ahead': velocity_ahead, 
                'space_one_ahead': space_one_ahead, 'msgs': to_notify[coords]}, 'velocity')

        step(road, vehicle_list)
        step_count += 1
        print_road(road, carnames)

    total_distance = 0
    for car in vehicle_list:
        print("{}: {}".format(carnames[car], car.vel_tracker))
        total_distance += sum(car.vel_tracker)
    highway_mean_velocity = (total_distance / step_count) / len(vehicle_list)

    print("Average freeway velocity: {}".format(highway_mean_velocity))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=int, default=15)
    parser.add_argument('-t', type=float, required=True)
    parser.add_argument('-s', type=float, required=True)

    args = parser.parse_args()

    main(args.r, args.t, args.s)
