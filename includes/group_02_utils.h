#include <queue>
#include <deque>
#include <string>
#include <iostream>
#include <iomanip>
#include <cassert>
#include <limits>
#include <unistd.h>
#include <string>
// #include "QuoteEventMsg.h"
// #include "MarketModels/Quote.h"
// #include <Strategy.h>
#include <Analytics/ScalarRollingWindow.h>
#include <Analytics/InhomogeneousOperators.h>
#include <Analytics/IncrementalEstimation.h>
// #include ""
// #include "Instrument.h"
// #include "NBBOQuote.h"
#include <MarketModels/Quote.h>
#include <Utilities/TimeType.h>

#include <Utilities/ParseConfig.h>
// #include <MarketModels/Quote.h>



#include <fstream>
#include <string>


#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

class Logger {
public:
    Logger(const std::string& fileName) {
        logFile.open(fileName, std::ios::app); // Open in append mode
    }

    ~Logger() {
        if (logFile.is_open()) {
            logFile.close();
        }
    }

    void Log(const std::string& message) {
        if (logFile.is_open()) {

            // check if printing inf in string
            if (message.find("inf") != std::string::npos)
            {
                std::cout << "Found inf in string" << std::endl;
                return;
            }
            logFile << message << std::endl;
        }
    }

private:
    std::ofstream logFile;
};



namespace RCM {
namespace StrategyStudio {
namespace MarketModels {

class Candlestick {
    public:

    double best_ask_price; // Highest Ask price recieved
    double best_bid_price; // Lowest Bid price recieved
    int volume; // Volume of the candlestick
    double open_price; // Open price of the candlestick
    double close_price; // Close price of the candlestick
    bool SIDE; // True if Ask, False if Bid
    bool isaskupdated; // True if the candlestick is updated
    bool isbidupdated; // True if the candlestick is updated
    bool isclosed = false; // True if the candlestick is closed
    TimeType source_time;

    
    // Candlestick() : best_ask_price(std::numeric_limits<double>::infinity()), best_bid_price(0), volume(0), open_price(0.0), close_price(0.0) {
    //     isaskupdated = false;
    //     isbidupdated = false;
    //     isclosed = false;
    // }

    // Candlestick(double open_price)
    // : best_ask_price(std::numeric_limits<double>::infinity()), best_bid_price(0), volume(0), open_price(open_price), close_price(0.0) 
    // {
    //     isaskupdated = false;
    //     isbidupdated = false;
    //     isclosed = false;
    // }

    Candlestick() : best_ask_price(std::numeric_limits<double>::infinity()), best_bid_price(0), volume(0), open_price(0.0), close_price(0.0) {
        isaskupdated = false;
        isbidupdated = false;
        isclosed = false;
    }

    Candlestick(double open_price)
    : best_ask_price(std::numeric_limits<double>::infinity()), best_bid_price(0), volume(0), open_price(open_price), close_price(0.0) 
    {
        isaskupdated = false;
        isbidupdated = false;
        isclosed = false;
    }


    void set_source_time(TimeType source_time)
    {
        this->source_time = source_time;
    }

    TimeType get_source_time()
    {
        return this->source_time;
    }

