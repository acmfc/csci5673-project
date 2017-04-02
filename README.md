CSCI 5673 Project: Phantom Traffic Jam Resolution
=================================================
This implements a basic Nagel-Schreckenberg cellular automaton model with
support for independent solution vehicle processes.

Run
---
Running the traffic model server:
```shell
    $ python traffic_model.py --run 25 --sv 2
```
`--run` delimits the number of steps to run the traffic model.
`--sv` informs the server how many solution vehicles will connect to it. 

Running solution vehicles (in separate terminals):
```shell
    $ python solution_vehicle_client.py --loc 0
    $ python solution_vehicle_client.py --loc 1
```
`--loc` sets the initial location of the solution vehicle.
`--lane` sets the initial lane of the solution vehicle.
`--vel` sets the initial velocity of the solution vehicle

The server runs two lanes, one densely populated and one with a single vehicle
to demonstrate phantom traffic jams.
