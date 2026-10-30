#!/bin/bash


# check user 
echo "Checking user..."
echo "Current user: $(whoami)"

# echo current directory
echo "Current directory: $(pwd)"

if [ "$(whoami)" == "ashitabh" ]; then
    source ./provision_scripts/ashitabh.sh
elif [ "$(whoami)" == "akshay" ]; then
    source ./provision_scripts/akshay.sh
fi

# copy build_strategy.sh, delete_instance.py, run_backtest.sh, results_analytics.py, git_pull.sh to current folder
echo "Copying build_strategy.sh, delete_instance.py, run_backtest.sh, results_analytics.py, git_pull.sh to current folder..."
cp ../base_provisional_scripts/build_strategy.sh ./provision_scripts
cp ../base_provisional_scripts/delete_instance.py ./provision_scripts
cp ../base_provisional_scripts/run_backtest.sh ./provision_scripts
cp ../base_provisional_scripts/results_analytics.py ./provision_scripts
cp ../base_provisional_scripts/git_pull.sh ./provision_scripts

if [ "$(whoami)" == "ashitabh" ] || [ "$(whoami)" == "akshay" ]; then

    # find and replace in build_strategy.sh
    echo "Replacing in build_strategy.sh..."
    sed -i "s|/home/vagrant/ss|${FIN_SS_PATH}|g" ./provision_scripts/build_strategy.sh

    # find and replace in run_backtest.sh
    echo "Replacing in run_backtest.sh..."
    sed -i "s|/home/vagrant/ss|${FIN_SS_PATH}|g" ./provision_scripts/run_backtest.sh

    # find and replace in delete_instance.py
    echo "Replacing in delete_instance.py..."
    sed -i "s|~/ss|${FIN_SS_PATH}|g" ./provision_scripts/delete_instance.py

    # find and replace in results_analytics.py
    echo "Replacing in results_analytics.py..."
    sed -i "s|~/ss|${FIN_SS_PATH}|g" ./provision_scripts/results_analytics.py
fi