    std::string get_log_string()
    {
        std::string log_string = "";
        log_string += RCM::StrategyStudio::Utilities::TimeTypeToString(source_time) + ",";
        log_string += std::to_string(open_price) + ",";
        log_string += std::to_string(best_ask_price) + ",";
        log_string += std::to_string(best_bid_price) + ",";
        log_string += std::to_string(close_price) + ",";
        log_string += std::to_string(volume);
        return log_string;
    }
    void add_best_ask_price(double price){
        if (price > best_ask_price && price != 0.0)
        {
            this->best_ask_price = price;
            this->isaskupdated = true;
        }
        else
        {
            this->isaskupdated = false;
        }
        this->close_price = (this->best_ask_price+this->best_bid_price)/2;
    }
    bool is_open() {return !isclosed;}
    void set_open() {this->isclosed = false;}
    void add_best_bid_price(double price)
    {
        // std::cout << "Current best bid price(saved): " << this->best_bid_price << std::endl;
        // std::cout << "New bid price(getting from ss): " << price << std::endl;
        // if (price == 0.0)
        // {
        //     this->isbidupdated = false;
        //     return;
        // }
        if (price < best_bid_price && price != std::numeric_limits<double>::infinity())
        {
            
            this->best_bid_price = price;
            this->isbidupdated = true;
        }
        else
        {
            this->isbidupdated = false;
        }
        this->close_price = (this->best_ask_price+this->best_bid_price)/2;
    }
    void set_volume(int volume){this->volume = volume;}
    // void add_open_price(double price){open_price = price;}
    void set_close_price(double price)
    {
        this->close_price = price;
        this->isclosed = true;
        // std::cout <<"candlestick closed at " << this->close_price << std::endl;
    }
    void set_quote(const Quote& quote)
    {

        if(quote.IsAskValid() && quote.IsBidValid())
        {
            this->add_best_bid_price(quote.bid());
            this->add_best_ask_price(quote.ask());

            if (isaskupdated)
            {
                // #ifdef PrintDebugInfo
                // std::cout << " Ask updated " << std::endl;
                // #endif
                this->set_volume(quote.ask_size());
            }
            else if (isbidupdated)
            {
                // #ifdef PrintDebugInfo
                // std::cout << " Bid updated " << std::endl;
                // #endif
                this->set_volume(quote.bid_size());
            }
        }


        // add_best_ask_price(quote.ask());
        // // std::cout << "Bid price check : " << this->best_bid_price << std::endl ;
        // add_best_bid_price(quote.bid());


        // if (isaskupdated)
        // {
        //     // std::cout << "Ask size: " << quote.ask_size() << std::endl;
        //     set_volume(quote.ask_size());
        // }
        // if (isbidupdated)
        // {
        //     set_volume(quote.bid_size());
        // }
    }

    void set_open_price(double price) {this->open_price = price; this->isclosed = false;}

    void reset()
    {
        // std::cout << "candlestick reset " << std::endl;
        best_ask_price = 0;
        best_bid_price = std::numeric_limits<double>::infinity();
        volume = 0;
        open_price = 0.0;
        close_price = 0.0;
        isaskupdated = false;
        isbidupdated = false;
        isclosed = false;
    }

    // Print statement with operator overloading

    friend std::ostream& operator<<(std::ostream& os, const Candlestick& candlestick)
{
        int width = 20; // Set the column width

        os << std::left; // Align text to the left
        os << std::setw(width) << "Candlestick:";
        os << std::endl;

        os << std::setw(width) << "Best Ask Price:" << candlestick.best_ask_price << std::endl;
        os << std::setw(width) << "Best Bid Price:" << candlestick.best_bid_price << std::endl;
        os << std::setw(width) << "Volume:" << candlestick.volume << std::endl;
        os << std::setw(width) << "Open Price:" << candlestick.open_price << std::endl;
        os << std::setw(width) << "Close Price:" << candlestick.close_price << std::endl;
        os << std::setw(width) << "Is Ask Updated:" << candlestick.isaskupdated << std::endl;
        os << std::setw(width) << "Is Bid Updated:" << candlestick.isbidupdated << std::endl;
        os << std::setw(width) << "Is Closed:" << candlestick.isclosed << std::endl;

    return os;
}

};

class CandlestickQueue {
private:
    std::deque<Candlestick> candleQueue;
    int maxSize;
    int short_window_size_cq;
    int mid_window_size_cq;
    int long_window_size_cq;
    double highest_ask_price_short;
    
    double lowest_bid_price_short;
    double highest_ask_price_mid;
    double lowest_bid_price_mid;
    double highest_ask_price_long;
    double lowest_bid_price_long;
    double most_recent_close_price; 

    int highest_ask_price_short_index;
    int lowest_bid_price_short_index;
    int highest_ask_price_mid_index;
    int lowest_bid_price_mid_index;
    int highest_ask_price_long_index;
    int lowest_bid_price_long_index;

