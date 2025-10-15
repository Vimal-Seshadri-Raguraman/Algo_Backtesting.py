"""
###############################################################################
# Example: Strategy - Creating and Running Trading Strategies
###############################################################################
# This example demonstrates:
# 1. Creating custom strategy classes
# 2. Implementing strategy logic
# 3. Placing trades within strategies
# 4. Standalone vs. linked strategies
# 5. Using pandas for price data
###############################################################################
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


from core import TradeAccount, Strategy, Trade
import pandas as pd
import numpy as np

print("=" * 80)
print("EXAMPLE: Strategy - Implementing Trading Logic")
print("=" * 80)

###############################################################################
# PART 1: Create Sample Price Data with Pandas
###############################################################################

print("\n📊 Part 1: Creating Sample Market Data with Pandas")
print("-" * 80)

# Generate sample price data for demonstration
np.random.seed(42)
dates = pd.date_range('2025-01-01', periods=100, freq='D')
prices = {
    'AAPL': pd.Series(150 + np.cumsum(np.random.randn(100) * 2), index=dates),
    'GOOGL': pd.Series(140 + np.cumsum(np.random.randn(100) * 2), index=dates),
    'MSFT': pd.Series(350 + np.cumsum(np.random.randn(100) * 5), index=dates)
}

price_df = pd.DataFrame(prices)
print(f"✅ Created price data for {len(prices)} symbols over {len(dates)} days")
print(f"\nLatest Prices:")
print(price_df.tail())

###############################################################################
# PART 2: Simple Strategy Implementation
###############################################################################

print("\n📊 Part 2: Simple Buy-and-Hold Strategy")
print("-" * 80)

class BuyAndHoldStrategy(Strategy):
    """
    Simple strategy that buys and holds stocks
    """
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None):
        super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
        self.symbols_to_buy = ['AAPL', 'GOOGL', 'MSFT']
    
    def run(self, prices):
        """
        Execute trades based on price data
        
        Args:
            prices: Dict of {symbol: price}
        """
        print(f"\n🔷 Running {self.strategy_name}...")
        
        # Calculate equal allocation
        cash_per_symbol = self.strategy_balance / len(self.symbols_to_buy)
        
        for symbol in self.symbols_to_buy:
            price = prices[symbol]
            quantity = int(cash_per_symbol / price)
            
            if quantity > 0:
                trade = self.place_trade(
                    symbol=symbol,
                    direction=Trade.BUY,
                    quantity=quantity,
                    trade_type=Trade.MARKET,
                    price=price
                )
                print(f"   ✓ Bought {quantity} {symbol} @ ${price:.2f}")
        
        print(f"   ✅ Completed: {len(self.trades)} trades")

# Setup hierarchy
account = TradeAccount("ACC001", "Trading Account")
fund = account.create_fund("FUND001", "Growth Fund", 1_000_000.00)
portfolio = fund.create_portfolio("PORT001", "Tech Portfolio", 500_000.00)

# Create and run strategy
buy_hold = BuyAndHoldStrategy(
    strategy_id="STRAT001",
    strategy_name="Buy & Hold",
    strategy_balance=100_000.00,
    portfolio=portfolio
)

# Use latest prices from our pandas dataframe
latest_prices = price_df.iloc[-1].to_dict()
buy_hold.run(latest_prices)

###############################################################################
# PART 3: Moving Average Crossover Strategy
###############################################################################

print("\n📊 Part 3: Moving Average Crossover Strategy")
print("-" * 80)

class MovingAverageCrossover(Strategy):
    """
    Strategy that trades based on moving average crossovers
    """
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None,
                 short_window=10, long_window=30):
        super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
        self.short_window = short_window
        self.long_window = long_window
    
    def run(self, price_data):
        """
        Execute trades based on MA crossover
        
        Args:
            price_data: pandas DataFrame with price history
        """
        print(f"\n🔷 Running {self.strategy_name}...")
        print(f"   Parameters: Short MA={self.short_window}, Long MA={self.long_window}")
        
        for symbol in price_data.columns:
            # Calculate moving averages
            short_ma = price_data[symbol].rolling(window=self.short_window).mean()
            long_ma = price_data[symbol].rolling(window=self.long_window).mean()
            
            # Get latest values
            latest_price = price_data[symbol].iloc[-1]
            latest_short_ma = short_ma.iloc[-1]
            latest_long_ma = long_ma.iloc[-1]
            
            # Check for crossover (bullish signal)
            if latest_short_ma > latest_long_ma:
                # Calculate position size (25% of capital per symbol)
                position_value = self.strategy_balance * 0.25
                quantity = int(position_value / latest_price)
                
                if quantity > 0:
                    trade = self.place_trade(
                        symbol=symbol,
                        direction=Trade.BUY,
                        quantity=quantity,
                        trade_type=Trade.MARKET,
                        price=latest_price
                    )
                    print(f"   ✓ BUY Signal: {symbol} @ ${latest_price:.2f}")
                    print(f"      Short MA: ${latest_short_ma:.2f}, Long MA: ${latest_long_ma:.2f}")
            else:
                print(f"   ⊗ No signal for {symbol} (Short MA: ${latest_short_ma:.2f} < Long MA: ${latest_long_ma:.2f})")
        
        print(f"   ✅ Completed: {len(self.trades)} trades")

# Create MA crossover strategy
ma_strategy = MovingAverageCrossover(
    strategy_id="STRAT002",
    strategy_name="MA Crossover",
    strategy_balance=100_000.00,
    portfolio=portfolio,
    short_window=10,
    long_window=30
)

ma_strategy.run(price_df)

###############################################################################
# PART 4: Standalone Strategy (No Validation)
###############################################################################

print("\n📊 Part 4: Standalone Strategy (No Hierarchy)")
print("-" * 80)

class AggressiveStrategy(Strategy):
    """
    Aggressive strategy that runs without validation
    """
    
    def run(self, prices):
        print(f"\n🔷 Running {self.strategy_name} (Standalone Mode)...")
        
        # Can trade without any restrictions
        for symbol, price in prices.items():
            quantity = 100  # Fixed quantity
            
            self.place_trade(
                symbol=symbol,
                direction=Trade.BUY,
                quantity=quantity,
                trade_type=Trade.MARKET,
                price=price
            )
            print(f"   ✓ Bought {quantity} {symbol} @ ${price:.2f}")
        
        print(f"   ✅ Completed: {len(self.trades)} trades (no validation)")

# Create standalone strategy (no portfolio parameter)
aggressive = AggressiveStrategy(
    strategy_id="STRAT003",
    strategy_name="Aggressive",
    strategy_balance=50_000.00,
    portfolio=None  # Standalone mode
)

aggressive.run(latest_prices)

###############################################################################
# PART 5: Strategy Comparison
###############################################################################

print("\n📊 Part 5: Comparing Strategies")
print("-" * 80)

strategies = [buy_hold, ma_strategy, aggressive]

print(f"\n{'Strategy':<25} {'Mode':<15} {'Balance':<15} {'Trades':<10} {'Cash Left':<15}")
print("-" * 80)
for strat in strategies:
    mode = "Linked" if strat.portfolio else "Standalone"
    cash_left = strat.get_cash_balance()
    print(f"{strat.strategy_name:<25} {mode:<15} ${strat.strategy_balance:<13,.0f} {len(strat.trades):<10} ${cash_left:<13,.2f}")

###############################################################################
# PART 6: Strategy Helper Methods
###############################################################################

print("\n📊 Part 6: Strategy Helper Methods")
print("-" * 80)

# Demonstrate helper methods on linked strategy
print(f"\n{buy_hold.strategy_name} Capabilities:")
print(f"  Max Position %: {buy_hold.get_max_position_pct()}%")
print(f"  Max Position $: ${buy_hold.get_max_position_value():,.2f}")
print(f"  Can Short: {buy_hold.can_short()}")
print(f"  Allowed Trade Types: {len(buy_hold.get_allowed_trade_types())} types")
print(f"  Cash Balance: ${buy_hold.get_cash_balance():,.2f}")
print(f"  Open Positions: {len(buy_hold.get_open_positions())}")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Strategy Example")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Strategy Implementation
   - Subclass Strategy base class
   - Implement run() method with trading logic
   - Use self.place_trade() to execute

2. ✅ Using Pandas for Price Data
   - Create DataFrames with historical prices
   - Calculate technical indicators (moving averages)
   - Pass price data to strategy.run()

3. ✅ Strategy Types
   - Buy & Hold: Simple equal-weight allocation
   - MA Crossover: Technical indicator-based
   - Aggressive: High-frequency, no restrictions

4. ✅ Linked vs. Standalone
   - Linked: Validation against portfolio/fund rules
   - Standalone: No validation, maximum flexibility

5. ✅ Helper Methods
   - get_max_position_pct(): Query position limits
   - get_cash_balance(): Check available capital
   - get_open_positions(): View current holdings
   - can_short(): Check if shorting allowed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strategies Created:
  1. Buy & Hold (Linked) - 3 trades executed
  2. MA Crossover (Linked) - Technical indicator-based
  3. Aggressive (Standalone) - No validation

Next Steps:
  → See example_trade.py for different trade types
  → See example_position.py for position management
  → See example_performance.py for performance analysis
  → See example_complete.py for end-to-end workflow
""")

print("=" * 80)


