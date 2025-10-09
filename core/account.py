"""
###############################################################################
# TradeAccount - Top level trading account that holds all funds
###############################################################################
"""

from .fund import Fund
from .ledger import Ledger


class TradeAccount:
    ###############################################################################
    # TradeAccount - Top level trading account that holds all funds
    # DATA SOURCE AGNOSTIC: Pass any market data provider that implements get_quote()
    ###############################################################################
    
    def __init__(self, account_id, account_name, data_provider=None):
        """
        Initialize TradeAccount
        
        Args:
            account_id: Unique identifier for the account
            account_name: Name of the trading account
            data_provider: Market data provider (must implement get_quote() method)
                          Examples: Yahoo Finance, Alpha Vantage, Interactive Brokers, Alpaca, etc.
        """
        self.account_id = account_id
        self.account_name = account_name
        self.data_provider = data_provider
        self.funds = {}  # Dictionary: "fund_id:fund_name" -> Fund
        
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

