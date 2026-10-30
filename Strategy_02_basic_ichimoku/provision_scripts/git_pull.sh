#!/bin/bash

# cd /home/vagrant/ss/sdk/RCM/StrategyStudio/examples/strategies/
USERNAME="$(whoami)"
if [ "$USERNAME" = "ashitabh" ]; then
    cd "/home/ashitabh/Documents/ss/sdk/RCM/StrategyStudio/examples/strategies/"
elif [ "$USERNAME" = "akshay" ]; then
    cd "/media/akshay/Data/ss/sdk/RCM/StrategyStudio/examples/strategies/"
fi

REPO_DIR="group_02_project"
# rm -rf "$REPO_DIR"

if [ -d "$REPO_DIR" ]; then

    cd "$REPO_DIR"
    echo "Working directory (git_pull.sh): $(pwd)"
    git fetch origin
    git reset --hard origin/main # we do hard reset because we want to overwrite any local changes
    cd ..
    echo "We pulled the repo."
else
    # USE YOUR HTTPS URL HERE IF SSH DOESN'T WORK
    git clone -b main git@gitlab.engr.illinois.edu:fin556_algo_market_micro_fall_2023/fin556_algo_fall_2023_group_02/group_02_project.git
    echo "We created the repo."
fi