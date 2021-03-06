# PRINCESS Challenge Problem 1

This directory contains software and scripts for the PRINCESS Challenge Problem 1.
## How to run
`cd src/cp1_src/cp1` <br />
`python start.py`


## Start Script
The start script runs through the following steps:
1. Loads in data from [data.json](conf/data.json)
2. Generates an MDL shell file with `num_tas` number of TAs, and 1 channel
3. Imports the newly created MDL file into the `cra_mdl` OrientDB database, located on http://http:localhost:2480
4. Generates a ConstraintsObject based on [data.json](conf/data.json)
5. Stores the constraints in the OrientDB database, `cra_constraints`
6. Retrieves the constraints from `cra_constraints`
7. Creates a newly optimized schedule using the specified algorithm(s)
8. Updates the OrientDB version of the MDL file in `cra_mdl`
9. Exports the contents of `cra_mdl` into a new MDL file, under the [output folder](output/mdl)
10. Allows the user to select which Algorithm to score the MDL file for  

## Data.json
### How to generate TAs and Channels
The configuration for how to run CP1 is entirely contained within  [data.json](conf/data.json). There is a definition for each field in the following format: <br />
*[field_name]*: *[description]*.*[data_type]*.
###### *data_type* values:
Most are self explanatory, here are the ones you need to know: <br />
**PRF**: Percentage, Range Format (see below) <br />
**0/1**: 1 indicates to use the algorithm, 0 to skip <br />


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

#### Algorithms
**Optimization**: The type of optimization algorithm to use when selecting which TAs to communicate over which channels. There are three optimization algorithm types; `CBC`, `Dynamic Program`, `Greedy`. 0/1. <br />
**Scheduling**: The type of scheduling algorithm to use when selecting the order in which TAs should communicate over a channel. The only current algorithm implemented is a `Greedy` scheduler. 0/1. <br />
**Discretization**: The type of discretization strategy to use when considering how much bandwidth to provide a TA at a given bandwidth. There are three discretization strategy types; `Accuracy`, `Bandwidth` and `Value`. 0/1.

#### Files and Database
**constraints_db_name**: Name of the MDL Database to store the ConstraintsObject in. str. <br />
**mdl_db_name**: Name of the database to store the MDL file in. str. <br />
**mdl_output_file**: Base name of the modified MDL file. A timestamp and  str. <br />
**mdl_input_file**: Name of the MDL File to store in the MDL database. This is the file generated by the MDL Shell Generator. str. <br />
**orientdb_config_file**: Path to config file to use when connecting to OrientDB. str. <br />



### Percentage, Range Format
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
1. [[0.5, [100]], [0.5, [250, 1000]]] <br />
50% chance that the value 100 is selected. <br />
50% chance that an integer between 250 and 1000 is selected (i.e. 478)

2. [[0.1, [0.5, 1.0]], [0.85, [1, 10]], [0.05, [11]]] <br />
10% chance that a float between 0.5 and 1 will be selected (i.e. 0.784392) <br />
85% chance that an int between 1 and 10 will be selected (i.e. 10) <br />
5% chance that the int 11 will be selected.

3. [[1, [10]]] <br />
100% chance that the int 10 will be selected
