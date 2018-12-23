#!/bin/bash

# Setting options and parameters

# Executing the code
module purge
module load  python/3.6.3-anaconda5.0.1

cd Test
python main_test.py
