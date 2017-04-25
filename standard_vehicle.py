import random

from driver_constants import *


class StandardVehicle():
    def __init__(self, road, lane, location, velocity, vel_tracker=None):
        if road[lane][location] is not None:
            raise ValueError('Requested location is already occupied')

        self.road_lane = lane
        self.road_index = location
        self.velocity = velocity
        self.road = road
        if vel_tracker is None:
            self.vel_tracker = []
        else:
            self.vel_tracker = vel_tracker

        road[lane][location] = self

    def set_location(self, road_lane, road_index):
        self.road_lane = road_lane
        self.road_index = road_index

    def update_velocity(self):
        self.accelerate()
        self.decelerate()
        self.randomize()

    def accelerate(self):
        if self.velocity < MAX_VELOCITY:
            self.velocity += 1

    def decelerate(self):
        space = self.space_ahead(self.road, self.road_lane, self.road_index)
        if space < self.velocity:
            self.velocity = space

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

    def randomize(self):
        if self.velocity >= 1 and random.uniform(0, 1) < PROBABILITY_DECELERATE:
            self.velocity -= 1

    def move(self):
        self.road_index = (self.road_index + self.velocity) % ROAD_LENGTH

    def notify(self, msg, command):
        '''Deliver a broadcast message. Non-solution vehicles can ignore
        these.'''
        pass