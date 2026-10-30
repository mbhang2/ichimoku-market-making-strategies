#!/bin/bash

instanceName="$1"
strategyName="$2"
startDate="$3"
endDate="$4"

echo $instanceName
echo $strategyName
echo $startDate
echo $endDate

echo "Original Host directory: $(pwd)"
OriginalHostDirectory=$(pwd)

cd /home/ashitabh/Documents/ss/bt/utilities; ./StrategyCommandLine cmd quit
sleep 10
cd /home/ashitabh/Documents/ss/bt/ ; ./StrategyServerBacktesting &
sleep 1
echo "Started server"
cd /home/ashitabh/Documents/ss/bt/utilities

if [[ $OriginalHostDirectory == *"Crypto"* ]]; then
    echo "Pick MSFT symbol pwd: $(pwd)"
    symbol="MSFT"
else
    echo "Pick SPY symbol pwd: $(pwd)"
    symbol="SPY"
fi


echo "Symbol: $symbol"

# Add Symbol for Crypto here 
./StrategyCommandLine cmd create_instance "$instanceName" "$strategyName" UIUC SIM-1001-101 dlariviere 1000000 -symbols $symbol
echo "Created instance"
sleep 1