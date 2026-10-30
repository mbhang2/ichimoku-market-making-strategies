// Refer to the header files for the explanation of the functions in detail
// In VSCode, hovering your mouse above the function renders the explanation of from the .h file as a pop up
#ifdef _WIN32
    #include "stdafx.h"
#endif

#include "BasicIchimokuStrategy.h"
// #include "BarDataTypes.h"
// #include "QuoteEventMsg.h"
#include <iostream>
// #include "vwap_element.h"

// Constructor to initialize member variables of the class to their initial values.
BasicIchimokuStrategy::BasicIchimokuStrategy(StrategyID strategyID,
                    const std::string& strategyName,
                    const std::string& groupName):
    Strategy(strategyID, strategyName, groupName), rolling_window_(10), 
    vwap_w1(boost::posix_time::time_duration(0,0,5,0)),
    vwap_w2(boost::posix_time::time_duration(0,0,10,0)){

    // Purpose of each variable explained in the header file.
    trade_size_each_time = 10;
	total_stock_position = 0;
	buy_price = 0;
	total_revenue = 0.0;
    total_trade_count = 0;

}

// Destructor for class
BasicIchimokuStrategy::~BasicIchimokuStrategy() {
}

void BasicIchimokuStrategy::DefineStrategyParams() {
}

// By default, SS will register to trades/quotes/depth data for the instruments you have requested via command_line.
void BasicIchimokuStrategy::RegisterForStrategyEvents(StrategyEventRegister* eventRegister, DateType currDate) {
}

void BasicIchimokuStrategy::OnTrade(const TradeDataEventMsg& msg) {
    std::cout << "On trade event occured" << std::endl;
    std::cout << "Total trade count: " << total_trade_count << std::endl;

    // std::cout << "On trade event occured" << std::endl;
    // Element current_element(msg.trade().size(), msg.trade().price(), msg.source_time());
    // std::cout << "Element" << std::endl;
    // std::cout << current_element << std::endl;
    // std::cout << "----------------" << std::endl;

    // std::cout << "VWAP not full yet" << std::endl;
    // std::cout << "Tradetime: " << msg.source_time() << std::endl;
    // std::cout << "Price: " << msg.trade().price() << std::endl;
    // std::cout << "Size: " << msg.trade().size() << std::endl;
    // // auto trade_occured = msg.trade();
    // vwap_w1.Update(msg.source_time(), msg.trade().size(), msg.trade().price());
    // vwap_w2.Update(msg.source_time(), msg.trade().size(), msg.trade().price());
    // // // std::cout << "VWAP full" << std::endl;
    // std::cout << "Print the mean VWAP: " << vwap_w1.Mean() << std::endl;
    // std::cout << "Print the mean VWAP: " << vwap_w2.Mean() << std::endl;

    
    // const Instrument* instrument = &msg.instrument();
    // double bid_price = msg.instrument().top_quote().bid();
    // double ask_price = msg.instrument().top_quote().ask();
    // int market_sell_quantity = msg.instrument().top_quote().bid_size();
    // // int sell_quantity = total_stock_position;
    // int sell_quantity = (market_sell_quantity > total_stock_position) ? total_stock_position : market_sell_quantity;
    // int buy_quantity = msg.instrument().top_quote().ask_size();

    // // If we don't own an stock, buy trade_size_each_time quantity of stock,
    // if (vwap_w1.Mean() >= vwap_w2.Mean()) {
    //     // Send order to matching engine
    //     SendOrder(instrument, sell_quantity, bid_price, 1);
    //     total_stock_position -= sell_quantity;
    //     }
        
    // else {
    //     SendOrder(instrument, buy_quantity, ask_price, 0);
    //     total_stock_position += buy_quantity;
    //     }
    
    // std::cout << "Total stock position: " << total_stock_position << std::endl;
    }
    // if (total_stock_position == 0) {
        
    //     // Send order to matching engine
    //     SendOrder(instrument, trade_size_each_time);
        
    //     // Buying price = level 1 bid price
    //     buy_price = bid_price;
        
    //     // Our total position
    //     total_stock_position += trade_size_each_time;
        
    //     // Reduce total total_revenue because we buy aka cash outflow
    //     total_revenue -= bid_price * trade_size_each_time;    
        
    //     // increment counter for number of times traded
    //     total_trade_count += 1;

    //     } 
    
    // If the bid price is larger than the buy price by 0.05, sell the position and generate profit
