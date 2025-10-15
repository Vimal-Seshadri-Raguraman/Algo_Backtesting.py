"""
###############################################################################
# Example: Backtesting - Historical Strategy Testing
###############################################################################
# This example demonstrates:
# 1. Creating historical price data
# 2. Defining strategies for backtesting
# 3. Running backtests with Backtester
# 4. Analyzing backtest results
# 5. Comparing multiple strategies
# 6. Walk-forward testing concept
###############################################################################
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import Strategy, Trade
from tools import Backtester
import pandas as pd
import numpy as np

print("=" * 80)
print("EXAMPLE: Backtesting - Historical Strategy Testing")
print("=" * 80)

###############################################################################
# PART 1: Create Historical Market Data
###############################################################################

print("\n📊 Part 1: Creating Historical Market Data")
print("-" * 80)

# Generate realistic price data for backtesting
np.random.seed(42)

# 252 trading days (1 year)
dates = pd.date_range('2024-01-01', periods=252, freq='B')  # Business days

# Simulate realistic price movements
symbols = ['AAPL', 'GOOGL', 'MSFT']
prices_dict = {}

for symbol in symbols:
    # Different characteristics per symbol
    initial_prices = {'AAPL': 150, 'GOOGL': 140, 'MSFT': 350}
    volatilities = {'AAPL': 0.015, 'GOOGL': 0.020, 'MSFT': 0.012}
    
    # Simulate with trend and volatility
    returns = np.random.normal(0.0005, volatilities[symbol], len(dates))  # Slight upward drift
    price_series = initial_prices[symbol] * np.exp(np.cumsum(returns))
    prices_dict[symbol] = price_series

price_df = pd.DataFrame(prices_dict, index=dates)

print(f"✅ Created historical data:")
print(f"   Symbols: {', '.join(symbols)}")
print(f"   Period: {price_df.index[0].date()} to {price_df.index[-1].date()}")
print(f"   Trading Days: {len(price_df)}")

print(f"\n📈 Price Summary:")
print(price_df.describe())

###############################################################################
# PART 2: Define Strategy to Backtest
###############################################################################

print("\n📊 Part 2: Defining Strategy for Backtesting")
print("-" * 80)

class SimpleBuyAndHold(Strategy):
    """
    Simple buy-and-hold strategy for backtesting
    Buys at start, holds till end
    """
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None):
        super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
        self.has_bought = False
    
    def run(self, price_data):
        """Buy on first day if haven't bought yet"""
        if not self.has_bought and len(price_data) >= 1:
            # Buy equal amounts of each symbol
            current_prices = price_data.iloc[-1]
            cash_per_symbol = self.strategy_balance / len(current_prices)
            
            for symbol in current_prices.index:
                price = current_prices[symbol]
                quantity = int(cash_per_symbol / price)
                
                if quantity > 0:
                    self.place_trade(
                        symbol=symbol,
                        direction=Trade.BUY,
                        quantity=quantity,
                        trade_type=Trade.MARKET,
                        price=price
                    )
            
            self.has_bought = True

print("✅ Defined SimpleBuyAndHold strategy")

###############################################################################
# PART 3: Run Backtest
###############################################################################

print("\n📊 Part 3: Running Backtest")
print("-" * 80)

backtester = Backtester(
    strategy_class=SimpleBuyAndHold,
    historical_data=price_df,
    initial_capital=100_000,
    commission_pct=0.001,  # 0.1% commission
    slippage_pct=0.0005    # 0.05% slippage
)

results = backtester.run()

###############################################################################
# PART 4: Analyze Results
###############################################################################

print("\n📊 Part 4: Analyzing Backtest Results")
print("-" * 80)

results.summary()

###############################################################################
# PART 5: Moving Average Crossover Strategy
###############################################################################

print("\n📊 Part 5: Backtesting Moving Average Crossover")
print("-" * 80)

class MovingAverageCrossover(Strategy):
    """
    MA crossover strategy - buy when short MA > long MA
    """
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None,
                 short_window=20, long_window=50):
        super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
        self.short_window = short_window
        self.long_window = long_window
        self.positions_opened = set()
    
    def run(self, price_data):
        """Execute MA crossover logic"""
        # Need enough data for long MA
        if len(price_data) < self.long_window:
            return
        
        for symbol in price_data.columns:
            # Calculate moving averages
            sma_short = price_data[symbol].rolling(window=self.short_window).mean()
            sma_long = price_data[symbol].rolling(window=self.long_window).mean()
            
            # Get latest values
            latest_short = sma_short.iloc[-1]
            latest_long = sma_long.iloc[-1]
            latest_price = price_data[symbol].iloc[-1]
            
            # Check if we already have position
            current_position = self.get_position(symbol)
            
            # Bullish crossover - buy
            if latest_short > latest_long and symbol not in self.positions_opened:
                quantity = int((self.strategy_balance * 0.3) / latest_price)  # 30% per symbol
                if quantity > 0:
                    self.place_trade(symbol, Trade.BUY, quantity, Trade.MARKET, price=latest_price)
                    self.positions_opened.add(symbol)
            
            # Bearish crossover - sell
            elif latest_short < latest_long and symbol in self.positions_opened:
                if current_position and not current_position.is_closed:
                    self.place_trade(symbol, Trade.SELL, current_position.quantity, 
                                   Trade.MARKET, price=latest_price)
                    self.positions_opened.discard(symbol)

