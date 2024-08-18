#!/bin/bash

sudo apt update

# Python
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Torch Numpy
python3 -m pip install torch numpy

# Cmake
sudo apt install -y cmake

# GCC as CC and CXX for building buggy compilers
sudo apt install -y gcc-7 g++-7
sudo ln -sf /usr/bin/gcc-7 /usr/bin/gcc
sudo ln -sf /usr/bin/g++-7 /usr/bin/g++
sudo ln -sf /usr/bin/gcov-7 /usr/bin/gcov

# Additional dependencies for building GCC Compilers
sudo apt install -y libmpfr-dev libmpfr-doc libgmp-dev libmpc3 libmpc-dev flex gcc-multilib