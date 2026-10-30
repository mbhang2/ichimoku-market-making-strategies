#!/bin/bash

instanceName="$1"
strategyName="$2"
startDate="$3"
endDate="$4"

echo $instanceName
echo $strategyName
echo $startDate
echo $endDate

cd /home/ashitabh/Documents/ss/bt/utilities; ./StrategyCommandLine cmd quit
sleep 10
cd /home/ashitabh/Documents/ss/bt/ ; ./StrategyServerBacktesting &
sleep 1
echo "Started server"
cd /home/ashitabh/Documents/ss/bt/utilities
./StrategyCommandLine cmd create_instance "$instanceName" "$strategyName" UIUC SIM-1001-101 dlariviere 1000000 -symbols AAPL
echo "Created instance"
sleep 1
