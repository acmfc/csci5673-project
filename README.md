CSCI 5673 Project: Phantom Traffic Jam Resolution
=================================================
This implements a basic Nagel-Schreckenberg cellular automaton model with
support for independent solution vehicle processes.

Run
---
Running the traffic model server:
```shell
    $ python traffic_model.py
```

Running solution vehicles (in separate terminals):
```shell
    $ python solution_vehicle_client.py --loc 0
    $ python solution_vehicle_client.py --loc 1
```

The server runs two lanes, one densely populated and one with a single vehicle
to demonstrate phantom traffic jams.
