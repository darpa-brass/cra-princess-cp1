# Challenge Problem 1 Results Format
## Bash Start
Running the bash script [start](start) will begin the build process for our challenge problems.
The purpose of this script is to build CP1 and SwRI source code into distributable python eggs,
and then invoke [start.py](src/cp1_src/cp1/start.py).

## Start.py
CP1 is executed from [start.py](src/cp1_src/cp1/start.py), which:
1. Loads in data from [data.json](conf/data.json)
2. Generates a shell MDL shell file with for `num_tas` TAs using a SwRI provided MDL Generator
3. Imports the newly created MDL file into the `cra_mdl` OrientDB database, located on http://http:localhost:2480
4. Generates a Constraints Object based on other parameters defined in [data.json](conf/data.json)
5. Stores the constraints in the OrientDB database, `cra_constraints`
6. Retrieves the constraints from `cra_constraints`. The purpose of storing and retrieving the same constraints is to highlight that CRA can interact with future constraints within OrientDB. For evaluation, SwRI will have to provide these.
7. Creates a newly optimized schedule using the specified algorithm(s)
8. Stores raw results based on the Optimization and Discretization algorithms under the [raw output folder](output/raw)
9. Updates the OrientDB version of the MDL file in `cra_mdl`
10. Exports the contents of `cra_mdl` into a new MDL file, under the [mdl output folder](output/mdl)

## Outputs
### Format
Files are named by the following convention: <br><br>
`<Discretizer>(<disc_write_value>)_<Optimizer>_<Scheduler>_<"%Y-%m-%d_%H-%M-%S">_<seed>`

`disc_write_value`:
If [AccuracyDiscretizer](src/cp1_src/cp1/processing/algorithms/discretization/accuracy_discretization.py) has been invoked, this is the percentage guaranteed of the optimal solution specified.
                    If [BandwidthDiscretizer](src/cp1_src/cp1/processing/algorithms/discretization/bandwidth_discretization.py) or [ValueDiscretizer](src/cp1_src/cp1/processing/algorithms/discretization/value_discretization.py) has been invoked, this is the number of discretizations specified.

<br>For example, in the file name: `AccuracyDiscretization(0.9)_CBC_GreedySchedule_2019-07-23_15-16-51.xml`<br>
 An [AccuracyDiscretization](src/cp1_src/cp1/processing/algorithms/discretization/accuracy_discretization.py) was used with an accuracy of 0.9 (90% of the optimal solution is guaranteed), the [CBC Engine](src/cp1_src/cp1/processing/algorithms/optimization/integer_program.py) selected TAs, TAs were scheduled in the MDL file using the [Greedy Schedule](src/cp1_src/cp1/processing/algorithms/scheduling/greedy_schedule.py), and this was run at 3:15:51pm July 23rd, 2019.

 If a Perturbation has been applied to the file, it's name will be
 prepended with the following string: <br>
 `<reconsider>_<combine>_<ta_bandwidth>_<channel_dropoff>_<channel_capacity>`<br>
 These values correspond to the perturbation settings in the config file.


#### Raw
We also output Raw files to assist in evaluation. Raw files are useful for larger sets of data where understanding the trends of CP1, such as the average increase in value based on the type of algorithm used. The format of our Raw files is CSV, and the output is as follows: <br>
`<seed>,<disc_count>,<accuracy>,<total_value>,<run_time>,<solve_time>`
<br>
<br>
`seed`: The seed used in this run.<br>
`disc_count`: If a [Bandwidth](src/cp1_src/cp1/processing/algorithms/discretization/bandwidth_discretization.py) or [Value Discretization](src/cp1_src/cp1/processing/algorithms/discretization/value_discretization.py) was used this value is set to `disc_count`. Otherwise it is blank.<br>
`accuracy`: If an [Accuracy Discretization](src/cp1_src/cp1/processing/algorithms/discretization/accuracy_discretization.py) was used, this value is set to `epsilon`. Otherwise it is blank.<br>
`total_value`: The total value achieved as a result of the TAs selected by an [Optimization Algorithm](src/cp1_src/cp1/processing/algorithms/optimization). This may later increase once TAs run through a [Scheduling Algorithm](src/cp1_src/cp1/processing/algorithms/scheduling).<br>
`run_time`: The total run time of the Optimization Algorithm used.<br>
`solve_time`: The solve time of the Optimization Algorithm used. [GreedyOptimizer](src/cp1_src/cp1/processing/algorithms/optimization/greedy_optimization.py) and [DynamicProgram](src/cp1_src/cp1/processing/algorithms/optimization/dynamic_program.py) do not have complex solvers, as us the case in Integer Programming, therefore this value is identical to `solve_time`.

## Data.json
### How to generate TAs and Channels
The configuration for how to run CP1 is entirely contained within  [data.json](conf/data.json). There is a definition for each field in the following format: <br><br>
`[field_name]:[description][data_type]`

