"""
###############################################################################
# Example: Trading Rules - Compliance & Validation
###############################################################################
# This example demonstrates:
# 1. Setting up trading rules at fund and portfolio levels
# 2. Position size limits
# 3. Symbol restrictions (whitelist/blacklist)
# 4. Trade type restrictions
# 5. Handling compliance violations
# 6. Catching and handling errors
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Strategy, Trade, TradeComplianceError, InsufficientFundsError

print("=" * 80)
print("EXAMPLE: Trading Rules - Compliance & Validation")
print("=" * 80)

###############################################################################
# PART 1: Setting Up Rules
###############################################################################

print("\n📊 Part 1: Configuring Trading Rules")
print("-" * 80)

account = TradeAccount("ACC001", "Regulated Account")
fund = account.create_fund("FUND001", "Compliance Fund", 1_000_000)
portfolio = fund.create_portfolio("PORT001", "Regulated Portfolio", 500_000)

# Configure comprehensive fund rules
print("\nFund-Level Rules (Compliance):")
fund.trade_rules.max_position_size_pct = 20.0  # Max 20% of portfolio
fund.trade_rules.max_single_trade_pct = 10.0   # Max 10% per trade
fund.trade_rules.allow_short_selling = False   # Long-only fund
fund.trade_rules.allow_margin = False
fund.trade_rules.allowed_trade_types = {Trade.MARKET, Trade.LIMIT}  # Only these types
fund.trade_rules.allowed_symbols = {"AAPL", "GOOGL", "MSFT", "NVDA"}  # Whitelist
fund.trade_rules.restricted_symbols = {"GME", "AMC"}  # Blacklist

print(f"  Max Position Size: {fund.trade_rules.max_position_size_pct}%")
print(f"  Max Single Trade: {fund.trade_rules.max_single_trade_pct}%")
print(f"  Short Selling: {fund.trade_rules.allow_short_selling}")
print(f"  Allowed Symbols: {fund.trade_rules.allowed_symbols}")
print(f"  Restricted Symbols: {fund.trade_rules.restricted_symbols}")

# Portfolio rules (more restrictive)
print("\nPortfolio-Level Rules (Risk Management - Stricter):")
portfolio.trade_rules.max_position_size_pct = 15.0  # More restrictive than fund
portfolio.trade_rules.max_single_trade_pct = 5.0    # More restrictive than fund

print(f"  Max Position Size: {portfolio.trade_rules.max_position_size_pct}%")
print(f"  Max Single Trade: {portfolio.trade_rules.max_single_trade_pct}%")

###############################################################################
# PART 2: Valid Trades (Pass Compliance)
###############################################################################

print("\n📊 Part 2: Valid Trades (Within Limits)")
print("-" * 80)

class CompliantStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name}...")
        
        # Small trade - within limits
        trade1 = self.place_trade("AAPL", Trade.BUY, 50, Trade.MARKET, price=150.00)
        print(f"   ✅ PASS: BUY 50 AAPL @ $150 (${50*150:,.0f} = 1.5% of portfolio)")
        
        # Another valid trade
        trade2 = self.place_trade("GOOGL", Trade.BUY, 30, Trade.MARKET, price=140.00)
        print(f"   ✅ PASS: BUY 30 GOOGL @ $140 (${30*140:,.0f} = 0.84% of portfolio)")

compliant = CompliantStrategy("STRAT001", "Compliant", 100_000, portfolio)
compliant.run()

###############################################################################
# PART 3: Position Size Violation
###############################################################################

print("\n📊 Part 3: Position Size Limit Violation")
print("-" * 80)

class OversizeStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name} - Attempting oversized trade...")
        
        try:
            # Try to buy too much (would be >15% of portfolio)
            trade = self.place_trade(
                symbol="MSFT",
                direction=Trade.BUY,
                quantity=500,  # 500 * $350 = $175,000 (35% of $500k portfolio!)
                trade_type=Trade.MARKET,
                price=350.00
            )
            print(f"   ✅ Trade executed (shouldn't happen!)")
        except TradeComplianceError as e:
            print(f"   ❌ REJECTED: {e}")
            print(f"   Reason: Trade would be $175,000 (35% of portfolio)")
            print(f"   Limit: Max 15% per position = $75,000")

oversize = OversizeStrategy("STRAT002", "Oversize Test", 100_000, portfolio)
oversize.run()

###############################################################################
# PART 4: Restricted Symbol Violation
###############################################################################

print("\n📊 Part 4: Restricted Symbol Violation")
print("-" * 80)

class RestrictedSymbolStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name} - Attempting restricted symbol...")
        
        try:
            # Try to trade a blacklisted symbol
            trade = self.place_trade(
                symbol="GME",  # In restricted_symbols list
                direction=Trade.BUY,
                quantity=100,
                trade_type=Trade.MARKET,
                price=25.00
            )
            print(f"   ✅ Trade executed (shouldn't happen!)")
        except TradeComplianceError as e:
            print(f"   ❌ REJECTED: {e}")
            print(f"   Reason: GME is in restricted symbols list")
            print(f"   Restricted: {fund.trade_rules.restricted_symbols}")

restricted = RestrictedSymbolStrategy("STRAT003", "Restricted Test", 100_000, portfolio)
restricted.run()

###############################################################################
# PART 5: Not in Allowed Symbols (Whitelist)
###############################################################################

print("\n📊 Part 5: Symbol Not in Whitelist Violation")
print("-" * 80)

class NonAllowedSymbolStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name} - Attempting non-whitelisted symbol...")
        
        try:
            # Try to trade symbol not in allowed list
            trade = self.place_trade(
                symbol="TSLA",  # Not in allowed_symbols
                direction=Trade.BUY,
                quantity=50,
                trade_type=Trade.MARKET,
                price=250.00
            )
            print(f"   ✅ Trade executed (shouldn't happen!)")
        except TradeComplianceError as e:
            print(f"   ❌ REJECTED: {e}")
            print(f"   Reason: TSLA not in allowed symbols")
            print(f"   Allowed: {fund.trade_rules.allowed_symbols}")

non_allowed = NonAllowedSymbolStrategy("STRAT004", "Non-Allowed Test", 100_000, portfolio)
non_allowed.run()

###############################################################################
# PART 6: Short Selling Violation
###############################################################################

print("\n📊 Part 6: Short Selling Violation (Long-Only Fund)")
print("-" * 80)

class ShortAttemptStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name} - Attempting short in long-only fund...")
        
        try:
            # Try to short in long-only fund
            trade = self.place_trade(
                symbol="AAPL",
                direction=Trade.SELL_SHORT,
                quantity=50,
                trade_type=Trade.MARKET,
                price=150.00
            )
            print(f"   ✅ Trade executed (shouldn't happen!)")
        except TradeComplianceError as e:
            print(f"   ❌ REJECTED: {e}")
            print(f"   Reason: Short selling not allowed")
            print(f"   Fund Rule: allow_short_selling = {fund.trade_rules.allow_short_selling}")

short_attempt = ShortAttemptStrategy("STRAT005", "Short Attempt", 100_000, portfolio)
short_attempt.run()

###############################################################################
# PART 7: Insufficient Funds Error
###############################################################################

print("\n📊 Part 7: Insufficient Funds Error")
print("-" * 80)

class InsufficientFundsStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name} - Attempting trade with insufficient funds...")
        print(f"   Strategy balance: ${self.strategy_balance:,.2f}")
        print(f"   Available cash: ${self.get_cash_balance():,.2f}")
        
        try:
            # Buy a small position first to reduce cash
            self.place_trade("AAPL", Trade.BUY, 500, Trade.MARKET, price=150.00)
            print(f"   1. First trade: BUY 500 AAPL @ $150 = $75,000")
            print(f"      Remaining cash: ${self.get_cash_balance():,.2f}")
            
            # Now try another trade that exceeds remaining cash
            trade = self.place_trade(
                symbol="GOOGL",
                direction=Trade.BUY,
                quantity=250,  # 250 * $140 = $35,000 (but only $25k cash left)
                trade_type=Trade.MARKET,
                price=140.00
            )
            print(f"   ✅ Trade executed (shouldn't happen!)")
        except InsufficientFundsError as e:
            print(f"   2. ❌ REJECTED (Insufficient Funds): {e}")
            print(f"      Trade would cost: $35,000")
            print(f"      Cash remaining: ~$25,000")
        except TradeComplianceError as e:
            print(f"   ❌ REJECTED (Compliance): {e}")

insufficient = InsufficientFundsStrategy("STRAT006", "Insufficient Funds Test", 100_000, portfolio)
insufficient.run()

###############################################################################
# PART 8: Successful Error Handling Pattern
###############################################################################

print("\n📊 Part 8: Proper Error Handling in Production")
print("-" * 80)

class ProductionStrategy(Strategy):
    def run(self, trade_list):
        """
        Production strategy with proper error handling
        
        Args:
            trade_list: List of (symbol, quantity, price) tuples
        """
        print(f"\n🔷 {self.strategy_name} - Production error handling...")
        
        executed = 0
        rejected = 0
        
        for symbol, quantity, price in trade_list:
            try:
                trade = self.place_trade(
                    symbol=symbol,
                    direction=Trade.BUY,
                    quantity=quantity,
                    trade_type=Trade.MARKET,
                    price=price
                )
                executed += 1
                print(f"   ✅ Executed: BUY {quantity} {symbol} @ ${price:.2f}")
                
            except TradeComplianceError as e:
                rejected += 1
                print(f"   ⚠️  Compliance: {symbol} - {str(e)[:50]}...")
                
            except InsufficientFundsError as e:
                rejected += 1
                print(f"   ⚠️  Funds: {symbol} - {str(e)[:50]}...")
                
            except Exception as e:
                rejected += 1
                print(f"   ❌ Error: {symbol} - {str(e)[:50]}...")
        
        print(f"\n   Summary: {executed} executed, {rejected} rejected")

production = ProductionStrategy("STRAT007", "Production Pattern", 100_000, portfolio)

# Mix of valid and invalid trades
trade_requests = [
    ("AAPL", 50, 150.00),    # Valid
    ("GOOGL", 30, 140.00),   # Valid
    ("TSLA", 20, 250.00),    # Invalid - not in allowed symbols
    ("GME", 100, 25.00),     # Invalid - restricted symbol
    ("NVDA", 500, 500.00),   # Invalid - insufficient funds
]

production.run(trade_requests)

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Trading Rules & Compliance")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Rule Configuration
   - Fund-level compliance rules (max position, allowed symbols)
   - Portfolio-level risk rules (more restrictive)
   - Trade type and direction restrictions

2. ✅ Position Size Limits
   - max_position_size_pct: Maximum % per symbol
   - max_single_trade_pct: Maximum % per individual trade
   - Automatically validated before execution

3. ✅ Symbol Restrictions
   - allowed_symbols: Whitelist (None = all allowed)
   - restricted_symbols: Blacklist
   - Compliance checked on every trade

4. ✅ Trading Permissions
   - allow_short_selling: Enable/disable shorting
   - allow_margin: Enable/disable margin trading
   - allow_options/futures: Future asset classes

5. ✅ Error Handling
   - TradeComplianceError: Rule violations
   - InsufficientFundsError: Not enough cash
   - Graceful handling in production code

6. ✅ Multi-Level Validation
   - Portfolio rules checked first
   - Fund rules checked second
   - Strategy executes only if both pass

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Rule Hierarchy:
  Fund Rules (Compliance Layer)
      ↓
  Portfolio Rules (Risk Layer - More Restrictive)
      ↓
  Strategy Execution (No Rules - Validated Against Parents)

Common Violations Caught:
  ❌ Position too large (exceeds max_position_size_pct)
  ❌ Trade too large (exceeds max_single_trade_pct)
  ❌ Symbol not allowed (not in allowed_symbols or in restricted_symbols)
  ❌ Direction not allowed (e.g., shorting in long-only fund)
  ❌ Trade type not allowed (e.g., options when disabled)
  ❌ Insufficient funds (not enough cash)

Next Steps:
  → See example_fund.py for more rule configurations
  → See example_portfolio.py for multi-level rules
  → See example_short_selling.py for directional restrictions
""")

print("=" * 80)


