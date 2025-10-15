"""
###############################################################################
# Comprehensive Example - Trade Engine with Ledger System
###############################################################################
# This demonstrates:
# 1. Basic hierarchy setup (Account → Fund → Portfolio → Strategy)
# 2. Trading rule configuration
# 3. Multiple strategies and trade execution
# 4. Hierarchical ledger system
# 5. Performance reporting and analysis
# 6. Query capabilities
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Strategy, Trade
# Note: PerformanceMetrics is now in tools package if you need it
# from tools import PerformanceMetrics

# Note: Framework is DATA-SOURCE AGNOSTIC - YOU provide all price data!
# The framework NEVER fetches prices - you control everything
#
# Common data patterns:
#   1. Pass as parameters: strategy.run(price_dataframe)
#   2. Extend classes: Add your own data_source attribute
#   3. Fetch in strategy: Call your API directly in run() method
#   4. Use dict/DataFrame: prices = {'AAPL': 150.00} or pd.DataFrame
#
# In this example, prices are provided explicitly (simple dict pattern)

###############################################################################
# PART 1: ACCOUNT SETUP
###############################################################################

print("=" * 80)
print("PART 1: CREATING ACCOUNT HIERARCHY")
print("=" * 80)

account = TradeAccount(
    account_id="ACC001",
    account_name="Multi-Strategy Trading Account",
      # Optional: Add your data provider here for live prices
)

print(f"\n✅ Account created: {account.account_name}")
print(f"   Ledger: {account.ledger}")

###############################################################################
# PART 2: FUND CREATION & RULE CONFIGURATION
###############################################################################

print("\n" + "=" * 80)
print("PART 2: CREATING FUNDS WITH TRADING RULES")
print("=" * 80)

# Create Growth Fund (aggressive)
fund1 = account.create_fund(
    fund_id="FUND001",
    fund_name="Growth Fund",
    fund_balance=1_000_000.00
)

# Configure aggressive fund-level rules
fund1.trade_rules.max_position_size_pct = 25.0  # Max 25% per position
fund1.trade_rules.max_single_trade_pct = 10.0   # Max 10% per trade
fund1.trade_rules.allow_short_selling = True

print(f"\n✅ {fund1.fund_name} created: ${fund1.fund_balance:,.2f}")
print(f"   Max Position: {fund1.trade_rules.max_position_size_pct}%")
print(f"   Short Selling: {fund1.trade_rules.allow_short_selling}")
print(f"   Ledger: {fund1.ledger}")

# Create Value Fund (conservative)
fund2 = account.create_fund(
    fund_id="FUND002",
    fund_name="Value Fund",
    fund_balance=500_000.00
)

# Configure conservative fund-level rules
fund2.trade_rules.max_position_size_pct = 15.0  # Max 15% per position
fund2.trade_rules.max_single_trade_pct = 5.0    # Max 5% per trade
fund2.trade_rules.allow_short_selling = False   # Long-only

print(f"\n✅ {fund2.fund_name} created: ${fund2.fund_balance:,.2f}")
print(f"   Max Position: {fund2.trade_rules.max_position_size_pct}%")
print(f"   Short Selling: {fund2.trade_rules.allow_short_selling}")
print(f"   Ledger: {fund2.ledger}")

###############################################################################
# PART 3: PORTFOLIO CREATION
###############################################################################

print("\n" + "=" * 80)
print("PART 3: CREATING PORTFOLIOS")
print("=" * 80)

# Tech Portfolio (Growth Fund)
portfolio1 = fund1.create_portfolio(
    portfolio_id="PORT001",
    portfolio_name="Tech Portfolio",
    portfolio_balance=500_000.00
)

# Configure portfolio-level rules (more restrictive than fund)
portfolio1.trade_rules.max_position_size_pct = 20.0
portfolio1.trade_rules.max_single_trade_pct = 5.0

print(f"\n✅ {portfolio1.portfolio_name} created: ${portfolio1.portfolio_balance:,.2f}")
print(f"   Parent Fund: {fund1.fund_name}")
print(f"   Ledger: {portfolio1.ledger}")

# Finance Portfolio (Value Fund)
portfolio2 = fund2.create_portfolio(
    portfolio_id="PORT002",
    portfolio_name="Finance Portfolio",
    portfolio_balance=300_000.00
)

# Configure portfolio-level rules
portfolio2.trade_rules.max_position_size_pct = 12.0
portfolio2.trade_rules.max_single_trade_pct = 4.0

print(f"\n✅ {portfolio2.portfolio_name} created: ${portfolio2.portfolio_balance:,.2f}")
print(f"   Parent Fund: {fund2.fund_name}")
print(f"   Ledger: {portfolio2.ledger}")

###############################################################################
# PART 4: STRATEGY CREATION
###############################################################################

print("\n" + "=" * 80)
print("PART 4: CREATING TRADING STRATEGIES")
print("=" * 80)

class TechMomentumStrategy(Strategy):
    """
    Tech stock momentum strategy
    Buys high-growth tech stocks
    """
    
    def run(self):
        """Execute tech stock trades"""
        print(f"\n🔷 Running {self.strategy_name}...")
        
        # YOU provide prices from YOUR data source
        # Options: DataFrame, API call, CSV, dict, etc.
        # For this demo, we use fixed prices for simplicity
        
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150.00)
        print("   ✓ Bought 100 AAPL @ $150")
        
        self.place_trade("GOOGL", Trade.BUY, 50, Trade.MARKET, price=140.00)
        print("   ✓ Bought 50 GOOGL @ $140")
        
        self.place_trade("MSFT", Trade.BUY, 70, Trade.MARKET, price=350.00)
        print("   ✓ Bought 70 MSFT @ $350")
        
        print(f"   ✅ {self.strategy_name} completed: {len(self.trades)} trades")


class BankValueStrategy(Strategy):
    """
    Financial sector value strategy
    Buys undervalued bank stocks
    """
    
    def run(self):
        """Execute finance stock trades"""
        print(f"\n🔷 Running {self.strategy_name}...")
        
        # YOU provide prices from YOUR data source
        # Options: yfinance, API, DataFrame, CSV, etc.
        # For this demo, we use fixed prices
        
        self.place_trade("JPM", Trade.BUY, 80, Trade.MARKET, price=145.00)
        print("   ✓ Bought 80 JPM @ $145")
        
        self.place_trade("BAC", Trade.BUY, 300, Trade.MARKET, price=32.00)
        print("   ✓ Bought 300 BAC @ $32")
        
        self.place_trade("GS", Trade.BUY, 30, Trade.MARKET, price=375.00)
        print("   ✓ Bought 30 GS @ $375")
        
        print(f"   ✅ {self.strategy_name} completed: {len(self.trades)} trades")


# Instantiate strategies
tech_strategy = TechMomentumStrategy(
    strategy_id="STRAT001",
    strategy_name="FAANG Momentum",
    strategy_balance=100_000.00,
    portfolio=portfolio1
)

bank_strategy = BankValueStrategy(
    strategy_id="STRAT002",
    strategy_name="Bank Value",
    strategy_balance=100_000.00,
    portfolio=portfolio2
)

print(f"\n✅ {tech_strategy.strategy_name} created")
print(f"   Balance: ${tech_strategy.strategy_balance:,.2f}")
print(f"   Ledger: {tech_strategy.ledger}")

print(f"\n✅ {bank_strategy.strategy_name} created")
print(f"   Balance: ${bank_strategy.strategy_balance:,.2f}")
print(f"   Ledger: {bank_strategy.ledger}")

###############################################################################
# PART 5: EXECUTE TRADES
###############################################################################

print("\n" + "=" * 80)
print("PART 5: EXECUTING TRADES")
print("=" * 80)

tech_strategy.run()
bank_strategy.run()

print("\n✅ All trades executed successfully!")

###############################################################################
# PART 6: PERFORMANCE SUMMARIES
###############################################################################

print("\n" + "=" * 80)
print("PART 6: PERFORMANCE SUMMARIES")
print("=" * 80)

print("\n" + "-" * 80)
print("STRATEGY PERFORMANCE")
print("-" * 80)

tech_strategy.summary(show_positions=True)
print()
bank_strategy.summary(show_positions=True)

print("\n" + "-" * 80)
print("PORTFOLIO SUMMARIES")
print("-" * 80)

portfolio1.summary(show_children=False)
print()
portfolio2.summary(show_children=False)

print("\n" + "-" * 80)
print("FUND SUMMARIES")
print("-" * 80)

fund1.summary(show_children=False)
print()
fund2.summary(show_children=False)

print("\n" + "-" * 80)
print("ACCOUNT SUMMARY")
print("-" * 80)

account.summary(show_children=False)

###############################################################################
# PART 7: LEDGER SYSTEM DEMONSTRATION
###############################################################################

print("\n" + "=" * 80)
print("PART 7: LEDGER SYSTEM - HIERARCHICAL RECORDING")
print("=" * 80)

print("\n📒 Strategy Level Ledgers:")
print("-" * 80)
print(f"Tech Strategy:  {len(tech_strategy.ledger)} trades")
print(f"Bank Strategy:  {len(bank_strategy.ledger)} trades")

print("\n📒 Portfolio Level Ledgers:")
print("-" * 80)
print(f"Tech Portfolio:     {len(portfolio1.ledger)} trades")
print(f"Finance Portfolio:  {len(portfolio2.ledger)} trades")

print("\n📒 Fund Level Ledgers:")
print("-" * 80)
print(f"Growth Fund: {len(fund1.ledger)} trades")
print(f"Value Fund:  {len(fund2.ledger)} trades")

print("\n📒 Account Level Ledger:")
print("-" * 80)
print(f"Total Trades: {len(account.ledger)} trades")

# Verification
expected_total = len(tech_strategy.ledger) + len(bank_strategy.ledger)
actual_total = len(account.ledger)
print(f"\n🔍 Verification: Expected {expected_total}, Got {actual_total}")
print(f"✅ Hierarchical recording works correctly!" if expected_total == actual_total else "❌ Mismatch!")

###############################################################################
# PART 8: DETAILED LEDGER REPORTS
###############################################################################

print("\n" + "=" * 80)
print("PART 8: DETAILED LEDGER REPORTS")
print("=" * 80)

print("\n📊 Tech Strategy Ledger (Detailed):")
tech_strategy.ledger.summary(show_recent=3)

print("\n📊 Bank Strategy Ledger (Detailed):")
bank_strategy.ledger.summary(show_recent=3)

print("\n📊 Account-Wide Ledger (All Trades):")
account.ledger.summary(show_recent=5)

###############################################################################
# PART 9: LEDGER QUERY CAPABILITIES
###############################################################################

print("\n" + "=" * 80)
print("PART 9: ADVANCED LEDGER QUERIES")
print("=" * 80)

# Query by symbol
print("\n🔍 Query 1: All AAPL trades across entire account")
aapl_trades = account.ledger.get_trades_by_symbol("AAPL")
for trade in aapl_trades:
    print(f"   {trade}")

# Buy vs Sell breakdown
print("\n🔍 Query 2: Buy vs Sell breakdown")
ratios = account.ledger.get_buy_vs_sell_ratio()
print(f"   BUY trades:        {ratios['BUY']}")
print(f"   SELL trades:       {ratios['SELL']}")
print(f"   SELL_SHORT trades: {ratios['SELL_SHORT']}")
print(f"   BUY_TO_COVER:      {ratios['BUY_TO_COVER']}")
print(f"   Total Long trades: {ratios['TOTAL_LONG']}")
print(f"   Total Short trades: {ratios['TOTAL_SHORT']}")

# Total volume
print(f"\n🔍 Query 3: Total trading volume")
print(f"   ${account.ledger.get_total_volume():,.2f}")

# Symbol-specific volume
print(f"\n🔍 Query 4: AAPL-specific volume")
print(f"   ${account.ledger.get_total_volume('AAPL'):,.2f}")

# Unique symbols
print(f"\n🔍 Query 5: All symbols traded")
print(f"   {sorted(account.ledger.get_symbols_traded())}")

# Filled trades
print(f"\n🔍 Query 6: Filled vs Total trades")
print(f"   Filled: {account.ledger.get_filled_trade_count()}")
print(f"   Total:  {account.ledger.get_trade_count()}")

# Export data
print(f"\n🔍 Query 7: Export ledger data")
ledger_data = tech_strategy.ledger.export_to_dict()
print(f"   Owner: {ledger_data['owner_name']}")
print(f"   Type: {ledger_data['owner_type']}")
print(f"   Total Trades: {ledger_data['total_trades']}")
print(f"   Filled Trades: {ledger_data['filled_trades']}")
print(f"   Symbols: {ledger_data['symbols_traded']}")
print(f"   Total Volume: ${ledger_data['total_volume']:,.2f}")

###############################################################################
# PART 10: STRATEGY HELPER METHODS
###############################################################################

print("\n" + "=" * 80)
print("PART 10: STRATEGY CAPABILITIES & HELPER METHODS")
print("=" * 80)

print(f"\n🎯 Tech Strategy Capabilities:")
print(f"   Max Position %: {tech_strategy.get_max_position_pct()}%")
print(f"   Max Position $: ${tech_strategy.get_max_position_value():,.2f}")
print(f"   Can Short: {tech_strategy.can_short()}")
print(f"   Cash Available: ${tech_strategy.get_cash_balance():,.2f}")
print(f"   Allowed Trade Types: {tech_strategy.get_allowed_trade_types()}")

print(f"\n🎯 Bank Strategy Capabilities:")
print(f"   Max Position %: {bank_strategy.get_max_position_pct()}%")
print(f"   Max Position $: ${bank_strategy.get_max_position_value():,.2f}")
print(f"   Can Short: {bank_strategy.can_short()}")
print(f"   Cash Available: ${bank_strategy.get_cash_balance():,.2f}")
print(f"   Allowed Trade Types: {bank_strategy.get_allowed_trade_types()}")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("COMPREHENSIVE EXAMPLE COMPLETE")
print("=" * 80)

print(f"""
Summary:
- Account:    {account.account_name}
- Funds:      {len(account.funds)}
- Portfolios: {sum(len(f.portfolios) for f in account.funds.values())}
- Strategies: {sum(len(p.strategies) for f in account.funds.values() for p in f.portfolios.values())}
- Trades:     {len(account.ledger)}
- Volume:     ${account.ledger.get_total_volume():,.2f}
- Symbols:    {len(account.ledger.get_symbols_traded())}

✅ All features demonstrated successfully!
""")

print("=" * 80)

