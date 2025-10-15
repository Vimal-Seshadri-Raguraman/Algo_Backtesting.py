# Core - Trading Engine Framework

The `core` package contains all base classes for the Trade Engine framework. **All classes can be used directly OR extended** - your choice!

---

## 🎯 Framework Philosophy

**Like Django, Flask, and other frameworks:**
- ✅ Use base classes directly (quick start, prototyping)
- ✅ Extend base classes (production, custom behavior)
- ✅ No penalty either way - both are first-class approaches

---

## 📦 Base Classes

| Module | Class | Type | Description |
|--------|-------|------|-------------|
| **account.py** | TradeAccount | Base Class | Top-level container for funds |
| **fund.py** | Fund | Base Class | Raised capital unit with compliance rules |
| **portfolio.py** | Portfolio | Base Class | Capital allocation with risk rules |
| **strategy.py** | Strategy | Base Class | Trading logic (must subclass) |
| **position.py** | Position | Utility Class | Symbol position aggregate |
| **trade.py** | Trade | Data Class | Individual trade order |
| **rules.py** | TradeRules | Configuration | Compliance rules |
| **ledger.py** | Ledger | Utility Class | Automatic trade recording |
| **exceptions.py** | Exceptions | Error Classes | Custom exceptions |

---

## 🔧 Base Class: TradeAccount

**Top-level container for all trading activity.**

### Direct Usage
```python
from core import TradeAccount

account = TradeAccount("ACC001", "My Account")
fund = account.create_fund("FUND001", "Growth Fund", 1_000_000)
```

### Extended Usage
```python
class HedgeFundAccount(TradeAccount):
    def __init__(self, account_id, account_name, fund_manager):
        super().__init__(account_id, account_name)
        self.fund_manager = fund_manager
    
    def generate_sec_filing(self):
        """Custom SEC reporting"""
        print(f"SEC Filing for {self.account_name}")
        self.summary(show_children=True)

account = HedgeFundAccount("HF001", "Quantum Fund", "John Doe")
account.generate_sec_filing()
```

### Extension Points
- Override `create_fund()` to return custom Fund subclasses
- Add reporting methods (SEC filings, investor statements)
- Add compliance checks
- Add database integration

**See:** `examples/example_account.py`

---

## 🔧 Base Class: Fund

**Manages raised capital with compliance enforcement.**

### Direct Usage
```python
from core import Fund

fund = Fund("FUND001", "Growth Fund", 1_000_000)
fund.trade_rules.max_position_size_pct = 20.0
portfolio = fund.create_portfolio("PORT001", "Tech", 500_000)
```

### Extended Usage
```python
class AutoRebalancingFund(Fund):
    def __init__(self, fund_id, fund_name, fund_balance, rebalance_freq='quarterly'):
        super().__init__(fund_id, fund_name, fund_balance)
        self.rebalance_freq = rebalance_freq
    
    def auto_rebalance(self):
        """Rebalance portfolios to target weights"""
        # Custom rebalancing logic
        pass
    
    def calculate_nav(self):
        """Calculate NAV per share"""
        return self.fund_balance / 1000

fund = AutoRebalancingFund("FUND001", "Auto Fund", 10_000_000)
fund.auto_rebalance()
```

### Extension Points
- Override `create_portfolio()` for custom Portfolio subclasses
- Add auto-rebalancing
- Add NAV calculation
- Add fee calculation (management, performance)
- Add investor subscription/redemption
- Override `validate_trade()` for custom compliance

**See:** `examples/example_fund.py`

---

## 🔧 Base Class: Portfolio

**Allocates capital to strategies with risk management.**

### Direct Usage
```python
from core import Portfolio

portfolio = Portfolio("PORT001", "Tech Portfolio", 500_000)
portfolio.trade_rules.max_position_size_pct = 15.0
```

### Extended Usage
```python
class RiskManagedPortfolio(Portfolio):
    def __init__(self, portfolio_id, portfolio_name, portfolio_balance, var_limit=0.05):
        super().__init__(portfolio_id, portfolio_name, portfolio_balance)
        self.var_limit = var_limit
        self.risk_alerts = []
    
    def calculate_var(self):
        """Calculate Value at Risk"""
        var = self.portfolio_balance * self.var_limit
        return var
    
    def check_concentration(self):
        """Monitor strategy concentration"""
        for strategy in self.strategies.values():
            concentration = strategy.strategy_balance / self.portfolio_balance
            if concentration > 0.30:
                print(f"⚠️ {strategy.strategy_name} at {concentration*100:.0f}%")

portfolio = RiskManagedPortfolio("PORT001", "Risk Port", 5_000_000)
portfolio.check_concentration()
```

### Extension Points
- Add VaR monitoring
- Add concentration limits
- Add auto-rebalancing across strategies
- Add performance attribution
- Override `validate_trade()` for custom risk checks

**See:** `examples/example_portfolio.py`

---

## 🔧 Base Class: Strategy

**Implements trading logic (must be subclassed).**

### Basic Usage (Must Subclass)
```python
from core import Strategy, Trade

class SimpleStrategy(Strategy):
    def run(self):
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)

strategy = SimpleStrategy("STRAT001", "Simple", 100_000)
strategy.run()
```

