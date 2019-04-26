Charles River Analytics Inc.
PRINCESS
Probabilistic Representation of Intent Commitments to Ensure Software Survival
01-APR-2019

Challenge Problem 1

*****************
Required Software
*****************

* Docker

All other required software will be downloaded and installed through Docker.
See /CP1/bootstrap.sh for more information.

*****************************
Running the Challenge Problem
*****************************

Step 1. Open a terminal window

Step 2. Switch to your local PRINCESS Challenge Problem 1 release directory

Step 3. Start the CP VM

Step 4. Connect to the CP VM

Step 5. Start the Challenge Problem

    ./start

*********************************
Configuring the Challenge Problem
*********************************

The PRINCESS system is configured through a single properties file

    princess.properties

This file can be found in the root of the Team CP release directory.

* Configuring the Test Harness URL *

The princess.properties file contains the following property:

    baseUrl

You should change the value of this property to reflect the URL of the Test
Harness service.
