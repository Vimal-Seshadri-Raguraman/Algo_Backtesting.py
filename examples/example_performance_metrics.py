"""
###############################################################################
# Performance Metrics Example - Demonstrates performance analysis at all levels
###############################################################################
# This demonstrates:
# 1. Running strategies with trades
# 2. Calculating performance metrics at Strategy level
# 3. Calculating performance metrics at Portfolio level
# 4. Calculating performance metrics at Fund level
# 5. Calculating performance metrics at Account level
# 6. Comparing performance across hierarchy
###############################################################################
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""

from core import TradeAccount, Strategy, Trade
# Performance metrics moved to tools package
# (automatically imported by strategy.performance_metrics())

###############################################################################
# PART 1: SETUP HIERARCHY AND RUN TRADES
###############################################################################

print("=" * 80)
print("PART 1: CREATING ACCOUNT HIERARCHY AND EXECUTING TRADES")
print("=" * 80)

# Create account
account = TradeAccount(
    account_id="ACC001",
    account_name="Multi-Strategy Trading Account",
    
)

# Create fund
fund = account.create_fund(
    fund_id="FUND001",
    fund_name="Growth Fund",
    fund_balance=1_000_000.00
)

# Create portfolio
portfolio = fund.create_portfolio(
    portfolio_id="PORT001",
    portfolio_name="Tech Portfolio",
    portfolio_balance=500_000.00
)

print(f"\n✅ Created hierarchy: Account → Fund → Portfolio")
print(f"   Fund Balance: ${fund.fund_balance:,.2f}")
print(f"   Portfolio Balance: ${portfolio.portfolio_balance:,.2f}")

###############################################################################
# PART 2: CREATE AND RUN STRATEGIES
###############################################################################

print("\n" + "=" * 80)
print("PART 2: CREATING STRATEGIES AND EXECUTING TRADES")
print("=" * 80)


class TechMomentumStrategy(Strategy):
    """Tech stock momentum strategy"""
    
    def run(self):
        """Execute tech stock trades"""
        print(f"\n🔷 Running {self.strategy_name}...")
        
        # Execute trades (simulate profitable strategy)
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150.00)
        print("   ✓ Bought 100 AAPL @ $150")
        
        self.place_trade("GOOGL", Trade.BUY, 50, Trade.MARKET, price=140.00)
        print("   ✓ Bought 50 GOOGL @ $140")
        
        self.place_trade("MSFT", Trade.BUY, 70, Trade.MARKET, price=350.00)
        print("   ✓ Bought 70 MSFT @ $350")
        
        print(f"   ✅ Completed: {len(self.trades)} trades")


class TechValueStrategy(Strategy):
    """Tech value strategy"""
    
    def run(self):
        """Execute value trades"""
        print(f"\n🔷 Running {self.strategy_name}...")
        
        self.place_trade("NVDA", Trade.BUY, 40, Trade.MARKET, price=500.00)
        print("   ✓ Bought 40 NVDA @ $500")
        
        self.place_trade("AMD", Trade.BUY, 150, Trade.MARKET, price=100.00)
        print("   ✓ Bought 150 AMD @ $100")
        
        print(f"   ✅ Completed: {len(self.trades)} trades")


# Create strategies
momentum_strat = TechMomentumStrategy(
    strategy_id="STRAT001",
    strategy_name="Tech Momentum",
    strategy_balance=100_000.00,
    portfolio=portfolio
)

value_strat = TechValueStrategy(
    strategy_id="STRAT002",
    strategy_name="Tech Value",
    strategy_balance=150_000.00,
    portfolio=portfolio
)

# Run strategies
momentum_strat.run()
value_strat.run()

print("\n✅ All trades executed successfully!")

###############################################################################
# PART 3: PERFORMANCE METRICS AT STRATEGY LEVEL
###############################################################################

print("\n" + "=" * 80)
print("PART 3: STRATEGY-LEVEL PERFORMANCE METRICS")
print("=" * 80)

# Simulate price changes (profits!)
current_prices = {
    "AAPL": 165.00,   # +10% gain
    "GOOGL": 154.00,  # +10% gain
    "MSFT": 385.00,   # +10% gain
    "NVDA": 550.00,   # +10% gain
    "AMD": 110.00     # +10% gain
}

print("\n📊 Tech Momentum Strategy Performance:")
print("-" * 80)
momentum_strat.performance_metrics(current_prices=current_prices)

print("\n📊 Tech Value Strategy Performance:")
print("-" * 80)
value_strat.performance_metrics(current_prices=current_prices)

###############################################################################
# PART 4: PERFORMANCE METRICS AT PORTFOLIO LEVEL
###############################################################################

print("\n" + "=" * 80)
print("PART 4: PORTFOLIO-LEVEL PERFORMANCE METRICS")
print("=" * 80)

print("\n📊 Tech Portfolio Performance (Aggregated):")
print("-" * 80)
portfolio.performance_metrics(current_prices=current_prices)

###############################################################################
# PART 5: PERFORMANCE METRICS AT FUND LEVEL
###############################################################################

print("\n" + "=" * 80)
print("PART 5: FUND-LEVEL PERFORMANCE METRICS")
print("=" * 80)

print("\n📊 Growth Fund Performance (Aggregated):")
print("-" * 80)
fund.performance_metrics(current_prices=current_prices)

###############################################################################
# PART 6: PERFORMANCE METRICS AT ACCOUNT LEVEL
###############################################################################

print("\n" + "=" * 80)
print("PART 6: ACCOUNT-LEVEL PERFORMANCE METRICS")
print("=" * 80)

print("\n📊 Account Performance (Aggregated):")
print("-" * 80)
account.performance_metrics(current_prices=current_prices)

###############################################################################
# PART 7: COMPARING METRICS ACROSS STRATEGIES
###############################################################################

print("\n" + "=" * 80)
print("PART 7: COMPARING STRATEGY PERFORMANCE")
print("=" * 80)

# Get metrics objects for comparison
momentum_metrics = momentum_strat.performance_metrics(current_prices=current_prices, show_summary=False)
value_metrics = value_strat.performance_metrics(current_prices=current_prices, show_summary=False)

print("\n📈 Strategy Comparison:")
print("-" * 80)
print(f"{'Metric':<25} {'Tech Momentum':<20} {'Tech Value':<20}")
print("-" * 80)
print(f"{'Total Return':<25} ${momentum_metrics.total_return():<19,.2f} ${value_metrics.total_return():<19,.2f}")
print(f"{'Return %':<25} {momentum_metrics.total_return_pct():<19.2f}% {value_metrics.total_return_pct():<19.2f}%")
print(f"{'Sharpe Ratio':<25} {momentum_metrics.sharpe_ratio():<19.2f} {value_metrics.sharpe_ratio():<19.2f}")
print(f"{'Max Drawdown':<25} {momentum_metrics.max_drawdown():<19.2f}% {value_metrics.max_drawdown():<19.2f}%")
print(f"{'Total Trades':<25} {momentum_metrics.total_trades():<19} {value_metrics.total_trades():<19}")
print(f"{'Trade Volume':<25} ${momentum_metrics.total_volume():<18,.2f} ${value_metrics.total_volume():<18,.2f}")
print("-" * 80)

# Determine winner
if momentum_metrics.total_return() > value_metrics.total_return():
    print(f"\n🏆 Winner: Tech Momentum (Higher absolute return)")
elif value_metrics.total_return() > momentum_metrics.total_return():
    print(f"\n🏆 Winner: Tech Value (Higher absolute return)")
else:
    print(f"\n🤝 Tie: Both strategies performed equally")

###############################################################################
# PART 8: EXPORTING METRICS
###############################################################################

print("\n" + "=" * 80)
print("PART 8: EXPORTING METRICS TO DICTIONARY")
print("=" * 80)

# Export account metrics
account_metrics = account.performance_metrics(current_prices=current_prices, show_summary=False)
metrics_dict = account_metrics.to_dict()

print("\n📤 Exported Account Metrics:")
print("-" * 80)
print(f"  Owner: {metrics_dict['owner_name']}")
print(f"  Type: {metrics_dict['owner_type']}")
print(f"  Initial Balance: ${metrics_dict['initial_balance']:,.2f}")
print(f"  Current Balance: ${metrics_dict['current_balance']:,.2f}")
print(f"  Total Return: ${metrics_dict['total_return']:,.2f} ({metrics_dict['total_return_pct']:.2f}%)")
print(f"  Sharpe Ratio: {metrics_dict['sharpe_ratio']:.2f}")
print(f"  Sortino Ratio: {metrics_dict['sortino_ratio']:.2f}")
print(f"  Max Drawdown: {metrics_dict['max_drawdown']:.2f}%")
print(f"  Total Trades: {metrics_dict['total_trades']}")
print("-" * 80)

print("\n💡 These metrics can be saved to JSON/CSV for further analysis!")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("PERFORMANCE METRICS EXAMPLE COMPLETE")
print("=" * 80)

print(f"""
Summary:
- ✅ Performance metrics available at ALL 4 levels
- ✅ Strategy-level: Individual strategy performance
- ✅ Portfolio-level: Aggregated strategy performance
- ✅ Fund-level: Aggregated portfolio performance
- ✅ Account-level: Complete account performance
- ✅ Comparison tools: Compare strategies side-by-side
- ✅ Export capability: Convert to dict/JSON

Key Metrics Calculated:
- Total Return ($ and %)
- Annualized Return (CAGR)
- Sharpe Ratio (risk-adjusted return)
- Sortino Ratio (downside risk-adjusted)
- Calmar Ratio (return vs max drawdown)
- Max Drawdown
- Volatility
- Win Rate
- Trade Statistics

✅ All performance metrics features demonstrated successfully!
""")

print("=" * 80)


