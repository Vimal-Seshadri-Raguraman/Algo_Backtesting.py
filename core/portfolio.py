"""
###############################################################################
# Portfolio - Allocation of fund capital to specific investment portfolios
###############################################################################
"""

from .rules import TradeRules
from .ledger import Ledger
from .oms_tms_mixin import OMSTMSMixin


class Portfolio(OMSTMSMixin):
    ###############################################################################
    # Portfolio - Allocation of fund capital (BASE CLASS - Extend or use directly)
    # ENFORCED RULES: Portfolio-level risk rules are checked before trade execution
    ###############################################################################
    
    def __init__(self, portfolio_id, portfolio_name, portfolio_balance, fund=None):
        """
        Initialize Portfolio - Base class for portfolio management
        
        Can be used directly OR extended for custom behavior (both valid!).
        
        Args:
            portfolio_id: Unique identifier for the portfolio
            portfolio_name: Name of the portfolio
            portfolio_balance: Capital for this portfolio
            fund: Optional parent Fund (None = standalone mode)
        
        Basic Usage (Direct - Quick Start):
            portfolio = Portfolio("PORT001", "Tech Portfolio", 500_000)
            strategy = MyStrategy("STRAT001", "Strategy", 100_000, portfolio)
        
        Advanced Usage (Extend - Production/Custom):
            class RiskManagedPortfolio(Portfolio):
                def __init__(self, portfolio_id, portfolio_name, portfolio_balance, 
                           fund=None, var_limit=0.05, price_feed=None):
                    super().__init__(portfolio_id, portfolio_name, portfolio_balance, fund)
                    self.var_limit = var_limit
                    self.price_feed = price_feed  # Add your own data source
                
                def calculate_var(self):
                    # Your custom VaR calculation using self.price_feed
                    pass
                
                def enforce_var_limit(self):
                    # Your custom risk enforcement
                    var = self.calculate_var()
                    if var > self.var_limit:
                        # Take action
                        pass
            
            portfolio = RiskManagedPortfolio("PORT001", "Risk Managed", 5_000_000,
                                            price_feed=my_dataframe)
            portfolio.enforce_var_limit()
        
        Extension Points:
            - Add your own data source attributes (DataFrame, API client, CSV reader)
            - Add risk monitoring (VaR, concentration, correlation)
            - Add auto-rebalancing across strategies
            - Add sector/asset class allocation tracking
            - Add drawdown monitoring and alerts
            - Add performance attribution by strategy
            - Override validate_trade() for custom pre-trade checks
        """
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        self.name = portfolio_name  # For OMSTMSMixin
        self.portfolio_balance = portfolio_balance
        self.fund = fund
        
        # Initialize or inherit OMS/TMS
        self._initialize_or_inherit_systems(parent=fund)
        
        self.strategies = {}  # Dictionary: "strategy_id:strategy_name" -> Strategy
        
        # Initialize trade rules for this portfolio
        self.trade_rules = TradeRules(name=f"{portfolio_name} Portfolio Rules")
        
        # Initialize ledger for portfolio-level trade tracking
        self.ledger = Ledger(portfolio_name, "Portfolio")
    
    def get_strategy(self, strategy_id):
        """Get a strategy by ID"""
        for key, strategy in self.strategies.items():
            if strategy.strategy_id == strategy_id:
                return strategy
        return None
    
    def get_strategy_by_key(self, key):
        """
        Get a strategy directly by composite key "strategy_id:strategy_name"
        
        Args:
            key: Composite key in format "strategy_id:strategy_name"
            
        Returns:
            Strategy or None
        """
        return self.strategies.get(key)
    
    def update_strategy(self, strategy_id, **kwargs):
        """
        Update a strategy's properties
        
        Args:
            strategy_id: ID of strategy to update
            **kwargs: Properties to update (strategy_name, strategy_balance)
        """
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        if 'strategy_name' in kwargs:
            old_key = f"{strategy.strategy_id}:{strategy.strategy_name}"
            strategy.strategy_name = kwargs['strategy_name']
            new_key = f"{strategy.strategy_id}:{strategy.strategy_name}"
            del self.strategies[old_key]
            self.strategies[new_key] = strategy
        
        if 'strategy_balance' in kwargs:
            # Check if new balance is valid
            new_balance = kwargs['strategy_balance']
            balance_change = new_balance - strategy.strategy_balance
            if balance_change > self.cash_balance:
                raise ValueError(f"Cannot increase balance by ${balance_change:,.2f}: only ${self.cash_balance:,.2f} available")
            strategy.strategy_balance = new_balance
        
        return strategy
    
    def remove_strategy(self, strategy_id):
        """
        Remove a strategy from the portfolio
        
        Args:
            strategy_id: ID of strategy to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        strategy = self.get_strategy(strategy_id)
        if strategy:
            key = f"{strategy.strategy_id}:{strategy.strategy_name}"
            del self.strategies[key]
            return True
        return False
    
    @property
    def allocated_balance(self):
        """Total capital allocated to strategies"""
        return sum(strategy.strategy_balance for strategy in self.strategies.values())
    
    @property
    def cash_balance(self):
        """Unallocated capital (cash) remaining in portfolio"""
        return self.portfolio_balance - self.allocated_balance
    
    def validate_trade(self, trade, current_position=None):
        """
        Enforce portfolio-level risk rules
        Called before fund validation
        
        Args:
            trade: Trade object to validate
            current_position: Current Position for the symbol (if exists)
            
        Returns:
            tuple: (bool, str) - (is_allowed, reason_if_not)
        """
        return self.trade_rules.is_trade_allowed(trade, self.portfolio_balance, current_position)
    
    def performance_metrics(self, current_prices=None, show_summary=True):
        """
        Calculate and display performance metrics for this portfolio
        (aggregates all strategy performance)
        
        Args:
            current_prices: Dict of {symbol: price} for accurate balance calculation.
            show_summary: If True, displays formatted summary. If False, returns metrics object.
        
        Returns:
            PerformanceMetrics object if show_summary=False
        
        Example:
            # Display summary
            portfolio.performance_metrics()
            
            # Get metrics object for analysis
            metrics = portfolio.performance_metrics(show_summary=False)
            print(f"Sharpe Ratio: {metrics.sharpe_ratio()}")
        """
        from tools import PerformanceMetrics
        
        # Calculate current balance: unallocated cash + all strategy values
        current_balance = self.cash_balance  # Start with unallocated cash
        
        # Add all strategy values
        for strategy in self.strategies.values():
            # Get strategy cash (at entry prices)
            strategy_cash = strategy.get_cash_balance(current_prices=None)
            current_balance += strategy_cash
            
            # Add current value of strategy's open positions
            for symbol, position in strategy.get_open_positions().items():
                if not position.is_closed:
                    price = current_prices.get(symbol, position.avg_entry_price) if current_prices else position.avg_entry_price
                    current_balance += position.get_market_value(price)
            
            # Add realized P&L from closed positions
            realized_pnl = sum(pos.realized_pnl for pos in strategy.positions.values())
            current_balance += realized_pnl
        
        # Create performance metrics object
        metrics = PerformanceMetrics(
            owner_name=self.portfolio_name,
            owner_type="Portfolio",
            ledger=self.ledger,
            initial_balance=self.portfolio_balance,
            current_balance=current_balance,
            current_prices=current_prices
        )
        
        if show_summary:
            metrics.summary()
        else:
            return metrics
    
    def summary(self, show_children=False):
        """
        Display comprehensive summary of the portfolio
        
        Args:
            show_children: If True, recursively show summaries of all strategies
        """
        print("=" * 80)
        print(f"📁 PORTFOLIO SUMMARY: {self.portfolio_name} (ID: {self.portfolio_id})")
        print("=" * 80)
        print(f"Total Capital:     ${self.portfolio_balance:>15,.2f}")
        print(f"Allocated:         ${self.allocated_balance:>15,.2f} ({self.allocated_balance/self.portfolio_balance*100:>5.1f}%)")
        print(f"Cash (Unallocated):${self.cash_balance:>15,.2f} ({self.cash_balance/self.portfolio_balance*100:>5.1f}%)")
        print(f"Number of Strategies: {len(self.strategies):>12}")
        print()
        
        if self.strategies:
            print("Strategy Breakdown:")
            print("-" * 80)
            for i, strategy in enumerate(self.strategies.values(), 1):
                pct = (strategy.strategy_balance / self.portfolio_balance * 100) if self.portfolio_balance > 0 else 0
                print(f"  {i}. {strategy.strategy_name:<40} ${strategy.strategy_balance:>12,.2f} ({pct:>5.1f}%)")
            print("=" * 80)
            
            if show_children:
                print()
                for strategy in self.strategies.values():
                    strategy.summary()
        else:
            print("  No strategies created yet.")
            print("=" * 80)

