#include <iostream>

// Primary template for argument container
template <typename... Args>
struct ArgumentContainer;

// Partial specialization for a container with one argument
template <typename FirstArg, typename... RestArgs>
struct ArgumentContainer<FirstArg, RestArgs...> {
    FirstArg first;
    ArgumentContainer<RestArgs...> rest;

    // Constructor to initialize the first argument and the rest of the container
    ArgumentContainer(FirstArg arg, RestArgs... restArgs)
        : first(arg), rest(restArgs...) {}
};

// Specialization for an empty container
template <>
struct ArgumentContainer<> {};

int main() {
    // Example usage
    ArgumentContainer<int, double, char> args(42, 3.14, 'A');

    // Accessing arguments
    std::cout << "First argument: " << args.first << std::endl;
    std::cout << "Second argument: " << args.rest.first << std::endl;
    std::cout << "Third argument: " << args.rest.rest.first << std::endl;

    return 0;
}