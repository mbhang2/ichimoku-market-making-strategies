/*================================================================================
*     Source: ../RCM/StrategyStudio/examples/strategies/SimpleMomentumStrategy/SimpleMomentumStrategy.cpp
*     Last Update: 2021/04/15 13:55:14
*     Contents:
*     Distribution:
*
*
*     Copyright (c) RCM-X, 2011 - 2021.
*     All rights reserved.
*
*     This software is part of Licensed material, which is the property of RCM-X ("Company"), 
*     and constitutes Confidential Information of the Company.
*     Unauthorized use, modification, duplication or distribution is strictly prohibited by Federal law.
*     No title to or ownership of this software is hereby transferred.
*
*     The software is provided "as is", and in no event shall the Company or any of its affiliates or successors be liable for any 
*     damages, including any lost profits or other incidental or consequential damages relating to the use of this software.       
*     The Company makes no representations or warranties, express or implied, with regards to this software.                        
/*================================================================================*/

#ifdef _WIN32
    #include "stdafx.h"
#endif

#include "CandlestickLogger.h"
// #include "group_02_utils.hpp"

#include "FillInfo.h"
#include "AllEventMsg.h"
#include "ExecutionTypes.h"
#include <Utilities/Cast.h>
#include <Utilities/utils.h>


// #include <MarketModels/group_02_utils.h>
#include <cstdlib> 

#include <math.h>
#include <iostream>
#include <cassert>
#include <algorithm>

using namespace RCM::StrategyStudio;
using namespace RCM::StrategyStudio::MarketModels;
using namespace RCM::StrategyStudio::Utilities;


using namespace std;

CandlestickLogger::CandlestickLogger(StrategyID strategyID, const std::string& strategyName, const std::string& groupName):
    Strategy(strategyID, strategyName, groupName),
    candlestickQueue(5,9,13),
    regime_map_(),    
    aggressiveness_(0.2),
    position_size_(30),
    constant_fraction_position(1),
    time_interval(1),
    debug_(false),
    short_window_size_(9),
    medium_window_size_(26),
    long_window_size_(50),
    i_threshold_min(2),
    i_threshold_max(5),
    target_inventory(0),
    target_time(),
    total_stock_position(0),
    logger_custom("/home/ashitabh/Documents/ss/sdk/RCM/StrategyStudio/examples/strategies/group_02_project/CandlestickLogger/csv_files/cstk_20230105.csv")
{
    
    // by default current_candlestick is open 
    current_candlestick.set_open();
    
    #ifdef ShortWindow
    #pragma message("ShortWindow given: " ShortWindow)
    std::string shortWindowStr = ShortWindow;
    int temp_short_window_size = std::stoi(shortWindowStr);
    candlestickQueue.set_short_window_size(temp_short_window_size);
    #endif

    #ifdef MediumWindow
    #pragma message("MidWindow given: " MediumWindow)
    std::string midWindowStr = MediumWindow;
    int temp_mid_window_size = std::stoi(midWindowStr);
    candlestickQueue.set_mid_window_size(temp_mid_window_size);
    #endif

    #ifdef LongWindow
    #pragma message("LongWindow given: " LongWindow)
    std::string longWindowStr = LongWindow;
    int temp_long_window_size = std::stoi(longWindowStr);
    candlestickQueue.set_long_window_size(temp_long_window_size);
    #endif

    logger_custom.Log("best_ask_price,best_bid_price,volume,open_price,close_price,source_time");


    std::cout << "Basic Ichimoku constructor called" << std::endl;

    std::cout << "Candlestick windows are set to: " << std::endl;
    std::cout << "short_window_size: " << candlestickQueue.get_short_window_size() << std::endl;
    std::cout << "mid_window_size: " << candlestickQueue.get_mid_window_size() << std::endl;
    std::cout << "long_window_size: " << candlestickQueue.get_long_window_size() << std::endl;

    
}

CandlestickLogger::~CandlestickLogger(){}


void CandlestickLogger::OnResetStrategyState()
{
    regime_map_.clear();
}

