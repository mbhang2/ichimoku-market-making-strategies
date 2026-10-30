

## Exact commands I used right after I sshed into the lab VM

Installing pandas for results_analytics.py
```sh
python3 -m pip install pandas
```
Navigate to directory
```sh
cd /ss/sdk/RCM/StrategyStudio/examples/strategies
```
Clone the repo. Use SSH link, it should work.
```sh
git clone git@gitlab.engr.illinois.edu:fin556_algo_market_micro_fall_2023/fin556_algo_fall_2023_group_01/group_01_project.git
```
Navigate to strategy
```sh
cd group_01_project/0_Helloworld_strategy
```
Run the backtest
```sh
make run_backtest
```


## What is in this directory?
1. Makefile:
- This contains instructions for automating all the steps we need to follow for a successful backtest.
- It defines various variables and targets
- You need to understand every line in the Makefile as it acts as the brain for our backtesting. 
2. .cpp file:
- This contains the implementation of the HelloworldStrategy class.
- This is the main file that defines the logic of the strategy.
3. .h file: 
- This contains the declaration of the Helloworld_Strategy class.
- This file is included in the .cpp file to provide the necessary interface to the class.
4. provision_scripts directory:
- Contains all our shell scripts & python scripts which interact with the Strategy Studio's Command Line Interface

## How to view results of your backtest?
- When you run the backtest, if you can see that it has successfully run, you will see a message saying that a json file has either been created or updated.
- That file is backtest_data.json, which you can find in the same directory as the Makefile. Do ```ls``` after the backtest to see the file
- I tried to push it back to the repo, but it looks like we do not have permissions.
- You can view this file using nano ```backtest_data.json```.
- CTRL + X to exit nano
- Make sure to not make any changes to the json when you are viewing it
- You should add more functions to calculate more statistics on fill and order csvs
- You can use the csv homework files and change the directory to test your functions before doing analytics after a backtest.
- I haven't figured out how/if we could download the json to our local machine.

## How to backtest?
- Any and every change you make must go through gitlab.
- You should commit every change you want to be reflected during a backtest.
- There is a git pull target in the Makefile, which will do a git pull every time you run_backtest
- If you are making changes to the Makefile itself, you should do the following
- ```git fetch origin main```
- ```git reset --hard origin/main```
- Note: ```git pull``` might fail because changing permissions for provision scripts cause a conflict

## Other Notes
- I have not tested multiple tickers in a strategy
- I have not tested multiple days for a backtest
- I will try and add the SimplePairs strategy from the examples in another folder
- YOU HAVE TO MAINTAIN THE STRUCTURE OF THE FOLDER.
- All the paths are designed keeping that in mind.
- The strategy needs to be 1 sub directory deep from the repo.
- The provision scripts need to be 1 sub directory deep from the strategy.
- The backtest is way faster if the orders/trades are not printed on the terminal in the cpp file.