    #ifdef LOGGING
    std::ofstream logFile;
    #endif

       
public:
    CandlestickQueue(int short_window_size, int mid_window_size, int long_window_size) : maxSize(long_window_size), short_window_size_cq(short_window_size), mid_window_size_cq(mid_window_size) 
    {
        assert(short_window_size < mid_window_size);
        assert(mid_window_size < long_window_size);
        this->long_window_size_cq = maxSize;
        highest_ask_price_short = 0;
        lowest_bid_price_short = 0;
        highest_ask_price_mid = 0;
        lowest_bid_price_mid = 0;
        highest_ask_price_long = 0;
        lowest_bid_price_long = 0;
        

        #ifdef LOGGING
        // std::vector<std::array<float, 5>> candleStickdata;
        
        #ifdef INSTANCE_NAME
        #pragma message("Instance Name: " INSTANCE_NAME)
        std::string instanceName = INSTANCE_NAME;
        std::cout << "Instance Name: " << instanceName << std::endl;
        #endif

        #ifdef START_DATE
        #pragma message("Start Date: " START_DATE)
        std::string startDate = START_DATE;
        std::cout << "Start Date: " << startDate << std::endl;
        #endif

        #ifdef END_DATE
        #pragma message("End Date: " END_DATE)
        std::string endDate = "END_DATE";
        std::cout << "End Date: " << endDate << std::endl;
        #endif
        std::string fileName = "CANDLESTICK_"+ instanceName + "_" + startDate + "_to_" + endDate + ".csv";
        logFile.open(fileName);
        
        if (!logFile.is_open()) {
            // Handle the error, such as displaying a message or throwing an exception
            std::cout << "Error opening file" << std::endl;
        }
        else
        {
            char buff[250]; // Create a buffer
            std::cout << "Logging happening...." << std::endl;
            getcwd(buff, FILENAME_MAX);
            std::string current_working_dir(buff);

            std::cout << "Current working directory..." << current_working_dir << std::endl;
        }
        #endif
    }

    // Default constructor
    CandlestickQueue() : CandlestickQueue(5, 13, 26) {}
    

    
    ~CandlestickQueue() {
        #ifdef LOGGING
        if (logFile.is_open()) {
            logFile.close();
        }
        #endif
    }

    double get_most_recent_closefriend()
    {
        return candleQueue.back().close_price;
    }

    double get_first_best_ask_price()
    {
        return candleQueue.front().best_ask_price;
    }

    double get_first_best_bid_price()
    {
        return candleQueue.front().best_bid_price;
    }

    bool is_empty() {return candleQueue.empty();}
    int get_size() {return candleQueue.size();}
    std::pair<double, int> get_highest_ask_price_in_window(int start_index, int end_index)
    {
        double highest_price = 0;
        int index;
        // int high_ask_price_index = -1;
        for (int i = start_index; i >= end_index; i= i - 1)
        {
            if (candleQueue[i].best_ask_price > highest_price)
            {
                highest_price = candleQueue[i].best_ask_price;
                index = i;
            }
        }
        return {highest_price, index};
    }

    std::pair<double, int> get_lowest_bid_price_in_window(int start_index, int end_index)
    {
        double lowest_price = std::numeric_limits<double>::infinity();
        int index;
        for (int i = start_index; i >= end_index; i= i - 1)
        {
            if (candleQueue[i].best_bid_price < lowest_price)
            {
                lowest_price = candleQueue[i].best_bid_price;
                index = i;
            }
        }

        return {lowest_price, index};
        
    }

    void print_close_prices()
    {
        std::cout << "Close price : ";
        for (int i = 0; i < candleQueue.size(); i++)
        {
            std::cout << candleQueue[i].close_price << ", ";
        }
        std::cout << std::endl;
    }


    void print_high_asks()
    {
        std::cout << "High ask prices : ";
        for (int i = 0; i < candleQueue.size(); i++)
        {
            std::cout << candleQueue[i].best_ask_price << ", ";
        }
        std::cout << std::endl;
    }
    

    double get_most_recent_close_price()
    {
        return candleQueue.back().close_price;
    }

    int size()
    {
        return candleQueue.size();
    }

