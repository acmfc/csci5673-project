CSCI 5673 Project: Phantom Traffic Jam Resolution
=================================================
This implements a basic Nagel-Schreckenberg cellular automaton model with
support for independent solution vehicle processes.

Run
---
Running the traffic model server:
    $ python traffic_model.py

Running solution vehicles (in separate terminals):
    $ python solution_vehicle_client.py 0
    $ python solution_vehicle_client.py 1

The server runs two lanes, one densely populated and one with a single vehicle
to demonstrate phantom traffic jams.
