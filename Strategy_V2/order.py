from abc import ABC, abstractmethod

class Order(ABC):
    """
    Abstract base class representing a generic order.

    Attributes:
        order_num (int): The order number.
        submitted_timestamp (str): The timestamp when the order was submitted.
        order_type (str): The type of order (market, limit, stop).
        side (str): The side of the order (buy, sell).
        price (float): The price of the order.
        size (float): The size of the order.
        filled_timestamp (str): The timestamp when the order was filled.
        filled_price (float): The price at which the order was filled.
        flag: A flag associated with the order.
        status (str): The status of the order (working, filled, cancelled).
    """

    def __init__(self, order_num, submitted_timestamp, order_type, side, \
                 price, size, filled_timestamp, filled_price, flag):
        """
        Initialize the Order object with the given parameters.
        """
        self.order_num = order_num
        self.submitted_timestamp = submitted_timestamp
        self.order_type = order_type.lower()
        self.side = side.lower()
        self.price = price
        self.size = size
        self.filled_timestamp = filled_timestamp
        self.filled_price = filled_price
        self.status = "working"
        self.flag = flag

    @property
    def get_order_num(self):
        """Get the order number."""
        return self.order_num
    
    @property
    def get_submitted_timestamp(self):
        """Get the submitted timestamp."""
        return self.submitted_timestamp

    @property
    def get_order_type(self):
        """Get the order type."""
        return self.order_type
    
    @property
    def get_side(self):
        """Get the order side."""
        return self.side
    
    @property
    def get_price(self):
        """Get the order price."""
        return self.price
    
    @property
    def get_size(self):
        """Get the order size."""
        return self.size
    
    @property
    def get_filled_timestamp(self):
        """Get the filled timestamp."""
        return self.filled_timestamp
    
    @property
    def get_filled_price(self):
        """Get the filled price."""
        return self.filled_price
    
    @property
    def get_status(self):
        """Get the order status."""
        return self.status
    
    @property
    def get_flag(self):
        """Get the order flag."""
        return self.flag if self.flag is not None else "None"
    
    def modify_order(self, price, size, flag):
        """
        Modify the order with the given price, size, and flag.

        Args:
            price (float): The new price for the order.
            size (float): The new size for the order.
            flag: The new flag for the order.
        """
        if self.status == "working":
            self.price = price
            self.size = size
            self.flag = flag
    
    def fill_order(self, timestamp, price):
        """
        Fill the order with the given timestamp and price.

        Args:
            timestamp (str): The timestamp when the order was filled.
            price (float): The price at which the order was filled.
        """
        self.filled_timestamp = timestamp
        self.filled_price = price
        self.status = "filled"
    
    def cancel_order(self):
        """Cancel the order."""
        self.status = "cancelled"
    
    def __str__(self):
        """
        Return a string representation of the Order object.
        """
        return f"Order No. {self.order_num}, \
                Submitted: {self.submitted_timestamp}, \
                Type: {self.order_type}, \
                Side: {self.side}, \
                Price: {self.price}, \
                Size: {self.size}, \
                Status: {self.status}, \
                Filled: {self.filled_timestamp}, \
                Fill Price: {self.filled_price}, \

                Flag: {self.flag}"

    @abstractmethod
    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        """
        Check if the order can be filled based on bid and ask prices and sizes.

        Args:
            bid_price (float): The bid price in the market.
            bid_size (float): The bid size in the market.
            ask_price (float): The ask price in the market.
            ask_size (float): The ask size in the market.

        Returns:
            bool: True if the order can be filled, False otherwise.
        """
        pass


class Limit(Order):
    """
    Class representing a limit order.

    Attributes:
        order_num (int): The order number.
        submitted_timestamp (str): The timestamp when the order was submitted.
        order_type (str): The type of order (market, limit, stop).
        side (str): The side of the order (buy, sell).
        price (float): The price of the order.
        size (float): The size of the order.
        filled_timestamp (str): The timestamp when the order was filled.
        filled_price (float): The price at which the order was filled.
        flag: A flag associated with the order.
        status (str): The status of the order (working, filled, cancelled).
        competing_order (Order): Reference to a competing Order object. 
    """

    def __init__(self, order_num, submitted_timestamp, order_type, side, \
                 price, size, filled_timestamp, filled_price, flag, \
                 competing_order):
        """
        Initialize the Limit object with the given parameters.
        """
        super().__init__(order_num, submitted_timestamp, order_type, side, \
                         price, size, filled_timestamp, filled_price, flag)
        self.competing_order = competing_order

    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        """
        Check if the limit order can be filled based on bid/ask prices/sizes.

        Args:
            bid_price (float): The bid price in the market.
            bid_size (float): The bid size in the market.
            ask_price (float): The ask price in the market.
            ask_size (float): The ask size in the market.

        Returns:
            bool: True if the limit order can be filled, False otherwise.
        """
        if self.status == "working":
            if (self.side == "buy" and ask_price <= self.price) or \
               (self.side == "sell" and bid_price >= self.price):
                return True
        return False

class Market(Order):
    """
    Class representing a market order.
    """

    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        """
        Check if the market order can be filled based on bid/ask prices/sizes.

        Args:
            bid_price (float): The bid price in the market.
            bid_size (float): The bid size in the market.
            ask_price (float): The ask price in the market.
            ask_size (float): The ask size in the market.

        Returns:
            bool: True if the market order can be filled, False otherwise.
        """
        
        if self.status == "working":
            return True
        return False

class Stop(Order):
    """
    Class representing a stop order, a type of order.

    Attributes:
        order_num (int): The order number.
        submitted_timestamp (str): The timestamp when the order was submitted.
        order_type (str): The type of order (market, limit, stop).
        side (str): The side of the order (buy, sell).
        price (float): The price of the order.
        size (float): The size of the order.
        filled_timestamp (str): The timestamp when the order was filled.
        filled_price (float): The price at which the order was filled.
        flag: A flag associated with the order.
        status (str): The status of the order (working, filled, cancelled).
        competing_order (Order): Reference to a competing Order object. 
        active (bool): Flag to indicate whether the order is active. 
    """

    def __init__(self, order_num, submitted_timestamp, \
                 order_type, side, price, size, \
                 filled_timestamp, filled_price, \
                 flag, competing_order):
        """
        Initialize the Stop object with the given parameters.
        """
        super().__init__(order_num, submitted_timestamp, order_type, side, \
                         price, size, filled_timestamp, filled_price, flag)
        
        self.competing_order = competing_order
        self.active = False
    
    # TODO: Do we need this? 
    @property
    def get_competing_order(self):
        """Get the competing order."""
        return self.competing_order
    
    # TODO: Do we need this? 
    @property
    def get_active(self):
        """Get the active status."""
        return self.active
    
    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        """
        Checks if the stop order can be filled based on bid/ask prices/sizes.

        Args:
            bid_price (float): The bid price in the market.
            bid_size (float): The bid size in the market.
            ask_price (float): The ask price in the market.
            ask_size (float): The ask size in the market.

        Returns:
            bool: True if the stop order can be filled, False otherwise.
        """
        
        if self.status == "working" or self.competing_order.status == "working":
            if (self.side == "buy" and ask_price >= self.price) or \
               (self.side == "sell" and bid_price <= self.price):
                return True
        return False
