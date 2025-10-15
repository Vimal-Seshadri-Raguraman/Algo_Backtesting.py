"""
###############################################################################
# Example: Complete Workflow with Real Market Data (Pandas)
###############################################################################
# This example demonstrates a complete end-to-end workflow:
# 1. Loading historical price data with pandas
# 2. Creating full hierarchy (Account → Fund → Portfolio → Strategy)
# 3. Implementing strategies with technical indicators
# 4. Executing trades based on signals
# 5. Tracking positions and P&L
# 6. Analyzing performance metrics
###############################################################################
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""

import sys
from pathlib import Path

# Add parent directory to path to import core and tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import TradeAccount, Strategy, Trade
from tools import PerformanceMetrics
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print("COMPLETE WORKFLOW - Real Market Data with Pandas")
print("=" * 80)

###############################################################################
# PART 1: Generate Realistic Market Data
###############################################################################

print("\n📊 Part 1: Loading Historical Market Data")
print("-" * 80)

# Generate realistic price data (in production, load from CSV/API)
np.random.seed(42)

# Create 252 trading days (1 year)
start_date = datetime(2024, 1, 1)
dates = pd.date_range(start=start_date, periods=252, freq='B')  # Business days

# Simulate realistic price movements for tech stocks
symbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']
prices = {}

for symbol in symbols:
    # Different starting prices
    initial_prices = {'AAPL': 150, 'GOOGL': 140, 'MSFT': 350, 'NVDA': 500, 'AMD': 100}
    start_price = initial_prices[symbol]
    
    # Simulate price with drift and volatility
    returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
    price_series = start_price * np.exp(np.cumsum(returns))
    prices[symbol] = pd.Series(price_series, index=dates)

# Create DataFrame
price_df = pd.DataFrame(prices)

print(f"✅ Loaded price data:")
print(f"   Symbols: {', '.join(symbols)}")
print(f"   Date Range: {price_df.index[0].date()} to {price_df.index[-1].date()}")
print(f"   Trading Days: {len(price_df)}")

print(f"\n📈 Latest Prices (Last 5 Days):")
print(price_df.tail())

print(f"\n📊 Price Statistics:")
stats = price_df.describe()[['AAPL', 'GOOGL', 'MSFT']]
print(stats)

###############################################################################
# PART 2: Setup Trading Hierarchy
###############################################################################

print("\n📊 Part 2: Creating Trading Account Hierarchy")
print("-" * 80)

# Create account
account = TradeAccount(
    account_id="ACC001",
    account_name="Quantitative Hedge Fund",
    
)

# Create fund with rules
fund = account.create_fund(
    fund_id="FUND001",
    fund_name="Tech Growth Fund",
    fund_balance=10_000_000.00
)

fund.trade_rules.max_position_size_pct = 25.0
fund.trade_rules.max_single_trade_pct = 10.0
fund.trade_rules.allow_short_selling = True

# Create portfolio
portfolio = fund.create_portfolio(
    portfolio_id="PORT001",
    portfolio_name="Tech Momentum Portfolio",
    portfolio_balance=5_000_000.00
)

portfolio.trade_rules.max_position_size_pct = 20.0
portfolio.trade_rules.max_single_trade_pct = 5.0

print(f"✅ Created hierarchy:")
print(f"   Account: {account.account_name}")
print(f"   └── Fund: {fund.fund_name} (${fund.fund_balance:,.0f})")
print(f"       └── Portfolio: {portfolio.portfolio_name} (${portfolio.portfolio_balance:,.0f})")

###############################################################################
# PART 3: Implement Momentum Strategy with Pandas
###############################################################################

print("\n📊 Part 3: Implementing Momentum Strategy")
print("-" * 80)

class TechnicalMomentumStrategy(Strategy):
    """
    Momentum strategy using multiple technical indicators:
    - 20-day and 50-day moving averages
    - RSI (Relative Strength Index)
    - Volume analysis
    """
    
    def __init__(self, strategy_id, strategy_name, strategy_balance, portfolio=None):
        super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
        self.short_window = 20
        self.long_window = 50
    
    def calculate_indicators(self, price_series):
        """Calculate technical indicators"""
        # Moving averages
        sma_20 = price_series.rolling(window=self.short_window).mean()
        sma_50 = price_series.rolling(window=self.long_window).mean()
        
        # RSI (simplified)
        delta = price_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Momentum (rate of change)
        momentum = price_series.pct_change(periods=10) * 100
        
        return {
            'sma_20': sma_20.iloc[-1],
            'sma_50': sma_50.iloc[-1],
            'rsi': rsi.iloc[-1],
            'momentum': momentum.iloc[-1]
        }
    
    def run(self, price_data):
        """
        Execute momentum strategy
        
        Args:
            price_data: pandas DataFrame with historical prices
        """
        print(f"\n🔷 Running {self.strategy_name}...")
        print(f"   Analyzing {len(price_data.columns)} symbols...")
        
        signals = []
        
        for symbol in price_data.columns:
            # Calculate indicators
            indicators = self.calculate_indicators(price_data[symbol])
            current_price = price_data[symbol].iloc[-1]
            
            # Generate signal
            bullish_conditions = 0
            
            # MA crossover: Short MA > Long MA
            if indicators['sma_20'] > indicators['sma_50']:
                bullish_conditions += 1
            
            # RSI in buy zone (30-70)
            if 30 < indicators['rsi'] < 70:
                bullish_conditions += 1
            
            # Positive momentum
            if indicators['momentum'] > 0:
                bullish_conditions += 1
            
            # Strong buy signal: 3/3 conditions
            if bullish_conditions >= 2:
                signals.append({
                    'symbol': symbol,
                    'price': current_price,
                    'signal_strength': bullish_conditions,
                    'indicators': indicators
                })
        
        # Execute trades on strong signals
        print(f"\n   Found {len(signals)} buy signals:")
        
        # Allocate capital equally among signals
        if signals:
            capital_per_trade = self.strategy_balance / len(signals)
            
            for signal in signals:
                symbol = signal['symbol']
                price = signal['price']
                quantity = int(capital_per_trade / price)
                
                if quantity > 0:
                    trade = self.place_trade(
                        symbol=symbol,
                        direction=Trade.BUY,
                        quantity=quantity,
                        trade_type=Trade.MARKET,
                        price=price
                    )
                    
                    print(f"   ✓ BUY {quantity} {symbol} @ ${price:.2f}")
                    print(f"      Indicators: SMA20=${signal['indicators']['sma_20']:.2f}, "
                          f"RSI={signal['indicators']['rsi']:.1f}, "
                          f"Momentum={signal['indicators']['momentum']:.1f}%")
        
        print(f"\n   ✅ Executed {len(self.trades)} trades")

# Create and run strategy
momentum_strategy = TechnicalMomentumStrategy(
    strategy_id="STRAT001",
    strategy_name="Tech Momentum",
    strategy_balance=1_000_000.00,
    portfolio=portfolio
)

momentum_strategy.run(price_df)

###############################################################################
# PART 4: Track Positions and P&L
###############################################################################

print("\n📊 Part 4: Position Tracking")
print("-" * 80)

print(f"\nOpen Positions:")
print(f"{'Symbol':<10} {'Quantity':<12} {'Entry Price':<15} {'Current Price':<15} {'Market Value':<15} {'Unrealized P&L':<15}")
print("-" * 95)

current_prices = price_df.iloc[-1].to_dict()
total_unrealized_pnl = 0

for symbol, position in momentum_strategy.get_open_positions().items():
    current_price = current_prices.get(symbol, position.avg_entry_price)
    market_value = position.get_market_value(current_price)
    unrealized_pnl = position.get_unrealized_pnl(current_price)
    total_unrealized_pnl += unrealized_pnl
    
    print(f"{symbol:<10} {position.quantity:<12} ${position.avg_entry_price:<14,.2f} ${current_price:<14,.2f} ${market_value:<14,.2f} ${unrealized_pnl:<14,.2f}")

print(f"\nTotal Unrealized P&L: ${total_unrealized_pnl:,.2f}")

###############################################################################
# PART 5: Ledger Analysis
###############################################################################

print("\n📊 Part 5: Ledger Analysis")
print("-" * 80)

print(f"\nLedger Statistics:")
print(f"  Total Trades: {momentum_strategy.ledger.get_trade_count()}")
print(f"  Total Volume: ${momentum_strategy.ledger.get_total_volume():,.2f}")
print(f"  Symbols Traded: {', '.join(momentum_strategy.ledger.get_symbols_traded())}")

# Show recent trades
print(f"\nRecent Trades:")
recent_trades = momentum_strategy.ledger.get_all_trades()[-5:]
for trade in recent_trades:
    print(f"  {trade.symbol}: {trade.direction} {trade.filled_quantity} @ ${trade.avg_fill_price:.2f}")

###############################################################################
# PART 6: Performance Metrics
###############################################################################

print("\n📊 Part 6: Performance Analysis")
print("-" * 80)

# Calculate performance with current prices
momentum_strategy.performance_metrics(current_prices=current_prices)

###############################################################################
# PART 7: Portfolio and Fund Aggregation
###############################################################################

print("\n📊 Part 7: Portfolio & Fund Performance")
print("-" * 80)

print("\n📈 Portfolio Performance:")
portfolio.performance_metrics(current_prices=current_prices)

print("\n📈 Fund Performance:")
fund.performance_metrics(current_prices=current_prices)

###############################################################################
# PART 8: Price Chart Summary (using pandas)
###############################################################################

print("\n📊 Part 8: Market Data Summary")
print("-" * 80)

# Calculate returns
returns = price_df.pct_change()
cumulative_returns = (1 + returns).cumprod() - 1

print(f"\nCumulative Returns (from start to end):")
for symbol in price_df.columns:
    total_return = cumulative_returns[symbol].iloc[-1] * 100
    print(f"  {symbol}: {total_return:+.2f}%")

# Volatility
print(f"\nAnnualized Volatility:")
for symbol in price_df.columns:
    vol = returns[symbol].std() * np.sqrt(252) * 100  # Annualized
    print(f"  {symbol}: {vol:.2f}%")

# Correlation matrix
print(f"\nCorrelation Matrix:")
corr_matrix = returns.corr()
print(corr_matrix.round(2))

###############################################################################
# SUMMARY
###############################################################################

print("\n" + "=" * 80)
print("COMPLETE WORKFLOW - SUMMARY")
print("=" * 80)

# Export metrics for further analysis
metrics = momentum_strategy.performance_metrics(current_prices=current_prices, show_summary=False)
metrics_dict = metrics.to_dict()

print(f"""
📊 Workflow Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Market Data
   - Loaded {len(price_df)} days of price data for {len(price_df.columns)} symbols
   - Used pandas DataFrames for analysis
   - Calculated technical indicators (MA, RSI, Momentum)

