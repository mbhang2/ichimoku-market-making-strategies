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

#include "MVWAP.h"
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

#define STRINGIZE(x) #x
#define TO_STRING(x) STRINGIZE(x)

// using namespace RCM::StrategyStudio::Utilities::TimeType;
using namespace std;
int total_trades = 0;
int buy_trades = 0;
int sell_trades = 0;
int bid_act_count = 0;
int ask_act_count = 0;

MVWAP::MVWAP(StrategyID strategyID, const std::string& strategyName, const std::string& groupName):
    Strategy(strategyID, strategyName, groupName),
    candlestickQueue(5,15,17),
    regime_map_(),    
    aggressiveness_(0),
    position_size_(5),
    constant_fraction_position(1),
    time_interval(1),
    debug_(false),
    short_window_size_(9),
    medium_window_size_(26),
    long_window_size_(30),
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
    
    // #ifdef Aggression
    // #pragma message("Aggressiveness given: " Aggression)
    // std::string aggressivenessStr = Aggression;
    // double temp_aggressiveness = std::stod(aggressivenessStr);
    // aggressiveness_ = temp_aggressiveness;
    // std::cout << "Aggressiveness set to: " << aggressiveness_ << std::endl;
    // #endif

    #ifdef AggressionMultiplier
    #pragma message("AggressionMultiplier given: " TO_STRING(AggressionMultiplier))
    // std::string aggressionMultiplierStr = AggressionMultiplier;
    double temp_aggression_multiplier = AggressionMultiplier;
    this->aggression_multiplier = temp_aggression_multiplier;
    std::cout << "Aggression multiplier set to: " << aggression_multiplier << std::endl;
    #endif

    #ifdef SpreadTick
    #pragma message("SpreadTick given: " TO_STRING(SpreadTick))
    // std::string spreadTickStr = SpreadTick;
    double temp_spread_tick = SpreadTick;
    this->spread_tick_value = temp_spread_tick;
    std::cout << "Spread tick set to: " << spread_tick_value << std::endl;
    #endif

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

MVWAP::~MVWAP(){}


void MVWAP::OnResetStrategyState()
{
    regime_map_.clear();
}

