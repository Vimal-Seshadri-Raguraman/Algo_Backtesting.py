"""
###############################################################################
# TradeRules - Defines compliance rules for Fund/Portfolio levels
###############################################################################
"""

from .trade import Trade


class TradeRules:
    ###############################################################################
    # TradeRules - Defines compliance rules for Fund/Portfolio levels
    # NOTE: Strategies do NOT have TradeRules - programmer implements compliance
    ###############################################################################
    
    def __init__(self, name="Default Rules"):
        """
        Initialize TradeRules
        
        Args:
            name: Descriptive name for these rules
        """
        self.name = name
        
        # Allowed trade types
        self.allowed_trade_types = {
            Trade.MARKET, Trade.LIMIT, Trade.STOP_LOSS, 
            Trade.STOP_LIMIT, Trade.TRAILING_STOP
        }
        
        # Allowed directions
        self.allowed_directions = {Trade.BUY, Trade.SELL, Trade.SELL_SHORT, Trade.BUY_TO_COVER}
        
        # Position constraints
        self.allow_short_selling = True
        self.allow_margin = True
        self.allow_options = False
        self.allow_futures = False
        
        # Size limits (as percentage)
        self.max_position_size_pct = 100.0  # % of portfolio value
        self.max_single_trade_pct = 100.0   # % of portfolio value
        
        # Symbol restrictions
        self.allowed_symbols = None  # None = all allowed, or set of symbols
        self.restricted_symbols = set()  # Blacklist
    
    def is_trade_allowed(self, trade, portfolio_value, current_position=None):
        """
        Validate if a trade is allowed under these rules
        
        Args:
            trade: Trade object to validate
            portfolio_value: Current portfolio/fund value for percentage calculations
            current_position: Current Position object for the symbol (if exists)
        
        Returns:
            tuple: (bool, str) - (is_allowed, reason_if_not_allowed)
        """
        # Check trade type
        if trade.trade_type not in self.allowed_trade_types:
            return False, f"Trade type '{trade.trade_type}' not allowed"
        
        # Check direction
        if trade.direction not in self.allowed_directions:
            return False, f"Trade direction '{trade.direction}' not allowed"
        
        # Check short selling
        if trade.direction in {Trade.SELL_SHORT, Trade.BUY_TO_COVER}:
            if not self.allow_short_selling:
                return False, "Short selling not allowed"
        
        # Check symbol restrictions
        if self.allowed_symbols is not None:
            if trade.symbol not in self.allowed_symbols:
                return False, f"Symbol '{trade.symbol}' not in allowed list"
        
        if trade.symbol in self.restricted_symbols:
            return False, f"Symbol '{trade.symbol}' is restricted"
        
        # Check position size limits
        if portfolio_value > 0:
            # Price must be provided for size validation
            if trade.price is None:
                return False, "Trade price required for position size validation"
            
            trade_value = trade.quantity * trade.price
            
            # Check single trade size
            trade_pct = (trade_value / portfolio_value) * 100
            if trade_pct > self.max_single_trade_pct:
                return False, (f"Trade size {trade_pct:.1f}% exceeds "
                             f"max single trade limit {self.max_single_trade_pct}%")
            
            # Check resulting position size
            if current_position:
                new_position_qty = current_position.quantity
                if trade.direction in {Trade.BUY, Trade.BUY_TO_COVER}:
                    new_position_qty += trade.quantity
                else:
                    new_position_qty -= trade.quantity
                
                new_position_value = abs(new_position_qty) * trade.price
                position_pct = (new_position_value / portfolio_value) * 100
                
                if position_pct > self.max_position_size_pct:
                    return False, (f"Resulting position size {position_pct:.1f}% exceeds "
                                 f"max position limit {self.max_position_size_pct}%")
        
        return True, "OK"
    
    def __repr__(self):
        return (f"TradeRules('{self.name}', Types: {len(self.allowed_trade_types)}, "
                f"Shorts: {self.allow_short_selling}, Max Pos: {self.max_position_size_pct}%)")

