import json
import socket
import threading

from driver_constants import *
from message import *


class SolutionVehicle():

    def __init__(self, socket):
        self.socket = socket

        self.road_lane
        self.road_index
        self.velocity
        self.vel_tracker
        self.broadcast_handler

    def set_broadcast_handler(self, handler):
        self.broadcast_handler = handler

    def set_location(self, road_lane, road_index):
        self.road_lane = road_lane
        self.road_index = road_index

    def start(self):
        self.recv_thread = threading.Thread()
        self.send_thread = threading.Thread()


        #send info to client

    def send_data(self):


    def recv_data(self):


    def receive_msg(self, command):
        '''
        # TODO Ensure the entire message was received.
        try:
            if command is not 'pass':
                self.socket.sendall(command.encode('utf-8'))

            msg = self.socket.recv(1024)
            return json.loads(msg.decode('utf-8'))
        except ConnectionResetError:
            print('Lost connection to SV at {}'.format(self.socket))
        '''

        if command == CMD_BROADCAST:
            self.handle_broadcast(self, command)

        elif command ==

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