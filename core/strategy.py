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
from .oms_tms_mixin import OMSTMSMixin


class Strategy(OMSTMSMixin):
    ###############################################################################
    # Strategy - Base class for trading strategies (BASE CLASS - MUST subclass)
    # NO ENFORCED RULES: Subclass this to implement your custom trading logic
    # Auto-registers with portfolio when instantiated
    ###############################################################################
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None):
        """
        Initialize Strategy - Base class for implementing trading strategies
        
        MUST be subclassed to implement trading logic (abstract-like base class).
        Can run standalone OR linked to portfolio hierarchy (both valid!).
        
        Args:
            strategy_id: Unique identifier for the strategy
            strategy_name: Name of the trading strategy
            strategy_balance: Capital allocated to this strategy
            portfolio: Optional parent Portfolio (None = standalone mode)
        
        Basic Usage (Subclass and Implement):
            class MomentumStrategy(Strategy):
                def run(self, price_data):
                    # Get price from YOUR data source
                    price = price_data['AAPL'].iloc[-1]
                    self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=price)
            
            strategy = MomentumStrategy("STRAT001", "Momentum", 100_000)
            strategy.run(my_price_dataframe)
        
        Advanced Usage (Add Custom Data Sources):
            class MovingAverageCrossover(Strategy):
                def __init__(self, strategy_id, strategy_name, strategy_balance, 
                           portfolio=None, short_window=20, long_window=50, 
                           data_api=None):
                    super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
                    self.short_window = short_window
                    self.long_window = long_window
                    self.data_api = data_api  # Add YOUR data source
                
                def run(self, price_data):
                    # Calculate MAs and trade based on crossover
                    sma_short = price_data.rolling(window=self.short_window).mean()
                    sma_long = price_data.rolling(window=self.long_window).mean()
                    # Trading logic...
            
            # Use with DataFrame
            strategy = MovingAverageCrossover("STRAT001", "MA Cross", 100_000,
                                             short_window=10, long_window=30)
            strategy.run(price_df)
            
            # Or with API
            strategy = MovingAverageCrossover("STRAT001", "MA Cross", 100_000,
                                             data_api=yfinance_client)
        
        Extension Points (Methods to Override/Add):
            - run(): REQUIRED - Implement your trading logic (pass data as parameter)
            - Add your own data source attributes (API, DataFrame, CSV reader)
            - Override place_trade() for custom trade execution
            - Add signal generation methods
            - Add entry/exit logic
            - Add position sizing algorithms
            - Add risk management methods
            - Add custom performance tracking
        """
        self.strategy_id = strategy_id
        self.strategy_name = strategy_name
        self.name = strategy_name  # For OMSTMSMixin
        self.strategy_balance = strategy_balance
        self.portfolio = portfolio
        
        # Initialize or inherit OMS/TMS (lazy initialization pattern)
        self._initialize_or_inherit_systems(parent=portfolio)
        
        # Auto-register with portfolio when linked
        if portfolio is not None:
            key = f"{strategy_id}:{strategy_name}"
            portfolio.strategies[key] = self
        
        # Trading state (NO trade_rules - programmer's responsibility!)
        # Note: positions and trades are managed by TMS, accessed via properties
        self.trades = []  # All trades executed by this strategy (TMS will populate)
        
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
    
    def place_order(self, symbol, action, quantity, order_type, price, **kwargs):
        """
        Place an order via OMS (simple interface - just say BUY or SELL)
        
        OMS handles:
        - Rule aggregation from hierarchy
        - Smart direction determination
        - Order validation
        - Order splitting if needed
        
        Args:
            symbol: Ticker symbol
            action: "BUY" or "SELL" (simple intent)
            quantity: Desired quantity
            order_type: Trade.MARKET, Trade.LIMIT, etc.
            price: Execution price
            **kwargs: Additional parameters (trade_date, stop_price, etc.)
        
        Returns:
            tuple: (Order object, list of executed Trade objects)
        
        Example:
            # Simple!
            order, trades = strategy.place_order("AAPL", "BUY", 100, Trade.MARKET, 150.0)
            
            # With backtest date
            order, trades = strategy.place_order("AAPL", "SELL", 100, Trade.MARKET, 155.0, 
                                                  trade_date=historical_date)
        """
        # Create order via OMS
        order = self._oms.create_order(
            strategy=self,
            symbol=symbol,
            action=action,
            quantity=quantity,
            order_type=order_type,
            price=price,
            **kwargs
        )
        
        # Submit order to TMS for execution
        executed_trades = self._oms.submit_order(order)
        
        return order, executed_trades
    
    # Backward compatibility: map old interface to new OMS
    def place_trade(self, symbol, direction, quantity, trade_type, price=None, stop_price=None, trade_date=None):
        """
        Backward compatibility wrapper - maps old interface to new OMS system
        
        Note: This is now a wrapper around place_order() which uses OMS/TMS
        
        Args:
            symbol: Ticker symbol
            direction: Trade.BUY, Trade.SELL, Trade.SELL_SHORT, Trade.BUY_TO_COVER
            quantity: Number of shares
            trade_type: Trade.MARKET, Trade.LIMIT, etc.
            price: Execution price
            stop_price: Stop price (optional)
            trade_date: Optional datetime for backtesting
            
        Returns:
            Trade object (first trade from executed trades)
        """
        # Map direction to simple action
        if direction in {Trade.BUY, Trade.BUY_TO_COVER}:
            action = "BUY"
        else:
            action = "SELL"
        
        # Use new OMS system
        order, trades = self.place_order(
            symbol=symbol,
            action=action,
            quantity=quantity,
            order_type=trade_type,
            price=price,
            stop_price=stop_price,
            trade_date=trade_date
        )
        
        # Return first trade for backward compatibility
        return trades[0] if trades else None
    
    ###########################################################################
    # SMART TRADE - Intelligent trade placement with automatic direction
    ###########################################################################
    
    def smart_trade(self, symbol, action, quantity, trade_type, price, 
                    stop_price=None, allow_partial=True, verbose=True, trade_date=None):
        """
        Smart trade wrapper - now uses OMS system for all logic
        
        Note: This is now a wrapper around place_order() which uses OMS/TMS.
        The OMS handles all the smart direction determination automatically.
        
        Args:
            symbol: Ticker symbol
            action: "BUY" or "SELL" (simple intent)
            quantity: Desired quantity
            trade_type: Trade.MARKET, Trade.LIMIT, etc.
            price: Execution price
            stop_price: Optional stop price
            allow_partial: Ignored (OMS always allows splits)
            verbose: Ignored (OMS handles logging internally)
            trade_date: Optional datetime for backtesting
        
        Returns:
            list: List of Trade objects executed
        
        Examples:
            # Simple - OMS does everything!
            trades = strategy.smart_trade("AAPL", "BUY", 100, Trade.MARKET, 150.0)
            trades = strategy.smart_trade("AAPL", "SELL", 100, Trade.MARKET, 155.0)
        """
        # Use new OMS system - it does everything smart_trade used to do!
        order, trades = self.place_order(
            symbol=symbol,
            action=action,
            quantity=quantity,
            order_type=trade_type,
            price=price,
            stop_price=stop_price,
            trade_date=trade_date
        )
        
        return trades
    
    def get_position(self, symbol):
        """
        Get current position for a symbol from TMS
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Position object or None
        """
        return self._tms.get_position(self, symbol)
    
    @property
    def positions(self):
        """
        Get all positions from TMS as a dict {symbol: Position}
        
        Returns:
            dict: Dictionary of symbol -> Position
        """
        positions_dict = {}
        # Get all positions from TMS for this strategy
        for key, position in self._tms.positions.items():
            strategy_id, symbol = key
            if strategy_id == self.strategy_id:
                positions_dict[symbol] = position
        return positions_dict
    
    def get_open_positions(self):
        """Get all open positions from TMS"""
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
    
    def performance_metrics(self, current_prices=None, show_summary=True):
        """
        Calculate and display performance metrics for this strategy
        
        Args:
            current_prices: Dict of {symbol: price} for accurate balance calculation.
                          If None, uses cash + positions at entry prices.
            show_summary: If True, displays formatted summary. If False, returns metrics object.
        
        Returns:
            PerformanceMetrics object if show_summary=False
        
        Example:
            # Display summary
            strategy.performance_metrics()
            
            # Get metrics object for analysis
            metrics = strategy.performance_metrics(show_summary=False)
            print(f"Sharpe Ratio: {metrics.sharpe_ratio()}")
        """
        from tools import PerformanceMetrics
        
        # Calculate current balance properly:
        # cash (at entry prices) + positions (at current prices) + realized P&L
        
        # Get cash balance using ENTRY prices (actual cash remaining)
        cash_balance = self.get_cash_balance(current_prices=None)
        
        # Add current value of open positions (at current prices)
        positions_value = 0
        for symbol, position in self.get_open_positions().items():
            if not position.is_closed:
                price = current_prices.get(symbol, position.avg_entry_price) if current_prices else position.avg_entry_price
                positions_value += position.get_market_value(price)
        
        # Add realized P&L from closed positions
        realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        
        current_balance = cash_balance + positions_value + realized_pnl
        
        # Create performance metrics object
        metrics = PerformanceMetrics(
            owner_name=self.strategy_name,
            owner_type="Strategy",
            ledger=self.ledger,
            initial_balance=self.strategy_balance,
            current_balance=current_balance,
            current_prices=current_prices
        )
        
        if show_summary:
            metrics.summary()
        else:
            return metrics
    
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

