# Tools - Analysis & Utilities

The `tools` package contains analysis and utility modules that enhance the core trading engine.

---

## 📦 Available Tools

| Module | Description | Dependencies | Status |
|--------|-------------|--------------|--------|
| **performance** | Performance metrics & analytics | None (Pure Python) | ✅ Complete |
| **backtesting** | Historical strategy testing | pandas, numpy | ✅ Complete |
| **optimization** | Strategy parameter optimization | pandas, numpy | ✅ Complete |
| **risk** | Risk analytics & VaR | pandas, numpy | ✅ Complete |
| **reporting** | Report generation (CSV/JSON) | pandas | ✅ Complete |

### Installation

Core framework has **NO dependencies**. Tools require pandas/numpy:

```bash
pip install pandas numpy

# Optional: For visualization
pip install matplotlib
```

---

## 📊 1. Performance Metrics

### Overview

The `PerformanceMetrics` class calculates comprehensive trading performance metrics at any hierarchy level (Strategy, Portfolio, Fund, or Account).

### Features

#### **Return Metrics**
- Total Return ($ and %)
- Annualized Return (CAGR)

#### **Trade Statistics**
- Total Trades
- Winning/Losing Trades
- Win Rate
- Profit Factor (gross profit / gross loss)
- Average Trade P&L
- Largest Win/Loss
- Trade Volume
- Trade Frequency

#### **Risk Metrics**
- Max Drawdown
- Volatility (Annualized)
- Downside Deviation

#### **Risk-Adjusted Returns**
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio

### Usage

```python
from core import Strategy, Trade
from tools import PerformanceMetrics

# Via Strategy (Recommended)
strategy = MyStrategy("STRAT001", "Strategy", 100_000)
strategy.run()
strategy.performance_metrics(current_prices={"AAPL": 165})

# Direct Usage
metrics = PerformanceMetrics(
    owner_name="My Strategy",
    owner_type="Strategy",
    ledger=strategy.ledger,
    initial_balance=100_000,
    current_balance=101_500,
    current_prices={"AAPL": 165}
)

metrics.summary()
print(f"Sharpe Ratio: {metrics.sharpe_ratio():.2f}")
print(f"Win Rate: {metrics.win_rate():.2f}%")
```

### API

```python
# Returns
metrics.total_return()              # Total P&L ($)
metrics.total_return_pct()          # Total return (%)
metrics.annualized_return()         # CAGR

# Trade Stats
metrics.win_rate()                  # Win rate %
metrics.profit_factor()             # Gross profit / gross loss
metrics.largest_win()               # Largest win ($)
metrics.largest_loss()              # Largest loss ($)

# Risk
metrics.max_drawdown()              # Max drawdown %
metrics.volatility()                # Annualized volatility %
metrics.sharpe_ratio()              # Sharpe ratio
metrics.sortino_ratio()             # Sortino ratio
metrics.calmar_ratio()              # Calmar ratio

# Export
metrics.summary()                   # Print report
metrics.to_dict()                   # Export as dict
```

---

## 🔁 2. Backtesting

### Overview

The `Backtester` class provides event-driven historical strategy testing with realistic execution simulation.

### Features

- **Event-Driven Simulation**: Day-by-day replay (no look-ahead bias)
- **Commission & Slippage**: Realistic cost modeling
- **Performance Integration**: Full PerformanceMetrics integration
- **Multiple Strategies**: Compare different approaches
- **Flexible Data**: Works with any pandas DataFrame

### Usage

```python
from tools import Backtester
import pandas as pd

# Prepare historical data
price_df = pd.DataFrame({
    'AAPL': [150, 152, 148, 155, 160],
    'GOOGL': [140, 142, 141, 145, 148]
}, index=pd.date_range('2024-01-01', periods=5, freq='B'))

# Define strategy to backtest
class MyStrategy(Strategy):
    def run(self, price_data):
        # Strategy logic using historical data
        if len(price_data) >= 20:
            # Calculate moving average, place trades, etc.
            pass

# Run backtest
backtester = Backtester(
    strategy_class=MyStrategy,
    historical_data=price_df,
    initial_capital=100_000,
    commission_pct=0.001,  # 0.1%
    slippage_pct=0.0005    # 0.05%
)

results = backtester.run()
results.summary()

# Access results
print(f"Total Return: {results.total_return_pct():.2f}%")
print(f"Sharpe Ratio: {results.sharpe_ratio():.2f}")
print(f"Max Drawdown: {results.max_drawdown():.2f}%")

# Export
equity_df = results.get_equity_curve()
trades_df = results.get_trades_dataframe()
results_dict = results.to_dict()
```

