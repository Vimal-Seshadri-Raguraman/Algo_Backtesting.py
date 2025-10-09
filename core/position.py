"""
###############################################################################
# Position - Represents an open position (aggregate of trades)
###############################################################################
"""

from datetime import datetime
import uuid
from .trade import Trade


class Position:
    ###############################################################################
    # Position - Represents an open position (aggregate of trades)
    ###############################################################################
    
    def __init__(self, symbol, strategy):
        """
        Initialize a Position
        
        Args:
            symbol: Ticker symbol
            strategy: Parent Strategy object
        """
        self.position_id = str(uuid.uuid4())
        self.symbol = symbol
        self.strategy = strategy
        
        # Position state
        self.quantity = 0  # +ve = long, -ve = short
        self.avg_entry_price = 0.0
        self.total_cost_basis = 0.0
        
        # P&L tracking
        self.realized_pnl = 0.0
        # Note: unrealized_pnl is calculated dynamically via @property
        
        # Trade history
        self.opening_trades = []
        self.closing_trades = []
        
        # Timestamps
        self.opened_at = datetime.now()
        self.closed_at = None
    
    @property
    def is_long(self):
        """Check if position is long"""
        return self.quantity > 0
    
    @property
    def is_short(self):
        """Check if position is short"""
        return self.quantity < 0
    
    @property
    def is_closed(self):
        """Check if position is closed"""
        return self.quantity == 0
    
    def get_current_price(self):
        """
        Fetch current market price from data provider
        
        Returns:
            float: Current market price (or entry price if no provider)
        """
        if self.strategy.data_provider is None:
            # Fallback to entry price when no data provider available
            return self.avg_entry_price if self.avg_entry_price > 0 else 0.0
        quote = self.strategy.data_provider.get_quote(self.symbol)
        return quote['price']
    
    @property
    def market_value(self):
        """
        Current market value of position using live price
        """
        if self.quantity == 0:
            return 0
        current_price = self.get_current_price()
        return abs(self.quantity) * current_price
    
    @property
    def unrealized_pnl(self):
        """
        Calculate unrealized P&L using current market price
        """
        if self.quantity == 0:
            return self.realized_pnl
        
        current_price = self.get_current_price()
        return (current_price - self.avg_entry_price) * self.quantity
    
    def update_from_trade(self, trade):
        """
        Update position when a trade is filled
        Uses average cost basis method
        
        Args:
            trade: Filled Trade object
        """
        if trade.direction in {Trade.BUY, Trade.BUY_TO_COVER}:
            # Adding to position or covering short
            old_value = self.quantity * self.avg_entry_price
            new_value = trade.filled_quantity * trade.avg_fill_price
            
            self.quantity += trade.filled_quantity
            
            if self.quantity != 0:
                self.avg_entry_price = (old_value + new_value) / self.quantity
            
            self.opening_trades.append(trade)
            
        elif trade.direction in {Trade.SELL, Trade.SELL_SHORT}:
            # Reducing position or opening short
            if trade.direction == Trade.SELL and self.quantity > 0:
                # Closing long position - calculate realized P&L
                realized = (trade.avg_fill_price - self.avg_entry_price) * trade.filled_quantity
                self.realized_pnl += realized
                self.closing_trades.append(trade)
            
            self.quantity -= trade.filled_quantity
            
            if self.is_closed:
                self.closed_at = datetime.now()
        
        self.total_cost_basis = abs(self.quantity) * self.avg_entry_price
    
    def __repr__(self):
        position_type = "LONG" if self.is_long else "SHORT" if self.is_short else "CLOSED"
        return (f"Position({self.symbol}, {position_type}, Qty: {self.quantity}, "
                f"Avg: ${self.avg_entry_price:.2f})")

