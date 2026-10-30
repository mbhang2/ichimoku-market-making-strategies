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

#include "IchimokuATR.h"
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
int total_trades = 0;
int buy_trades = 0;
int sell_trades = 0;
int bid_act_count = 0;
int ask_act_count = 0;

IchimokuATR::IchimokuATR(StrategyID strategyID, const std::string& strategyName, const std::string& groupName):
    Strategy(strategyID, strategyName, groupName),
    candlestickQueue(5,13,26),
    regime_map_(),    
    aggressiveness_(0),
    position_size_(300),
    constant_fraction_position(0.1),
    time_interval(1),
    debug_(false),
    short_window_size_(5),
    medium_window_size_(13),
    long_window_size_(26),
    i_threshold_min(2),
    i_threshold_max(5),
    target_inventory(0),
    target_time(),
    total_stock_position(0),
    threshold_time(20,58,0),
    crossed_threshold_time(false)
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


    std::cout << "Basic Ichimoku constructor called" << std::endl;

    std::cout << "Candlestick windows are set to: " << std::endl;
    std::cout << "short_window_size: " << candlestickQueue.get_short_window_size() << std::endl;
    std::cout << "mid_window_size: " << candlestickQueue.get_mid_window_size() << std::endl;
    std::cout << "long_window_size: " << candlestickQueue.get_long_window_size() << std::endl;

    
}

IchimokuATR::~IchimokuATR(){}


void IchimokuATR::OnResetStrategyState()
{
    regime_map_.clear();
}

