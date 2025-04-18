Pantheon Congestion Control Analysis

A comprehensive framework for evaluating and comparing congestion control algorithms using the Pantheon platform with MahiMahi network emulation.

Overview:

This repository provides tools and scripts for analyzing the performance of various congestion control algorithms BBR, Cubic, Vegas across different network conditions. By leveraging Pantheon's standardized test harness, the project enables consistent and fair comparison of algorithm behaviors.

Features:

1. Automated testing of multiple congestion control algorithms
2. Performance analysis across diverse network scenarios
3. Comprehensive visualization of results including throughput, loss rate, and RTT metrics
4. Comparative analysis between different network profiles

Prerequisites

Ubuntu 20.04 or later
Python 3.8+
Git
MahiMahi network emulator


Installation

STEP 1: Clone the repository

git clone https://github.com/vbramhadevi/Pantheon.git

STEP 2: Navigate to the project directory

cd/Pantheon

STEP 3: Install dependencies

Install all necessary dependencies for the Pantheon and MahiMahi environments.

STEP 4: Running Experiments

To execute experiments:

python3 src/run.py

STEP 5: Output Structure

After running the experiments, results will be organized in the following directories:

Logs: Pantheon/logs/

Graphs: Pantheon/graphs/

CSV Results:

Profile A: Pantheon/results/profile_A/
Profile B: Pantheon/results/profile_B/


Analyzing Results:

The analysis tools provide insights into how different congestion control algorithms perform under varying network conditions, helping researchers and network engineers make informed decisions about algorithm selection for specific use cases.

