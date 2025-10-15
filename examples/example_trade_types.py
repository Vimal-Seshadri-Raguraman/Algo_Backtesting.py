"""
###############################################################################
# Example: Trade Types - Demonstrating All 5 Trade Order Types
###############################################################################
# This example demonstrates:
# 1. MARKET orders - Execute immediately at current price
# 2. LIMIT orders - Execute at specified price or better
# 3. STOP_LOSS orders - Trigger when price hits stop level
# 4. STOP_LIMIT orders - Combination of stop and limit
# 5. TRAILING_STOP orders - Dynamic stop that follows price
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Strategy, Trade

print("=" * 80)
print("EXAMPLE: Trade Types - All 5 Order Types Demonstrated")
print("=" * 80)

###############################################################################
# Setup
###############################################################################

account = TradeAccount("ACC001", "Trading Account")
fund = account.create_fund("FUND001", "Growth Fund", 1_000_000)
portfolio = fund.create_portfolio("PORT001", "Tech Portfolio", 500_000)

# Sample market data (simulating current market prices)
market_prices = {
    'AAPL': 150.00,
    'GOOGL': 140.00,
    'MSFT': 350.00,
    'TSLA': 250.00,
    'NVDA': 500.00
}

###############################################################################
# PART 1: MARKET Orders (Trade.MARKET)
###############################################################################

print("\n📊 Part 1: MARKET Orders")
print("-" * 80)
print("Execute immediately at current market price (fastest execution)")

class MarketOrderStrategy(Strategy):
    def run(self, prices):
        print(f"\n🔷 Executing MARKET orders...")
        
        # Market order - executes immediately at current price
        trade = self.place_trade(
            symbol="AAPL",
            direction=Trade.BUY,
            quantity=100,
            trade_type=Trade.MARKET,
            price=prices['AAPL']  # Current market price
        )
        
        print(f"   ✅ MARKET Order: BUY 100 AAPL @ ${prices['AAPL']:.2f}")
        print(f"      Trade ID: {trade.trade_id}")
        print(f"      Status: {trade.status}")
        print(f"      Filled: {trade.filled_quantity} shares @ ${trade.avg_fill_price:.2f}")

market_strat = MarketOrderStrategy("STRAT001", "Market Orders", 100_000, portfolio)
market_strat.run(market_prices)

###############################################################################
# PART 2: LIMIT Orders (Trade.LIMIT)
###############################################################################

print("\n📊 Part 2: LIMIT Orders")
print("-" * 80)
print("Execute only at specified price or better (price protection)")

class LimitOrderStrategy(Strategy):
    def run(self, prices):
        print(f"\n🔷 Executing LIMIT orders...")
        
        current_price = prices['GOOGL']
        limit_price = 138.00  # Want to buy cheaper than current price
        
        # Limit order - only executes at limit price or better
        trade = self.place_trade(
            symbol="GOOGL",
            direction=Trade.BUY,
            quantity=50,
            trade_type=Trade.LIMIT,
            price=limit_price  # Will only buy at $138 or less
        )
        
        print(f"   ✅ LIMIT Order: BUY 50 GOOGL")
        print(f"      Current Market Price: ${current_price:.2f}")
        print(f"      Limit Price: ${limit_price:.2f}")
        print(f"      Status: {trade.status}")
        print(f"      Note: In real system, would wait for price to reach limit")

limit_strat = LimitOrderStrategy("STRAT002", "Limit Orders", 100_000, portfolio)
limit_strat.run(market_prices)

###############################################################################
# PART 3: STOP_LOSS Orders (Trade.STOP_LOSS)
###############################################################################

print("\n📊 Part 3: STOP_LOSS Orders")
print("-" * 80)
print("Trigger sell when price drops to stop level (loss protection)")

class StopLossStrategy(Strategy):
    def run(self, prices):
        print(f"\n🔷 Executing STOP_LOSS orders...")
        
        # First, buy the stock
        entry_price = prices['MSFT']
        self.place_trade("MSFT", Trade.BUY, 75, Trade.MARKET, price=entry_price)
        print(f"   1. Opened position: BUY 75 MSFT @ ${entry_price:.2f}")
        
        # Then place stop loss to protect against losses
        stop_price = entry_price * 0.95  # 5% below entry
        
        trade = self.place_trade(
            symbol="MSFT",
            direction=Trade.SELL,
            quantity=75,
            trade_type=Trade.STOP_LOSS,
            price=entry_price,  # Current price
            stop_price=stop_price  # Triggers at this price
        )
        
        print(f"   2. STOP_LOSS Order placed: SELL 75 MSFT")
        print(f"      Entry Price: ${entry_price:.2f}")
        print(f"      Stop Price: ${stop_price:.2f} (5% below entry)")
        print(f"      Protection: Will auto-sell if price drops below ${stop_price:.2f}")
        print(f"      Status: {trade.status}")

stoploss_strat = StopLossStrategy("STRAT003", "Stop Loss Orders", 100_000, portfolio)
stoploss_strat.run(market_prices)

###############################################################################
# PART 4: STOP_LIMIT Orders (Trade.STOP_LIMIT)
###############################################################################

print("\n📊 Part 4: STOP_LIMIT Orders")
print("-" * 80)
print("Trigger at stop price, then execute as limit order (price + trigger protection)")

class StopLimitStrategy(Strategy):
    def run(self, prices):
        print(f"\n🔷 Executing STOP_LIMIT orders...")
        
        current_price = prices['TSLA']
        stop_trigger = 255.00  # Trigger when price rises to this
        limit_price = 260.00   # But don't pay more than this
        
        trade = self.place_trade(
            symbol="TSLA",
            direction=Trade.BUY,
            quantity=40,
            trade_type=Trade.STOP_LIMIT,
            price=limit_price,      # Maximum price willing to pay
            stop_price=stop_trigger  # Triggers when price hits this
        )
        
        print(f"   ✅ STOP_LIMIT Order: BUY 40 TSLA")
        print(f"      Current Price: ${current_price:.2f}")
        print(f"      Stop Trigger: ${stop_trigger:.2f} (activates order)")
        print(f"      Limit Price: ${limit_price:.2f} (max price to pay)")
        print(f"      Logic: If price rises to ${stop_trigger:.2f}, buy at ${limit_price:.2f} or better")
        print(f"      Status: {trade.status}")

stoplimit_strat = StopLimitStrategy("STRAT004", "Stop Limit Orders", 100_000, portfolio)
stoplimit_strat.run(market_prices)

###############################################################################
# PART 5: TRAILING_STOP Orders (Trade.TRAILING_STOP)
###############################################################################

print("\n📊 Part 5: TRAILING_STOP Orders")
print("-" * 80)
print("Stop price that moves with market price (dynamic protection)")

class TrailingStopStrategy(Strategy):
    def run(self, prices):
        print(f"\n🔷 Executing TRAILING_STOP orders...")
        
        # First, buy the stock
        entry_price = prices['NVDA']
        self.place_trade("NVDA", Trade.BUY, 20, Trade.MARKET, price=entry_price)
        print(f"   1. Opened position: BUY 20 NVDA @ ${entry_price:.2f}")
        
        # Trailing stop - follows price up, protects gains
        trailing_amount = 25.00  # $25 trailing distance
        
        trade = self.place_trade(
            symbol="NVDA",
            direction=Trade.SELL,
            quantity=20,
            trade_type=Trade.TRAILING_STOP,
            price=entry_price,
            stop_price=entry_price - trailing_amount
        )
        
        print(f"   2. TRAILING_STOP Order placed: SELL 20 NVDA")
        print(f"      Entry Price: ${entry_price:.2f}")
        print(f"      Trailing Amount: ${trailing_amount:.2f}")
        print(f"      Initial Stop: ${entry_price - trailing_amount:.2f}")
        print(f"      Logic: If price rises to $550, stop moves to $525")
        print(f"              If price then drops to $525, auto-sell")
        print(f"      Status: {trade.status}")

trailing_strat = TrailingStopStrategy("STRAT005", "Trailing Stop Orders", 100_000, portfolio)
trailing_strat.run(market_prices)

###############################################################################
# PART 6: Comparing All Trade Types
###############################################################################

print("\n📊 Part 6: Trade Type Comparison")
print("-" * 80)

print(f"\n{'Trade Type':<20} {'Use Case':<35} {'Execution':<30}")
print("-" * 85)
print(f"{'MARKET':<20} {'Immediate execution':<35} {'At current price':<30}")
print(f"{'LIMIT':<20} {'Price protection':<35} {'At limit price or better':<30}")
print(f"{'STOP_LOSS':<20} {'Loss protection':<35} {'Triggers at stop price':<30}")
print(f"{'STOP_LIMIT':<20} {'Trigger + price control':<35} {'Trigger then limit order':<30}")
print(f"{'TRAILING_STOP':<20} {'Dynamic stop (lock gains)':<35} {'Follows price, protects gains':<30}")

###############################################################################
# PART 7: Trade Summary
###############################################################################

print("\n📊 Part 7: All Trades Executed")
print("-" * 80)

all_strategies = [market_strat, limit_strat, stoploss_strat, stoplimit_strat, trailing_strat]
total_trades = sum(len(s.trades) for s in all_strategies)

print(f"\nTotal Trades Executed: {total_trades}")
print(f"\nBy Trade Type:")
for strat in all_strategies:
    for trade in strat.trades:
        print(f"  {trade.trade_type:<15} {trade.symbol:<6} {trade.direction:<12} {trade.quantity:>4} @ ${trade.avg_fill_price:.2f}")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Trade Types Example")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ MARKET Orders
   - Execute immediately at current market price
   - Fastest execution, no price control
   - Use when: Need immediate fill

2. ✅ LIMIT Orders
   - Execute only at specified price or better
   - Price protection, may not fill immediately
   - Use when: Want to control entry/exit price

3. ✅ STOP_LOSS Orders
   - Trigger when price hits stop level
   - Protects against losses
   - Use when: Want automatic loss protection

4. ✅ STOP_LIMIT Orders
   - Combines stop trigger with limit price
   - More control but may not fill
   - Use when: Want trigger + price control

5. ✅ TRAILING_STOP Orders
   - Stop price moves with market price
   - Locks in gains while allowing upside
   - Use when: Want to protect profits dynamically

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All 5 Trade Types:
  MARKET       - Immediate execution
  LIMIT        - Price-controlled execution  
  STOP_LOSS    - Loss protection trigger
  STOP_LIMIT   - Trigger + limit combination
  TRAILING_STOP - Dynamic stop following price

Usage:
  strategy.place_trade(symbol, direction, quantity, trade_type, price, stop_price)
  
  - price: Required (limit price or current price)
  - stop_price: Required for STOP orders (trigger price)

Next Steps:
  → See example_short_selling.py for short positions
  → See example_rules.py for compliance and validation
  → See example_pnl_tracking.py for P&L with multiple trades
""")

print("=" * 80)





