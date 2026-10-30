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

# find and replace in Makefile in current directory
# sed -i "s/START_DATE=[^#]*#/START_DATE=${START_DATE}#/g" ../Makefile
# sed -i "s/END_DATE=[^#]*#/END_DATE=${END_DATE}#/g" ../Makefile
# # change '/home/vagrant/' to $FIN_SS_PATH
# sed -i "s|/home/vagrant/ss|${FIN_SS_PATH}|g" ../Makefile

# find and replace in build_strategy.sh
echo "Replacing in build_strategy.sh..."
sed -i "s|/home/vagrant/ss|${FIN_SS_PATH}|g" ./provision_scripts/build_strategy.sh


# # find and replace in git_pull.sh
# echo "Replacing in git_pull.sh..."
# sed -i "s|/home/vagrant/ss|${FIN_SS_PATH}|g" ./provision_scripts_Helloworld/git_pull.sh


# find and replace in run_backtest.sh
echo "Replacing in run_backtest.sh..."
sed -i "s|/home/vagrant/ss|${FIN_SS_PATH}|g" ./provision_scripts/run_backtest.sh

# find and replace in delete_instance.py
echo "Replacing in delete_instance.py..."
sed -i "s|~/ss|${FIN_SS_PATH}|g" ./provision_scripts/delete_instance.py

# find and replace in results_analytics.py
echo "Replacing in results_analytics.py..."
sed -i "s|~/ss|${FIN_SS_PATH}|g" ./provision_scripts/results_analytics.py