`data_type`:
The following are the allowed values in data.json: <br>
**PRF**: [Percentage, Range Format](#PRF) <br />
**0/1**: 1 indicates to use the algorithm, 0 to skip <br />
**str**: string <br>
**int**: integer <br>

### Field Definitions
#### TAs
**num_tas**: The number of TA objects to generate. int. <br />
**voice_bandwidth**: Minimum required Voice Bandwidth. PRF. <br />
**safety_bandwidth**: Minimum required Safety Bandwidth. PRF. <br />
**latency**: Latency this TA requires. PRF. <br />
**scaling_factor**: Scaling factor in the TA's value equation. PRF. <br />
**c**: Coefficient 'c' in the TA's value equation. PRF. <br />

#### Channels
**num_channels**: The number of Channel objects to generate. int. <br />
**base_frequency**: The base frequency to start from, followed by the amount to increase for each subsequent channel.
i.e. [4919500000, 100000] means that the first channel generated will have a frequency of 4919500000, the second
channel generated have a frequency of 4919600000 etc. [int, int] <br />
**capacity**: Throughput capacity of the channel. PRF. <br />

#### Constraints Object
**guard_band**: The guard_band value in ms. int. <br />
**goal_throughput_bulk**: The goal_throughput values for bulk communication in Kbps. int. <br />
**goal_throughput_voice**: The goal_throughput value for voice communication in Kbps. int. <br />
**goal_throughput_safety**: The goal_throughput value for safety communication in Kbps. int. <br />
**epoch**: The epoch of the MDL file in ms. int. <br />
**txop_timeout**: The TxOpTimeout element value in terms of Epochs. int. <br />
**seeds**: The seeds to run each instance of CP1 on. This will run every number in the range of seeds, inclusive of the lower and upper bounds. Set this field to the string `timestamp` to randomly generate data every run. [int, int] OR `timestamp`.

#### Algorithms
**Optimization**: The type of optimization algorithm to use when selecting which TAs to communicate over which channels. There are four optimization algorithm types; [CBC](src/cp1_src/cp1/processing/algorithms/optimization/integer_program.py), [Gurobi](src/cp1_src/cp1/processing/algorithms/optimization/gurobi.py), [Dynamic Program](src/cp1_src/cp1/processing/algorithms/optimization/dynamic_program.py) and [Greedy](src/cp1_src/cp1/processing/algorithms/optimization/greedy_optimization.py). 0/1. <br />
**Scheduling**: The type of scheduling algorithm to use when selecting the order in which TAs should communicate over a channel. There are three scheduling algorithm types: [Greedy](src/cp1_src/cp1/processing/algorithms/scheduling/greedy_schedule.py) and [Hybrid](src/cp1_src/cp1/processing/algorithms/scheduling/hybrid_schedule.py) 0/1. <br />
**Discretization**: The type of discretization strategy to use when considering how much bandwidth to provide a TA at a given bandwidth. There are three discretization strategy types; [Accuracy](src/cp1_src/cp1/processing/algorithms/discretization/accuracy_discretization.py), [Bandwidth](src/cp1_src/cp1/processing/algorithms/discretization/bandwidth_discretization.py) and [Value](src/cp1_src/cp1/processing/algorithms/discretization/value_discretization.py). 0/1.

#### Perturbations
**perturb**: Whether or not to apply the below perturbations. Quick hand
for not setting every field to 0. 0/1. <br>
**reconsider**: How many TAs to reconsider from the list of unscheduled TAs. int. <br>
**combine**: Whether or not to apply all perturbations at once. 0/1. <br>
**ta_bandwidth**: The amount by which to increase the TA minimum bandwidth. Can be negative to decrease this amount. int. <br>
**channel_dropoff**: The amount of TAs to kick off currently scheduled channels. int. <br>
**channel_capacity**: The amount by which to increase or decrease the capacity of one channel. int. <br>

#### Files and Database
**visualize**: Will optionally the SwRI provided [TxOpScheduleViewer](external/TxOpScheduleViewer/brass_visualization_tools/TxOpSchedViewer.py) on each file output by the CP1 framework. Once one run has completed, it will provide a new terminal window. Pressing 'q' key exits this window, and the next run is started. This will not work in a docker container, and must be set to 0. 0/1. <br>
**clear**: Clear files under `output\mdl` and `output\raw` before running. 0/1.  
**orientdb_config_file**: Path to config file to use when connecting to OrientDB. str. <br />
**constraints_db_name**: Name of the MDL Database to store the ConstraintsObject in. str. <br />
**mdl_db_name**: Name of the database to store the MDL file in. str. <br />
**mdl_input_file**: Name of the MDL File to store in the MDL database. This is the file generated by the MDL Shell Generator. str. <br />
**mdl_output_file**: Base name of the modified MDL file. A timestamp and  str. <br />
**mdl_output_folder**: Name of the folder where MDL files will be output. str. <br>
**raw_output_folder**: Name of the folder where .csv files will be output. str. <br>


### <a name="PRF"></a> Percentage, Range Format
[[**percentage**, [**range**]]]

**percentage**: Defines the likelihood a number within the specified range will be selected. <br />
Must be a number between 0 and 1. <br />
The sum of all percentages must add up to 1. <br />

**range**:  Defines a range, in which 1 number will be selected. <br />
If a single value is present, that will be the value considered. i.e. *[100]* <br />
If two values are present, it will generate a number between them i.e. *[100, 200]*. <br />
To consider generating floats within this range (i.e. 100.58 or 148.29) make either of the numbers defined in range a float *[100.0, 200.0]*. <br />
Ranges are inclusive, meaning 100 and 200 will also be considered.


##### Examples
1. `[[0.5, [100]], [0.5, [250, 1000]]]` <br />
50% chance that the value 100 is selected. <br />
50% chance that an integer between 250 and 1000 is selected (i.e. 478)

2. `[[0.1, [0.5, 1.0]], [0.85, [1, 10]], [0.05, [11]]]` <br />
10% chance that a float between 0.5 and 1 will be selected (i.e. 0.784392) <br />
85% chance that an int between 1 and 10 will be selected (i.e. 10) <br />
5% chance that the int 11 will be selected.

3. `[[1, [10]]]` <br />
100% chance that the int 10 will be selected
