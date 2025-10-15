"""
###############################################################################
# TradeAccount - Top level trading account that holds all funds
###############################################################################
"""

from .fund import Fund
from .ledger import Ledger
from .oms_tms_mixin import OMSTMSMixin


class TradeAccount(OMSTMSMixin):
    ###############################################################################
    # TradeAccount - Top level trading account (BASE CLASS - Extend or use directly)
    # DATA SOURCE AGNOSTIC: Pass any market data provider that implements get_quote()
    ###############################################################################
    
    def __init__(self, account_id, account_name):
        """
        Initialize TradeAccount - Base class for trading accounts
        
        Can be used directly OR extended for custom behavior (both valid!).
        
        Args:
            account_id: Unique identifier for the account
            account_name: Name of the trading account
        
        Basic Usage (Direct - Quick Start):
            account = TradeAccount("ACC001", "My Account")
            fund = account.create_fund("FUND001", "Fund", 1_000_000)
        
        Advanced Usage (Extend - Production/Custom):
            class HedgeFundAccount(TradeAccount):
                def __init__(self, account_id, account_name, fund_manager, data_api=None):
                    super().__init__(account_id, account_name)
                    self.fund_manager = fund_manager
                    self.data_api = data_api  # Add your own data source
                
                def generate_sec_filing(self):
                    # Your custom reporting logic
                    pass
            
            account = HedgeFundAccount("ACC001", "Fund", "John Doe", data_api=my_api)
            account.generate_sec_filing()
        
        Extension Points:
            - Override create_fund() to return custom Fund subclasses
            - Add data source attributes (your choice: API, DataFrame, CSV reader)
            - Add reporting methods (SEC filings, monthly statements)
            - Add compliance checks (account-level limits)
            - Add data export methods (database, APIs)
            - Add notification systems (alerts, webhooks)
        """
        self.account_id = account_id
        self.account_name = account_name
        self.name = account_name  # For OMSTMSMixin
        self.funds = {}  # Dictionary: "fund_id:fund_name" -> Fund
        
        # Initialize OMS/TMS at account level (highest level, no parent)
        self._initialize_or_inherit_systems(parent=None)
        
        # Initialize ledger for account-level trade tracking
        self.ledger = Ledger(account_name, "TradeAccount")
    
    def create_fund(self, fund_id, fund_name, fund_balance):
        """
        Factory method to create a new fund (automatically links to this account)
        
        Args:
            fund_id: Unique identifier for the fund
            fund_name: Name of the fund
            fund_balance: Total capital raised for this fund
            
        Returns:
            Fund: The newly created fund
        """
        # Pass self (account) as parent - automatically links
        fund = Fund(fund_id, fund_name, fund_balance, trade_account=self)
        key = f"{fund_id}:{fund_name}"
        self.funds[key] = fund
        return fund
    
    def get_fund(self, fund_id):
        """
        Get a fund by ID (searches across all keys)
        
        Args:
            fund_id: ID of the fund to retrieve
            
        Returns:
            Fund or None
        """
        for key, fund in self.funds.items():
            if fund.fund_id == fund_id:
                return fund
        return None
    
    def get_fund_by_key(self, key):
        """
        Get a fund directly by composite key "fund_id:fund_name"
        
        Args:
            key: Composite key in format "fund_id:fund_name"
            
        Returns:
            Fund or None
        """
        return self.funds.get(key)
    
    def update_fund(self, fund_id, **kwargs):
        """
        Update a fund's properties
        
        Args:
            fund_id: ID of fund to update
            **kwargs: Properties to update (fund_name, fund_balance)
        """
        fund = self.get_fund(fund_id)
        if not fund:
            raise ValueError(f"Fund {fund_id} not found")
        
        # If name is changing, need to update dictionary key
        if 'fund_name' in kwargs:
            old_key = f"{fund.fund_id}:{fund.fund_name}"
            fund.fund_name = kwargs['fund_name']
            new_key = f"{fund.fund_id}:{fund.fund_name}"
            
            # Re-add with new key
            del self.funds[old_key]
            self.funds[new_key] = fund
        
        if 'fund_balance' in kwargs:
            fund.fund_balance = kwargs['fund_balance']
        
        return fund
    
    def remove_fund(self, fund_id):
        """
        Remove a fund from the account
        
        Args:
            fund_id: ID of fund to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        fund = self.get_fund(fund_id)
        if fund:
            key = f"{fund.fund_id}:{fund.fund_name}"
            del self.funds[key]
            return True
        return False
    
    @property
    def account_balance(self):
        """Total balance = sum of all fund balances"""
        return sum(fund.fund_balance for fund in self.funds.values())
    
    @property
    def allocated_balance(self):
        """Total capital allocated to funds (same as account_balance for TradeAccount)"""
        return self.account_balance
    
    @property
    def cash_balance(self):
        """
        Cash held at account level (not allocated to any fund).
        For TradeAccount, this is always 0 since all capital comes from funds.
        """
        return 0
    
    def performance_metrics(self, current_prices=None, show_summary=True):
        """
        Calculate and display performance metrics for this account
        (aggregates all fund performance)
        
        Args:
            current_prices: Dict of {symbol: price} for accurate balance calculation.
            show_summary: If True, displays formatted summary. If False, returns metrics object.
        
        Returns:
            PerformanceMetrics object if show_summary=False
        
        Example:
            # Display summary
            account.performance_metrics()
            
            # Get metrics object for analysis
            metrics = account.performance_metrics(show_summary=False)
            print(f"Sharpe Ratio: {metrics.sharpe_ratio()}")
        """
        from tools import PerformanceMetrics
        
        # Calculate current balance across all funds
        initial_balance = self.account_balance
        current_balance = 0
        
        # Add all fund values
        for fund in self.funds.values():
            # Add fund unallocated cash
            current_balance += fund.cash_balance
            
            # Add all portfolio values in this fund
            for portfolio in fund.portfolios.values():
                # Add portfolio unallocated cash
                current_balance += portfolio.cash_balance
                
                # Add all strategy values in this portfolio
                for strategy in portfolio.strategies.values():
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
            owner_name=self.account_name,
            owner_type="TradeAccount",
            ledger=self.ledger,
            initial_balance=initial_balance,
            current_balance=current_balance,
            current_prices=current_prices
        )
        
        if show_summary:
            metrics.summary()
        else:
            return metrics
    
    def summary(self, show_children=False):
        """
        Display comprehensive summary of the trading account
        
        Args:
            show_children: If True, recursively show summaries of all children
        """
        print("=" * 80)
        print(f"📊 TRADE ACCOUNT SUMMARY: {self.account_name} (ID: {self.account_id})")
        print("=" * 80)
        print(f"Total Capital:     ${self.account_balance:>15,.2f}")
        print(f"Number of Funds:   {len(self.funds):>15}")
        print()
        
        if self.funds:
            print("Fund Breakdown:")
            print("-" * 80)
            for i, fund in enumerate(self.funds.values(), 1):
                pct = (fund.fund_balance / self.account_balance * 100) if self.account_balance > 0 else 0
                print(f"  {i}. {fund.fund_name:<40} ${fund.fund_balance:>12,.2f} ({pct:>5.1f}%)")
            print("=" * 80)
            
            if show_children:
                print()
                for fund in self.funds.values():
                    fund.summary(show_children=True)
        else:
            print("  No funds registered yet.")
            print("=" * 80)

