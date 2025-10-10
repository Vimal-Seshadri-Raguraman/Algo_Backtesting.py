"""
###############################################################################
# Fund - Represents capital raised independently and registered to TradeAccount
###############################################################################
"""

from .rules import TradeRules
from .portfolio import Portfolio
from .ledger import Ledger


class Fund:
    ###############################################################################
    # Fund - Represents capital raised independently and registered to TradeAccount
    # ENFORCED RULES: Fund-level compliance rules are checked before trade execution
    ###############################################################################
    
    def __init__(self, fund_id, fund_name, fund_balance, trade_account=None, data_provider=None):
        """
        Initialize Fund - works standalone or linked to account
        
        Args:
            fund_id: Unique identifier for the fund
            fund_name: Name of the fund
            fund_balance: Total capital for this fund
            trade_account: Optional parent TradeAccount (None = standalone mode)
            data_provider: Optional data provider (used if trade_account=None)
        
        Examples:
            # Standalone mode
            fund = Fund("F001", "Growth Fund", 1_000_000,
                       trade_account=None, data_provider=my_provider)
            
            # Linked mode (with parent account)
            fund = Fund("F001", "Growth Fund", 1_000_000, trade_account=my_account)
        """
        self.fund_id = fund_id
        self.fund_name = fund_name
        self.fund_balance = fund_balance
        self.trade_account = trade_account
        
        # Get data provider from account OR use direct parameter
        if trade_account is not None:
            self.data_provider = trade_account.data_provider
        else:
            self.data_provider = data_provider
        
        self.portfolios = {}  # Dictionary: "portfolio_id:portfolio_name" -> Portfolio
        
        # Initialize trade rules for this fund
        self.trade_rules = TradeRules(name=f"{fund_name} Fund Rules")
        
        # Initialize ledger for fund-level trade tracking
        self.ledger = Ledger(fund_name, "Fund")
    
    def create_portfolio(self, portfolio_id, portfolio_name, portfolio_balance):
        """
        Factory method to create a new portfolio (automatically links to this fund)
        
        Args:
            portfolio_id: Unique identifier for the portfolio
            portfolio_name: Name of the portfolio
            portfolio_balance: Capital allocated to this portfolio from fund
            
        Returns:
            Portfolio: The newly created portfolio
        """
        if portfolio_balance > self.cash_balance:
            raise ValueError(f"Insufficient funds: trying to allocate ${portfolio_balance:,.2f} but only ${self.cash_balance:,.2f} available")
        
        # Pass self (fund) as parent - automatically links
        portfolio = Portfolio(portfolio_id, portfolio_name, portfolio_balance, fund=self)
        key = f"{portfolio_id}:{portfolio_name}"
        self.portfolios[key] = portfolio
        return portfolio
    
    def get_portfolio(self, portfolio_id):
        """Get a portfolio by ID"""
        for key, portfolio in self.portfolios.items():
            if portfolio.portfolio_id == portfolio_id:
                return portfolio
        return None
    
    def get_portfolio_by_key(self, key):
        """
        Get a portfolio directly by composite key "portfolio_id:portfolio_name"
        
        Args:
            key: Composite key in format "portfolio_id:portfolio_name"
            
        Returns:
            Portfolio or None
        """
        return self.portfolios.get(key)
    
    def update_portfolio(self, portfolio_id, **kwargs):
        """
        Update a portfolio's properties
        
        Args:
            portfolio_id: ID of portfolio to update
            **kwargs: Properties to update (portfolio_name, portfolio_balance)
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        if 'portfolio_name' in kwargs:
            old_key = f"{portfolio.portfolio_id}:{portfolio.portfolio_name}"
            portfolio.portfolio_name = kwargs['portfolio_name']
            new_key = f"{portfolio.portfolio_id}:{portfolio.portfolio_name}"
            del self.portfolios[old_key]
            self.portfolios[new_key] = portfolio
        
        if 'portfolio_balance' in kwargs:
            # Check if new balance is valid
            new_balance = kwargs['portfolio_balance']
            balance_change = new_balance - portfolio.portfolio_balance
            if balance_change > self.cash_balance:
                raise ValueError(f"Cannot increase balance by ${balance_change:,.2f}: only ${self.cash_balance:,.2f} available")
            portfolio.portfolio_balance = new_balance
        
        return portfolio
    
    def remove_portfolio(self, portfolio_id):
        """
        Remove a portfolio from the fund
        
        Args:
            portfolio_id: ID of portfolio to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio:
            key = f"{portfolio.portfolio_id}:{portfolio.portfolio_name}"
            del self.portfolios[key]
            return True
        return False
    
    @property
    def allocated_balance(self):
        """Total capital allocated to portfolios"""
        return sum(portfolio.portfolio_balance for portfolio in self.portfolios.values())
    
    @property
    def cash_balance(self):
        """Unallocated capital (cash) remaining in fund"""
        return self.fund_balance - self.allocated_balance
    
    def validate_trade(self, trade, portfolio_value):
        """
        Enforce fund-level compliance rules
        Called before any trade execution
        
        Args:
            trade: Trade object to validate
            portfolio_value: Value of the portfolio attempting the trade
            
        Returns:
            tuple: (bool, str) - (is_allowed, reason_if_not)
        """
        return self.trade_rules.is_trade_allowed(trade, portfolio_value)
    
    def summary(self, show_children=False):
        """
        Display comprehensive summary of the fund
        
        Args:
            show_children: If True, recursively show summaries of all portfolios
        """
        print("=" * 80)
        print(f"💼 FUND SUMMARY: {self.fund_name} (ID: {self.fund_id})")
        print("=" * 80)
        print(f"Total Capital:     ${self.fund_balance:>15,.2f}")
        print(f"Allocated:         ${self.allocated_balance:>15,.2f} ({self.allocated_balance/self.fund_balance*100:>5.1f}%)")
        print(f"Cash (Unallocated):${self.cash_balance:>15,.2f} ({self.cash_balance/self.fund_balance*100:>5.1f}%)")
        print(f"Number of Portfolios: {len(self.portfolios):>12}")
        print()
        
        if self.portfolios:
            print("Portfolio Breakdown:")
            print("-" * 80)
            for i, portfolio in enumerate(self.portfolios.values(), 1):
                pct = (portfolio.portfolio_balance / self.fund_balance * 100) if self.fund_balance > 0 else 0
                print(f"  {i}. {portfolio.portfolio_name:<40} ${portfolio.portfolio_balance:>12,.2f} ({pct:>5.1f}%)")
            print("=" * 80)
            
            if show_children:
                print()
                for portfolio in self.portfolios.values():
                    portfolio.summary(show_children=True)
        else:
            print("  No portfolios created yet.")
            print("=" * 80)