void CandlestickLogger::DefineStrategyParams()
{
    params().CreateParam(CreateStrategyParamArgs("aggressiveness", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_DOUBLE, aggressiveness_));
    params().CreateParam(CreateStrategyParamArgs("position_size", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_INT, position_size_));
    params().CreateParam(CreateStrategyParamArgs("short_window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, short_window_size_));
    params().CreateParam(CreateStrategyParamArgs("long_window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, long_window_size_));
    params().CreateParam(CreateStrategyParamArgs("debug", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_BOOL, debug_));
}

void CandlestickLogger::DefineStrategyCommands()
{
    commands().AddCommand(StrategyCommand(1, "Reprice Existing Orders"));
    commands().AddCommand(StrategyCommand(2, "Cancel All Orders"));
}

void CandlestickLogger::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate)
{    
    std::cout << "Called Event register" << std::endl;
    // for (SymbolSetConstIter it = symbols_begin(); it != symbols_end(); ++it) {
    //     eventRegister->RegisterForBars(*it, BAR_TYPE_TIME, time_interval);
    // }
}

void CandlestickLogger::OnDepth(const MarketDepthEventMsg& msg){}

void CandlestickLogger::OnTrade(const TradeDataEventMsg& msg)
{

    std::cout << "Called OnTrade" << std::endl;
    current_candlestick.set_close_price(msg.trade().price());
    current_candlestick.set_source_time(msg.source_time());
    bool candle_is_added = candlestickQueue.addCandlestick(current_candlestick);
    if(candle_is_added)
    {
    //     std::cout << "Logging Candlestick: " << std::endl;
    //     std::cout << "Current besk ask price: " << candlestickQueue.get_first_best_ask_price() << std::endl;
    //     std::cout << "Current best bid price: " << candlestickQueue.get_first_best_bid_price() << std::endl;
        std:cout << "candlestick added" << std::endl;
        if(candlestickQueue.size() == candlestickQueue.get_long_window_size())
        {
            std::string log_string = current_candlestick.get_log_string();
            // std::cout << log_string << std::endl;

            // Check if the is 'inf' string in log_string
            if (std::string::npos != log_string.find("inf"))
            {
                std::cout << "inf found in log_string" << std::endl;
            }
            

            logger_custom.Log(log_string);
        }
        
    }
    // if(current_candlestick.volume == 0 ) std::cout << "Volume 0 candlestick added; "<<std::endl;
    current_candlestick.reset();
    current_candlestick.set_open_price(msg.instrument().last_trade().price());
    
}

void CandlestickLogger::OnBar(const BarEventMsg& msg)
{ 

}

void CandlestickLogger::OnQuote(const QuoteEventMsg& msg)
{
    // #ifdef PrintDebugInfo
    // std::cout << "Called OnQuote" << std::endl;
    // #endif
   if (current_candlestick.is_open())
   {

        const Quote& quote = msg.quote();
        current_candlestick.set_quote(quote);
   }
   
}

double CandlestickLogger::CalculateInventoryGap(const Instrument* instrument)
{
    // int current_inventory = portfolio().position(instrument);
    // return (target_inventory - current_inventory);
}

int CandlestickLogger::CalculateTargetInventory(const Instrument* instrument,double indicator)
{
    // double indicator_scale = min(indicator/instrument->min_tick_size(),double(i_threshold_max))/(i_threshold_max - i_threshold_min);
    // int target = int(indicator_scale*position_size_);
    // return target;
}

void CandlestickLogger::OnOrderUpdate(const OrderUpdateEventMsg& msg){}

double CandlestickLogger::TimeDifferenceInMicroseconds(TimeType time1, TimeType time2)
{
    // Convert the TimeType objects to microsecond precision if needed
    TimeType t1_microsec = boost::posix_time::time_from_string(boost::posix_time::to_iso_extended_string(time1) + ".000");
    TimeType t2_microsec = boost::posix_time::time_from_string(boost::posix_time::to_iso_extended_string(time2) + ".000");

    // Calculate the difference in microseconds
    boost::posix_time::time_duration diff = t2_microsec - t1_microsec;
    return diff.total_microseconds();
}

double CandlestickLogger::NormalisedTime(TimeType time1)
{
    double t1 = TimeDifferenceInMicroseconds(time1, target_time);
    return t1/time_interval;
}

void CandlestickLogger::MakeOrder(const Instrument& instrument, int action_type)
{
    // std::cout << "Called makeorder" << std::endl;
   
}

void CandlestickLogger::AdjustPortfolio(const Instrument* instrument, int desired_position)
{
    
}

void CandlestickLogger::SendOrder(const Instrument* instrument, int trade_size)
{
    

}

void CandlestickLogger::RepriceAll()
{
    for (IOrderTracker::WorkingOrdersConstIter ordit = orders().working_orders_begin(); ordit != orders().working_orders_end(); ++ordit) {
        Reprice(*ordit);
    }
}

void CandlestickLogger::Reprice(Order* order)
{
    OrderParams params = order->params();
    params.price = (order->order_side() == ORDER_SIDE_BUY) ? order->instrument()->top_quote().bid() + aggressiveness_ : order->instrument()->top_quote().ask() - aggressiveness_;
    trade_actions()->SendCancelReplaceOrder(order->order_id(), params);
}

void CandlestickLogger::OnStrategyCommand(const StrategyCommandEventMsg& msg)
{
    switch (msg.command_id()) {
        case 1:
            RepriceAll();
            break;
        case 2:
            trade_actions()->SendCancelAll();
            break;
        default:
            logger().LogToClient(LOGLEVEL_DEBUG, "Unknown strategy command received");
            break;
    }
}

void CandlestickLogger::OnParamChanged(StrategyParam& param)
{    
    if (param.param_name() == "aggressiveness") {
        if (!param.Get(&aggressiveness_))
            throw StrategyStudioException("Could not get aggressiveness");
    } else if (param.param_name() == "position_size") {
        if (!param.Get(&position_size_))
            throw StrategyStudioException("Could not get position_size");
    } else if (param.param_name() == "short_window_size") {
        if (!param.Get(&short_window_size_))
            throw StrategyStudioException("Could not short_window_size");
    } else if (param.param_name() == "long_window_size") {
        if (!param.Get(&long_window_size_))
            throw StrategyStudioException("Could not get long_window_size");
    } else if (param.param_name() == "debug") {
        if (!param.Get(&debug_))
            throw StrategyStudioException("Could not get debug");
    } 
}