//     else if ((bid_price - buy_price) >= buy_price * 0.05) {
        
//         // We multiply -1 into trade_size_each_time because we are selling the position.
//         SendOrder(instrument, -1 * trade_size_each_time);

//         //Update the size of your position
//         total_stock_position -= trade_size_each_time;

//         //Update the total_revenue generated from this sell order. If total_revenue decreases when buying a position, then selling a position means...
//         total_revenue += bid_price * trade_size_each_time;

//         }
    
//     // If the bid price is lesser than the buy price by 0.05, sell the position and minimize out loss
//     else if ((bid_price - buy_price) <= buy_price * 0.05) {
//         // We multiply -1 into trade_size_each_time because we are selling the position.
//         SendOrder(instrument, -1 * trade_size_each_time);

//         //Update the size of your position
//         total_stock_position -= trade_size_each_time;

//         //Update the total_revenue generated from this sell order. If total_revenue decreases when buying a position, then selling a position means...
//         total_revenue += bid_price * trade_size_each_time;
//         }
// }

void BasicIchimokuStrategy::OnScheduledEvent(const ScheduledEventMsg& msg) {
}

void BasicIchimokuStrategy::OnOrderUpdate(const OrderUpdateEventMsg& msg) {
    
    // // Examples of other information that can be accessed through the msg object, but they are not used in this implementation.
    // std::cout << "name = " << msg.name() << std::endl;
    // std::cout << "order id = " << msg.order_id() << std::endl;
    // std::cout << "fill occurred = " << msg.fill_occurred() << std::endl;
    // std::cout << "update type = " << msg.update_type() << std::endl;

    // Update time of the order update event is printed to the console using std::cout.
    // std::cout << "time " << msg.update_time() << std::endl;

}

void BasicIchimokuStrategy::OnBar(const BarEventMsg& msg) {
    std::cout << "On bar event occured" << std::endl;
    // std::cout <<" On bar function invoked" << std::endl;
    // double bar_interval = msg.interval();
    // std::cout << "bar interval = " << bar_interval << std::endl;
    const Bar& current_bar = msg.bar();
    std::cout << "Current bar: " << current_bar << std::endl;
    total_trade_count += 1;

}

// void BasicIchimokuStrategy::OnQuote(const QuoteEventMsg& msg) {
//     std::cout << "On quote event occured" << std::endl;
// }

void BasicIchimokuStrategy::AdjustPortfolio() {
}

void BasicIchimokuStrategy::SendOrder(const Instrument* instrument, int quantity, double price, bool action) {


    // if (trade_size_each_time > 0) { // buy
    //     price = instrument->top_quote().ask();
    // } else { // sell
    //     price = instrument->top_quote().bid();
    // }

    // Create an order object with the specified parameters
    OrderParams params(
                    *instrument,     // Instrument to trade
                    abs(quantity), // Absolute value of trade size
                    price,           // Price at which to trade
                    MARKET_CENTER_ID_IEX, // Market center ID
                    (action) ? ORDER_SIDE_BUY : ORDER_SIDE_SELL, // Order side (buy or sell)
                    ORDER_TIF_DAY,   // Time in force (how long the order is valid for)
                    ORDER_TYPE_LIMIT // Order type (limit or market)
                    );

    // During the first run of your backtest, you would've seen a lot of lines being printed out to the console.
    // Below are those lines. I've commented them out to reduce clutter and speed up the backtest (printing many lines slows down the backtest)
    // std::string action;
    // if (trade_size_each_time > 0) {
    //         action = "buy ";
    // } else {
    //         action = "sell ";
    // }

    // Print a message indicating that a new order is being sent
    // AM : Uncomment the below line to see the message later
    // std::cout << "SendTradeOrder(): about to send new order for size "
    //         << trade_size_each_time
    //         << " at $"
    //         << price
    //         << " to "
    //         << action
    //         << instrument->symbol()
    //         << std::endl;
    
    TradeActionResult tra = trade_actions()->SendNewOrder(params);
    // Check if the order was sent successfully and print a message indicating the result
    if (tra == TRADE_ACTION_RESULT_SUCCESSFUL) {
            std::cout << "Sending new trade order successful! AP: pushed message" << std::endl;
    } else {
            std::cout << "Error sending new trade order..." << tra << std::endl;
    }

}

void BasicIchimokuStrategy::OnResetStrategyState() {
}

void BasicIchimokuStrategy::OnParamChanged(StrategyParam& param) {
}