    void set_best_asks_and_best_bids()
    {
        std::pair<double, int> short_window_best_ask_price_exclusive = get_highest_ask_price_in_window(this->long_window_size_cq-1, this->long_window_size_cq - this->short_window_size_cq);
        std::pair<double, int> medium_window_best_ask_price_exclusive = get_highest_ask_price_in_window(this->long_window_size_cq - this->short_window_size_cq - 1, this->long_window_size_cq- this->mid_window_size_cq);
        std::pair<double, int> long_window_best_ask_price_exclusive = get_highest_ask_price_in_window(this->long_window_size_cq - this->mid_window_size_cq -1, 0);

        if (short_window_best_ask_price_exclusive.first > medium_window_best_ask_price_exclusive.first)
        {
            medium_window_best_ask_price_exclusive.first = short_window_best_ask_price_exclusive.first;
            medium_window_best_ask_price_exclusive.second = short_window_best_ask_price_exclusive.second;
        }
        if (medium_window_best_ask_price_exclusive.first > long_window_best_ask_price_exclusive.first)
        {
            long_window_best_ask_price_exclusive.first = medium_window_best_ask_price_exclusive.first;
            long_window_best_ask_price_exclusive.second = medium_window_best_ask_price_exclusive.second;
        }

        std::pair<double,int> short_window_best_bid_price_exclusive = get_lowest_bid_price_in_window(this->long_window_size_cq-1, this->long_window_size_cq - this->short_window_size_cq);
        std::pair<double,int> medium_window_best_bid_price_exclusive = get_lowest_bid_price_in_window(this->long_window_size_cq - this->short_window_size_cq - 1, this->long_window_size_cq- this->mid_window_size_cq);
        std::pair<double,int> long_window_best_bid_price_exclusive = get_lowest_bid_price_in_window(this->long_window_size_cq - this->mid_window_size_cq -1, 0);

        if (short_window_best_bid_price_exclusive.first < medium_window_best_bid_price_exclusive.first)
        {
            medium_window_best_bid_price_exclusive.first = short_window_best_bid_price_exclusive.first;
            medium_window_best_bid_price_exclusive.second = short_window_best_bid_price_exclusive.second;
        }
        if (medium_window_best_bid_price_exclusive.first < long_window_best_bid_price_exclusive.first)
        {
            long_window_best_bid_price_exclusive.first = medium_window_best_bid_price_exclusive.first;
            long_window_best_bid_price_exclusive.second = medium_window_best_bid_price_exclusive.second;
        }

        this->highest_ask_price_short = short_window_best_ask_price_exclusive.first;
        this->highest_ask_price_mid = medium_window_best_ask_price_exclusive.first;
        this->highest_ask_price_long = long_window_best_ask_price_exclusive.first;

        this->lowest_bid_price_short = short_window_best_bid_price_exclusive.first;
        this->lowest_bid_price_mid = medium_window_best_bid_price_exclusive.first;
        this->lowest_bid_price_long = long_window_best_bid_price_exclusive.first;

        // std::cout << "Short window best ask price: " << short_window_best_ask_price_exclusive.first << std::endl;
        // std::cout << "Medium window best ask price: " << medium_window_best_ask_price_exclusive.first << std::endl;
        // std::cout << "Long window best ask price: " << long_window_best_ask_price_exclusive.first << std::endl;

        // std::cout << "Short window best bid price: " << short_window_best_bid_price_exclusive.first << std::endl;
        // std::cout << "Medium window best bid price: " << medium_window_best_bid_price_exclusive.first << std::endl;
        // std::cout << "Long window best bid price: " << long_window_best_bid_price_exclusive.first << std::endl;


    }

    bool is_full()
    {
        return (int) candleQueue.size() == maxSize;
    }

