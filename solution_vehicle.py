import json
import socket

from driver_constants import *


class SolutionVehicle():
    '''Interface for networked solution vehicles.'''

    def __init__(self, socket, road):
        self.socket = socket

        msg = self.receive_msg('init')
        self.road_lane = msg['lane']
        self.road_index = msg['location']
        self.velocity = msg['velocity']
        self.vel_tracker = []

        if road[self.road_lane][self.road_index] is not None:
            raise ValueError('Requested location is already occupied')

        road[self.road_lane][self.road_index] = self
        self.road = road

    def set_location(self, road_lane, road_index):
        self.road_lane = road_lane
        self.road_index = road_index

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
        self.road_index = (self.road_index + self.velocity) % ROAD_LENGTH