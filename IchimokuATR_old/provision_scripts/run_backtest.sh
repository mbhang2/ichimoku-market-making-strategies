#!/bin/bash

instanceName="$1"
startDate="$2"
endDate="$3"
STRATEGYFOLDERNAME="$4"

echo $instanceName
echo $startDate
echo $endDate
echo $STRATEGYFOLDERNAME

# Start the backtesting server
(cd /home/ashitabh/Documents/ss/bt && pwd && ls && ./StrategyServerBacktesting & )

echo "Sleeping for 2 seconds while waiting for strategy studio to boot"
sleep 2

# (cd /home/ashitabh/Documents/ss/bt/utilities/ && pwd && ls && ./StrategyCommandLine cmd set_simulator_params -latency_to_exchange 1 -latency_from_exchange 10)
# Start the backtest
(cd /home/ashitabh/Documents/ss/bt/utilities/ && pwd && ls && ./StrategyCommandLine cmd start_backtest "$startDate" "$endDate" "$instanceName" 0)

foundFinishedLogFile=$(grep -nr "finished.$" /home/ashitabh/Documents/ss/bt/logs/main_log.txt | gawk '{print $1}' FS=":"|tail -1)

echo "Last line found:",$foundFinishedLogFile

while ((logFileNumLines > foundFinishedLogFile))
do
    foundFinishedLogFile=$(grep -nr "finished.$" /home/ashitabh/Documents/ss/bt/logs/main_log.txt | gawk '{print $1}' FS=":"|tail -1)
    echo "Waiting for strategy to finish"
    sleep 1
done

echo "Sleeping for 10 seconds..."
sleep 10
echo "run_backtest.sh completed"

cd /home/ashitabh/Documents/ss/bt/backtesting-results
latestCRA=$(ls /home/ashitabh/Documents/ss/bt/backtesting-results/BACK_*.cra -t | head -n1)
echo "Latest CRA file path:", $latestCRA
cd /home/ashitabh/Documents/ss/bt/utilities/
pwd
ls
./StrategyCommandLine cmd export_cra_file $latestCRA /home/ashitabh/Documents/ss/bt/backtesting-results/csv_files
sleep 5
# ./StrategyCommandLine cmd quit
cd /home/ashitabh/Documents/ss/sdk/RCM/StrategyStudio/examples/strategies/group_02_project/$STRATEGYFOLDERNAME/provision_scripts
# # Path to your Python script
# python_script="/home/ashitabh/Documents/ss/sdk/RCM/StrategyStudio/examples/strategies/group_01_project/0_Helloworld_strategy/provision_scripts_Helloworld/results_analytics.py"
if [ "$(whoami)" == "ashitabh" ]; then
    source ~/Documents/fin556_env/bin/activate
fi

python_script="results_analytics.py"
json_file_path="/home/ashitabh/Documents/ss/sdk/RCM/StrategyStudio/examples/strategies/group_02_project/$STRATEGYFOLDERNAME/backtest_data.json"

# # Call the Python script with the latest CRA file path and JSON file path
python3 "$python_script" "$latestCRA" "$json_file_path"
status=$?

# if [ $status -eq 0 ]; then
#     echo "Python script updated backtest_data.json."
#     cd ..
#     git config --global user.email "hm32@illinois.edu"
#     git config --global user.name "Hariharan Manickam"
#     git add backtest_data.json
#     git commit -m "Added new backtest result"
#     git push origin main
#     echo "Pushed new backtest result to gitlab repo."
# else
#     echo "Python script did not update backtest_data.json."
# fi
