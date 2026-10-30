
#include "vwap_element.h"


Element::Element(int v, double p, const Utilities::TimeSpanType t) {
    volume = v;
    price = p;
    timeOfTrade = t;
}

Element::Element(Element&& other) noexcept
    : volume(other.volume), price(other.price), timeOfTrade(std::move(other.timeOfTrade)) {
    // The std::move call is used for the string member to enable move semantics
}

Element Window::removeElement() {
    if (!elements.empty()) {
        Element frontElement = elements.front();
        elements.pop();
        return frontElement;
    } else {
        throw std::runtime_error("Attempt to remove from empty queue");
    }
}

std::ostream& operator<<(std::ostream& os, const Element& element) {
    os << "Volume: " << element.volume << ", Time: " << element.timeOfTrade << ", Price: " << element.price;
    return os;
}

bool Window::isEmpty() const {
    return elements.empty();
}

size_t Window::size() const {
    return elements.size();
}

double Window::mean() const {
    if (!elements.empty()) {
        double sum = 0;
        for (const Element& element : elements) {
            sum += element.price;
        }
        return sum / elements.size();
    } else {
        throw std::runtime_error("Attempt to calculate mean of empty queue");
    }
}


double Window::sum_volume() const {
    if (!elements.empty()) {
        double sum = 0;
        for (const Element& element : elements) {
            sum += element.volume;
        }
        return sum;
    } else {
        throw std::runtime_error("Attempt to calculate sum of empty queue");
    }
}

double Window::volume_weighted_average_price() const {
    if (!elements.empty()) {
        double sum = 0;
        for (const Element& element : elements) {
            sum += element.price * element.volume;
        }
        return sum / sum_volume();
    } else {
        throw std::runtime_error("Attempt to calculate volume weighted average price of empty queue");
    }
}

std::string Window::prettyPrintMarkdown() const {
    std::stringstream ss;
    ss << "| Volume | Price | Time of Trade |\n";
    ss << "| ------ | ----- | ------------- |\n";
    for (const auto& element : elements) {
        ss << "| " << element.volume << " | " << element.price << " | " << element.timeOfTrade << " |\n";
    }
    return ss.str();
}