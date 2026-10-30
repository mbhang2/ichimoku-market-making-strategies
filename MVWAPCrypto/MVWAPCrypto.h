#pragma once

#ifndef _STRATEGY_STUDIO_LIB_MVWAPCrypto_H_
#define _STRATEGY_STUDIO_LIB_MVWAPCrypto_H_

#ifdef _WIN32
    #define _STRATEGY_EXPORTS __declspec(dllexport)
#else
    #ifndef _STRATEGY_EXPORTS
    #define _STRATEGY_EXPORTS
    #endif
#endif

#include <Strategy.h>
// #include "group_02_utils.h"
// #include <Analytics/ScalarRollingWindow.h>
// #include <Analytics/InhomogeneousOperators.h>
// #include <Analytics/IncrementalEstimation.h>
#include "group_02_utils.h"
#include "TradeRecord.h"
#include "ITradeTracker.h"
// #include <Utilities/ParseConfig.h>



#include <vector>
#include <map>
#include <iostream>

using namespace RCM::StrategyStudio;
using namespace RCM::StrategyStudio::MarketModels;

class MarketRegime {
public:
    MarketRegime(int short_window_size = 10, int long_window_size = 30) : short_window_(short_window_size), long_window_(long_window_size) {}

    void Reset()
    {
        short_window_.clear();
        long_window_.clear();
    }

    double Update(double val)
    {
        short_window_.push_back(val);
        long_window_.push_back(val);
        return short_window_.Mean() - long_window_.Mean();
    }

    bool FullyInitialized() { return (short_window_.full() && long_window_.full()); }
    
    Analytics::ScalarRollingWindow<double> short_window_;
    Analytics::ScalarRollingWindow<double> long_window_;
};

class MVWAPCrypto : public Strategy {
public:
    typedef boost::unordered_map<const Instrument*, MarketRegime> RegimeMap; 
    // creates an unordered map where keys are instrument names and values are corresponding classes 
    // all these pairs are set to a map called MomentumMap
    typedef RegimeMap::iterator RegimeMapIterator; 
    // CandlestickQueue candlestickQueue;
    CandlestickQueue candlestickQueue;
    Candlestick current_candlestick;
    ITradeTracker* trade_tracker;
    // DateType current_date;
    TimeDuration threshold_time;
    bool crossed_threshold_time;
    // we define an iterator that iterates through these key value pairs 

public:
    MVWAPCrypto(StrategyID strategyID, const std::string& strategyName, const std::string& groupName);
    
    ~MVWAPCrypto();

public: /* from IEventCallback */
    /**
     * This event triggers whenever trade message arrives from a market data source.
     */ 
    virtual void OnTrade(const TradeDataEventMsg& msg);

    /**
     * This event triggers whenever aggregate volume at best price changes, based 
     * on the best available source of liquidity information for the instrument.
     *
     * If the quote datasource only provides ticks that change the NBBO, top quote will be set to NBBO
     */ 
    virtual void OnTopQuote(const QuoteEventMsg& msg){}
    
    /**
     * This event triggers whenever a new quote for a market center arrives from a consolidate or direct quote feed,
     * or when the market center's best price from a depth of book feed changes.
     *
     * User can check if quote is from consolidated or direct, or derived from a depth feed. This will not fire if
     * the data source only provides quotes that affect the official NBBO, as this is not enough information to accurately
     * mantain the state of each market center's quote.
     */ 
    virtual void OnQuote(const QuoteEventMsg& msg);
    
    /**
     * This event triggers whenever a order book message arrives. This will be the first thing that
     * triggers if an order book entry impacts the exchange's DirectQuote or Strategy Studio's TopQuote calculation.
     */ 
    virtual void OnDepth(const MarketDepthEventMsg& msg);

    /**
     * This event triggers whenever a Bar interval completes for an instrument
     */ 
    virtual void OnBar(const BarEventMsg& msg);

    /**
     * This event contains alerts about the state of the market
     */
    virtual void OnMarketState(const MarketStateEventMsg& msg){}

    /**
     * This event triggers whenever new information arrives about a strategy's orders
     */ 
    virtual void OnOrderUpdate(const OrderUpdateEventMsg& msg);

    /**
     * This event contains strategy control commands arriving from the Strategy Studio client application (eg Strategy Manager)
     */ 
    virtual void OnStrategyControl(const StrategyStateControlEventMsg& msg){}

    /**
     *  Perform additional reset for strategy state 
     */
    void OnResetStrategyState();

    /**
     * This event contains alerts about the status of a market data source
     */ 
    void OnDataSubscription(const DataSubscriptionEventMsg& msg){}

    /**
     * This event triggers whenever a custom strategy command is sent from the client
     */ 
    void OnStrategyCommand(const StrategyCommandEventMsg& msg);

    /**
     * Create Order object for the strategy
     */
    void MakeOrder(const Instrument& instrument, int action_type);

    DateType get_current_date();

    float GetAggression(double current_closing_price);

    /**
     * Notifies strategy for every succesfull change in the value of a strategy parameter.
     *
     * Will be called any time a new parameter value passes validation, including during strategy initialization when default parameter values
     * are set in the call to CreateParam and when any persisted values are loaded. Will also trigger after OnResetStrategyState
     * to remind the strategy of the current parameter values.
     */ 
    void OnParamChanged(StrategyParam& param);

private: // Helper functions specific to this strategy
    void AdjustPortfolio(const Instrument* instrument, int desired_position);
    void SendOrder(const Instrument* instrument, int trade_size, bool flag = true, double spread_tick = 0.05);
    void RepriceAll();
    void Reprice(Order* order);
    double CalculateInventoryGap(const Instrument* instrument);
    int CalculateTargetInventory(const Instrument* instrument,double indicator);
    double TimeDifferenceInMicroseconds(TimeType time1, TimeType time2);
    double NormalisedTime(TimeType time1);

private: /* from Strategy */
    virtual void RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate); 
    
    /**
     * Define any params for use by the strategy 
     */     
    virtual void DefineStrategyParams();

    /**
     * Define any strategy commands for use by the strategy
     */ 
    virtual void DefineStrategyCommands();

private:
    boost::unordered_map<const Instrument*, MarketRegime> regime_map_;
    double aggressiveness_;
    int position_size_;
    int time_interval;
    TimeType target_time;
    int short_window_size_;
    float constant_fraction_position;
    int medium_window_size_;
    int long_window_size_;
    bool debug_;
    int i_threshold_min;
    int i_threshold_max;
    int target_inventory;
    int total_stock_position;


    // Group 02s: code here remove old code later

    bool current_candlestick_open;
    double current_close_next_open;
    double current_highest_ask_price; // High
    double current_lowest_bid_price; // Low

    

};

extern "C" {
    _STRATEGY_EXPORTS const char* GetType()
    {
        return "MVWAPCrypto";
    }

    _STRATEGY_EXPORTS IStrategy* CreateStrategy(const char* strategyType,
                                   unsigned strategyID,
                                   const char* strategyName,
                                   const char* groupName) {
        if (strcmp(strategyType, GetType()) == 0) {
            return *(new MVWAPCrypto(strategyID, strategyName, groupName));
        } else {
            return NULL;
        }
    }

    _STRATEGY_EXPORTS const char* GetAuthor() {
        return "dlariviere";
    }

    _STRATEGY_EXPORTS const char* GetAuthorGroup() {
        return "UIUC";
    }

    _STRATEGY_EXPORTS const char* GetReleaseVersion() {
        return Strategy::release_version();
    }
}

#endif