void IchimokuATR::DefineStrategyParams()
{
    params().CreateParam(CreateStrategyParamArgs("aggressiveness", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_DOUBLE, aggressiveness_));
    params().CreateParam(CreateStrategyParamArgs("position_size", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_INT, position_size_));
    params().CreateParam(CreateStrategyParamArgs("short_window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, short_window_size_));
    params().CreateParam(CreateStrategyParamArgs("long_window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, long_window_size_));
    params().CreateParam(CreateStrategyParamArgs("debug", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_BOOL, debug_));
}

void IchimokuATR::DefineStrategyCommands()
{
    commands().AddCommand(StrategyCommand(1, "Reprice Existing Orders"));
    commands().AddCommand(StrategyCommand(2, "Cancel All Orders"));
}

void IchimokuATR::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate)
{    
    for (SymbolSetConstIter it = symbols_begin(); it != symbols_end(); ++it) {
        eventRegister->RegisterForBars(*it, BAR_TYPE_TIME, time_interval);
    }
}

void IchimokuATR::OnDepth(const MarketDepthEventMsg& msg){}

void IchimokuATR::OnTrade(const TradeDataEventMsg& msg)
{
    // std::cout << "On trade called" << std::endl;

    const Instrument& instrument = msg.instrument();
    int num_working_orders = orders().num_working_orders(&instrument);
    int num_of_open_trades = trades().num_open_trades(&instrument);
    int num_of_closed_trades = trades().num_closed_trades(&instrument);
    auto filled_orders = orders().stats().num_orders_filled();
    // std::cout << "checkpoint 0" << std::endl;
    
    // candlestickQueue.print_high_asks();
    // candlestickQueue.print_close_prices();

    current_candlestick.set_close_price(msg.trade().price());

    
    TimeType current_time = msg.source_time();
    #ifdef END_METHOD
    #pragma message("END_METHOD given: " END_METHOD)
    DateType current_date;
    std::string end_method = END_METHOD;
    if (end_method == "Current")
    {
        current_date = current_time.date();
    }
    else if (end_method == "Last")
    {
        current_date = end_date;
    }
    else
    {
        std::cout << "Invalid end method" << std::endl;
    }
    #endif
    // DateType current_date = current_time.date();
    TimeType final_threshold_time = TimeType(current_date, threshold_time);

    if (current_time > final_threshold_time)
    {
        this->crossed_threshold_time = true;
    }
    else
    {
        this->crossed_threshold_time = false;
    }

    if(crossed_threshold_time)
    {
        
     int current_inventory = portfolio().position(&instrument);

     #ifdef IchimokuATRDebugMessages
            // #pragma message("IchimokuATRDebugMessages given: " TOSTRING(IchimokuATRDebugMessages))

        bool debug_message = IchimokuATRDebugMessages;
        if (debug_message)
        {
            std::cout << "Threshold time crossed" << 
            "- Current inventory: " << current_inventory<<std::endl;
        }
        #endif
    if (current_inventory > 0)
        {

                #ifdef IchimokuATRDebugMessages
                // #pragma message("IchimokuATRDebugMessages given: " TOSTRING(IchimokuATRDebugMessages))

                // bool debug_message = IchimokuATRDebugMessages;
                if (debug_message)
                {
                    std::cout << "Found positive current_inventory, sending sell order" << std::endl;
                }
                #endif
                OrderParams params(instrument,
                       abs(current_inventory),
                       instrument.top_quote().bid(),
                       MARKET_CENTER_ID_IEX,
                       (current_inventory > 0) ? ORDER_SIDE_SELL : ORDER_SIDE_BUY,
                       ORDER_TIF_DAY,
                       ORDER_TYPE_MARKET);

                const Order* order = *orders().working_orders_begin(&instrument);

                for(auto it = orders().working_orders_begin(&instrument); it != orders().working_orders_end(&instrument); ++it)
                {
                    
                    trade_actions()->SendCancelOrder((*it)->order_id());
                    
                }


                // if (order && ((IsBuySide(order->order_side()) ) || 
                //                 ((IsSellSide(order->order_side()))))) {
                //     trade_actions()->SendCancelOrder(order->order_id());
                //     // we're avoiding sending out a new order for the other side immediately to simplify the logic to the case where we're only tracking one order per instrument at any given time
                // }

                trade_actions()->SendNewOrder(params);
            
        }
        else if (current_inventory < 0)
        {

            #ifdef IchimokuATRDebugMessages
                // #pragma message("IchimokuATRDebugMessages given: " TOSTRING(IchimokuATRDebugMessages))

                // bool debug_message = IchimokuATRDebugMessages;
                if (debug_message)
                {
                    std::cout << "Found negative current_inventory, sending buy order" << std::endl;
                }
            #endif
            OrderParams params(instrument,
                       abs(current_inventory),
                       instrument.top_quote().ask(),
                       MARKET_CENTER_ID_IEX,
                       (current_inventory > 0) ? ORDER_SIDE_SELL : ORDER_SIDE_BUY,
                       ORDER_TIF_DAY,
                       ORDER_TYPE_MARKET);

            for(auto it = orders().working_orders_begin(&instrument); it != orders().working_orders_end(&instrument); ++it)
            {
                
                trade_actions()->SendCancelOrder((*it)->order_id());
                
            }

            trade_actions()->SendNewOrder(params);
        }
        else
        {
            #ifdef IchimokuATRDebugMessages
            // #pragma message("IchimokuATRDebugMessages given: " TOSTRING(IchimokuATRDebugMessages))

            // bool debug_message = IchimokuATRDebugMessages;
            if (debug_message)
            {
                std:cout << "No inventory to close, and crossed threshold time" << std::endl;
            }
            #endif
            return ;
        }
    }
    else{


    if(candlestickQueue.size() < candlestickQueue.get_long_window_size())
    {
        // std::cout << "checkpoint 0.1" << std::endl;
        candlestickQueue.addCandlestick(current_candlestick);
        current_candlestick.reset();
        current_candlestick.set_open_price(msg.trade().price());
        return;
    }
    else
    {
        
        double previous_CL = (candlestickQueue.highest_high_short() + candlestickQueue.lowest_low_short())/2;
        double previous_BL = (candlestickQueue.highest_high_mid() + candlestickQueue.lowest_low_mid())/2;

        bool candle_is_added = candlestickQueue.addCandlestick(current_candlestick);
        
        if(candle_is_added)
        {
            double ATR_constant = 0.5;
            double current_CL = (candlestickQueue.highest_high_short() + candlestickQueue.lowest_low_short())/2;
            double current_BL = (candlestickQueue.highest_high_mid() + candlestickQueue.lowest_low_mid())/2;
            double ATR_short = candlestickQueue.average_true_range_short();
            double ATR_mid = candlestickQueue.average_true_range_mid();

            // Using ATR, predict the next candlestick's BL and CL
            double predictive_CL = (std::max(candlestickQueue.highest_high_short_minus_one(), candlestickQueue.get_most_recent_close_price()+ATR_short*ATR_constant) + std::min(candlestickQueue.lowest_low_short_minus_one(), candlestickQueue.get_most_recent_close_price()-ATR_short*ATR_constant))/2;
            double predictive_BL = (std::max(candlestickQueue.highest_high_mid_minus_one(), candlestickQueue.get_most_recent_close_price()+ATR_mid*ATR_constant) + std::min(candlestickQueue.lowest_low_mid_minus_one(), candlestickQueue.get_most_recent_close_price()-ATR_mid*ATR_constant))/2;

            // Buy Side 
            double top_quote_ask = instrument.top_quote().ask();    
            double top_quote_bid = instrument.top_quote().bid();

            // Non-predictive signal
            // bool buy_signal = previous_CL < previous_BL && current_CL > current_BL;
            // bool sell_signal = previous_CL > previous_BL && current_CL < current_BL;


            // predictive signal - If BL/CL crossover predicted, send signal
            bool buy_signal = current_CL < current_BL && predictive_CL > predictive_CL;
            bool sell_signal = current_CL > current_BL && predictive_CL < predictive_BL;


            // bool buy_signal = current_short_MA > current_mid_MA && (top_quote_ask - top_quote_bid) < ATR_short;
            // bool sell_signal= current_short_MA < current_mid_MA && (top_quote_ask - top_quote_bid) < ATR_short;

            if(buy_signal)
            {
                
                const Order* order = *orders().working_orders_begin(&instrument);
                int counter = 0;
                for(auto it = orders().working_orders_begin(&instrument); it != orders().working_orders_end(&instrument); ++it)
                {
                    
                    trade_actions()->SendCancelOrder((*it)->order_id());
                    counter +=1;
                    
                }
                std::cout << "Buy Signal" << std::endl;
                // std::cout << "previous_short_MA: " << previous_short_MA << std::endl;
                // std::cout << "previous_mid_MA: " << previous_mid_MA << std::endl;
                // std::cout << "current_short_MA: " << current_short_MA << std::endl;
                // std::cout << "current_mid_MA: " << current_mid_MA << std::endl;
                this->MakeOrder(instrument,1);
            }
            else if (sell_signal)
            {
                const Order* order = *orders().working_orders_begin(&instrument);
                int counter = 0;
                for(auto it = orders().working_orders_begin(&instrument); it != orders().working_orders_end(&instrument); ++it)
                {
                    
                    trade_actions()->SendCancelOrder((*it)->order_id());
                    counter += 1;
                    
                }
                std::cout << "Sell Signal" << std::endl;
                // std::cout << "previous_short_MA: " << previous_short_MA << std::endl;
                // std::cout << "previous_mid_MA: " << previous_mid_MA << std::endl;
                // std::cout << "current_short_MA: " << current_short_MA << std::endl;
                // std::cout << "current_mid_MA: " << current_mid_MA << std::endl;
                this->MakeOrder(instrument,-1);
            }
            else if ( !(buy_signal || sell_signal))
            {
                // std::cout << " No Signal" << std::endl;
            }

        }

        current_candlestick.reset();
        current_candlestick.set_open_price(msg.trade().price());
    }
    } 
}

void IchimokuATR::OnBar(const BarEventMsg& msg)
{ 
    // std::cout << "RUNNING ONBAR" << std::endl;
    // const Instrument* instrument = &msg.instrument();
    // if (debug_) {
    //     ostringstream str;
    //     str << instrument->symbol() << ": " << msg.bar();
    //     logger().LogToClient(LOGLEVEL_DEBUG, str.str().c_str());
    // }

    // //check if we're already tracking the momentum object for this instrument, if not create a new one
    // RegimeMapIterator regime_iter = regime_map_.find(instrument);
    // if (regime_iter == regime_map_.end()) {
    //     regime_iter = regime_map_.insert(make_pair(instrument, MarketRegime(short_window_size_, long_window_size_))).first;
    // }

    // double side = regime_iter->second.Update(msg.bar().close());
    // target_time = msg.bar_time();
    // if (regime_iter->second.FullyInitialized()) {
    //     if (side > i_threshold_min * instrument->min_tick_size()){
    //         cout << "Bullish State" << endl;
    //         target_inventory = CalculateTargetInventory(instrument,side);
    //     } else if (side < -i_threshold_min * instrument->min_tick_size()){
    //         cout << "Bearish State" << endl;
    //         target_inventory = CalculateTargetInventory(instrument,side);
    //     } else {
    //         cout << "Range_Bound" << endl;
    //         target_inventory = 0;
    //     }
    // cout << "target_inventory :- " << target_inventory << endl;
    // AddSecondsToTimeType(target_time,1);
    // cout << "target_time:- " << target_time << endl;
    // }
}

void IchimokuATR::OnQuote(const QuoteEventMsg& msg)
{
    /*
        Step 1. Keep track of the best bid and best ask 
    */
//    std::cout << "RUNNING ONQUOTE" << std::endl;

   if (current_candlestick.is_open())
   {
        const Quote& quote = msg.quote();
        current_candlestick.set_quote(quote);
   }
    // #ifdef DEB
    //     std::cout << "current_candlestick: " << current_candlestick << std::endl;
    // #endif
//    std::cout << "current_candlestick: " << current_candlestick << std::endl;
   
}

double IchimokuATR::CalculateInventoryGap(const Instrument* instrument)
{
    int current_inventory = portfolio().position(instrument);
    return (target_inventory - current_inventory);
}

int IchimokuATR::CalculateTargetInventory(const Instrument* instrument,double indicator)
{
    // double indicator_scale = min(indicator/instrument->min_tick_size(),double(i_threshold_max))/(i_threshold_max - i_threshold_min);
    // int target = int(indicator_scale*position_size_);
    // return target;
}

void IchimokuATR::OnOrderUpdate(const OrderUpdateEventMsg& msg){}

double IchimokuATR::TimeDifferenceInMicroseconds(TimeType time1, TimeType time2)
{
    // Convert the TimeType objects to microsecond precision if needed
    TimeType t1_microsec = boost::posix_time::time_from_string(boost::posix_time::to_iso_extended_string(time1) + ".000");
    TimeType t2_microsec = boost::posix_time::time_from_string(boost::posix_time::to_iso_extended_string(time2) + ".000");

    // Calculate the difference in microseconds
    boost::posix_time::time_duration diff = t2_microsec - t1_microsec;
    return diff.total_microseconds();
}

double IchimokuATR::NormalisedTime(TimeType time1)
{
    double t1 = TimeDifferenceInMicroseconds(time1, target_time);
    return t1/time_interval;
}

void IchimokuATR::MakeOrder(const Instrument& instrument, int action_type)
{
    // std::cout << "Called makeorder" << std::endl;
    int current_position = portfolio().position(&instrument);
    auto all_buy_orders = orders().stats().long_working_order_size();
    auto all_sell_orders = orders().stats().short_working_order_size();
    // auto long_order_pending = orders().stats().long_working_order_size();
    auto filled_orders = orders().stats().num_orders_filled();
    
    int num_working_orders = orders().num_working_orders(&instrument);
    int trade_size = action_type == 1 ? position_size_ * constant_fraction_position : -position_size_ * constant_fraction_position;
    
    
    #ifdef IchimokuATRDebugMessages
            // #pragma message("IchimokuATRDebugMessages given: " TOSTRING(IchimokuATRDebugMessages))

    bool debug_message = IchimokuATRDebugMessages;
    if (debug_message)
    {
        std:cout << "Bid act count: " << bid_act_count << "\t" <<
        std::endl;
    }
    #endif
    

    if (action_type == 1)
        {
            SendOrder(&instrument, 50);
            // std::cout << "filled orders: " << filled_orders << std::endl;
            SendOrder(&instrument, -50, false);
            bid_act_count += 1;
        }
    else
    {
        SendOrder(&instrument, 50, false);
    
        SendOrder(&instrument, -50);
        ask_act_count += 1;
    }    
   

}

void IchimokuATR::AdjustPortfolio(const Instrument* instrument, int desired_position)
{
    // total_stock_position = portfolio().position(instrument);
    // if (total_stock_position == 0)
    // if (trade_size != 0) {
    //     // if we're not working an order for the instrument already, place a new order
    //     if (orders().num_working_orders(instrument) == 0) {
    //         SendOrder(instrument, trade_size);
    //     } else {  
    //         // otherwise find the order and cancel it if we're now trying to trade in the other direction
    //         const Order* order = *orders().working_orders_begin(instrument);
    //         if (order && ((IsBuySide(order->order_side()) && trade_size < 0) || 
    //                      ((IsSellSide(order->order_side()) && trade_size > 0)))) {
    //             trade_actions()->SendCancelOrder(order->order_id());
    //             // we're avoiding sending out a new order for the other side immediately to simplify the logic to the case where we're only tracking one order per instrument at any given time
    //         }
    //     }
    // }
}

void IchimokuATR::SendOrder(const Instrument* instrument, int trade_size, bool flag = true, double spread_tick = 0.05)
{
      
    if (!instrument->top_quote().ask_side().IsValid() || !instrument->top_quote().ask_side().IsValid()) {
            std::stringstream ss;
            ss << "Skipping trade due to lack of two sided quote"; 
            logger().LogToClient(LOGLEVEL_DEBUG, ss.str());
            return;
        }
    const Trade& last_trade = instrument->last_trade();
    // double closing_price_last_trade = last_trade.price();
    double agg_bid = candlestickQueue.GetAggression(instrument->top_quote().bid(), false);
    double agg_ask = candlestickQueue.GetAggression(instrument->top_quote().ask(), true);
    double spread_final_ask = agg_ask >= spread_tick ? agg_ask + spread_tick : spread_tick;
    double spread_final_bid = agg_bid >= spread_tick ? agg_bid + spread_tick : spread_tick;

    #ifdef SpreadTick
    #pragma message("SpreadTick given: " TOSTRING(SpreadTick))
    // std::string spreadTickStr = SpreadTick;
    spread_tick = SpreadTick;
    // std::cout << "spread_tick: " << spread_tick << std::endl;
    #endif

    // bool is_ask_side =last_trade.is_ask_side();
    // std::cout << "Send Order called" << std::endl;
    double price;

    #ifdef IchimokuATRDebugMessages
    bool debug_message = IchimokuATRDebugMessages;
    if (debug_message)
    {
        std::cout << "Entered SendOrder()" << " Flag: " << flag << std::endl;
    }
    #endif


    //For each buy or sell signal, flag provides the information whether we are placing the main order (true) or the corresponding directional trade (false)
    if (flag)
    {
        price = trade_size > 0 ? std::round((instrument->top_quote().bid() + agg_bid) * 100)/100: round((instrument->top_quote().ask() - agg_ask) *100)/100;
        // std::cout << "price" << price << std::endl;
    }
    else
    {
        price = trade_size > 0 ? round((instrument->top_quote().bid() - spread_final_bid)*100)/100: round(instrument->top_quote().ask() + spread_final_ask * 100)/100;
        // std::cout << "agg_bid: " << agg_bid << std::endl;
    }

    #ifdef IchimokuATRDebugMessages
    if (debug_message)
    {
        std::cout << "Price calculated:  " << price << 
        std::endl;
    }
    #endif

    OrderParams params(*instrument,
                       abs(trade_size),
                       price,
                       MARKET_CENTER_ID_IEX,
                       (trade_size > 0) ? ORDER_SIDE_BUY : ORDER_SIDE_SELL,
                       ORDER_TIF_DAY,
                       ORDER_TYPE_LIMIT);

    double std_current_closing_prices = candlestickQueue.get_standard_deviation_short_window();
        
    trade_actions()->SendNewOrder(params);
}

void IchimokuATR::RepriceAll()
{
    for (IOrderTracker::WorkingOrdersConstIter ordit = orders().working_orders_begin(); ordit != orders().working_orders_end(); ++ordit) {
        Reprice(*ordit);
    }
}

void IchimokuATR::Reprice(Order* order)
{
    OrderParams params = order->params();
    params.price = (order->order_side() == ORDER_SIDE_BUY) ? order->instrument()->top_quote().bid() + aggressiveness_ : order->instrument()->top_quote().ask() - aggressiveness_;
    trade_actions()->SendCancelReplaceOrder(order->order_id(), params);
}

void IchimokuATR::OnStrategyCommand(const StrategyCommandEventMsg& msg)
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

void IchimokuATR::OnParamChanged(StrategyParam& param)
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