### API

#### Backtester

```python
backtester = Backtester(
    strategy_class=MyStrategy,      # Strategy class (not instance)
    historical_data=price_df,       # DataFrame with DatetimeIndex
    initial_capital=100_000,        # Starting capital
    commission_pct=0.001,           # Commission %
    slippage_pct=0.0005,            # Slippage %
    start_date='2024-01-01',        # Optional
    end_date='2024-12-31'           # Optional
)

results = backtester.run(strategy_params={'window': 20})
```

#### BacktestResults

```python
results.summary()                   # Print comprehensive report
results.total_return()              # Total return ($)
results.total_return_pct()          # Total return (%)
results.sharpe_ratio()              # Sharpe ratio
results.max_drawdown()              # Max drawdown %
results.win_rate()                  # Win rate %
results.total_trades()              # Number of trades

# Export
results.get_equity_curve()          # DataFrame with equity/returns
results.get_trades_dataframe()      # DataFrame with all trades
results.to_dict()                   # Dictionary (JSON-ready)
results.plot_equity_curve()         # Plot (requires matplotlib)
```

---

## ⚙️ 3. Optimization

### Overview

The `StrategyOptimizer` class finds optimal strategy parameters through systematic backtesting.

### Features

- **Grid Search**: Test all parameter combinations
- **Random Search**: Sample parameter space efficiently
- **Multiple Objectives**: Optimize for Sharpe, return, Sortino, etc.
- **Parallel Ready**: Easy to extend for parallel execution
- **Result Analysis**: Compare top N parameter sets

### Usage

```python
from tools import StrategyOptimizer

# Define parameter search space
optimizer = StrategyOptimizer(
    strategy_class=MovingAverageCrossover,
    historical_data=price_df,
    optimize_params={
        'short_window': [5, 10, 15, 20],
        'long_window': [30, 50, 70, 100]
    },
    initial_capital=100_000,
    objective='sharpe_ratio'  # or 'return', 'sortino', 'calmar', 'win_rate'
)

# Run optimization
results = optimizer.optimize(method='grid_search')

# Get best parameters
best_params = results.get_best_parameters()
print(f"Best Parameters: {best_params}")
print(f"Best Sharpe: {results.get_best_objective_value():.2f}")

# View top 10
results.summary(top_n=10)

# Export results
df = results.to_dataframe()
df.to_csv('optimization_results.csv')
```

### API

```python
optimizer = StrategyOptimizer(
    strategy_class=MyStrategy,
    historical_data=price_df,
    optimize_params={'param1': [1,2,3], 'param2': [10,20,30]},
    objective='sharpe_ratio',   # sharpe_ratio, return, sortino, calmar, win_rate, profit_factor
    commission_pct=0.001
)

# Methods
results = optimizer.optimize(method='grid_search')    # Exhaustive search
results = optimizer.optimize(method='random_search', max_iterations=100)

# Results
results.get_best_parameters()       # Dict of best params
results.get_best_objective_value()  # Best metric value
results.get_top_n(10)               # Top 10 param combos
results.to_dataframe()              # Export as DataFrame
results.summary(top_n=5)            # Print top 5
```

---

## ⚠️ 4. Risk Analytics

### Overview

The `RiskAnalyzer` class provides comprehensive risk analysis for portfolios and strategies.

### Features

- **Value at Risk (VaR)**: Historical and parametric methods
- **CVaR (Expected Shortfall)**: Tail risk measurement
- **Correlation Analysis**: Inter-asset correlation
- **Beta & Alpha**: Market risk metrics
- **Portfolio Volatility**: Risk calculation
- **Position Exposure**: Breakdown by symbol

### Usage

```python
from tools import RiskAnalyzer
import pandas as pd

# Analyze strategy risk
analyzer = RiskAnalyzer(
    strategy=my_strategy,
    price_history=price_df,
    benchmark=sp500_returns  # Optional
)

analyzer.summary()

# Individual metrics
var_95 = analyzer.calculate_var(confidence=0.95)
cvar_95 = analyzer.calculate_cvar(confidence=0.95)
print(f"VaR (95%): {var_95:.2f}%")
print(f"CVaR (95%): {cvar_95:.2f}%")

# Correlation analysis
corr_matrix = analyzer.get_correlation_matrix()
print(corr_matrix)

# Market risk (if benchmark provided)
beta = analyzer.calculate_beta()
alpha = analyzer.calculate_alpha()
print(f"Beta: {beta:.2f}")
print(f"Alpha: {alpha:.2f}%")

# Exposure
exposures = analyzer.get_position_exposure()
```

