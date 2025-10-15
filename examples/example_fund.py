"""
###############################################################################
# Example: Fund - Fund Management & Compliance Rules
###############################################################################
# This example demonstrates:
# 1. Creating funds (standalone and within account)
# 2. Configuring fund-level compliance rules
# 3. Creating portfolios within a fund
# 4. Fund capital allocation
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Fund, Trade

print("=" * 80)
print("EXAMPLE: Fund - Capital Management & Compliance")
print("=" * 80)

###############################################################################
# PART 1: Create Fund (Two Ways)
###############################################################################

print("\n📊 Part 1: Creating Funds")
print("-" * 80)

# Method 1: Standalone fund (no parent account)
standalone_fund = Fund(
    fund_id="FUND_STANDALONE",
    fund_name="Independent Fund",
    fund_balance=1_000_000.00,
    trade_account=None  # No parent
)
print(f"✅ Created standalone fund: {standalone_fund.fund_name}")
print(f"   Balance: ${standalone_fund.fund_balance:,.2f}")
print(f"   Parent Account: None (standalone mode)")

# Method 2: Fund within account (recommended)
account = TradeAccount("ACC001", "Main Account")
linked_fund = account.create_fund(
    fund_id="FUND001",
    fund_name="Growth Fund",
    fund_balance=5_000_000.00
)
print(f"\n✅ Created linked fund: {linked_fund.fund_name}")
print(f"   Balance: ${linked_fund.fund_balance:,.2f}")
print(f"   Parent Account: {account.account_name}")

###############################################################################
# PART 2: Configure Fund-Level Compliance Rules
###############################################################################

print("\n📊 Part 2: Setting Up Compliance Rules")
print("-" * 80)

# Configure what's allowed at the fund level
linked_fund.trade_rules.allowed_trade_types = {
    Trade.MARKET,
    Trade.LIMIT,
    Trade.STOP_LOSS
}

linked_fund.trade_rules.allowed_directions = {
    Trade.BUY,
    Trade.SELL,
    Trade.SELL_SHORT,
    Trade.BUY_TO_COVER
}

# Position size limits (as % of portfolio value)
linked_fund.trade_rules.max_position_size_pct = 20.0  # Max 20% per position
linked_fund.trade_rules.max_single_trade_pct = 10.0   # Max 10% per trade

# Trading permissions
linked_fund.trade_rules.allow_short_selling = True
linked_fund.trade_rules.allow_margin = True
linked_fund.trade_rules.allow_options = False
linked_fund.trade_rules.allow_futures = False

print("✅ Compliance Rules Configured:")
print(f"   Max Position Size: {linked_fund.trade_rules.max_position_size_pct}%")
print(f"   Max Single Trade: {linked_fund.trade_rules.max_single_trade_pct}%")
print(f"   Short Selling: {linked_fund.trade_rules.allow_short_selling}")
print(f"   Margin Trading: {linked_fund.trade_rules.allow_margin}")
print(f"   Options: {linked_fund.trade_rules.allow_options}")
print(f"   Futures: {linked_fund.trade_rules.allow_futures}")

###############################################################################
# PART 3: Create Portfolios Within Fund
###############################################################################

print("\n📊 Part 3: Allocating Capital to Portfolios")
print("-" * 80)

# Create tech portfolio
tech_portfolio = linked_fund.create_portfolio(
    portfolio_id="PORT001",
    portfolio_name="Technology Portfolio",
    portfolio_balance=2_000_000.00
)
print(f"✅ Created {tech_portfolio.portfolio_name}")
print(f"   Allocated: ${tech_portfolio.portfolio_balance:,.2f}")

# Create healthcare portfolio
healthcare_portfolio = linked_fund.create_portfolio(
    portfolio_id="PORT002",
    portfolio_name="Healthcare Portfolio",
    portfolio_balance=1_500_000.00
)
print(f"✅ Created {healthcare_portfolio.portfolio_name}")
print(f"   Allocated: ${healthcare_portfolio.portfolio_balance:,.2f}")

# Create finance portfolio
finance_portfolio = linked_fund.create_portfolio(
    portfolio_id="PORT003",
    portfolio_name="Finance Portfolio",
    portfolio_balance=1_000_000.00
)
print(f"✅ Created {finance_portfolio.portfolio_name}")
print(f"   Allocated: ${finance_portfolio.portfolio_balance:,.2f}")

###############################################################################
# PART 4: Fund Capital Status
###############################################################################

print("\n📊 Part 4: Fund Capital Status")
print("-" * 80)

print(f"Total Fund Capital:    ${linked_fund.fund_balance:,.2f}")
print(f"Allocated to Portfolios: ${linked_fund.allocated_balance:,.2f} ({linked_fund.allocated_balance/linked_fund.fund_balance*100:.1f}%)")
print(f"Unallocated Cash:      ${linked_fund.cash_balance:,.2f} ({linked_fund.cash_balance/linked_fund.fund_balance*100:.1f}%)")
print(f"Number of Portfolios:  {len(linked_fund.portfolios)}")

###############################################################################
# PART 5: Query Portfolios
###############################################################################

print("\n📊 Part 5: Querying Portfolios")
print("-" * 80)

# Get specific portfolio
tech = linked_fund.get_portfolio("PORT001")
if tech:
    print(f"Found portfolio: {tech.portfolio_name}")
    print(f"  Balance: ${tech.portfolio_balance:,.2f}")

# List all portfolios
print("\nAll Portfolios:")
for key, portfolio in linked_fund.portfolios.items():
    pct = (portfolio.portfolio_balance / linked_fund.fund_balance) * 100
    print(f"  - {portfolio.portfolio_name}: ${portfolio.portfolio_balance:,.2f} ({pct:.1f}%)")

###############################################################################
# PART 6: Conservative vs Aggressive Fund Comparison
###############################################################################

print("\n📊 Part 6: Comparing Fund Strategies")
print("-" * 80)

# Create conservative fund
conservative_fund = account.create_fund(
    fund_id="FUND002",
    fund_name="Conservative Fund",
    fund_balance=2_000_000.00
)

# Conservative rules
conservative_fund.trade_rules.max_position_size_pct = 10.0  # Max 10%
conservative_fund.trade_rules.max_single_trade_pct = 5.0    # Max 5%
conservative_fund.trade_rules.allow_short_selling = False   # Long only
conservative_fund.trade_rules.allow_margin = False

# Create aggressive fund
aggressive_fund = account.create_fund(
    fund_id="FUND003",
    fund_name="Aggressive Fund",
    fund_balance=1_000_000.00
)

# Aggressive rules
aggressive_fund.trade_rules.max_position_size_pct = 30.0  # Max 30%
aggressive_fund.trade_rules.max_single_trade_pct = 15.0   # Max 15%
aggressive_fund.trade_rules.allow_short_selling = True
aggressive_fund.trade_rules.allow_margin = True

print("Fund Comparison:")
print(f"\n{'Metric':<25} {'Conservative':<20} {'Growth':<20} {'Aggressive':<20}")
print("-" * 85)
print(f"{'Max Position Size':<25} {conservative_fund.trade_rules.max_position_size_pct:<20.1f}% {linked_fund.trade_rules.max_position_size_pct:<20.1f}% {aggressive_fund.trade_rules.max_position_size_pct:<20.1f}%")
print(f"{'Max Single Trade':<25} {conservative_fund.trade_rules.max_single_trade_pct:<20.1f}% {linked_fund.trade_rules.max_single_trade_pct:<20.1f}% {aggressive_fund.trade_rules.max_single_trade_pct:<20.1f}%")
print(f"{'Short Selling':<25} {str(conservative_fund.trade_rules.allow_short_selling):<20} {str(linked_fund.trade_rules.allow_short_selling):<20} {str(aggressive_fund.trade_rules.allow_short_selling):<20}")
print(f"{'Margin Trading':<25} {str(conservative_fund.trade_rules.allow_margin):<20} {str(linked_fund.trade_rules.allow_margin):<20} {str(aggressive_fund.trade_rules.allow_margin):<20}")

###############################################################################
# PART 7: Fund Summary
###############################################################################

print("\n📊 Part 7: Fund Summary")
print("-" * 80)

linked_fund.summary(show_children=False)

###############################################################################
# PART 8: ADVANCED - Extending Fund (Framework Pattern)
###############################################################################

print("\n📊 Part 8: ADVANCED - Extending Fund for Custom Behavior")
print("-" * 80)

class AutoRebalancingFund(Fund):
    """
    Custom Fund with automatic quarterly rebalancing
    
    This demonstrates extending the base class for production use
    """
    
    def __init__(self, fund_id, fund_name, fund_balance, rebalance_freq='quarterly', 
                 target_allocations=None):
        super().__init__(fund_id, fund_name, fund_balance)
        self.rebalance_freq = rebalance_freq
        self.target_allocations = target_allocations or {}
        self.last_rebalance_date = None
    
    def should_rebalance(self):
        """Check if rebalancing is needed based on frequency"""
        # Simplified logic
        return len(self.portfolios) > 0
    
    def execute_rebalance(self):
        """Rebalance all portfolios to target weights"""
        print(f"\n⚖️  Rebalancing {self.fund_name}...")
        print(f"   Frequency: {self.rebalance_freq}")
        print(f"   Total Capital: ${self.fund_balance:,.2f}")
        
        # Show current allocations
        print(f"\n   Current Allocations:")
        for portfolio in self.portfolios.values():
            actual_pct = (portfolio.portfolio_balance / self.fund_balance) * 100
            print(f"     - {portfolio.portfolio_name}: {actual_pct:.1f}%")
        
        print(f"\n   ✅ Rebalancing complete")
    
    def calculate_nav(self):
        """Calculate Net Asset Value per share"""
        # Custom NAV calculation
        nav_per_share = self.fund_balance / 1000  # Assuming 1000 shares
        print(f"\n💰 NAV Calculation:")
        print(f"   Total Assets: ${self.fund_balance:,.2f}")
        print(f"   Shares Outstanding: 1,000")
        print(f"   NAV per Share: ${nav_per_share:,.2f}")
        return nav_per_share

# Create extended fund
print("\nCreating extended AutoRebalancingFund:")
auto_fund = AutoRebalancingFund(
    fund_id="FUND_AUTO",
    fund_name="Quarterly Rebalanced Fund",
    fund_balance=20_000_000.00,
    rebalance_freq='quarterly',
    target_allocations={'tech': 0.40, 'healthcare': 0.30, 'finance': 0.30}
)

# Create portfolios
auto_fund.create_portfolio("PORT001", "Technology", 8_000_000.00)
auto_fund.create_portfolio("PORT002", "Healthcare", 6_000_000.00)
auto_fund.create_portfolio("PORT003", "Finance", 6_000_000.00)

# Use custom methods
if auto_fund.should_rebalance():
    auto_fund.execute_rebalance()

auto_fund.calculate_nav()

print("\n✅ Extended Fund with custom rebalancing and NAV calculation!")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Fund Example")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Fund Creation
   - Standalone mode (no parent account)
   - Linked mode (within account hierarchy)

2. ✅ Compliance Rules
   - Position size limits (max % per position and trade)
   - Trading permissions (short selling, margin, options, futures)
   - Trade type restrictions (MARKET, LIMIT, STOP_LOSS, etc.)

3. ✅ Portfolio Allocation
   - Create multiple portfolios within a fund
   - Allocate capital from fund to portfolios
   - Track allocated vs. unallocated capital

4. ✅ Fund Strategies
   - Conservative: Lower limits, long-only
   - Growth: Balanced risk/reward
   - Aggressive: Higher limits, margin enabled

5. ✅ Capital Management
   - Monitor allocated vs. unallocated capital
   - Query portfolio balances
   - Automatic ledger tracking

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fund Hierarchy:
  Account: Main Account
  ├── Growth Fund ($5,000,000)
  │   ├── Technology Portfolio ($2,000,000)
  │   ├── Healthcare Portfolio ($1,500,000)
  │   └── Finance Portfolio ($1,000,000)
  ├── Conservative Fund ($2,000,000)
  └── Aggressive Fund ($1,000,000)

Next Steps:
  → See example_portfolio.py for portfolio-level operations
  → See example_strategy.py for strategy implementation
  → See example_complete.py for full trading workflow
""")

print("=" * 80)


