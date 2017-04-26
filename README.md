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
    $ python solution_vehicle_client.py --loc 5
```
`--loc` sets the initial location of the solution vehicle.
`--lane` sets the initial lane of the solution vehicle.
`--vel` sets the initial velocity of the solution vehicle.

To make the solution vehicles consistent with the initial spacing of a model with no solution vehicles, insert the vehicles at an interval according to the density of the model. For example, if the road length is 40, with a density of 0.2, we would have 8 total vehicles at an interval of 5 road lengths between each. Thus, with 2 solution vehicles, insert them at `--loc 0` and `--loc 5`.

The server runs two lanes, one densely populated and one with a single vehicle
to demonstrate phantom traffic jams.

Running the UI:
```shell
    $ python ui_server.py
    $ python -u traffic_model.py --run=10000 | python ui_adapter.py
```

Direct a browser to localhost:8081/ui_adapter_demo.html.

