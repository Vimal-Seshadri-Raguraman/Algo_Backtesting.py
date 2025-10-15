"""
###############################################################################
# Example: Portfolio - Portfolio Management & Strategy Allocation
###############################################################################
# This example demonstrates:
# 1. Creating portfolios
# 2. Allocating capital to strategies
# 3. Portfolio-level risk rules
# 4. Monitoring portfolio performance
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Portfolio, Strategy, Trade

print("=" * 80)
print("EXAMPLE: Portfolio - Capital Allocation & Risk Management")
print("=" * 80)

###############################################################################
# PART 1: Setup Hierarchy
###############################################################################

print("\n📊 Part 1: Setting Up Account → Fund → Portfolio")
print("-" * 80)

account = TradeAccount("ACC001", "Trading Account")
fund = account.create_fund("FUND001", "Growth Fund", 10_000_000.00)

# Create portfolio
portfolio = fund.create_portfolio(
    portfolio_id="PORT001",
    portfolio_name="Tech Growth Portfolio",
    portfolio_balance=5_000_000.00
)

print(f"✅ Created: {portfolio.portfolio_name}")
print(f"   Balance: ${portfolio.portfolio_balance:,.2f}")
print(f"   Parent Fund: {fund.fund_name}")

###############################################################################
# PART 2: Configure Portfolio-Level Risk Rules
###############################################################################

print("\n📊 Part 2: Portfolio Risk Rules (More Restrictive Than Fund)")
print("-" * 80)

# Set portfolio rules (stricter than fund rules)
portfolio.trade_rules.max_position_size_pct = 15.0  # Max 15% per position
portfolio.trade_rules.max_single_trade_pct = 5.0    # Max 5% per trade

print(f"Portfolio Rules:")
print(f"  Max Position Size: {portfolio.trade_rules.max_position_size_pct}%")
print(f"  Max Single Trade: {portfolio.trade_rules.max_single_trade_pct}%")

###############################################################################
# PART 3: Allocate Capital to Strategies
###############################################################################

print("\n📊 Part 3: Allocating Capital to Strategies")
print("-" * 80)

# Define strategy classes
class MomentumStrategy(Strategy):
    def run(self):
        pass  # Strategy implementation

class MeanReversionStrategy(Strategy):
    def run(self):
        pass

class BreakoutStrategy(Strategy):
    def run(self):
        pass

# Create strategies within portfolio
momentum = MomentumStrategy(
    strategy_id="STRAT001",
    strategy_name="Momentum",
    strategy_balance=2_000_000.00,
    portfolio=portfolio
)
print(f"✅ Allocated ${momentum.strategy_balance:,.2f} to {momentum.strategy_name}")

mean_reversion = MeanReversionStrategy(
    strategy_id="STRAT002",
    strategy_name="Mean Reversion",
    strategy_balance=1_500_000.00,
    portfolio=portfolio
)
print(f"✅ Allocated ${mean_reversion.strategy_balance:,.2f} to {mean_reversion.strategy_name}")

breakout = BreakoutStrategy(
    strategy_id="STRAT003",
    strategy_name="Breakout",
    strategy_balance=1_000_000.00,
    portfolio=portfolio
)
print(f"✅ Allocated ${breakout.strategy_balance:,.2f} to {breakout.strategy_name}")

###############################################################################
# PART 4: Portfolio Capital Status
###############################################################################

print("\n📊 Part 4: Portfolio Capital Allocation")
print("-" * 80)

print(f"Total Portfolio Capital: ${portfolio.portfolio_balance:,.2f}")
print(f"Allocated to Strategies: ${portfolio.allocated_balance:,.2f} ({portfolio.allocated_balance/portfolio.portfolio_balance*100:.1f}%)")
print(f"Unallocated Cash:        ${portfolio.cash_balance:,.2f} ({portfolio.cash_balance/portfolio.portfolio_balance*100:.1f}%)")
print(f"Number of Strategies:    {len(portfolio.strategies)}")

###############################################################################
# PART 5: Strategy Breakdown
###############################################################################

print("\n📊 Part 5: Strategy Breakdown")
print("-" * 80)

print(f"\n{'Strategy':<25} {'Balance':<20} {'% of Portfolio':<15}")
print("-" * 60)
for strategy in portfolio.strategies.values():
    pct = (strategy.strategy_balance / portfolio.portfolio_balance) * 100
    print(f"{strategy.strategy_name:<25} ${strategy.strategy_balance:<18,.2f} {pct:<14.1f}%")

###############################################################################
# PART 6: Query Strategies
###############################################################################

print("\n📊 Part 6: Querying Strategies")
print("-" * 80)

# Get specific strategy
found_strategy = portfolio.get_strategy("STRAT001")
if found_strategy:
    print(f"✅ Found: {found_strategy.strategy_name}")
    print(f"   Balance: ${found_strategy.strategy_balance:,.2f}")
    print(f"   ID: {found_strategy.strategy_id}")

###############################################################################
# PART 7: Multiple Portfolio Comparison
###############################################################################

print("\n📊 Part 7: Comparing Multiple Portfolios")
print("-" * 80)

# Create additional portfolios for comparison
portfolio2 = fund.create_portfolio(
    portfolio_id="PORT002",
    portfolio_name="Value Portfolio",
    portfolio_balance=3_000_000.00
)
portfolio2.trade_rules.max_position_size_pct = 12.0
portfolio2.trade_rules.max_single_trade_pct = 4.0

portfolio3 = fund.create_portfolio(
    portfolio_id="PORT003",
    portfolio_name="Dividend Portfolio",
    portfolio_balance=2_000_000.00
)
portfolio3.trade_rules.max_position_size_pct = 10.0
portfolio3.trade_rules.max_single_trade_pct = 3.0

print(f"\n{'Portfolio':<25} {'Balance':<20} {'Max Position':<15} {'Max Trade':<15}")
print("-" * 75)
for port in [portfolio, portfolio2, portfolio3]:
    print(f"{port.portfolio_name:<25} ${port.portfolio_balance:<18,.2f} {port.trade_rules.max_position_size_pct:<14.1f}% {port.trade_rules.max_single_trade_pct:<14.1f}%")

###############################################################################
# PART 8: Portfolio Summary
###############################################################################

print("\n📊 Part 8: Portfolio Summary")
print("-" * 80)

portfolio.summary(show_children=False)

###############################################################################
# PART 9: ADVANCED - Extending Portfolio (Framework Pattern)
###############################################################################

print("\n📊 Part 9: ADVANCED - Extending Portfolio for Custom Behavior")
print("-" * 80)

class RiskManagedPortfolio(Portfolio):
    """
    Custom Portfolio with VaR monitoring and concentration limits
    
    This demonstrates extending the base class for production use
    """
    
    def __init__(self, portfolio_id, portfolio_name, portfolio_balance, fund=None,
                 var_limit=0.05, concentration_limit=0.25):
        super().__init__(portfolio_id, portfolio_name, portfolio_balance, fund)
        self.var_limit = var_limit
        self.concentration_limit = concentration_limit
        self.risk_alerts = []
    
    def calculate_var(self, confidence=0.95):
        """Calculate Value at Risk"""
        # Simplified VaR calculation
        print(f"\n📉 Value at Risk Calculation ({confidence*100:.0f}% confidence):")
        print(f"   Portfolio Value: ${self.portfolio_balance:,.2f}")
        print(f"   VaR Limit: {self.var_limit*100:.1f}%")
        print(f"   Max Acceptable Loss: ${self.portfolio_balance * self.var_limit:,.2f}")
        return self.portfolio_balance * self.var_limit
    
    def check_concentration(self):
        """Check if any strategy exceeds concentration limit"""
        print(f"\n🎯 Concentration Risk Check:")
        print(f"   Concentration Limit: {self.concentration_limit*100:.0f}%")
        
        for strategy in self.strategies.values():
            concentration = strategy.strategy_balance / self.portfolio_balance
            status = "✅ OK" if concentration <= self.concentration_limit else "⚠️ ALERT"
            print(f"   {strategy.strategy_name}: {concentration*100:.1f}% {status}")
    
    def add_risk_alert(self, alert_type, message):
        """Add risk alert for monitoring"""
        self.risk_alerts.append({'type': alert_type, 'message': message})
        print(f"   ⚠️  ALERT: {alert_type} - {message}")

# Create extended portfolio
print("\nCreating extended RiskManagedPortfolio:")
risk_portfolio = RiskManagedPortfolio(
    portfolio_id="PORT_RISK",
    portfolio_name="Risk-Controlled Portfolio",
    portfolio_balance=10_000_000.00,
    var_limit=0.05,  # 5% VaR limit
    concentration_limit=0.30  # Max 30% per strategy
)

# Add strategies
class DummyStrategy(Strategy):
    def run(self):
        pass

strat1 = DummyStrategy("S1", "Large Cap", 3_000_000, portfolio=risk_portfolio)
strat2 = DummyStrategy("S2", "Mid Cap", 4_000_000, portfolio=risk_portfolio)
strat3 = DummyStrategy("S3", "Small Cap", 2_000_000, portfolio=risk_portfolio)

# Use custom methods
risk_portfolio.calculate_var(confidence=0.95)
risk_portfolio.check_concentration()
risk_portfolio.add_risk_alert("CONCENTRATION", "Mid Cap strategy at 40% (above 30% limit)")

print("\n✅ Extended Portfolio with custom risk management!")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Portfolio Example")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Portfolio Creation
   - Create portfolios within a fund
   - Allocate capital from fund to portfolio

2. ✅ Risk Rules
   - Set portfolio-level risk limits (max position, max trade)
   - Usually MORE restrictive than fund rules
   - Provides additional safety layer

3. ✅ Strategy Allocation
   - Create multiple strategies within portfolio
   - Allocate capital to each strategy
   - Monitor allocated vs. unallocated capital

4. ✅ Capital Management
   - Track total portfolio capital
   - Monitor strategy allocations
   - Query individual strategies

5. ✅ Portfolio Strategies
   - Different portfolios can have different risk profiles
   - Tech Growth: More aggressive (15% max position)
   - Value: Moderate (12% max position)
   - Dividend: Conservative (10% max position)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Portfolio Hierarchy:
  Fund: Growth Fund
  ├── Tech Growth Portfolio ($5M) - 15% max position
  │   ├── Momentum Strategy ($2M)
  │   ├── Mean Reversion Strategy ($1.5M)
  │   └── Breakout Strategy ($1M)
  ├── Value Portfolio ($3M) - 12% max position
  └── Dividend Portfolio ($2M) - 10% max position

Next Steps:
  → See example_strategy.py for implementing trading strategies
  → See example_trade.py for executing trades
  → See example_complete.py for full workflow
""")

print("=" * 80)