    bool addCandlestick(const Candlestick& candle)
    {
        // std::cout << "Long window size: " << this->long_window_size_cq << std::endl;
        // std::cout << "entered addCandleStick checkpoint 0 " << std::endl;
        if (!candle.isclosed) {
            std::cerr << "Error: Candlestick must be closed." << std::endl;
            assert(false && "Candlestick is not closed.");
        }

        if(candle.volume == 0)
        {
            // std::cout << "Detected zero volume candlestick" << std::endl;
            return false;
        }

        #ifdef IgnoreOddLots
            #pragma message("IgnoreOddLots status, " TOSTRING(IgnoreOddLots))
            
            bool ignore_odd_lots = IgnoreOddLots;
            if (ignore_odd_lots && candle.volume <100)
            {
                // num_ignore_odd_lots += 1;
                // current_candlestick.reset();
                //  current_candlestick.set_open_price(msg.trade().price());
                // std::cout << "Ignore Odd Lot" << std::endl;
                return;
            }
        #endif

        

        // if( candleQueue.size() == 0)
        // {
        //     candleQueue.push_back(candle);
        //     set_best_asks_and_best_bids();
        //     return true;
        // }

        if (candle.best_ask_price == 0.0 || candle.best_bid_price== std::numeric_limits<double>::infinity())
        {
            std::cout << "Detected zero best ask or best bid price" << std::endl;
            return false;
        }
        // std::cout << "Assert passed" << std::endl;
        if (!candleQueue.empty() && candle.close_price == get_most_recent_close_price()) {

            // #ifdef PrintDebugInfo
            // #pragma message("PrintDebugInfo status, " TOSTRING(PrintDebugInfo))
            // std::cout << "Detected duplicate candlestick" << std::endl;
            // #endif
            
            return false; // Do not add if the close price is the same as the last candlestick
        }

        if (candleQueue.size() < this->long_window_size_cq && candle.close_price != get_most_recent_close_price() )
        {
            // std::cout << "entered if-state    size: " << candleQueue.size() << "< long window size : " << this->long_window_size_cq <<  std::endl;
             #ifdef PrintDebugInfo
            // #pragma message("PrintDebugInfo status, " TOSTRING(PrintDebugInfo))
            // std::cout << "Adding candlestick when total size is less than long window size" << std::endl;
            #endif
            candleQueue.push_back(candle);
            return true;
        }

        if (candleQueue.size() == this->long_window_size_cq && candle.close_price != get_most_recent_close_price())
        {
            // std::cout << "entered else-if-state    size: " << candleQueue.size() << "== long window size : " << this->long_window_size_cq <<  std::endl;
            candleQueue.pop_front();
            candleQueue.push_back(candle);
            set_best_asks_and_best_bids();
            return true;
        }
        
    }
    void manage_state(const Candlestick& candle){
        // Short window highest ask price and lowest bid price update
    
    }

    // Unoptimized for now
    double moving_average_short()
    {
        double closing_project = 0;
        for (int i = this->long_window_size_cq -1; i >= this->long_window_size_cq - this->short_window_size_cq; i= i - 1)
        {
            closing_project += candleQueue[i].close_price;
        }
        return closing_project/this->short_window_size_cq;
    }

    double minimum_closing_price_short()
    {
        // Check if the short window size is valid
        if (this->short_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the minimum closing price with a very high value
        double min_closing_price = std::numeric_limits<double>::max();

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->short_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].close_price < min_closing_price)
            {
                min_closing_price = candleQueue[i].close_price;
            }
        }

        // Return the minimum closing price found
        return min_closing_price;
    }

    float GetAggression(double closing_price, bool is_ask_side)
    {
        // int short_window_size = candlestickQueue.get_short_window_size();

        #ifdef Aggression
        #pragma message("Aggression status, " TOSTRING(Aggression))
        bool aggresion = Aggression;
        double multiplier = 0.01;

        #ifdef AggressionMultiplier
        #pragma message("AggressionMultiplier given: " TOSTRING(AggressionMultiplier))
        // std::string aggressionMultiplierStr = AggressionMultiplier;
        double temp_aggression_multiplier = AggressionMultiplier;
        multiplier = temp_aggression_multiplier;
        // multiplier = this->aggression_multiplier;
        // std::cout << "Aggression multiplier: " << multiplier << std::endl;
        #endif

        
        
        
        



        if (aggresion)
        {
            double min_price_short = this->minimum_closing_price_short();

            double average_closing_price_short_window = this->moving_average_short();

            if (is_ask_side)
            {
                // Mild Aggressiveness 
                if (closing_price > min_price_short)
                {
                    // double aggression = std::abs(std::pow((closing_price - min_price_short),2) / (min_price_short - average_closing_price_short_window));
                    // return aggression;

                    return 0;
                }
                else
                {
                     // More aggressiveness
                    return std::abs(multiplier*(closing_price - min_price_short) / (min_price_short - average_closing_price_short_window));
                }
            }
            else{
                if (closing_price > min_price_short)
                {
                    double aggression = std::abs(multiplier*(closing_price - min_price_short) / (min_price_short - average_closing_price_short_window));
                    return aggression;
                }
                else
                {
                    return 0;
                }
            }
           
            // return 
        }
        else
        {
            return 0;
        }
        #endif

        
    }

