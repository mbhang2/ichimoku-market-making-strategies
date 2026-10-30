#include <iostream>
#include <vector>
#include <tuple>


// Credit: CoPilot
// Primary template for argument container
template <typename... Args>
struct ArgumentContainer;

// Partial specialization for a container with one argument
template <typename FirstArg, typename... RestArgs>
struct ArgumentContainer<FirstArg, RestArgs...> {
    public:
    FirstArg first;
    ArgumentContainer<RestArgs...> rest;

    // Constructor to initialize the first argument and the rest of the container
    ArgumentContainer(FirstArg arg, RestArgs... restArgs)
        : first(arg), rest(restArgs...) {}

    // Copy constructor
    ArgumentContainer(const ArgumentContainer& other)
        : first(other.first), rest(other.rest) {}
};

// Specialization for an empty container
template <>
struct ArgumentContainer<> {};


// Base case: an empty tuple
std::tuple<> storeInTuple(const ArgumentContainer<>& container) {
    return std::make_tuple();
}

// Recursive case: store the first argument and recursively call for the rest
template <typename FirstArg, typename... RestArgs>
std::tuple<FirstArg, RestArgs...> storeInTuple(const ArgumentContainer<FirstArg, RestArgs...>& container) {
    return std::tuple_cat(std::make_tuple(container.first), storeInTuple(container.rest));
}

template <typename... Funcs>
auto storeFunctionsInTuple(Funcs... funcs) {
    return std::make_tuple(funcs...);
}
// CreditEnd: CoPilot


// // General template class
// template <typename... Args>
// class MyClass {
// public:
//     std::tuple<Args...> data;

//     MyClass(Args... args) : data(args...) {}
// };

// General template factory function
// template <template <typename...> class C, typename... Args>
// C<Args...> makeInstance(Args... args) {
//     // using K_type = decltype(std::declval<C>());
//     return C<K_type>(args...);
// }



class Modules {
    public:
};

template <typename T>
struct is_modules_derived {
    static constexpr bool value = std::is_base_of<Modules, T>::value;
};


class KalmanFilter_Toy : public Modules{
    public:
    int num = 5;
    int num_2 = 4;
    int num_3 = 45;
    std::vector<int> vec = {1,2,3,4,5};

    std::tuple<int&, int&, int&, std::vector<int>& > Tunable{num, num_2, num_3, vec}; // Mandatory Line in every class you want to superoptimize
    
    KalmanFilter_Toy(){}
};


class NN : public Modules{
    public:
    int num = 5;
    int num_2 = 4;
    int num_3 = 45;
    std::vector<int> vec = {1,2,3,4,5};

    std::tuple<int&, int&, int&, std::vector<int>& > Tunable{num, num_2, num_3, vec}; // Mandatory Line in every class you want to superoptimize
    
    NN(){}
};



template <typename T, typename... GridSearchTy>
typename std::enable_if<is_modules_derived<T>::value, void>::type
superoptimizer(T module, GridSearchTy... grid_args){
    auto tunable_params = module.Tunable;
    std::size_t num_tunable_params = std::tuple_size<decltype(tunable_params)>::value;
    std::cout << "Number of tunable params: " << num_tunable_params << std::endl;

    auto funcs_tuple = storeFunctionsInTuple(grid_args...);
    using func_1_type = std::tuple_element_t<1, decltype(funcs_tuple)>;
    

    if constexpr (std::is_same_v<func_1_type, int>) {
        std::cout << "It's an int: " << std::get<1>(funcs_tuple) << std::endl;
    }

    if constexpr (std::is_same_v<T, KalmanFilter_Toy>)
    {
        std::cout << "It's a KalmanFilter_Toy" << std::endl;
    }
    std::cout << std::get<0>(funcs_tuple) << std::endl;

    //Create a copy of the module
    T module_copy = module;
    auto copy_tunable_params = module_copy.Tunable;

    // Access the second element of Tunable tuple and edit value in module_copy

    // Access tuple elements dynamically at runtime using a loop
    // for (std::size_t i = 0; i < num_tunable_params; ++i) {
    //     T& param = std::get<i>(tunable_params);
    //     // Use param as needed (for example, copy it to module_copy)
    //     // module_copy.some_member = param;
    // }

}


int main(){
    auto myKalmanFilter = KalmanFilter_Toy();
    // auto nn_trial = NN();
    // KalmanFilter_Toy<int, int, int> kf;
    // std::cout << std::get<0>(myKalmanFilter.Tunable) << std::endl;
    // myKalmanFilter.num = 1000;
    // std::cout << std::get<0>(myKalmanFilter.Tunable) << std::endl;

    superoptimizer(myKalmanFilter, 23,  3.4, std::vector<int>{1,2,3,4,5});
    // superoptimizer(nn_trial);

    // kf.print_all_args();
    // std::cout << kf.Tunable.first << std::endl;
    // std::cout << kf.Tunable.rest.first << std::endl;
    // superoptimizer(kf);
    // superoptimizer2(1,2.3,3,4,5);
    return 0;
}