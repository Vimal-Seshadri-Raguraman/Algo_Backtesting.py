"""
###############################################################################
# Strategy - Base class for custom trading strategies (meant to be subclassed)
###############################################################################
"""

from datetime import datetime
import uuid
from .trade import Trade
from .position import Position
from .exceptions import TradeComplianceError, InsufficientFundsError
from .ledger import Ledger


class Strategy:
    ###############################################################################
    # Strategy - Base class for custom trading strategies (meant to be subclassed)
    # NO ENFORCED RULES: Subclass this to implement your custom trading logic
    # Auto-registers with portfolio when instantiated
    ###############################################################################
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None, data_provider=None):
        """
        Initialize Strategy - works standalone or linked to portfolio
        
        Args:
            strategy_id: Unique identifier for the strategy
            strategy_name: Name of the trading strategy
            strategy_balance: Capital allocated to this strategy
            portfolio: Optional parent Portfolio (None = standalone mode)
            data_provider: Optional data provider (used if portfolio=None)
        
        Examples:
            # Standalone mode
            strategy = Strategy("S001", "My Strategy", 100_000, 
                              portfolio=None, data_provider=my_provider)
            
            # Linked mode (with parent hierarchy)
            strategy = Strategy("S001", "My Strategy", 100_000, portfolio=my_portfolio)
        """
        self.strategy_id = strategy_id
        self.strategy_name = strategy_name
        self.strategy_balance = strategy_balance
        self.portfolio = portfolio
        
        # Get data provider from portfolio OR use direct parameter
        if portfolio is not None:
            self.data_provider = portfolio.data_provider
            # Auto-register with portfolio when linked
            key = f"{strategy_id}:{strategy_name}"
            portfolio.strategies[key] = self
        else:
            self.data_provider = data_provider
        
        # Trading state (NO trade_rules - programmer's responsibility!)
        self.positions = {}  # symbol -> Position object
        self.trades = []  # All trades executed by this strategy
        
        # Initialize ledger for strategy-level trade tracking
        self.ledger = Ledger(strategy_name, "Strategy")
    
    def get_cash_balance(self, current_prices=None):
        """
        Calculate available cash
        
        Args:
            current_prices: Dict of {symbol: price} for open positions.
                          If None, uses entry prices (conservative estimate).
        
        Returns:
            float: Available cash balance
        
        Example:
            prices = {"AAPL": 150.0, "GOOGL": 2800.0}
            cash = strategy.get_cash_balance(prices)
        """
        if current_prices is None:
            current_prices = {}
        
        positions_value = 0
        for symbol, pos in self.positions.items():
            if not pos.is_closed:
                # Use provided price, or fall back to entry price
                price = current_prices.get(symbol, pos.avg_entry_price)
                positions_value += pos.get_market_value(price)
        
        return self.strategy_balance - positions_value
    
    def place_trade(self, symbol, direction, quantity, trade_type, price=None, stop_price=None):
        """
        Place a trade (after programmer has implemented logic correctly)
        
        This method trusts the programmer wrote good logic,
        but still validates against parent rules as safety net
        
        Args:
            symbol: Ticker symbol
            direction: Trade.BUY, Trade.SELL, etc.
            quantity: Number of shares
            trade_type: Trade.MARKET, Trade.LIMIT, etc.
            price: Limit price (required for LIMIT orders, fetched for MARKET)
            stop_price: Stop price (optional)
            
        Returns:
            Trade object
            
        Raises:
            TradeComplianceError: If trade violates parent rules
            InsufficientFundsError: If not enough cash
        """
        # Price is always required - user must provide it
        if price is None:
            raise ValueError(f"Price is required for all trade types. User must provide current market price.")
        
        # Create trade object
        trade = Trade(symbol, direction, quantity, trade_type, self, price, stop_price)
        
        # Get current position if exists
        current_position = self.positions.get(symbol)
        
        # Validate against parent rules (only if linked to hierarchy)
        if self.portfolio is not None:
            # Validate against Portfolio rules (first layer)
            allowed, reason = self.portfolio.validate_trade(trade, current_position)
            if not allowed:
                raise TradeComplianceError(f"Portfolio rule violation: {reason}")
            
            # Validate against Fund rules (second layer, if fund exists)
            if self.portfolio.fund is not None:
                allowed, reason = self.portfolio.fund.validate_trade(trade, self.portfolio.portfolio_balance)
                if not allowed:
                    raise TradeComplianceError(f"Fund rule violation: {reason}")
        
        # Check sufficient funds
        if direction in {Trade.BUY, Trade.BUY_TO_COVER}:
            estimated_cost = quantity * price
            # Use conservative cash estimate (entry prices for existing positions)
            available_cash = self.get_cash_balance()
            if estimated_cost > available_cash:
                raise InsufficientFundsError(
                    f"Insufficient funds: Need ${estimated_cost:,.2f}, have ${available_cash:,.2f}"
                )
        
        # Execute through TradeAccount (this would actually submit to broker)
        trade.trade_id = str(uuid.uuid4())
        trade.status = Trade.SUBMITTED
        trade.submitted_at = datetime.now()
        
        # Simulate immediate fill (in real system, this would be async)
        trade.status = Trade.FILLED
        trade.filled_quantity = quantity
        trade.avg_fill_price = price  # Use the actual/fetched price
        trade.filled_at = datetime.now()
        
        # Record trade in strategy
        self.trades.append(trade)
        
        # Record trade in all ledgers (cascade upward through hierarchy)
        self._record_trade_in_ledgers(trade)
        
        # Update position
        self._update_position(trade)
        
        return trade
    
    def _record_trade_in_ledgers(self, trade):
        """
        Record trade in ledgers up the hierarchy (cascade only if parents exist)
        Strategy → Portfolio → Fund → Account
        
        Args:
            trade: Trade object to record
        """
        # Always record at strategy level
        self.ledger.record_trade(trade)
        
        # Cascade to parent ledgers only if linked
        if self.portfolio is not None:
            self.portfolio.ledger.record_trade(trade)
            
            if self.portfolio.fund is not None:
                self.portfolio.fund.ledger.record_trade(trade)
                
                if self.portfolio.fund.trade_account is not None:
                    self.portfolio.fund.trade_account.ledger.record_trade(trade)
    
    def _update_position(self, trade):
        """Update or create position from filled trade"""
        if trade.symbol not in self.positions:
            self.positions[trade.symbol] = Position(trade.symbol, self)
        
        self.positions[trade.symbol].update_from_trade(trade)
    
    def get_position(self, symbol):
        """Get current position for a symbol"""
        return self.positions.get(symbol)
    
    def get_open_positions(self):
        """Get all open positions"""
        return {sym: pos for sym, pos in self.positions.items() if not pos.is_closed}
    
    ###########################################################################
    # Helper Methods - Query parent rules
    ###########################################################################
    
    def get_max_position_pct(self):
        """Get maximum position size percentage from portfolio rules (if linked)"""
        if self.portfolio is not None:
            return self.portfolio.trade_rules.max_position_size_pct
        return 100.0  # No limit in standalone mode
    
    def get_max_position_value(self):
        """Get maximum position value in dollars"""
        return self.strategy_balance * (self.get_max_position_pct() / 100)
    
    def can_short(self):
        """Check if short selling is allowed by fund rules (if linked)"""
        if self.portfolio is not None and self.portfolio.fund is not None:
            return self.portfolio.fund.trade_rules.allow_short_selling
        return True  # Allowed in standalone mode
    
    def get_allowed_trade_types(self):
        """Get allowed trade types from fund rules (if linked)"""
        if self.portfolio is not None and self.portfolio.fund is not None:
            return self.portfolio.fund.trade_rules.allowed_trade_types
        # All types allowed in standalone mode
        return {Trade.MARKET, Trade.LIMIT, Trade.STOP_LOSS, Trade.STOP_LIMIT, Trade.TRAILING_STOP}
    
    def summary(self, show_positions=False, current_prices=None):
        """
        Display summary of the strategy
        
        Args:
            show_positions: Show open positions detail
            current_prices: Dict of {symbol: price} for accurate cash calculation.
                          If None, uses entry prices.
        """
        print("=" * 80)
        print(f"🎯 STRATEGY SUMMARY: {self.strategy_name} (ID: {self.strategy_id})")
        print("=" * 80)
        print(f"Allocated Capital: ${self.strategy_balance:>15,.2f}")
        print(f"Cash Available:    ${self.get_cash_balance(current_prices):>15,.2f}")
        print(f"Open Positions:    {len(self.get_open_positions()):>15}")
        print(f"Total Trades:      {len(self.trades):>15}")
        if self.portfolio is not None:
            print(f"Parent Portfolio:  {self.portfolio.portfolio_name}")
        else:
            print(f"Parent Portfolio:  None (Standalone)")
        print("=" * 80)
        
        if show_positions and self.get_open_positions():
            print()
            print("Open Positions:")
            print("-" * 80)
            for symbol, position in self.get_open_positions().items():
                print(f"  {symbol}: {position}")
            print("=" * 80)

