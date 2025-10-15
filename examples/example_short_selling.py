"""
###############################################################################
# Example: Short Selling - SELL_SHORT and BUY_TO_COVER
###############################################################################
# This example demonstrates:
# 1. Opening short positions (SELL_SHORT)
# 2. Covering short positions (BUY_TO_COVER)
# 3. Profit from price declines
# 4. Risk of short squeezes
# 5. Short selling rules and compliance
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Strategy, Trade
import time

print("=" * 80)
print("EXAMPLE: Short Selling - SELL_SHORT → BUY_TO_COVER")
print("=" * 80)

###############################################################################
# Setup with Short Selling Enabled
###############################################################################

print("\n📊 Setup: Enabling Short Selling")
print("-" * 80)

account = TradeAccount("ACC001", "Trading Account")
fund = account.create_fund("FUND001", "Long/Short Fund", 1_000_000)

# Enable short selling at fund level
fund.trade_rules.allow_short_selling = True
fund.trade_rules.allowed_directions = {
    Trade.BUY,
    Trade.SELL,
    Trade.SELL_SHORT,
    Trade.BUY_TO_COVER
}

portfolio = fund.create_portfolio("PORT001", "Long/Short Portfolio", 500_000)

print(f"✅ Fund allows short selling: {fund.trade_rules.allow_short_selling}")
print(f"✅ Allowed directions: {fund.trade_rules.allowed_directions}")

###############################################################################
# PART 1: Profitable Short Trade
###############################################################################

print("\n📊 Part 1: Profitable Short Trade (Price Declines)")
print("-" * 80)

class ProfitableShortStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name}...")
        
        # SELL SHORT - Open short position (betting price will drop)
        short_entry_price = 250.00
        trade1 = self.place_trade(
            symbol="TSLA",
            direction=Trade.SELL_SHORT,
            quantity=100,
            trade_type=Trade.MARKET,
            price=short_entry_price
        )
        print(f"   1. SELL_SHORT: Sold 100 TSLA @ ${short_entry_price:.2f}")
        print(f"      Position: Short 100 shares")
        print(f"      Betting: Price will decline")
        
        time.sleep(0.01)
        
        # Price drops - profit opportunity!
        cover_price = 230.00  # Price dropped $20
        
        # BUY_TO_COVER - Close short position
        trade2 = self.place_trade(
            symbol="TSLA",
            direction=Trade.BUY_TO_COVER,
            quantity=100,
            trade_type=Trade.MARKET,
            price=cover_price
        )
        print(f"\n   2. BUY_TO_COVER: Bought back 100 TSLA @ ${cover_price:.2f}")
        print(f"      Profit: ${(short_entry_price - cover_price) * 100:,.2f}")
        print(f"      Position: Closed")
        
        # Show position P&L
        position = self.get_position("TSLA")
        print(f"\n   📊 Position Summary:")
        print(f"      Realized P&L: ${position.realized_pnl:,.2f}")
        print(f"      Status: {position.is_closed}")

profitable_short = ProfitableShortStrategy("STRAT001", "Profitable Short", 100_000, portfolio)
profitable_short.run()

###############################################################################
# PART 2: Losing Short Trade (Short Squeeze)
###############################################################################

print("\n📊 Part 2: Losing Short Trade (Price Rises - Short Squeeze)")
print("-" * 80)

class LosingShortStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name}...")
        
        # SELL SHORT at $140
        short_entry = 140.00
        trade1 = self.place_trade(
            symbol="GOOGL",
            direction=Trade.SELL_SHORT,
            quantity=50,
            trade_type=Trade.MARKET,
            price=short_entry
        )
        print(f"   1. SELL_SHORT: Sold 50 GOOGL @ ${short_entry:.2f}")
        print(f"      Position: Short 50 shares")
        
        time.sleep(0.01)
        
        # Price RISES - losses mount! (short squeeze)
        cover_price = 155.00  # Price rose $15
        
        # BUY_TO_COVER at higher price - realize loss
        trade2 = self.place_trade(
            symbol="GOOGL",
            direction=Trade.BUY_TO_COVER,
            quantity=50,
            trade_type=Trade.MARKET,
            price=cover_price
        )
        print(f"\n   2. BUY_TO_COVER: Bought back 50 GOOGL @ ${cover_price:.2f}")
        print(f"      Loss: ${(short_entry - cover_price) * 50:,.2f}")
        print(f"      Reason: Price increased (short squeeze)")
        
        position = self.get_position("GOOGL")
        print(f"\n   📊 Position Summary:")
        print(f"      Realized P&L: ${position.realized_pnl:,.2f}")
        print(f"      Status: Closed")

losing_short = LosingShortStrategy("STRAT002", "Losing Short", 100_000, portfolio)
losing_short.run()

###############################################################################
# PART 3: Multiple Short Positions
###############################################################################

print("\n📊 Part 3: Managing Multiple Short Positions")
print("-" * 80)

class MultiShortStrategy(Strategy):
    def run(self):
        print(f"\n🔷 {self.strategy_name}...")
        
        # Short multiple stocks
        shorts = [
            ('AAPL', 150.00, 50),
            ('MSFT', 350.00, 30),
            ('NVDA', 500.00, 20)
        ]
        
        print("   Opening short positions:")
        for symbol, price, quantity in shorts:
            self.place_trade(
                symbol=symbol,
                direction=Trade.SELL_SHORT,
                quantity=quantity,
                trade_type=Trade.MARKET,
                price=price
            )
            print(f"     - SHORT {quantity} {symbol} @ ${price:.2f}")
            time.sleep(0.01)
        
        print(f"\n   Total short positions: {len(self.get_open_positions())}")
        
        # Show all positions
        print(f"\n   Current Positions:")
        for symbol, position in self.get_open_positions().items():
            print(f"     {symbol}: {position}")

multi_short = MultiShortStrategy("STRAT003", "Multi Short", 150_000, portfolio)
multi_short.run()

###############################################################################
# PART 4: Long vs Short Comparison
###############################################################################

print("\n📊 Part 4: Long vs Short Position Comparison")
print("-" * 80)

print(f"\n{'Position Type':<15} {'Entry':<20} {'Exit':<20} {'Profit When':<25}")
print("-" * 80)
print(f"{'LONG':<15} {'BUY shares':<20} {'SELL shares':<20} {'Price INCREASES':<25}")
print(f"{'SHORT':<15} {'SELL_SHORT shares':<20} {'BUY_TO_COVER':<20} {'Price DECREASES':<25}")

print(f"\nExample:")
print(f"  LONG:  BUY @ $150 → SELL @ $165 = +$15/share profit")
print(f"  SHORT: SELL_SHORT @ $150 → BUY_TO_COVER @ $135 = +$15/share profit")

###############################################################################
# PART 5: Short Selling Risks
###############################################################################

print("\n📊 Part 5: Short Selling Risks & Rules")
print("-" * 80)

print("""
⚠️  SHORT SELLING RISKS:

