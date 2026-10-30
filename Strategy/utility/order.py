from abc import ABC, abstractmethod

class Order(ABC):
    def __init__(self, order_no, submitted_timestamp, type, side, price, size, filled_timestamp, filled_price, flag):
        pass

    # Getters
    @property
    @abstractmethod
    def submitted_timestamp(self):
        pass

    @property
    @abstractmethod
    def filled_timestamp(self):
        pass

    @property
    @abstractmethod
    def filled_price(self):
        pass

    @property
    @abstractmethod
    def type(self):
        pass

    @property
    @abstractmethod
    def side(self):
        pass

    @property
    @abstractmethod
    def price(self):
        pass

    @property
    @abstractmethod
    def size(self):
        pass

    @property
    @abstractmethod
    def status(self):
        pass

    @property
    @abstractmethod
    def flag(self):
        pass

    # Modify order
    @abstractmethod
    def modify_order(self, price, size, flag):  # We can only modify price, size, and flag of the order
        pass

    # Cancel order
    @abstractmethod
    def cancel_order(self):
        pass

    # Check if can be filled
    @abstractmethod
    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        pass

    # Fill order
    @abstractmethod
    def fill_order(self, timestamp, price):
        pass

    # Print overload
    @abstractmethod
    def __str__(self):
        pass

    
class Limit(Order):
    def __init__(self, order_no, submitted_timestamp, type, side, price, size, filled_timestamp, filled_price, competing_order, flag):
        self.order_no = order_no
        self.submitted_timestamp = submitted_timestamp
        self.filled_timestamp = filled_timestamp
        self.filled_price = filled_price
        self.type = type.lower()
        self.side = side.lower()
        self.price = price
        self.size = size
        self.status = "working"
        self.flag = flag
        self.competing_order = competing_order

    def competing_order(self):
        return self.competing_order

    def order_no(self):
        return self.order_no

    def submitted_timestamp(self):
        return self.submitted_timestamp

    def filled_timestamp(self):
        return self.filled_timestamp
    
    def filled_price(self):
        return self.filled_price

    def type(self):
        return self.type

    def side(self):
        return self.side
    
    def price(self):
        return self.price
    
    def size(self):
        return self.size
    
    def status(self):
        return self.status
    
    def flag(self):
        return "none" if self.flag == None else self.flag
    
    def modify_order(self, price, size, flag):
        if self.status != "working":
            return      # We cannot modify a filled order
        
        self.price = price
        self.size = size
        self.flag = flag

    def fill_order(self, timestamp, price):
        self.filled_timestamp = timestamp
        self.filled_price = price
        self.status = "filled"

    def cancel_order(self):
        self.status = "cancelled"

    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        if self.status != "working":
            return False
        
        if self.side == "buy" and ask_price <= self.price:
            return True
            
        elif self.side == "sell" and bid_price >= self.price:
            return True
        
        return False

    
    def __str__(self):
        return f"Order No. {self.order_no}, Submitted: {self.submitted_timestamp}, Type: {self.type}, Side: {self.side}, Price: {self.price}, Size: {self.size}, Status: {self.status}, Filled: {self.filled_timestamp}, Fill Price: {self.filled_price}, Flag: {self.flag}"


class Market(Order):
    def __init__(self, order_no, submitted_timestamp, type, side, price, size, filled_timestamp, filled_price, flag):
        self.order_no = order_no
        self.submitted_timestamp = submitted_timestamp
        self.filled_timestamp = filled_timestamp
        self.filled_price = filled_price
        self.type = type.lower()
        self.side = side.lower()
        self.price = price
        self.size = size
        self.status = "working"
        self.flag = flag

    def order_no(self):
        return self.order_no

    def submitted_timestamp(self):
        return self.submitted_timestamp

    def filled_timestamp(self):
        return self.filled_timestamp
    
    def filled_price(self):
        return self.filled_price

    def type(self):
        return self.type

    def side(self):
        return self.side
    
    def price(self):
        return self.price
    
    def size(self):
        return self.size
    
    def status(self):
        return self.status
    
    def flag(self):
        return "None" if self.flag == None else self.flag
    
    def modify_order(self, price, size, flag):
        if self.status != "working":
            return      # We cannot modify a filled order
        
        self.price = price
        self.size = size
        self.flag = flag

    def fill_order(self, timestamp, price):
        self.filled_timestamp = timestamp
        self.filled_price = price
        self.status = "filled"

    def cancel_order(self):
        self.status = "cancelled"


    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        if self.status != "working":
            return False
        
        return True

    def __str__(self):
        return f"Order No. {self.order_no}, Submitted: {self.submitted_timestamp}, Type: {self.type}, Side: {self.side}, Price: {self.price}, Size: {self.size}, Status: {self.status}, Filled: {self.filled_timestamp}, Fill Price: {self.filled_price}, Flag: {self.flag}"


class Stop(Order):
    def __init__(self, order_no, submitted_timestamp, type, side, price, size, filled_timestamp, filled_price, competing_order, flag):
        self.order_no = order_no
        self.submitted_timestamp = submitted_timestamp
        self.filled_timestamp = filled_timestamp
        self.filled_price = filled_price
        self.type = type.lower()
        self.side = side.lower()
        self.price = price
        self.size = size
        self.status = "working"
        self.competing_order = competing_order
        self.active = False
        self.flag = flag

    def competing_order(self):
        return self.competing_order

    def order_no(self):
        return self.order_no

    def submitted_timestamp(self):
        return self.submitted_timestamp

    def filled_timestamp(self):
        return self.filled_timestamp
    
    def filled_price(self):
        return self.filled_price

    def type(self):
        return self.type

    def side(self):
        return self.side
    
    def price(self):
        return self.price
    
    def size(self):
        return self.size
    
    def status(self):
        return self.status
    
    def active(self):
        return self.active
    
    def flag(self):
        return "none" if self.flag == None else self.flag
    
    def modify_order(self, price, size, flag):
        if self.status != "working":
            return      # We cannot modify a filled order
        
        self.price = price
        self.size = size
        self.flag = flag

    def fill_order(self, timestamp, price):
        self.filled_timestamp = timestamp
        self.filled_price = price
        self.status = "filled"

    def cancel_order(self):
        self.status = "cancelled"

    def check_fill_availability(self, bid_price, bid_size, ask_price, ask_size):
        if self.status != "working" or self.competing_order.status != "working":
            return False
        
        if self.side == "buy" and ask_price >= self.price:
            return True
            
        elif self.side == "sell" and bid_price <= self.price:
            return True
        
        return False
    
    def __str__(self):
        return f"Order No. {self.order_no}, Submitted: {self.submitted_timestamp}, Type: {self.type}, Side: {self.side}, Price: {self.price}, Size: {self.size}, Status: {self.status}, Filled: {self.filled_timestamp}, Fill Price: {self.filled_price}, Flag: {self.flag}"
