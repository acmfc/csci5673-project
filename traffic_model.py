import random
import time

NUM_LANES = 2
ROAD_LENGTH = 40
MAX_VELOCITY = 5
PROBABILITY_DECELERATE = 0.1

def make_road(num_lanes, length):
    '''Returns a 2d array representing a road with num_lanes lanes and length
    cells in each lane.'''
    # TODO Use a sparse representation of a road, like a linked list of cars
    # for each lane.
    return [[None for _ in range(length)] for _ in range(num_lanes)]

class RoadView():
    '''Represents a line-of-sight view from an initial location in the road. This
    is the information a vehicle would be able to gain without any network
    connection.'''

    def __init__(self, road, location, max_distance):
        self.road = road
        self.location = location
        self.max_distance = max_distance

    def get(self, lane, location_offset):
        if abs(location_offset) > self.max_distance:
            raise ValueError('Requested location not visible')

        location = (self.location + location_offset) % len(self.road[0])
        return self.road[lane][location]

class Car():
    def __init__(self, road, lane, location, velocity):
        if road[lane][location] is not None:
            raise ValueError('Requested location is already occupied')

        self.lane = lane
        self.location = location
        self.velocity = velocity
        self.view = RoadView(road, location, MAX_VELOCITY)

        road[lane][location] = self

    def accelerate(self):
        if self.velocity < MAX_VELOCITY:
            self.velocity += 1

    def decelerate(self):
        space_in_front = 0
        while (space_in_front < MAX_VELOCITY and
                self.view.get(self.lane, space_in_front + 1) is None):
            space_in_front += 1
        if space_in_front < self.velocity:
            self.velocity = space_in_front

    def randomize(self):
        if self.velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
            self.velocity -= 1

    def move(self):
        self.location += self.velocity
        self.view.location += self.velocity

def step(road, cars):
    '''Run one step in the Nagel-Schreckenberg model.'''
    # In an NS automaton, each operation happens on every object before moving
    # on to the next operation. In this case, accelerate, decelerate, and
    # randomize can be done together for every car because none of them depends
    # on any other.
    for car in cars:
        car.accelerate()
        car.decelerate()
        car.randomize()
    for car in cars:
        lane = road[car.lane]
        lane[car.location % len(lane)] = None
        car.move()
        lane = road[car.lane]
        lane[car.location % len(lane)] = car

def print_road(road, carnames):
    for lane in road:
        print(' '.join(
            carnames[car] if car is not None else '_' for car in lane))
    print()

def main():
    road = make_road(NUM_LANES, ROAD_LENGTH)
    cars = [Car(road, 0, i, 5) for i in range(0, ROAD_LENGTH, 5)]
    cars.append(Car(road, 1, 0, 5))

    ids = (chr(i) for i in range(ord('0'), ord('~')))
    carnames = {car: next(ids) for car in cars}

    print_road(road, carnames)

    while True:
        time.sleep(1)
        step(road, cars)
        print_road(road, carnames)

if __name__ == '__main__':
    main()