void MVWAP::DefineStrategyParams()
{
    params().CreateParam(CreateStrategyParamArgs("aggressiveness", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_DOUBLE, aggressiveness_));
    params().CreateParam(CreateStrategyParamArgs("position_size", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_INT, position_size_));
    params().CreateParam(CreateStrategyParamArgs("short_window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, short_window_size_));
    params().CreateParam(CreateStrategyParamArgs("long_window_size", STRATEGY_PARAM_TYPE_STARTUP, VALUE_TYPE_INT, long_window_size_));
    params().CreateParam(CreateStrategyParamArgs("debug", STRATEGY_PARAM_TYPE_RUNTIME, VALUE_TYPE_BOOL, debug_));
}


void MVWAP::DefineStrategyCommands()
{
    commands().AddCommand(StrategyCommand(1, "Reprice Existing Orders"));
    commands().AddCommand(StrategyCommand(2, "Cancel All Orders"));
}

void MVWAP::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate)
{    
    std::cout << "Called Event register" << std::endl;
    // for (SymbolSetConstIter it = symbols_begin(); it != symbols_end(); ++it) {
    //     eventRegister->RegisterForBars(*it, BAR_TYPE_TIME, time_interval);
    // }
}

void MVWAP::OnDepth(const MarketDepthEventMsg& msg){}

void MVWAP::OnTrade(const TradeDataEventMsg& msg)
{
    // std::cout << "On trade called" << std::endl;

    const Instrument& instrument = msg.instrument();
    int num_working_orders = orders().num_working_orders(&instrument);
    int num_of_open_trades = trades().num_open_trades(&instrument);
    int num_of_closed_trades = trades().num_closed_trades(&instrument);
    auto filled_orders = orders().stats().num_orders_filled();


    #ifdef MVWAPDebugMessages
                // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

        bool debug_message = MVWAPDebugMessages;
        if (debug_message)
        {
            std::cout << "Number of working orders: " << num_working_orders << "\t" <<
            " Number of filled orders: " << filled_orders << "\t" <<
            "Number of open trades: " << num_of_open_trades << "\t" <<
            "Number of closed trades: " << num_of_closed_trades << std::endl;
        }
    #endif


    current_candlestick.set_close_price(msg.trade().price());


    TimeType current_time = msg.source_time();
    DateType current_date = current_time.date();
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

     #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

        bool debug_message = MVWAPDebugMessages;
        if (debug_message)
        {
            std::cout << "Threshold time crossed" << 
            "- Current inventory: " << current_inventory<<std::endl;
        }
        #endif

        if (current_inventory > 0)
        {

                #ifdef MVWAPDebugMessages
                // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

                // bool debug_message = MVWAPDebugMessages;
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

            #ifdef MVWAPDebugMessages
                // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

                // bool debug_message = MVWAPDebugMessages;
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
            #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

            // bool debug_message = MVWAPDebugMessages;
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
        
            double previous_short_MA = candlestickQueue.moving_vwap_short();
        // std::cout << "checkpoint 0.6" << std::endl;
        double previous_mid_MA = candlestickQueue.moving_vwap_medium();

        

        bool candle_is_added = candlestickQueue.addCandlestick(current_candlestick);

        if(candle_is_added)
        {
            // std::cout << "checkpoint 2" << std::endl;
            double current_short_MA = candlestickQueue.moving_vwap_short();
            double current_mid_MA = candlestickQueue.moving_vwap_medium();

            // Buy Side 

            bool sell_signal= previous_short_MA < previous_mid_MA && current_short_MA > current_mid_MA;
            bool buy_signal= previous_short_MA > previous_mid_MA && current_short_MA < current_mid_MA;

            if(buy_signal)
            {
                #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

                bool debug_message = MVWAPDebugMessages;
                if (debug_message)
                {
                    std::cout << "Buy signal sent" << std::endl;
                }
                #endif

                const Order* order = *orders().working_orders_begin(&instrument);
                int counter = 0;
                for(auto it = orders().working_orders_begin(&instrument); it != orders().working_orders_end(&instrument); ++it)
                {
                    
                    trade_actions()->SendCancelOrder((*it)->order_id());
                    counter +=1;
                    
                }

                #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

                // bool debug_message = MVWAPDebugMessages;
                if (debug_message)
                {
                    std::cout << "Cancelled " << counter << " orders inside buy signal" <<
                    std::endl;
                }
                #endif
                // if (order && ((IsBuySide(order->order_side()) ) || 
                //                 ((IsSellSide(order->order_side()))))) {
                //     trade_actions()->SendCancelOrder(order->order_id());
                //     // we're avoiding sending out a new order for the other side immediately to simplify the logic to the case where we're only tracking one order per instrument at any given time
                // }
                // std::cout << "Buy Signal" << std::endl;
                // std::cout << "previous_short_MA: " << previous_short_MA << std::endl;
                // std::cout << "previous_mid_MA: " << previous_mid_MA << std::endl;
                // std::cout << "current_short_MA: " << current_short_MA << std::endl;
                // std::cout << "current_mid_MA: " << current_mid_MA << std::endl;
                this->MakeOrder(instrument,1);
            }
            else if (sell_signal)
            {

                 #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

                // bool debug_message = MVWAPDebugMessages;
                if (debug_message)
                {
                    std::cout << "Sell signal sent" << std::endl;
                }
                #endif
                const Order* order = *orders().working_orders_begin(&instrument);
                int counter = 0;
                for(auto it = orders().working_orders_begin(&instrument); it != orders().working_orders_end(&instrument); ++it)
                {
                    
                    trade_actions()->SendCancelOrder((*it)->order_id());
                    counter += 1;
                    
                }

                #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

                bool debug_message = MVWAPDebugMessages;
                if (debug_message)
                {
                    std::cout << "Cancelled " << counter << " orders inside sell signal" <<
                    std::endl;
                }
                #endif

                

                // if (order && ((IsBuySide(order->order_side())) || 
                //                 ((IsSellSide(order->order_side()))))) {
                //     trade_actions()->SendCancelOrder(order->order_id());
                //     // we're avoiding sending out a new order for the other side immediately to simplify the logic to the case where we're only tracking one order per instrument at any given time
                // }
               
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

    // #ifdef MVWAPDebugMessages
    // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

    // bool debug_message = MVWAPDebugMessages;
    // if (debug_message)
    // {
    //     std::cout << "Last source time: " << current_time << 
    //         "Final Threshold time: " << final_threshold_time << 
    //         "Source crossed threshold: " << (msg.source_time() > final_threshold_time) << std::endl;
    // }
    // #endif


    // std::cout << "checkpoint 0" << std::endl;
    
    // candlestickQueue.print_high_asks();
    // candlestickQueue.print_close_prices();

    

        
    
}



void MVWAP::OnBar(const BarEventMsg& msg)
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

void MVWAP::OnQuote(const QuoteEventMsg& msg)
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

double MVWAP::CalculateInventoryGap(const Instrument* instrument)
{
     int current_inventory = portfolio().position(instrument);
     return (target_inventory - current_inventory);
}

int MVWAP::CalculateTargetInventory(const Instrument* instrument,double indicator)
{
    // double indicator_scale = min(indicator/instrument->min_tick_size(),double(i_threshold_max))/(i_threshold_max - i_threshold_min);
    // int target = int(indicator_scale*position_size_);
    // return target;
}

void MVWAP::OnOrderUpdate(const OrderUpdateEventMsg& msg){}

double MVWAP::TimeDifferenceInMicroseconds(TimeType time1, TimeType time2)
{
    // Convert the TimeType objects to microsecond precision if needed
    TimeType t1_microsec = boost::posix_time::time_from_string(boost::posix_time::to_iso_extended_string(time1) + ".000");
    TimeType t2_microsec = boost::posix_time::time_from_string(boost::posix_time::to_iso_extended_string(time2) + ".000");

    // Calculate the difference in microseconds
    boost::posix_time::time_duration diff = t2_microsec - t1_microsec;
    return diff.total_microseconds();
}

double MVWAP::NormalisedTime(TimeType time1)
{
    double t1 = TimeDifferenceInMicroseconds(time1, target_time);
    return t1/time_interval;
}

void MVWAP::MakeOrder(const Instrument& instrument, int action_type)
{
    // std::cout << "Called makeorder" << std::endl;
    int current_position = portfolio().position(&instrument);
    auto all_buy_orders = orders().stats().long_working_order_size();
    auto all_sell_orders = orders().stats().short_working_order_size();
    // auto long_order_pending = orders().stats().long_working_order_size();
    auto filled_orders = orders().stats().num_orders_filled();
    
    int num_working_orders = orders().num_working_orders(&instrument);
    int trade_size = action_type == 1 ? position_size_ * constant_fraction_position : -position_size_ * constant_fraction_position;
    
    // if (num_working_orders > 0)
    // {
    //     const Order* order = *orders().working_orders_begin(&instrument);
    //     if (order && ((IsBuySide(order->order_side()) && trade_size > 0) || 
    //                     ((IsSellSide(order->order_side()) && trade_size < 0)))) {
    //         trade_actions()->SendCancelOrder(order->order_id());
    //         // we're avoiding sending out a new order for the other side immediately to simplify the logic to the case where we're only tracking one order per instrument at any given time
    //     }
    // }
    // std::cout << "Stock Position: " << current_position << std::endl;
    // std::cout << "short_order_pending: " << all_sell_orders << std::endl;
    // std::cout << "all_buy_orders: " << all_buy_orders << std::endl;
    // std::cout << "all_sell_orders: " << all_sell_orders << std::endl;
    #ifdef MVWAPDebugMessages
            // #pragma message("MVWAPDebugMessages given: " TOSTRING(MVWAPDebugMessages))

    bool debug_message = MVWAPDebugMessages;
    if (debug_message)
    {
        std:cout << "Bid act count: " << bid_act_count << "\t" <<
        std::endl;
    }
    #endif
    

    if (action_type == 1)
        {
            SendOrder(&instrument, trade_size);
            // std::cout << "filled orders: " << filled_orders << std::endl;
            SendOrder(&instrument, -trade_size, false);
            bid_act_count += 1;
        }
    else
    {
        SendOrder(&instrument, trade_size);
    
        SendOrder(&instrument, -trade_size, false);
        ask_act_count += 1;
    }    
    // if (current_position == 0)
    // {
    //     if (action_type == 1)
    //     {
    //         SendOrder(&instrument, position_size_);
            
    //     }
    //     else
    //     {
    //         SendOrder(&instrument, -position_size_);
    //     }
    //     // total_stock_position += position_size_;
    //     // total_trades += 1;
    // }

    // if (current_position > 0)
    // {       
    //     if (action_type == 1)
    //     {
    //         SendOrder(&instrument, trade_size);
    //         // total_stock_position += trade_size;
    //         // total_trades += 1;
    //     }
    //     if (action_type == -1)
    //     {
            
    //         if (current_position > -trade_size)
    //         {
    //             SendOrder(&instrument, trade_size);
    //             // total_stock_position -= position_size_;
    //             // total_trades += 1;
    //         }
    //         else
    //         {
    //             SendOrder(&instrument, -current_position);
    //             // total_stock_position -= current_position;
    //             // total_trades += 1;
    //         }
    //         // SendOrder(&instrument, -position_size_* constant_fraction_position);
    //     }
    // }

}

void MVWAP::AdjustPortfolio(const Instrument* instrument, int desired_position)
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

void MVWAP::SendOrder(const Instrument* instrument, int trade_size, bool flag = true, double spread_tick = 0.05)
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


    #ifdef SpreadTick
    #pragma message("SpreadTick given: " TOSTRING(SpreadTick))
    // std::string spreadTickStr = SpreadTick;
    double temp_spread_tick = SpreadTick;
    this->spread_tick_value = temp_spread_tick;
    spread_tick = this->spread_tick_value;
    // std::cout << "spread_tick: " << spread_tick << std::endl;
    #endif
    double spread_final_ask = agg_ask >= spread_tick ? agg_ask + spread_tick : spread_tick;
    double spread_final_bid = agg_bid >= spread_tick ? agg_bid + spread_tick : spread_tick;

    // bool is_ask_side =last_trade.is_ask_side();
    // std::cout << "Send Order called" << std::endl;
    double price;

    #ifdef MVWAPDebugMessages
    bool debug_message = MVWAPDebugMessages;
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

    #ifdef MVWAPDebugMessages
    if (debug_message)
    {
        std::cout << "Price calculated:  " << price << 
        std::endl;
    }
    #endif



    // bool is_ask_side =last_trade.is_ask_side();
    // std::cout << "Send Order called" << std::endl;
    // double price = trade_size > 0 ? instrument->top_quote().bid() + std::round(candlestickQueue.GetAggression(closing_price_last_trade, false)*100)/100 : instrument->top_quote().ask() - round(candlestickQueue.GetAggression(closing_price_last_trade, true)*100)/100;
    // double price = trade_size > 0 ? (1-stop_loss_param)*(instrument->top_quote().bid()) : (1+stop_loss_param)*(instrument->top_quote().ask()) ;

    OrderParams params(*instrument,
                       abs(trade_size),
                       price,
                       MARKET_CENTER_ID_IEX,
                       (trade_size > 0) ? ORDER_SIDE_BUY : ORDER_SIDE_SELL,
                       ORDER_TIF_DAY,
                       ORDER_TYPE_LIMIT);

    double std_current_closing_prices = candlestickQueue.get_standard_deviation_short_window();

    // double stop_price = trade_size > 0 ? price  + std_current_closing_prices : price - std_current_closing_prices;
    // params.stop_price = stop_price;

    
    // std::cout << "Sell side aggression: " << candlestickQueue.GetAggression(closing_price_last_trade, true) << std::endl;
    // std::cout << "Buy side aggression: " << candlestickQueue.GetAggression(closing_price_last_trade, false) << std::endl;
    // std::string side = trade_size > 0 ? "Buy" : "Sell";
    // std::cout << "Stop price: " << stop_price << ", Side: " << side << std::endl;
    // std::cout << "price: " << price << std::endl;
    // params.stop_price =  
    // Print a message indicating that a new order is being sent
    // std::cout << "SendTradeOrder(): about to send new order for size "
    //         << trade_size
    //         << " at $"
    //         << price
    //         << " for symbol "
    //         << instrument->symbol()
    //         << std::endl;
        
        trade_actions()->SendNewOrder(params);

}

void MVWAP::RepriceAll()
{
    for (IOrderTracker::WorkingOrdersConstIter ordit = orders().working_orders_begin(); ordit != orders().working_orders_end(); ++ordit) {
        Reprice(*ordit);
    }
}

void MVWAP::Reprice(Order* order)
{
    OrderParams params = order->params();
    params.price = (order->order_side() == ORDER_SIDE_BUY) ? order->instrument()->top_quote().bid() + aggressiveness_ : order->instrument()->top_quote().ask() - aggressiveness_;
    trade_actions()->SendCancelReplaceOrder(order->order_id(), params);
}

void MVWAP::OnStrategyCommand(const StrategyCommandEventMsg& msg)
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

void MVWAP::OnParamChanged(StrategyParam& param)
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