### Advanced Usage (Custom Parameters)
```python
class MovingAverageCrossover(Strategy):
    def __init__(self, strategy_id, strategy_name, strategy_balance,
                 portfolio=None, short_window=20, long_window=50):
        super().__init__(strategy_id, strategy_name, strategy_balance, portfolio)
        self.short_window = short_window
        self.long_window = long_window
    
    def run(self, price_data):
        # Calculate moving averages
        sma_short = price_data.rolling(window=self.short_window).mean()
        sma_long = price_data.rolling(window=self.long_window).mean()
        
        # Trade on crossover
        if sma_short.iloc[-1] > sma_long.iloc[-1]:
            self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=...)

strategy = MovingAverageCrossover("STRAT001", "MA Cross", 100_000,
                                  short_window=10, long_window=30)
strategy.run(price_df)
```

### Extension Points (Methods to Implement/Override)
- `run()` - **REQUIRED** - Your trading logic
- Override `place_trade()` for custom execution
- Add signal generation methods
- Add position sizing algorithms
- Add entry/exit logic
- Add custom risk management

**See:** `examples/example_strategy.py`

---

## 📊 Supporting Classes

### Position
Tracks aggregated position for a symbol within a strategy.

```python
position = strategy.get_position("AAPL")
print(f"Quantity: {position.quantity}")
print(f"Avg Entry: ${position.avg_entry_price:.2f}")
print(f"Realized P&L: ${position.realized_pnl:.2f}")
print(f"Unrealized P&L: ${position.get_unrealized_pnl(current_price):.2f}")
```

### Trade
Represents individual trade order.

```python
# Trade constants
Trade.MARKET, Trade.LIMIT, Trade.STOP_LOSS
Trade.BUY, Trade.SELL, Trade.SELL_SHORT, Trade.BUY_TO_COVER
Trade.FILLED, Trade.PENDING, Trade.CANCELLED

# Trade attributes
trade.trade_id
trade.status
trade.filled_quantity
trade.avg_fill_price
trade.realized_pnl
```

### TradeRules
Configuration for compliance at Fund/Portfolio levels.

```python
fund.trade_rules.max_position_size_pct = 20.0
fund.trade_rules.allow_short_selling = True
fund.trade_rules.allowed_symbols = {"AAPL", "GOOGL", "MSFT"}
```

### Ledger
Automatic hierarchical trade recording.

```python
strategy.ledger.get_trades_by_symbol("AAPL")
strategy.ledger.get_total_volume()
strategy.ledger.summary(show_recent=10)
data = strategy.ledger.export_to_dict()
```

### Exceptions
```python
from core import TradeComplianceError, InsufficientFundsError

try:
    strategy.place_trade(...)
except TradeComplianceError as e:
    print(f"Rule violation: {e}")
except InsufficientFundsError as e:
    print(f"Not enough cash: {e}")
```

---

## 🎨 Usage Patterns

### Pattern 1: Direct Usage (Beginner)
```python
account = TradeAccount("ACC001", "Account")
fund = account.create_fund("FUND001", "Fund", 1_000_000)
portfolio = fund.create_portfolio("PORT001", "Portfolio", 500_000)

class MyStrategy(Strategy):
    def run(self):
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)

strategy = MyStrategy("STRAT001", "Strategy", 100_000, portfolio)
```

### Pattern 2: Extended Usage (Production)
```python
class HedgeFundAccount(TradeAccount):
    def generate_report(self):
        pass

class AutoRebalancingFund(Fund):
    def auto_rebalance(self):
        pass

class RiskManagedPortfolio(Portfolio):
    def calculate_var(self):
        pass

class MomentumStrategy(Strategy):
    def run(self, price_data):
        # Trading logic
        pass

# Use extended classes
account = HedgeFundAccount("HF001", "Quantum Fund")
fund = AutoRebalancingFund("FUND001", "Auto Fund", 10_000_000)
portfolio = RiskManagedPortfolio("PORT001", "Risk Port", 5_000_000)
strategy = MomentumStrategy("STRAT001", "Momentum", 1_000_000)
```

---

## 📚 Documentation

### In-Code Documentation
Every class has comprehensive docstrings showing:
- Basic usage (direct instantiation)
- Advanced usage (extension examples)
- Extension points (what to override/add)
- Parameters and return values

### Examples
See `examples/` folder for complete demonstrations:
- `example_account.py` - TradeAccount usage & extension
- `example_fund.py` - Fund usage & extension
- `example_portfolio.py` - Portfolio usage & extension
- `example_strategy.py` - Strategy implementation patterns

---

## 🚀 Quick Reference

```python
# Import core classes
from core import TradeAccount, Fund, Portfolio, Strategy, Trade

# Use directly (valid)
account = TradeAccount("ACC001", "Account")

# Or extend (encouraged for production)
class MyAccount(TradeAccount):
    pass

# Both work perfectly!
```

---

**For complete framework guide and examples, see:**
- 📖 Main README: `../README.md`
- 📚 Examples: `../examples/README.md`
- 🛠️ Tools: `../tools/README.md`

---

*Core Framework - Version 1.0*

