# Trade Engine Examples

This folder contains focused examples demonstrating each component of the Trade Engine.

---

## 📁 Example Structure

### **Core Components**

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| **example_account.py** | TradeAccount basics | Account creation, fund management, hierarchy root, extension pattern |
| **example_fund.py** | Fund management | Compliance rules, portfolio allocation, capital management, extension pattern |
| **example_portfolio.py** | Portfolio operations | Strategy allocation, risk rules, capital tracking, extension pattern |
| **example_strategy.py** | Strategy implementation | Custom strategies, pandas integration, technical indicators |

### **Trading Features**

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| **example_trade_types.py** | All 5 trade types | MARKET, LIMIT, STOP_LOSS, STOP_LIMIT, TRAILING_STOP |
| **example_short_selling.py** | Short positions | SELL_SHORT, BUY_TO_COVER, P&L from shorts, risks |
| **example_rules.py** | Compliance & validation | Rule violations, error handling, symbol restrictions |

### **Analysis & Performance**

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| **example_backtesting.py** | Historical strategy testing | Backtesting, optimization comparison, event-driven simulation |
| **example_pnl_tracking.py** | P&L tracking | Win rate, profit factor, realized/unrealized P&L |
| **example_performance_metrics.py** | Performance analysis | Returns, Sharpe ratio, drawdown |

### **Complete Demos**

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| **example_comprehensive.py** | Original full demo | Complete workflow with all features |

### **Complete Workflows**

| Example | Description | Features |
|---------|-------------|----------|
| **example_complete.py** | End-to-end with pandas | Real market data, technical indicators, full analysis |

---

## 🚀 Quick Start

### Run Examples in Order

```bash
# Core components (Start here)
python3 examples/example_account.py      # 1. Learn accounts & extension
python3 examples/example_fund.py         # 2. Learn funds & extension
python3 examples/example_portfolio.py    # 3. Learn portfolios & extension
python3 examples/example_strategy.py     # 4. Learn strategies with pandas

# Trading features
python3 examples/example_trade_types.py  # 5. All 5 order types
python3 examples/example_short_selling.py # 6. Short selling workflow
python3 examples/example_rules.py        # 7. Compliance & violations

# Analysis & tools (requires pandas/numpy)
python3 examples/example_backtesting.py  # 8. Historical backtesting
python3 examples/example_pnl_tracking.py # 9. P&L tracking
python3 examples/example_performance_metrics.py # 10. Performance metrics

# Complete workflows
python3 examples/example_complete.py     # Full workflow with pandas
python3 examples/example_comprehensive.py # Original complete demo
```

---

## 📊 Example Details

### **example_account.py** - TradeAccount Basics
Learn the foundation of the hierarchy:
- Creating a TradeAccount
- Adding multiple funds
- Querying account information
- Understanding the hierarchy root

**Key Takeaway:** TradeAccount is the top-level container for all trading activity.

---

### **example_fund.py** - Fund Management
Master fund-level operations:
- Creating funds (standalone vs. linked)
- Configuring compliance rules (position limits, short selling, margin)
- Allocating capital to portfolios
- Comparing conservative vs. aggressive fund strategies

**Key Takeaway:** Funds enforce compliance rules and allocate capital to portfolios.

---

### **example_portfolio.py** - Portfolio Operations
Understand portfolio management:
- Creating portfolios within funds
- Setting portfolio-level risk rules (stricter than fund)
- Allocating capital to strategies
- Monitoring capital allocation

**Key Takeaway:** Portfolios provide additional risk management layer above strategies.

---

### **example_strategy.py** - Strategy Implementation
Implement trading strategies with pandas:
- Creating custom strategy classes
- Using pandas DataFrames for price data
- Calculating technical indicators (moving averages, RSI)
- Standalone vs. linked strategies
- Helper methods for position management

**Key Takeaway:** Strategies implement trading logic using pandas for data analysis.

---

### **example_trade_types.py** - All 5 Trade Types
Comprehensive demonstration of all order types:
- **MARKET**: Immediate execution at current price
- **LIMIT**: Execute at specified price or better
- **STOP_LOSS**: Trigger when price hits stop level (loss protection)
- **STOP_LIMIT**: Combination of stop trigger + limit price
- **TRAILING_STOP**: Dynamic stop that follows price (lock in gains)

Shows practical use cases for each type and when to use them.

**Key Takeaway:** Master all 5 order types for different trading scenarios.

---

### **example_short_selling.py** - Short Selling Workflow
Complete short selling demonstration:
- Opening short positions (SELL_SHORT)
- Closing short positions (BUY_TO_COVER)
- Profitable shorts (price declines)
- Losing shorts (short squeeze)
- Multiple short positions
- Short selling risks and compliance

**Key Takeaway:** Short selling workflow for profiting from price declines.

---

### **example_rules.py** - Compliance & Validation
Comprehensive rule system demonstration:
- Setting up trading rules (fund and portfolio levels)
- Position size limits (max_position_size_pct, max_single_trade_pct)
- Symbol restrictions (allowed_symbols whitelist, restricted_symbols blacklist)
- Trade type and direction restrictions
- Catching TradeComplianceError and InsufficientFundsError
- Production error handling patterns

Shows how rules protect against:
- Oversized positions
- Restricted symbols
- Unauthorized short selling
- Insufficient funds

**Key Takeaway:** Multi-level compliance protects against trading violations.

---

### **example_complete.py** - Complete Workflow ⭐
**Most comprehensive example** - demonstrates entire workflow:

**Part 1:** Generate realistic market data with pandas
- 252 trading days of price data
- 5 tech stocks (AAPL, GOOGL, MSFT, NVDA, AMD)
- Simulated realistic price movements