1. Unlimited Loss Potential
   - Long positions: Max loss = 100% (price → $0)
   - Short positions: Unlimited loss (price can rise infinitely)

2. Short Squeeze Risk
   - Rapid price increases force shorts to cover
   - Can cause cascading losses

3. Margin Requirements
   - Requires margin account
   - Subject to margin calls

4. Borrowing Costs
   - Must borrow shares to short
   - Pay interest/fees on borrowed shares

5. Forced Buy-Ins
   - Lender can recall shares
   - Must cover position immediately

✅ COMPLIANCE:
   - Must enable: fund.trade_rules.allow_short_selling = True
   - Must allow: Trade.SELL_SHORT in allowed_directions
   - Typically requires: fund.trade_rules.allow_margin = True
""")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Short Selling Example")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Opening Short Positions
   - Trade.SELL_SHORT to open short
   - Bet that price will decline
   - Receive cash from selling borrowed shares

2. ✅ Closing Short Positions  
   - Trade.BUY_TO_COVER to close short
   - Buy back shares to return to lender
   - Realize P&L (profit if price dropped, loss if price rose)

3. ✅ Profitable vs. Losing Shorts
   - Profit when price declines (sell high, buy low)
   - Loss when price rises (sell low, buy high)
   - Position tracks realized P&L

4. ✅ Multiple Short Positions
   - Can short multiple symbols simultaneously
   - Each tracked as separate position
   - Aggregate exposure monitoring

5. ✅ Short Selling Rules
   - Must enable: allow_short_selling = True
   - Include SELL_SHORT and BUY_TO_COVER in allowed_directions
   - Typically requires margin account

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow:
  1. SELL_SHORT @ $150 (open short, receive $150/share)
  2. Wait for price to drop
  3. BUY_TO_COVER @ $135 (close short, pay $135/share)
  4. Profit: $15/share

Risks:
  - Unlimited loss potential
  - Short squeeze risk
  - Margin requirements
  - Borrowing costs

Next Steps:
  → See example_trade_types.py for all order types
  → See example_rules.py for compliance violations
  → See example_pnl_tracking.py for detailed P&L analysis
""")

print("=" * 80)