### API

```python
analyzer = RiskAnalyzer(
    strategy=my_strategy,       # Optional
    portfolio=my_portfolio,     # Optional
    price_history=price_df,     # DataFrame with prices
    benchmark=benchmark_returns # Optional (for beta/alpha)
)

# Value at Risk
analyzer.calculate_var(confidence=0.95, method='historical')  # or 'parametric'
analyzer.calculate_cvar(confidence=0.95)

# Correlation & Volatility
analyzer.get_correlation_matrix()
analyzer.get_portfolio_volatility(weights=None)  # None = equal-weight

# Market Risk (requires benchmark)
analyzer.calculate_beta(symbol=None)    # None = portfolio beta
analyzer.calculate_alpha(symbol=None, risk_free_rate=0.02)

# Exposure
analyzer.get_position_exposure()

# Summary
analyzer.summary()
```

---

## 📄 5. Reporting

### Overview

The `ReportGenerator` class exports trading data and reports in multiple formats.

### Features

- **CSV Export**: Trades and ledger summaries
- **JSON Export**: Complete reports (API-friendly)
- **Text Reports**: Formatted text output
- **Performance Integration**: Includes metrics automatically
- **Hierarchical**: Works with Strategy, Portfolio, Fund, Account

### Usage

```python
from tools import ReportGenerator

# Create report generator
report = ReportGenerator(strategy=my_strategy)

# Export trades to CSV
trades_df = report.trades_to_csv('trades.csv')

# Export complete report to JSON
report_dict = report.to_json('report.json')

# Generate text report
report_text = report.generate_text_report('report.txt')

# Or print to console
report.generate_text_report()
```

### API

```python
report = ReportGenerator(
    strategy=my_strategy,       # or portfolio, fund, account
    # portfolio=my_portfolio,
    # fund=my_fund,
    # account=my_account
)

# CSV Export
report.trades_to_csv('trades.csv')              # All trades
report.ledger_summary_to_csv('summary.csv')     # Ledger summary

# JSON Export
report.to_json('report.json')                   # Complete report

# Text Report
report.generate_text_report('report.txt')       # Save to file
report.generate_text_report()                   # Print to console
```

---

## 🔗 Integration Example

Using multiple tools together:

```python
from core import Strategy, Trade
from tools import Backtester, StrategyOptimizer, RiskAnalyzer, ReportGenerator
import pandas as pd

# 1. Optimize strategy
optimizer = StrategyOptimizer(
    strategy_class=MyStrategy,
    historical_data=price_df,
    optimize_params={'window': [10, 20, 30]},
    objective='sharpe_ratio'
)
opt_results = optimizer.optimize()
best_params = opt_results.get_best_parameters()

# 2. Backtest with best parameters
backtester = Backtester(
    strategy_class=MyStrategy,
    historical_data=price_df,
    initial_capital=100_000
)
backtest_results = backtester.run(strategy_params=best_params)

# 3. Analyze risk
analyzer = RiskAnalyzer(
    strategy=backtest_results.strategy,
    price_history=price_df
)
analyzer.summary()

# 4. Generate reports
report = ReportGenerator(strategy=backtest_results.strategy)
report.to_json('final_report.json')
report.trades_to_csv('trades.csv')
```

---

## 📈 Example Workflow

1. **Develop Strategy** (core)
2. **Backtest Strategy** (backtesting)
3. **Optimize Parameters** (optimization)
4. **Analyze Risk** (risk)
5. **Generate Reports** (reporting)
6. **Monitor Performance** (performance)

---

## 📚 Examples

See `examples/` folder:
- `example_backtesting.py` - Complete backtesting workflow
- `example_performance_metrics.py` - Performance analysis
- `example_complete.py` - Full workflow demo

---

## 🎯 Dependencies

### Core Framework
- **NO dependencies** - Pure Python

### Tools
- **performance**: No dependencies
- **backtesting**: pandas, numpy
- **optimization**: pandas, numpy
- **risk**: pandas, numpy (scipy for parametric VaR)
- **reporting**: pandas

### Optional
- **matplotlib**: For plotting equity curves
- **scipy**: For advanced optimization methods

```bash
# Install all tool dependencies
pip install -r requirements.txt
```

---

**For complete documentation:**
- 📖 Main README: `../README.md`
- 🔧 Core Classes: `../core/README.md`
- 📚 Examples: `../examples/README.md`

---

*Tools Package - Version 2.0*

