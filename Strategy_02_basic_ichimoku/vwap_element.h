
#include <string>
#include <iostream>
#include <Utilities/TimeType.h>

class Element {
public:
    int volume;
    double price;
    Utilities::TimeSpanType timeOfTrade;

    Element(int v, double p, const Utilities::TimeSpanType t);
    Element(Element&& other) noexcept;
    friend std::ostream& operator<<(std::ostream& os, const Element& element);
};

class Window {
private:
    std::queue<Element> elements;

public:
    void addElement(const Element& element);
    Element removeElement();
    bool isEmpty() const;
    size_t size() const;
    double mean() const;
    double sum_volume() const;
    double volume_weighted_average_price() const;
    std::string prettyPrintMarkdown() const;
};