    double moving_vwap_short()
    {
        double vwap_project = 0;
        int volume_project = 0;
        for (int i = this->long_window_size_cq -1; i >= this->long_window_size_cq - this->short_window_size_cq; i= i - 1)
        {
            vwap_project += candleQueue[i].close_price * candleQueue[i].volume;
            volume_project += candleQueue[i].volume;
        }
        return vwap_project/volume_project;
    }


    double get_standard_deviation_short_window()
    {
        double average_closing_price_short_window = this->moving_average_short();
        double sum_of_squared_differences = 0;
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->short_window_size_cq; i--)
        {
            sum_of_squared_differences += std::pow((candleQueue[i].close_price - average_closing_price_short_window), 2);
        }
        return std::sqrt(sum_of_squared_differences/this->short_window_size_cq);
    }

    double moving_vwap_medium()
    {
        double vwap_project = 0;
        int volume_project = 0;
        for (int i = this->long_window_size_cq -1; i >= this->long_window_size_cq - this->mid_window_size_cq; i= i - 1)
        {
            vwap_project += candleQueue[i].close_price * candleQueue[i].volume;
            volume_project += candleQueue[i].volume;
        }
        return vwap_project/volume_project;
    }

    double moving_vwap_long()
    {
        double vwap_project = 0;
        int volume_project = 0;
        for (int i = this->long_window_size_cq -1; i >= 0; i= i - 1)
        {
            vwap_project += candleQueue[i].close_price * candleQueue[i].volume;
            volume_project += candleQueue[i].volume;
        }
        return vwap_project/volume_project;
    }