2. ✅ Account Hierarchy
   - Created complete hierarchy: Account → Fund → Portfolio → Strategy
   - Set compliance rules at fund and portfolio levels
   - Capital allocation: ${momentum_strategy.strategy_balance:,.0f} to strategy

3. ✅ Strategy Execution
   - Implemented technical momentum strategy
   - Analyzed {len(price_df.columns)} symbols
   - Executed {len(momentum_strategy.trades)} trades

4. ✅ Position Tracking
   - {len(momentum_strategy.get_open_positions())} open positions
   - Total Unrealized P&L: ${total_unrealized_pnl:,.2f}
   - Positions tracked with entry prices

5. ✅ Performance Analysis
   - Total Return: ${metrics_dict['total_return']:,.2f} ({metrics_dict['total_return_pct']:.2f}%)
   - Sharpe Ratio: {metrics_dict['sharpe_ratio']:.2f}
   - Max Drawdown: {metrics_dict['max_drawdown']:.2f}%
   - Win Rate: {metrics_dict['win_rate']:.2f}%

6. ✅ Hierarchical Aggregation
   - Strategy-level metrics calculated
   - Portfolio-level aggregation
   - Fund-level consolidation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Pandas Features Used:
  • DataFrame for multi-symbol price data
  • Rolling windows for moving averages
  • Correlation analysis
  • Returns and volatility calculations
  • Time-series indexing with business days

Next Steps:
  → Save price_df to CSV: price_df.to_csv('prices.csv')
  → Export metrics: pd.DataFrame([metrics_dict]).to_csv('metrics.csv')
  → Implement more strategies (mean reversion, pairs trading)
  → Add walk-forward optimization
  → Connect to real data sources (yfinance, Alpha Vantage, etc.)

""")

print("=" * 80)
print("✅ Complete workflow demonstration finished!")
print("=" * 80)


