# Project Plan 

## Project Overview

Financial experts have traditionally held the view that retail trading and professional trading, especially High-Frequency Trading (HFT), are two distinct realms of trading that cannot be effectively merged. Our trading project is committed to challenging this belief directly. Over the course of the project, we will develop a profitable interdisciplinary trading strategy that leverages cutting-edge techniques from these seemingly disparate domains. More precisely, we will fuse the LSTM/DNN model, Ichimoku Kinko Hyo, and Market Making Strategy into a unified approach.

## Technologies and Tools

- **Programming Languages**:  
  * Python 
  * C++

- **Libraries and Frameworks**: 
  * pandas 
  * numpy
  * statsmodels
  * arch
  * scipy
  * ta 

- **Data Sources**: 
  * polygon.io: Tick data from multiple exchanges, aggregate data, and technical analysis information.
  * gate.io: Depth of Order Book and Price Data
  * Binance: Trade Data
  * Kraken: Depth of Order Book and Price Data

- **Backtesting Period**: January 3, 2023 to February 9, 2023 
  * Rationale: 
    1) Height of Russia-Ukraine Conflict
    2) Earning statements of countries, companies from previous quarters are coming
    3) The volatility index(ViX) has a mix of low-ViX and high ViX which correspond to markets having a sense of stability to they going crazy nervous. 

## CI/CD (Continuous Integration/Continuous Deployment)

- **Automated Testing**: 
  * pytest
  * GitLab

- **Deployment**: 
  * We maintain a common Linux server where each team member implements their data analysis/strategy.  
  **Pros:**
    * Access to a shared data repository and providing access to a larger volume of data.
    * Common env management and avoid version clash.

## Finite State Machine

![Link to FSM Diagram](https://drive.google.com/file/d/1IV8ret8abh3oucDt6m3wMYHCyJAjrw9M/view?usp=drive_link)

**Algorithmic:**

We will utilize a special tick candlestick:

* Open: Last traded price
* High: Top ask price
* Low: Top bid price
* Close: Next traded price

**Update on:**

* *Order Book BBO:* The high and low of the current candle will be updated.
* *Trade:* Proceed to the next candle, where the close of the previous candle equals the open of the current candle, which equals the new last traded price.

1. We will input this candlestick data, along with other parameters such as volume, into the DNN/LSTM model to predict the next candlestick.
2. Ichimoku Kinko Hyo will be utilized for algorithmic trading signals.
3. If the entry condition is met based on the predicted next candle, we will execute a directional market-making strategy on the exchange with the lowest price (slowest reaction = highest latency at the instance).
4. The simple entry condition: conversion line and base line cross.

**Directional Market-Making Strategy:**

We will implement a directional market-making strategy, where the order in favor of the micro-trend (buy limit order if an expected bullish trend) is placed at the National Best Bid and Offer (NBBO), and the order against the micro-trend (sell limit order if an expected bullish trend) is placed several ticks above the NBBO.

By doing so, we can profit a few more ticks on top of the bid/ask spread, while "riding" along the micro-trend improves the chances of the limit order offset several ticks from the NBBO being filled.


## Project Timeline

Outline the project timeline, including milestones and deadlines.

- **11/06/2023**: 
  - *Goal:* 
    - Completion of data analysis of Polygon + IEX data.
  - *Deliverables:* 
    - Jupyter Notebook containing analysis methodology and insights for strategy development. 
    - Selection of symbol for strategy 

- **11/13/2023**: 
  - *Goal:*
    - Implementation of strategy in Python.
    - Implementation of strategy in Strategy Studio.
    - Training LSTM/DNN model. 
  - *Deliverables:*
    - Scripts/Jupyter notebook with strategy implementation. 
    - Source code in C++ for Strategy Studio implementation.
    - Documentation of methodology, motivation, and rationale for the strategy.
    - Accuracy report of the LSTM/DNN model.

- **11/20/2023**: 
  - *Goals:*
    - Backtesting strategy in Strategy Studio.
    - [REACH] Explore the possibility of adding an online LSTM/DNN model.
  - *Deliverables:*
    - Report containing a summary of strategy performance. 

- **11/27/2023**: 
  - *Goals*: 
    - Revising strategy based on backtesting results.
    - Backtesting revised strategy on Strategy Studio.
  _ *Deliverables*: 
    - 2nd report containing a summary of revised strategy performance. 

- **12/04/2023**: 
  - *Goals*: 
    - Backtest by simulating real-life latency and revise strategy accordingly. 
    - Complete final project report. 
  _ *Deliverables*: 
    - Performance summary given real-life latency conditions.
    - Draft project report. 

- **12/11/2023**: 
  - Final review of the report and submission.

**Buffer Week**
- **12/14/2023**: 
  - HARD DEADLINE: Project submission!

## Project Goals

1. **Bare Minimum Target**: 
  * Create a viable, profitable strategy for one cash equity symbol that leverages market microstructure. 
  * Implement a LSTM/DNN architecture as a base predictive model.
2. **Expected Completion Goals**: 
  * Achieve a non-negative P/L using a reasonable latency during backtesting and simulations. 
  * Maintain favorable performance statistics such as win-rate, profit-loss-ratio, or risk-to-reward ratio, for long-term risk management.
3. **Reach Goals**: 
  * Create an online version of the LSTM/DNN model.
  * Ensure that the strategy generates a positive alpha. 

## Team Members and Contributions

- Ashitabh Misra:
  - Contribution: 
    - Implementation of Strategy in Strategy Studio
    - Training LSTM/DNN Model
    - Server Setup
  - Skills: 
    - C++
    - ML/AI Experience

- Min Hyuk "Michael" Bhang:
  - Contribution: 
    - Strategy development based on analysis results
    - Technical analysis and interpretation
  - Skills: 
    - Python Programming 
    - Background in Finance/Trading

- Akshay Pandit
  - Contribution: 
    - Backtesting
    - Writing Parser
  - Skills: 
    - Python Programming
    - Experience with Strategy Studio

- Laxmi Vijayan:
  - Contribution: 
    - Analysis of IEX and Polygon.io Data
  - Skills: 
    - Python Programming
    - Data Analysis & Visualization

## External Resources

- Data from Polygon.io

## Deliverables

Specify the final deliverables of the project, such as code repository, documentation, reports, etc.

- **Code Repository:** Located on GitLab documenting our analysis, the development of our strategy and model, as well as our results. 

- **Report:** Located on our GitLab containing a detailed description of our project, including aims, methods, results, and discussion of future work. 

## Team Members

- [Team Member 1]: Ashitabh Misra
  - Graduation Semester: Fall 2025
  - Future Plans: Enter industry as ML Engineer, Quant Researcher or Quant Trader

- [Team Member 2]: Min Hyuk "Michael" Bhang
  - Graduation Semester: Spring 2024
  - Future Plans: Master's in Financial Engineering (MSFE)

- [Team Member 3]: Akshay Pandit
  - Graduation Semester: Fall 2025
  - Future Plans: Enter industry as ML Engineer, Quant Researcher or Quant Trader

- [Team Member 4]: Laxmi Vijayan
  - Graduation Semester: Fall 2024
  - Future Plans: Enter industry as ML Engineer, Quant Researcher or Quant Trader
---
