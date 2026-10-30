#!/bin/bash

#Creates a copy of SS backtesting results in the git repo directory based on strategy name and unique identifier. 
#Place in csv_files directory, change root path to the git repository folder, chmod +x copy_files.sh.
#$destination_basename = StrategyFolder/Results
#Example Usage: ./copy_files.sh StrategyFolder/Results unique_id <unique_id> <unique_id> 
#@Author: Laxmi Vijayan

if [ $# -lt 2 ]; then
    echo "Usage: $0 <destination_basename> <arg1> [<arg2> ...]"
    exit 1
fi

destination_basename="$1"
shift

destination="/home/ashitabh/Documents/ss/sdk/RCM/StrategyStudio/examples/strategies/group_02_project/$destination_basename/"

# It will create the destination folder if it doesn't exist
if [ ! -d "$destination" ]; then
    mkdir -p "$destination" || { echo "Error creating destination folder."; exit 1; }
fi

for arg in "$@"; do

    ls | grep "$arg" | xargs -I {} cp {} "$destination"

done

echo "Files successfully copied to: $destination."
