#!/bin/bash

# run the tiled server in a screen session

screen -dm -S tiled_server -h 5000 ./start-tiled.sh
