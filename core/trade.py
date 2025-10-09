"""
###############################################################################
# Trade - Represents a single trade order/execution
###############################################################################
"""

from datetime import datetime


class Trade:
    ###############################################################################
    # Trade - Represents a single trade order/execution
    ###############################################################################
    
    # Trade Types
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    
    # Directions
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_COVER = "BUY_TO_COVER"
    
    # Status
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    
    def __init__(self, symbol, direction, quantity, trade_type, strategy, 
                 price=None, stop_price=None):
        """
        Initialize a Trade
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL")
            direction: BUY, SELL, SELL_SHORT, or BUY_TO_COVER
            quantity: Number of shares/contracts
            trade_type: MARKET, LIMIT, STOP_LOSS, etc.
            strategy: Parent Strategy object
            price: Limit price (for LIMIT orders)
            stop_price: Stop trigger price (for STOP orders)
        """
        self.trade_id = None  # Assigned when executed
        self.symbol = symbol
        self.direction = direction
        self.quantity = quantity
        self.trade_type = trade_type
        self.strategy = strategy
        self.price = price
        self.stop_price = stop_price
        
        # Execution tracking
        self.status = self.PENDING
        self.filled_quantity = 0
        self.avg_fill_price = 0.0
        self.commission = 0.0
        self.created_at = datetime.now()
        self.submitted_at = None
        self.filled_at = None
        
    def __repr__(self):
        return (f"Trade({self.symbol}, {self.direction}, {self.quantity}@"
                f"{self.trade_type}, Status: {self.status})")

