"""
###############################################################################
# Portfolio - Allocation of fund capital to specific investment portfolios
###############################################################################
"""

from .rules import TradeRules
from .ledger import Ledger


class Portfolio:
    ###############################################################################
    # Portfolio - Allocation of fund capital to specific investment portfolios
    # ENFORCED RULES: Portfolio-level risk rules are checked before trade execution
    ###############################################################################
    
    def __init__(self, portfolio_id, portfolio_name, portfolio_balance, fund=None, data_provider=None):
        """
        Initialize Portfolio - works standalone or linked to fund
        
        Args:
            portfolio_id: Unique identifier for the portfolio
            portfolio_name: Name of the portfolio
            portfolio_balance: Capital for this portfolio
            fund: Optional parent Fund (None = standalone mode)
            data_provider: Optional data provider (used if fund=None)
        
        Examples:
            # Standalone mode
            portfolio = Portfolio("P001", "Tech Portfolio", 500_000,
                                fund=None, data_provider=my_provider)
            
            # Linked mode (with parent fund)
            portfolio = Portfolio("P001", "Tech Portfolio", 500_000, fund=my_fund)
        """
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        self.portfolio_balance = portfolio_balance
        self.fund = fund
        
        # Get data provider from fund OR use direct parameter
        if fund is not None:
            self.data_provider = fund.data_provider
        else:
            self.data_provider = data_provider
        
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

