"""
###############################################################################
# Example: TradeAccount - Top-Level Account Management
###############################################################################
# This example demonstrates:
# 1. Creating a TradeAccount
# 2. Adding multiple funds
# 3. Account-level operations
# 4. Viewing account summary
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount

print("=" * 80)
print("EXAMPLE: TradeAccount - Account Management")
print("=" * 80)

###############################################################################
# NOTE: Price Data Handling
###############################################################################
# The framework does NOT fetch prices - YOU control all data!
# Common patterns:
#   1. Create DataFrame: price_df = pd.DataFrame({'AAPL': [150, 151, ...]})
#   2. Load from CSV: price_df = pd.read_csv('prices.csv')
#   3. Fetch from API: price = yfinance.Ticker('AAPL').history()
#   4. Use dict: prices = {'AAPL': 150.00, 'GOOGL': 140.00}
#
# See example_strategy.py and example_complete.py for full pandas integration
###############################################################################

print("\n💡 Data Handling: Framework is data-source agnostic")
print("   You provide prices however you want (DataFrame, API, CSV, dict)")
print("   Examples below use simple dict for clarity")
print()

###############################################################################
# PART 1: Create Trade Account
###############################################################################

print("\n📊 Part 1: Creating Trade Account")
print("-" * 80)

# Create the top-level account
account = TradeAccount(
    account_id="ACC001",
    account_name="Multi-Strategy Hedge Fund"
)

print(f"✅ Created account: {account.account_name}")
print(f"   Account ID: {account.account_id}")
print(f"   Initial Balance: ${account.account_balance:,.2f}")
print(f"   Number of Funds: {len(account.funds)}")

###############################################################################
# PART 2: Add Multiple Funds
###############################################################################

print("\n📊 Part 2: Adding Funds to Account")
print("-" * 80)

# Create first fund - Growth focused
fund1 = account.create_fund(
    fund_id="FUND001",
    fund_name="Growth Fund",
    fund_balance=5_000_000.00
)
print(f"✅ Added {fund1.fund_name}: ${fund1.fund_balance:,.2f}")

# Create second fund - Value focused
fund2 = account.create_fund(
    fund_id="FUND002",
    fund_name="Value Fund",
    fund_balance=3_000_000.00
)
print(f"✅ Added {fund2.fund_name}: ${fund2.fund_balance:,.2f}")

# Create third fund - Dividend focused
fund3 = account.create_fund(
    fund_id="FUND003",
    fund_name="Dividend Income Fund",
    fund_balance=2_000_000.00
)
print(f"✅ Added {fund3.fund_name}: ${fund3.fund_balance:,.2f}")

###############################################################################
# PART 3: Query Account Information
###############################################################################

print("\n📊 Part 3: Querying Account Information")
print("-" * 80)

print(f"Total Account Balance: ${account.account_balance:,.2f}")
print(f"Number of Funds: {len(account.funds)}")
print(f"\nFunds List:")
for key, fund in account.funds.items():
    pct = (fund.fund_balance / account.account_balance) * 100
    print(f"  - {fund.fund_name}: ${fund.fund_balance:,.2f} ({pct:.1f}%)")

###############################################################################
# PART 4: Retrieve Specific Fund
###############################################################################

print("\n📊 Part 4: Retrieving Specific Fund")
print("-" * 80)

# Get fund by ID
growth_fund = account.get_fund("FUND001")
if growth_fund:
    print(f"✅ Found fund: {growth_fund.fund_name}")
    print(f"   Balance: ${growth_fund.fund_balance:,.2f}")
    print(f"   ID: {growth_fund.fund_id}")

###############################################################################
# PART 5: Account Summary
###############################################################################

print("\n📊 Part 5: Account Summary")
print("-" * 80)

account.summary()

###############################################################################
# PART 6: Account Ledger (before any trades)
###############################################################################

print("\n📊 Part 6: Account Ledger Status")
print("-" * 80)

print(f"Ledger: {account.ledger}")
print(f"Total Trades Recorded: {account.ledger.get_trade_count()}")
print(f"Symbols Traded: {account.ledger.get_symbols_traded()}")

###############################################################################
# PART 7: ADVANCED - Extending TradeAccount (Framework Pattern)
###############################################################################

print("\n📊 Part 7: ADVANCED - Extending TradeAccount for Custom Behavior")
print("-" * 80)

class HedgeFundAccount(TradeAccount):
    """
    Custom TradeAccount with SEC reporting and investor management
    
    This demonstrates extending the base class for production use
    """
    
    def __init__(self, account_id, account_name, fund_manager, aum_target):
        super().__init__(account_id, account_name)
        self.fund_manager = fund_manager
        self.aum_target = aum_target
        self.investor_count = 0
    
    def generate_sec_filing(self):
        """Generate SEC Form ADV filing"""
        print(f"\n📄 SEC Form ADV Filing:")
        print(f"   Fund Manager: {self.fund_manager}")
        print(f"   Total AUM: ${self.account_balance:,.2f}")
        print(f"   AUM Target: ${self.aum_target:,.2f}")
        print(f"   Utilization: {(self.account_balance/self.aum_target*100):.1f}%")
        print(f"   Number of Funds: {len(self.funds)}")
    
    def monthly_investor_statement(self):
        """Generate monthly statement for investors"""
        print(f"\n📊 Monthly Investor Statement - {self.account_name}")
        print(f"   Period: October 2025")
        print(f"   Total AUM: ${self.account_balance:,.2f}")
        print(f"   Number of Investors: {self.investor_count}")
        self.summary(show_children=False)
    
    def add_investor(self, investor_name, capital_committed):
        """Track investor additions"""
        self.investor_count += 1
        print(f"   ✅ Added investor: {investor_name} (${capital_committed:,.2f} committed)")

# Create custom account
print("Creating extended HedgeFundAccount:")
hedge_fund = HedgeFundAccount(
    account_id="HF001",
    account_name="Quantum Strategies Hedge Fund",
    fund_manager="Sarah Chen, CFA",
    aum_target=50_000_000.00
)

# Add some funds
hedge_fund.create_fund("FUND001", "Long/Short Equity", 10_000_000.00)
hedge_fund.create_fund("FUND002", "Market Neutral", 5_000_000.00)

# Use custom methods
hedge_fund.add_investor("ABC Pension Fund", 5_000_000)
hedge_fund.add_investor("XYZ Endowment", 10_000_000)

hedge_fund.generate_sec_filing()
hedge_fund.monthly_investor_statement()

print("\n✅ Extended TradeAccount with custom reporting and investor tracking!")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - TradeAccount Example")
print("=" * 80)

print(f"""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ TradeAccount Creation (Direct Usage)
   - Use TradeAccount directly for quick starts
   - Top-level container for all trading activity
   - Holds multiple funds with independent capital

2. ✅ Fund Management
   - Create multiple funds with create_fund()
   - Each fund tracks its own balance independently
   - Funds can have different investment strategies

3. ✅ Account Queries
   - Get total account balance (sum of all funds)
   - Retrieve specific funds by ID
   - List all funds with allocations

4. ✅ Hierarchy Foundation
   - TradeAccount is the root of the hierarchy
   - Each fund can contain multiple portfolios
   - Provides complete audit trail via ledger

5. ✅ FRAMEWORK PATTERN - Extending TradeAccount
   - Subclass TradeAccount for custom behavior
   - Add custom methods (SEC filings, investor management)
   - Add custom attributes (fund_manager, investor tracking)
   - Override methods for specialized logic
   - Both direct usage AND subclassing are valid approaches!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Account Structure:
  Account: {account.account_name}
  ├── {fund1.fund_name}: ${fund1.fund_balance:,.2f}
  ├── {fund2.fund_name}: ${fund2.fund_balance:,.2f}
  └── {fund3.fund_name}: ${fund3.fund_balance:,.2f}
  
  Total: ${account.account_balance:,.2f}

Next Steps:
  → See example_fund.py for fund-level operations
  → See example_complete.py for full trading workflow
""")

print("=" * 80)