print("Running MA Crossover backtest...")

ma_backtester = Backtester(
    strategy_class=MovingAverageCrossover,
    historical_data=price_df,
    initial_capital=100_000,
    commission_pct=0.001
)

ma_results = ma_backtester.run(strategy_params={
    'short_window': 20,
    'long_window': 50
})

ma_results.summary()

###############################################################################
# PART 6: Compare Strategies
###############################################################################

print("\n📊 Part 6: Comparing Backtest Results")
print("-" * 80)

print(f"\n{'Metric':<25} {'Buy & Hold':<20} {'MA Crossover':<20} {'Winner':<15}")
print("-" * 80)
print(f"{'Total Return':<25} ${results.total_return():<19,.2f} ${ma_results.total_return():<19,.2f} {'B&H' if results.total_return() > ma_results.total_return() else 'MA':<15}")
print(f"{'Return %':<25} {results.total_return_pct():<19.2f}% {ma_results.total_return_pct():<19.2f}% {'B&H' if results.total_return_pct() > ma_results.total_return_pct() else 'MA':<15}")
print(f"{'Sharpe Ratio':<25} {results.sharpe_ratio():<19.2f} {ma_results.sharpe_ratio():<19.2f} {'B&H' if results.sharpe_ratio() > ma_results.sharpe_ratio() else 'MA':<15}")
print(f"{'Max Drawdown':<25} {results.max_drawdown():<19.2f}% {ma_results.max_drawdown():<19.2f}% {'B&H' if abs(results.max_drawdown()) < abs(ma_results.max_drawdown()) else 'MA':<15}")
print(f"{'Win Rate':<25} {results.win_rate():<19.1f}% {ma_results.win_rate():<19.1f}% {'B&H' if results.win_rate() > ma_results.win_rate() else 'MA':<15}")
print(f"{'Total Trades':<25} {results.total_trades():<19} {ma_results.total_trades():<19} {'B&H' if results.total_trades() < ma_results.total_trades() else 'MA (more active)':<15}")

###############################################################################
# PART 7: Export Results
###############################################################################

print("\n📊 Part 7: Exporting Backtest Results")
print("-" * 80)

# Get equity curve
equity_df = ma_results.get_equity_curve()
print(f"\n📈 Equity Curve (Last 5 days):")
print(equity_df.tail())

# Get trades DataFrame
trades_df = ma_results.get_trades_dataframe()
print(f"\n📋 Trades DataFrame:")
print(trades_df.head())

# Export to dict
results_dict = ma_results.to_dict()
print(f"\n📤 Results Dictionary:")
for key, value in list(results_dict.items())[:8]:
    if isinstance(value, (int, float)):
        if isinstance(value, float) and abs(value) > 100:
            print(f"  {key}: ${value:,.2f}" if 'capital' in key or 'return' in key and 'pct' not in key else f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    else:
        print(f"  {key}: {value}")

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("SUMMARY - Backtesting Example")
print("=" * 80)

print("""
Key Concepts Demonstrated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Historical Data Preparation
   - Create pandas DataFrame with DatetimeIndex
   - Generate realistic price movements
   - 252 trading days (1 year) of data

2. ✅ Strategy Backtesting
   - Test strategies on historical data
   - Event-driven simulation (day-by-day)
   - Prevents look-ahead bias
   - Realistic execution

3. ✅ Commission & Slippage
   - Commission: 0.1% of trade value
   - Slippage: 0.05% of trade value
   - Automatically applied to trades
   - Reduces final equity

4. ✅ Performance Analysis
   - Integrated with PerformanceMetrics
   - Complete metrics (returns, Sharpe, drawdown)
   - Trade statistics (win rate, profit factor)
   - Risk-adjusted returns

5. ✅ Strategy Comparison
   - Run multiple backtests
   - Compare side-by-side
   - Determine best strategy
   - Statistical analysis

6. ✅ Results Export
   - Equity curve as DataFrame
   - Trades as DataFrame
   - Dictionary export (JSON-ready)
   - Easy integration with analysis tools

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backtesting Workflow:
  1. Prepare historical data (pandas DataFrame)
  2. Define strategy class
  3. Create Backtester with parameters
  4. Run backtest: results = backtester.run()
  5. Analyze: results.summary()
  6. Export: equity_df, trades_df, results_dict

Features:
  • Event-driven simulation (no look-ahead bias)
  • Commission and slippage modeling
  • Integrated performance metrics
  • Multiple strategy comparison
  • DataFrame export for further analysis

Next Steps:
  → Optimize parameters with optimization framework (coming soon)
  → Add walk-forward analysis (coming soon)
  → Add risk analytics integration (coming soon)
  → Generate backtest reports (coming soon)
""")

print("=" * 80)