    double moving_average_medium()
    {
        double closing_project = 0;
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->mid_window_size_cq; i= i - 1)
        {
            closing_project += candleQueue[i].close_price;
        }
        return closing_project/this->mid_window_size_cq;
    }

    double moving_average_long()
    {
        double closing_project = 0;
        for (int i = this->long_window_size_cq - 1; i >= 0; i= i - 1)
        {
            closing_project += candleQueue[i].close_price;
        }
        return closing_project/this->long_window_size_cq;
    }


    double average_true_range_long()
    {
        double cummulative_range = 0;
        for(int i = this->long_window_size_cq - 1; i >= 0; i = i - 1)
        {
            cummulative_range += candleQueue[i].best_ask_price - candleQueue[i].best_bid_price;
        }
        return cummulative_range/this->long_window_size_cq;
    }

    double average_true_range_short()
    {
        double cummulative_range = 0;
        for(int i = this->long_window_size_cq -1; i >= this->long_window_size_cq - this->short_window_size_cq; i= i - 1)
        {
            cummulative_range += candleQueue[i].best_ask_price - candleQueue[i].best_bid_price;
        }
        return cummulative_range/this->short_window_size_cq;
    }

    double average_true_range_mid()
    {
        double cummulative_range = 0;
        for(int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->mid_window_size_cq; i= i - 1)
        {
            cummulative_range += candleQueue[i].best_ask_price - candleQueue[i].best_bid_price;
        }
        return cummulative_range/this->mid_window_size_cq;
    }


    
    double getshort_avg_highest_ask_lowest_bid_price()
    {
        return (highest_ask_price_short + lowest_bid_price_short)/2;
    }
    double getmid_avg_highest_ask_lowest_bid_price()
    {
        return (highest_ask_price_mid + lowest_bid_price_mid)/2;
    }
    double getlong_avg_highest_ask_lowest_bid_price()
    {
        return (highest_ask_price_long + lowest_bid_price_long)/2;
    }
    void set_short_window_size(int short_window_size){this->short_window_size_cq = short_window_size;}
    void set_mid_window_size(int mid_window_size){this->mid_window_size_cq = mid_window_size;}
    void set_long_window_size(int long_window_size){this->long_window_size_cq = long_window_size;}
    int get_short_window_size(){return this->short_window_size_cq;}
    int get_mid_window_size(){return this->mid_window_size_cq;}
    int get_long_window_size(){return this->long_window_size_cq;}
    // Additional methods like getLatestCandlestick(), getSize(), isEmpty() can be added as needed

    double highest_high_short() {
        // Check if the short window size is valid
        if (this->short_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the highest high price with a negative value
        double max_high = -1;

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->short_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_ask_price > max_high)
            {
                max_high = candleQueue[i].best_ask_price;
            }
        }

        // Return the minimum closing price found
        return max_high;
    }

    double lowest_low_short() {
        // Check if the short window size is valid
        if (this->short_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the minimum closing price with a very high value
        double min_low = std::numeric_limits<double>::max();

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->short_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_bid_price < min_low)
            {
                min_low = candleQueue[i].best_bid_price;
            }
        }

        // Return the minimum closing price found
        return min_low;
    }

    double highest_high_mid() {
        // Check if the mid window size is valid
        if (this->mid_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the highest high price with a negative value
        double max_high = -1;

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->mid_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_ask_price > max_high)
            {
                max_high = candleQueue[i].best_ask_price;
            }
        }

        // Return the minimum closing price found
        return max_high;
    }

    double lowest_low_mid() {
        // Check if the short window size is valid
        if (this->mid_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the minimum closing price with a very high value
        double min_low = std::numeric_limits<double>::max();

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i >= this->long_window_size_cq - this->mid_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_bid_price < min_low)
            {
                min_low = candleQueue[i].best_bid_price;
            }
        }

        // Return the minimum closing price found
        return min_low;
    }


    double highest_high_short_minus_one() {
        // Check if the short window size is valid
        if (this->short_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the highest high price with a negative value
        double max_high = -1;

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i > this->long_window_size_cq - this->short_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_ask_price > max_high)
            {
                max_high = candleQueue[i].best_ask_price;
            }
        }

        // Return the minimum closing price found
        return max_high;
    }

    double lowest_low_short_minus_one() {
        // Check if the short window size is valid
        if (this->short_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the minimum closing price with a very high value
        double min_low = std::numeric_limits<double>::max();

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i > this->long_window_size_cq - this->short_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_bid_price < min_low)
            {
                min_low = candleQueue[i].best_bid_price;
            }
        }

        // Return the minimum closing price found
        return min_low;
    }

    double highest_high_mid_minus_one() {
        // Check if the mid window size is valid
        if (this->mid_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the highest high price with a negative value
        double max_high = -1;

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i > this->long_window_size_cq - this->mid_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_ask_price > max_high)
            {
                max_high = candleQueue[i].best_ask_price;
            }
        }

        // Return the minimum closing price found
        return max_high;
    }

    double lowest_low_mid_minus_one() {
        // Check if the short window size is valid
        if (this->mid_window_size_cq <= 0) {
            // Handle error: short window size is zero or negative
            return -1; // Returning -1 or another error code
        }

        // Initialize the minimum closing price with a very high value
        double min_low = std::numeric_limits<double>::max();

        // Iterate over the specified window
        for (int i = this->long_window_size_cq - 1; i > this->long_window_size_cq - this->mid_window_size_cq; i--)
        {
            // Update the min_closing_price if a lower closing price is found
            if (candleQueue[i].best_bid_price < min_low)
            {
                min_low = candleQueue[i].best_bid_price;
            }
        }

        // Return the minimum closing price found
        return min_low;
    }
};

}
}
}