**Part 2:** Create full hierarchy
- Account → Fund → Portfolio → Strategy
- Set compliance rules at each level

**Part 3:** Implement momentum strategy
- Calculate technical indicators (MA, RSI, Momentum)
- Generate trading signals
- Execute trades based on conditions

**Part 4:** Track positions and P&L
- Monitor open positions
- Calculate unrealized P&L
- Track market values

**Part 5:** Analyze ledger
- Query trades
- Calculate volumes
- View trading history

**Part 6:** Performance metrics
- Returns, Sharpe ratio, max drawdown
- Win rate, profit factor
- Volatility analysis

**Part 7:** Hierarchical aggregation
- Strategy, portfolio, and fund-level metrics
- Complete audit trail

**Part 8:** Market data analysis
- Cumulative returns
- Correlation matrix
- Volatility calculations

**Key Takeaway:** Complete production-ready workflow using pandas for real market data.

---

### **example_comprehensive.py** - Original Demo
Original comprehensive example showing:
- Multi-fund setup
- Multiple strategies
- Hierarchical ledger system
- All features working together

---

### **example_performance_metrics.py** - Performance Analysis
Focused on performance metrics:
- Strategy-level metrics
- Portfolio aggregation
- Fund and account-level analysis
- Comparing strategies

---

### **example_pnl_tracking.py** - P&L Tracking
Enhanced P&L tracking with:
- Opening and closing positions
- Realized P&L calculation
- Win rate and profit factor
- Largest win/loss tracking
- Multiple strategy comparison

---

## 🎓 Learning Path

### **Beginner** (Start Here)
1. `example_account.py` - Understand the hierarchy & extension pattern
2. `example_fund.py` - Learn fund management & extension pattern
3. `example_portfolio.py` - Understand portfolios & extension pattern

### **Intermediate** (Trading Features)
4. `example_strategy.py` - Implement strategies with pandas
5. `example_trade_types.py` - All 5 order types (MARKET, LIMIT, STOP, etc.)
6. `example_short_selling.py` - Short selling workflow (SELL_SHORT → BUY_TO_COVER)
7. `example_rules.py` - Compliance, validation, error handling

### **Advanced** (Analysis & Performance)
8. `example_pnl_tracking.py` - Track realized/unrealized P&L
9. `example_performance_metrics.py` - Sharpe, Sortino, win rate, etc.

### **Complete Workflows**
10. `example_complete.py` - Full workflow with pandas & technical indicators
11. `example_comprehensive.py` - Complex multi-strategy setup

---

## 📦 Using Pandas for Market Data

All modern examples use pandas for data management:

```python
import pandas as pd
import numpy as np

# Load historical data
price_df = pd.read_csv('prices.csv', index_col=0, parse_dates=True)

# Or generate sample data
dates = pd.date_range('2024-01-01', periods=252, freq='B')
prices = {'AAPL': pd.Series([...], index=dates)}
price_df = pd.DataFrame(prices)

# Calculate indicators
sma_20 = price_df['AAPL'].rolling(window=20).mean()
returns = price_df.pct_change()
volatility = returns.std() * np.sqrt(252)

# Pass to strategy
strategy.run(price_df)
```

---

## 🔧 Common Patterns

### **1. Setup Hierarchy**
```python
from core import TradeAccount, Strategy, Trade

account = TradeAccount("ACC001", "My Account")
fund = account.create_fund("FUND001", "Fund", 1_000_000)
portfolio = fund.create_portfolio("PORT001", "Portfolio", 500_000)
```

### **2. Configure Rules**
```python
fund.trade_rules.max_position_size_pct = 20.0
fund.trade_rules.allow_short_selling = True
portfolio.trade_rules.max_single_trade_pct = 5.0
```

### **3. Implement Strategy**
```python
class MyStrategy(Strategy):
    def run(self, price_data):
        # Your logic here
        for symbol in price_data.columns:
            price = price_data[symbol].iloc[-1]
            self.place_trade(symbol, Trade.BUY, 100, Trade.MARKET, price=price)

strategy = MyStrategy("S001", "My Strat", 100_000, portfolio=portfolio)
strategy.run(price_df)
```

### **4. Analyze Performance**
```python
from tools import PerformanceMetrics

# Via method (recommended)
strategy.performance_metrics(current_prices=prices)

# Or create directly
metrics = PerformanceMetrics(
    owner_name=strategy.strategy_name,
    owner_type="Strategy",
    ledger=strategy.ledger,
    initial_balance=strategy.strategy_balance,
    current_balance=current_balance
)
metrics.summary()
```

---

## 💡 Tips

1. **Start Simple:** Begin with `example_account.py` and work your way up
2. **Use Pandas:** Modern examples show pandas integration for real-world usage
3. **Understand Hierarchy:** Each level adds validation and audit capabilities
4. **Test Standalone:** Strategies can run without hierarchy for quick testing
5. **Check Performance:** Always analyze metrics after running strategies

---

## 🎯 Next Steps

After exploring the examples:

1. **Modify Examples:** Change parameters, add your own logic
2. **Real Data:** Connect to yfinance, Alpha Vantage, or your broker API
3. **Custom Strategies:** Implement your own trading algorithms
4. **Optimization:** Use tools for parameter optimization (coming soon)
5. **Backtesting:** Test strategies on historical data (coming soon)

---

## 📚 Additional Resources

- **Main README:** `../README.md` - Complete system documentation
- **Code Documentation:** All classes have detailed docstrings
- **API Reference:** See main README for complete API documentation

---

## 🆘 Need Help?

- Review the example that matches your use case
- Check docstrings in the source code
- See main README for architectural overview
- Examples are self-contained and well-commented

---

*Examples last updated: October 11, 2025*

