# Quant Trade Engine - Hierarchical Trading Framework

A comprehensive, production-ready trading system with multi-level compliance, hierarchical ledger recording, and data-source agnostic architecture.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage Guide](#detailed-usage-guide)
- [Ledger System](#ledger-system)
- [Trading Rules & Compliance](#trading-rules--compliance)
- [API Reference](#api-reference)
- [Module Structure](#module-structure)
- [Examples](#examples)
- [Design Philosophy](#design-philosophy)
- [Future Enhancements](#future-enhancements)

---

## Overview

The Trade Engine is a sophisticated, hierarchical trading framework designed for managing complex trading operations across multiple funds, portfolios, and strategies. It provides:

- **Multi-level hierarchy**: Account → Fund → Portfolio → Strategy
- **Automatic trade recording**: Ledger system tracks all trades at every level
- **Compliance enforcement**: Configurable rules at fund and portfolio levels
- **Data source agnostic**: Works with any market data provider
- **Position management**: Real-time P&L tracking and position aggregation
- **Flexible strategy implementation**: No enforced rules at strategy level

Perfect for:
- Hedge funds managing multiple strategies
- Trading firms with complex organizational structures
- Algorithmic trading systems requiring audit trails
- Educational purposes to learn trading system architecture

---

## Key Features

### 🏗️ Hierarchical Architecture
```
TradeAccount
    ├── Fund 1
    │   ├── Portfolio A
    │   │   ├── Strategy 1
    │   │   └── Strategy 2
    │   └── Portfolio B
    │       └── Strategy 3
    └── Fund 2
        └── Portfolio C
            └── Strategy 4
```

### 📒 Automatic Ledger System
- **Hierarchical Recording**: Every trade is automatically recorded at 4 levels
- **Fast Queries**: Indexed lookups by symbol, status, direction, date
- **Rich Analytics**: Volume, commission, buy/sell ratios, activity tracking
- **Export Ready**: JSON-compatible dictionary export for databases

### 🛡️ Multi-Layer Compliance
- **Fund Level**: Compliance rules (e.g., max position size, short selling)
- **Portfolio Level**: Risk rules (more restrictive than fund)
- **Strategy Level**: NO rules - programmer has full control
- **Safety Net**: All trades validated against parent rules before execution

### 💹 Position & Trade Management
- **5 Trade Types**: MARKET, LIMIT, STOP_LOSS, STOP_LIMIT, TRAILING_STOP
- **4 Directions**: BUY, SELL, SELL_SHORT, BUY_TO_COVER
- **Real-time P&L**: Realized and unrealized profit/loss tracking
- **Average Cost Basis**: Industry-standard accounting method

### 🔌 Data Source Agnostic (Pass-Through Only)
- **Framework never fetches data** - you control all price sourcing
- `data_provider` parameter is a **convenience pass-through** (set once, available everywhere)
- You decide when/how to use it in your custom strategies
- Compatible with any data source: Yahoo Finance, Alpha Vantage, Interactive Brokers, Alpaca, etc.
- Can operate without data provider (prices provided explicitly)

---

## Architecture

### Hierarchy Levels

| Level | Description | Has Ledger | Has Rules | Factory Method |
|-------|-------------|:----------:|:---------:|----------------|
| **TradeAccount** | Top-level container | ✅ | ❌ | `create_fund()` |
| **Fund** | Raised capital unit | ✅ | ✅ | `create_portfolio()` |
| **Portfolio** | Capital allocation | ✅ | ✅ | - |
| **Strategy** | Trading logic | ✅ | ❌ | Auto-registers |
| **Position** | Symbol aggregate | ❌ | ❌ | Auto-created |
| **Trade** | Individual order | ❌ | ❌ | Via `place_trade()` |

### Data Flow

```
Strategy.place_trade()
    ↓
Validate Portfolio Rules → ❌ Reject or ✅ Continue
    ↓
Validate Fund Rules → ❌ Reject or ✅ Continue
    ↓
Check Sufficient Funds → ❌ Reject or ✅ Continue
    ↓
Execute Trade (Fill)
    ↓
Record in All Ledgers (Strategy → Portfolio → Fund → Account)
    ↓
Update Position
    ↓
Return Trade Object
```

---

## Installation

### Prerequisites
- Python 3.7+
- No external dependencies required for core functionality

### Setup

```bash
# Clone or download the Trade_Engine directory
cd /path/to/Trade_Engine

# The core package is ready to use
python3 example_comprehensive.py
```

### Optional: Install as Package
```bash
# Create setup.py (if needed for pip install)
pip install -e .
```

### Import in Your Code
```python
from core import (
    TradeAccount,
    Fund,
    Portfolio,
    Strategy,
    Trade,
    Position,
    TradeRules,
    Ledger,
    TradeComplianceError,
    InsufficientFundsError
)
```

---

## Quick Start

### 30-Second Example (Linked Mode)

```python
from core import TradeAccount, Strategy, Trade

# 1. Create account
account = TradeAccount("ACC001", "My Account")

# 2. Create fund
fund = account.create_fund("FUND001", "Growth Fund", 1_000_000)

# 3. Create portfolio
portfolio = fund.create_portfolio("PORT001", "Tech", 500_000)

# 4. Create strategy (auto-links to portfolio)
class MyStrategy(Strategy):
    def run(self):
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)

strategy = MyStrategy("STRAT001", "My Strat", 100_000, portfolio=portfolio)

# 5. Run (automatic validation + ledger cascade)
strategy.run()

# 6. View results
account.summary()
strategy.ledger.summary()
```

### 30-Second Example (Standalone Mode)

```python
from core import Strategy, Trade

# 1. Create standalone strategy (no hierarchy needed!)
class MyStrategy(Strategy):
    def run(self):
        # You provide prices explicitly - framework doesn't fetch
        price = 150.00  # From your data source
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=price)

strategy = MyStrategy("STRAT001", "My Strat", 100_000, 
                     portfolio=None, data_provider=None)

# 2. Run (no validation, max flexibility)
strategy.run()

# 3. View results
strategy.ledger.summary()
```

---

## Understanding Optional Hierarchy

### Components Work Independently OR Linked

Every component in the Trade Engine can work **standalone** OR be **linked** to parents:

| Component | Can Work Alone? | Optional Parent | Auto-Links When? |
|-----------|:---------------:|-----------------|------------------|
| **Strategy** | ✅ Yes | Portfolio | Created with `portfolio=parent` |
| **Portfolio** | ✅ Yes | Fund | Created with `fund=parent` |
| **Fund** | ✅ Yes | TradeAccount | Created with `trade_account=parent` |
| **TradeAccount** | ✅ Yes | None | Always standalone |

### Benefits of Each Mode

**Standalone Mode** (portfolio=None):
- ✅ Quick testing and prototyping
- ✅ No validation overhead
- ✅ Maximum flexibility
- ✅ Perfect for backtesting
- ⚠️ No safety nets

**Linked Mode** (portfolio=parent):
- ✅ Automatic validation
- ✅ Automatic ledger cascade
- ✅ Safety nets (rules enforcement)
- ✅ Complete audit trail
- ⚠️ Requires full hierarchy setup

### Usage Patterns

```python
# Pattern 1: Standalone Strategy (fastest)
strategy = Strategy("S001", "Test", 100_000, portfolio=None, data_provider=None)

# Pattern 2: Portfolio + Strategy (partial chain)
portfolio = Portfolio("P001", "Tech", 500_000, fund=None, data_provider=None)
strategy = Strategy("S001", "Test", 100_000, portfolio=portfolio)

# Pattern 3: Fund + Portfolio + Strategy (partial chain)
fund = Fund("F001", "Growth", 1_000_000, trade_account=None, data_provider=None)
portfolio = fund.create_portfolio("P001", "Tech", 500_000)
strategy = Strategy("S001", "Test", 100_000, portfolio=portfolio)

# Pattern 4: Full Hierarchy (maximum safety)
account = TradeAccount("ACC001", "Account", data_provider=None)
fund = account.create_fund("F001", "Growth", 1_000_000)
portfolio = fund.create_portfolio("P001", "Tech", 500_000)
strategy = Strategy("S001", "Test", 100_000, portfolio=portfolio)
```

---

## Detailed Usage Guide

### 1. Creating the Account Hierarchy

#### Step 1: Create TradeAccount
```python
from core import TradeAccount

# With data provider (OPTIONAL - acts as pass-through for convenience)
# Set once here, accessible in all strategies via self.data_provider
# Framework NEVER calls it - YOU decide when to fetch prices
data_provider = YourBrokerAPI()  # Your choice: Yahoo Finance, IB, Alpaca, etc.
account = TradeAccount("ACC001", "My Account", data_provider=data_provider)

# Without data provider (prices provided explicitly in place_trade)
account = TradeAccount("ACC001", "My Account", data_provider=None)
```

#### Step 2: Create Funds
```python
# Create fund with raised capital
fund = account.create_fund(
    fund_id="FUND001",
    fund_name="Growth Fund",
    fund_balance=1_000_000.00
)

# Configure fund-level rules
fund.trade_rules.max_position_size_pct = 25.0  # Max 25% per position
fund.trade_rules.max_single_trade_pct = 10.0   # Max 10% per trade
fund.trade_rules.allow_short_selling = True
fund.trade_rules.allow_margin = True

print(f"Fund created: {fund.fund_name}")
print(f"Cash available: ${fund.cash_balance:,.2f}")
```

#### Step 3: Create Portfolios
```python
# Allocate capital from fund to portfolio
portfolio = fund.create_portfolio(
    portfolio_id="PORT001",
    portfolio_name="Tech Portfolio",
    portfolio_balance=500_000.00
)

# Configure portfolio-level rules (more restrictive than fund)
portfolio.trade_rules.max_position_size_pct = 20.0
portfolio.trade_rules.max_single_trade_pct = 5.0

print(f"Portfolio created: {portfolio.portfolio_name}")
print(f"Fund remaining cash: ${fund.cash_balance:,.2f}")
```

#### Step 4: Create Strategies
```python
from core import Strategy, Trade

class MomentumStrategy(Strategy):
    """
    Custom strategy - implement your trading logic
    """
    
    def run(self):
        """Your trading logic here"""
        # YOU fetch prices (framework never does this automatically)
        # Option 1: Use self.data_provider if you set it
        # price = self.data_provider.get_price("AAPL") if self.data_provider else 150.00
        
        # Option 2: Provide explicitly
        price = 150.00  # From your data source
        
        trade = self.place_trade(
            symbol="AAPL",
            direction=Trade.BUY,
            quantity=100,
            trade_type=Trade.MARKET,
            price=price  # Always required
        )
        print(f"Executed: {trade}")

# Instantiate strategy (auto-registers with portfolio)
strategy = MomentumStrategy(
    strategy_id="STRAT001",
    strategy_name="Momentum Strategy",
    strategy_balance=100_000.00,
    portfolio=portfolio
)

# Run your strategy
strategy.run()
```

### 2. Trading Operations

#### Place Different Trade Types
```python
# Note: Price is ALWAYS required - framework never auto-fetches
# Fetch prices however you want (API, CSV, database, etc.)

# Market Order
price = 150.00  # User fetches/provides
trade1 = strategy.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=price)

# Limit Order
price = 140.00
trade2 = strategy.place_trade("GOOGL", Trade.BUY, 50, Trade.LIMIT, price=price)

# Stop Loss
trade3 = strategy.place_trade("MSFT", Trade.SELL, 75, Trade.STOP_LOSS, 
                              price=340.00, stop_price=335.00)

# Short Selling (if allowed by fund rules)
price = 250.00
trade4 = strategy.place_trade("TSLA", Trade.SELL_SHORT, 200, Trade.MARKET, price=price)

# Cover Short
price = 240.00
trade5 = strategy.place_trade("TSLA", Trade.BUY_TO_COVER, 200, Trade.MARKET, price=price)
```

#### Error Handling
```python
from core import TradeComplianceError, InsufficientFundsError

try:
    trade = strategy.place_trade("AAPL", Trade.BUY, 1000, Trade.MARKET, price=150.00)
except TradeComplianceError as e:
    print(f"Compliance violation: {e}")
except InsufficientFundsError as e:
    print(f"Not enough cash: {e}")
```

### 3. Position Management

#### Query Positions
```python
# Get specific position
position = strategy.get_position("AAPL")
print(f"Position: {position}")
print(f"Quantity: {position.quantity}")
print(f"Entry Price: ${position.avg_entry_price:.2f}")

# Calculate market value and P&L at current price (you provide price)
current_price = 155.00  # Fetch from your data source
print(f"Market Value: ${position.get_market_value(current_price):,.2f}")
print(f"Unrealized P&L: ${position.get_unrealized_pnl(current_price):,.2f}")

# Get all open positions
open_positions = strategy.get_open_positions()
for symbol, pos in open_positions.items():
    print(f"{symbol}: {pos}")
```

### 4. Viewing Summaries

#### Strategy Summary
```python
strategy.summary(show_positions=True)
```

#### Portfolio Summary
```python
portfolio.summary(show_children=True)  # Shows all strategies
```

#### Fund Summary
```python
fund.summary(show_children=True)  # Shows all portfolios and strategies
```

#### Account Summary
```python
account.summary(show_children=True)  # Shows entire hierarchy
```

---

## Ledger System

### Overview

The Ledger system automatically records every trade at all hierarchy levels, providing comprehensive audit trails and analytics.

### Automatic Recording

When you execute a trade:
```python
strategy.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)
```

The trade is **automatically recorded** in:
1. ✅ Strategy ledger
2. ✅ Portfolio ledger
3. ✅ Fund ledger
4. ✅ Account ledger

### Accessing Ledgers

Every level has a `.ledger` attribute:
```python
print(strategy.ledger)    # Ledger(Strategy: My Strategy, Trades: 5, Symbols: 3)
print(portfolio.ledger)   # Ledger(Portfolio: Tech Portfolio, Trades: 12, Symbols: 8)
print(fund.ledger)        # Ledger(Fund: Growth Fund, Trades: 45, Symbols: 20)
print(account.ledger)     # Ledger(TradeAccount: My Account, Trades: 100, Symbols: 35)
```

### Ledger Queries

#### Basic Queries
```python
# Get all trades
all_trades = ledger.get_all_trades()

# Filter by symbol
aapl_trades = ledger.get_trades_by_symbol("AAPL")

# Filter by status
filled_trades = ledger.get_filled_trades()
pending_trades = ledger.get_pending_trades()

# Filter by direction
buy_trades = ledger.get_trades_by_direction(Trade.BUY)
sell_trades = ledger.get_trades_by_direction(Trade.SELL)

# Filter by date range
from datetime import datetime, timedelta
today = datetime.now()
yesterday = today - timedelta(days=1)
recent_trades = ledger.get_trades_by_date_range(yesterday, today)
```

#### Statistics & Metrics
```python
# Trade counts
total_trades = ledger.get_trade_count()
filled_count = ledger.get_filled_trade_count()

# Volume analysis
total_volume = ledger.get_total_volume()           # All symbols
aapl_volume = ledger.get_total_volume("AAPL")      # Specific symbol

# Commission tracking
total_commission = ledger.get_total_commission()

# Buy vs Sell analysis
ratios = ledger.get_buy_vs_sell_ratio()
print(f"BUY trades: {ratios['BUY']}")
print(f"SELL trades: {ratios['SELL']}")
print(f"SHORT trades: {ratios['SELL_SHORT']}")
print(f"COVER trades: {ratios['BUY_TO_COVER']}")

# Symbols traded
symbols = ledger.get_symbols_traded()
print(f"Traded symbols: {symbols}")

# Activity by date
activity = ledger.get_activity_by_date()
for date, count in activity.items():
    print(f"{date}: {count} trades")
```

### Ledger Reports

#### Basic Summary
```python
# Show summary
ledger.summary()

# Show summary with recent trades
ledger.summary(show_recent=10)
```

Example output:
```
================================================================================
📒 LEDGER SUMMARY: Momentum Strategy (Strategy)
================================================================================
Total Trades:                    15
Filled Trades:                   15
Pending Trades:                  0
Symbols Traded:                  5
Total Volume:      $    125,450.00
Total Commission:  $          0.00

Trade Direction Breakdown:
--------------------------------------------------------------------------------
  BUY trades:                     10
  SELL trades:                     5
  SELL_SHORT trades:               0
  BUY_TO_COVER:                    0

Symbols Traded:
--------------------------------------------------------------------------------
  AAPL       Trades:   5  Volume: $   75,000.00
  GOOGL      Trades:   3  Volume: $   21,000.00
  MSFT       Trades:   4  Volume: $   14,200.00
  TSLA       Trades:   2  Volume: $   10,000.00
  NVDA       Trades:   1  Volume: $    5,250.00
================================================================================
```

### Export Ledger Data

```python
# Export to dictionary (JSON-compatible)
data = ledger.export_to_dict()

# Structure:
{
    'owner_name': 'Momentum Strategy',
    'owner_type': 'Strategy',
    'created_at': '2025-10-09T12:00:00',
    'total_trades': 15,
    'filled_trades': 15,
    'symbols_traded': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'],
    'total_volume': 125450.0,
    'total_commission': 0.0,
    'trade_directions': {...},
    'activity_by_date': {...}
}

# Save to file
import json
with open('ledger_export.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

## Trading Rules & Compliance

### Rule Hierarchy

Rules cascade down the hierarchy:
```
Fund Rules (Compliance)
    ↓
Portfolio Rules (Risk) - Can be MORE restrictive
    ↓
Strategy - NO rules, but validated against parents
```

### Configuring Fund Rules

```python
fund = account.create_fund("FUND001", "Growth Fund", 1_000_000)

# Trade types allowed
fund.trade_rules.allowed_trade_types = {
    Trade.MARKET,
    Trade.LIMIT,
    Trade.STOP_LOSS
}

# Directions allowed
fund.trade_rules.allowed_directions = {Trade.BUY, Trade.SELL}  # Long-only

# Position constraints
fund.trade_rules.allow_short_selling = False
fund.trade_rules.allow_margin = False
fund.trade_rules.allow_options = False
fund.trade_rules.allow_futures = False

# Size limits (percentage of portfolio value)
fund.trade_rules.max_position_size_pct = 25.0   # Max 25% per position
fund.trade_rules.max_single_trade_pct = 10.0    # Max 10% per trade

# Symbol restrictions
fund.trade_rules.allowed_symbols = {"AAPL", "GOOGL", "MSFT"}  # Whitelist
fund.trade_rules.restricted_symbols = {"TSLA"}                 # Blacklist
```

### Configuring Portfolio Rules

```python
portfolio = fund.create_portfolio("PORT001", "Tech", 500_000)

# Portfolio rules can be MORE restrictive than fund rules
portfolio.trade_rules.max_position_size_pct = 20.0  # Tighter than fund's 25%
portfolio.trade_rules.max_single_trade_pct = 5.0    # Tighter than fund's 10%

# Portfolio rules CANNOT override fund restrictions
# If fund disallows short selling, portfolio cannot enable it
```

### Strategy Helper Methods

Strategies can query parent rules:

```python
# Query maximum position limits
max_pct = strategy.get_max_position_pct()        # Returns portfolio's limit
max_value = strategy.get_max_position_value()    # In dollars

# Query short selling permission
can_short = strategy.can_short()                 # From fund rules

# Query allowed trade types
allowed_types = strategy.get_allowed_trade_types()  # From fund rules

# Check available cash
cash = strategy.cash_balance
```

### Rule Validation Example

```python
# This will be validated against both portfolio and fund rules
try:
    trade = strategy.place_trade(
        symbol="AAPL",
        direction=Trade.BUY,
        quantity=1000,     # Large quantity
        trade_type=Trade.MARKET,
        price=150.00
    )
except TradeComplianceError as e:
    # Caught violations:
    # - Trade size exceeds max_single_trade_pct
    # - Position size would exceed max_position_size_pct
    # - Symbol not in allowed_symbols
    # - Direction not in allowed_directions
    print(f"Trade rejected: {e}")
```

---

## API Reference

### TradeAccount

```python
class TradeAccount(account_id, account_name, data_provider=None)
```

**Methods:**
- `create_fund(fund_id, fund_name, fund_balance)` → Fund
- `get_fund(fund_id)` → Fund | None
- `update_fund(fund_id, **kwargs)` → Fund
- `remove_fund(fund_id)` → bool
- `summary(show_children=False)` → None

**Properties:**
- `account_balance` - Total balance across all funds
- `ledger` - Account-level ledger
- `funds` - Dictionary of funds

---

### Fund

```python
class Fund(fund_id, fund_name, fund_balance, trade_account=None, data_provider=None)
```

**Parameters:**
- `trade_account` - Optional parent account (None = standalone mode)
- `data_provider` - Optional pass-through (used if trade_account=None)

**Methods:**
- `create_portfolio(portfolio_id, portfolio_name, portfolio_balance)` → Portfolio
- `get_portfolio(portfolio_id)` → Portfolio | None
- `update_portfolio(portfolio_id, **kwargs)` → Portfolio
- `remove_portfolio(portfolio_id)` → bool
- `validate_trade(trade, portfolio_value)` → (bool, str)
- `summary(show_children=False)` → None

**Properties:**
- `allocated_balance` - Capital allocated to portfolios
- `cash_balance` - Unallocated cash
- `trade_rules` - Fund-level TradeRules object
- `ledger` - Fund-level ledger
- `portfolios` - Dictionary of portfolios

---

### Portfolio

```python
class Portfolio(portfolio_id, portfolio_name, portfolio_balance, fund=None, data_provider=None)
```

**Parameters:**
- `fund` - Optional parent fund (None = standalone mode)
- `data_provider` - Optional pass-through (used if fund=None)

**Methods:**
- `get_strategy(strategy_id)` → Strategy | None
- `update_strategy(strategy_id, **kwargs)` → Strategy
- `remove_strategy(strategy_id)` → bool
- `validate_trade(trade, current_position=None)` → (bool, str)
- `summary(show_children=False)` → None

**Properties:**
- `allocated_balance` - Capital allocated to strategies
- `cash_balance` - Unallocated cash
- `trade_rules` - Portfolio-level TradeRules object
- `ledger` - Portfolio-level ledger
- `strategies` - Dictionary of strategies

---

### Strategy

```python
class Strategy(strategy_id, strategy_name, strategy_balance, portfolio=None, data_provider=None)
```

**Parameters:**
- `portfolio` - Optional parent portfolio (None = standalone mode)
- `data_provider` - Optional pass-through (used if portfolio=None)

**Methods:**
- `place_trade(symbol, direction, quantity, trade_type, price, stop_price=None)` → Trade
- `get_cash_balance(current_prices=None)` → float
- `get_position(symbol)` → Position | None
- `get_open_positions()` → dict
- `get_max_position_pct()` → float
- `get_max_position_value()` → float
- `can_short()` → bool
- `get_allowed_trade_types()` → set
- `summary(show_positions=False, current_prices=None)` → None

**Properties:**
- `positions` - Dictionary of positions
- `trades` - List of all trades
- `ledger` - Strategy-level ledger
- `data_provider` - Pass-through from parent or direct parameter

**Must Implement:**
- `run()` - Your custom trading logic

---

### Trade

```python
class Trade(symbol, direction, quantity, trade_type, strategy, price=None, stop_price=None)
```

**Constants:**
- Trade Types: `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LIMIT`, `TRAILING_STOP`
- Directions: `BUY`, `SELL`, `SELL_SHORT`, `BUY_TO_COVER`
- Status: `PENDING`, `SUBMITTED`, `FILLED`, `PARTIALLY_FILLED`, `CANCELLED`, `REJECTED`

**Properties:**
- `trade_id` - Unique identifier
- `status` - Current status
- `filled_quantity` - Shares filled
- `avg_fill_price` - Average fill price
- `commission` - Commission paid
- `created_at`, `submitted_at`, `filled_at` - Timestamps

---

### Position

```python
class Position(symbol, strategy)
```

**Methods:**
- `get_market_value(current_price)` → float
- `get_unrealized_pnl(current_price)` → float
- `update_from_trade(trade)` → None

**Properties:**
- `quantity` - Current quantity (+ve = long, -ve = short)
- `avg_entry_price` - Average entry price
- `realized_pnl` - Realized profit/loss
- `is_long`, `is_short`, `is_closed` - Position type checks
- `opening_trades`, `closing_trades` - Trade history

---

### Ledger

```python
class Ledger(owner_name, owner_type)
```

**Methods:**
- `record_trade(trade)` → None
- `get_all_trades()` → list
- `get_trades_by_symbol(symbol)` → list
- `get_trades_by_status(status)` → list
- `get_trades_by_direction(direction)` → list
- `get_trades_by_date_range(start, end)` → list
- `get_filled_trades()` → list
- `get_pending_trades()` → list
- `get_symbols_traded()` → set
- `get_trade_count()` → int
- `get_filled_trade_count()` → int
- `get_total_volume(symbol=None)` → float
- `get_total_commission()` → float
- `get_buy_vs_sell_ratio()` → dict
- `get_activity_by_date()` → dict
- `summary(show_recent=0)` → None
- `export_to_dict()` → dict

---

### TradeRules

```python
class TradeRules(name="Default Rules")
```

**Methods:**
- `is_trade_allowed(trade, portfolio_value, current_position=None)` → (bool, str)

**Properties:**
- `allowed_trade_types` - Set of allowed trade types
- `allowed_directions` - Set of allowed directions
- `allow_short_selling` - Boolean
- `allow_margin` - Boolean
- `allow_options` - Boolean
- `allow_futures` - Boolean
- `max_position_size_pct` - Maximum position size (%)
- `max_single_trade_pct` - Maximum single trade size (%)
- `allowed_symbols` - Set of allowed symbols (None = all)
- `restricted_symbols` - Set of restricted symbols

---

## Module Structure

```
Trade_Engine/
├── core/                          # Core trading system package
│   ├── __init__.py               # Package exports
│   ├── account.py                # TradeAccount class (5.6 KB)
│   ├── fund.py                   # Fund class (7.0 KB)
│   ├── portfolio.py              # Portfolio class (6.2 KB)
│   ├── strategy.py               # Strategy base class (8.4 KB)
│   ├── position.py               # Position class (4.4 KB)
│   ├── trade.py                  # Trade class (2.3 KB)
│   ├── rules.py                  # TradeRules class (4.7 KB)
│   ├── ledger.py                 # Ledger class (9.4 KB)
│   └── exceptions.py             # Custom exceptions (430 B)
│
├── example_comprehensive.py      # Complete example (14 KB, 391 lines)
├── README.md                     # This file
└── rough.ipynb                   # Original development notebook
```

---

## Examples

### Example 1: Standalone Strategy (No Hierarchy)

```python
from core import Strategy, Trade

# Create standalone strategy - fastest way to get started!
class BacktestStrategy(Strategy):
    def run(self):
        # No validation, no restrictions
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)
        self.place_trade("GOOGL", Trade.BUY, 50, Trade.MARKET, price=140)
        self.place_trade("TSLA", Trade.SELL_SHORT, 200, Trade.MARKET, price=250)

strategy = BacktestStrategy("BT001", "Backtest", 100_000, 
                           portfolio=None, data_provider=None)
strategy.run()

# View results
strategy.summary(show_positions=True)
strategy.ledger.summary()
```

### Example 2: Linked Mode (Full Hierarchy)

```python
from core import TradeAccount, Strategy, Trade

# Setup full hierarchy - maximum safety
account = TradeAccount("ACC001", "My Account")
fund = account.create_fund("FUND001", "Fund", 1_000_000)
portfolio = fund.create_portfolio("PORT001", "Portfolio", 500_000)

# Strategy auto-links and gets validation
class SafeStrategy(Strategy):
    def run(self):
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)

strategy = SafeStrategy("STRAT001", "Safe", 100_000, portfolio=portfolio)
strategy.run()  # Automatic validation + ledger cascade

# View complete chain
account.summary(show_children=True)
```

### Example 3: Long-Only Fund

```python
# Create long-only fund
fund = account.create_fund("FUND002", "Long-Only Fund", 1_000_000)
fund.trade_rules.allowed_directions = {Trade.BUY, Trade.SELL}
fund.trade_rules.allow_short_selling = False

# Attempts to short will be rejected
try:
    strategy.place_trade("TSLA", Trade.SELL_SHORT, 100, Trade.MARKET, price=250)
except TradeComplianceError as e:
    print(f"Rejected: {e}")  # "Fund rule violation: Trade direction 'SELL_SHORT' not allowed"
```

### Example 4: Ledger Analytics

```python
# Execute multiple trades
for symbol in ["AAPL", "GOOGL", "MSFT"]:
    strategy.place_trade(symbol, Trade.BUY, 100, Trade.MARKET, price=150)

# Query ledger
ledger = account.ledger
print(f"Total trades: {ledger.get_trade_count()}")
print(f"Total volume: ${ledger.get_total_volume():,.2f}")
print(f"Symbols: {ledger.get_symbols_traded()}")

# Export for analysis
data = ledger.export_to_dict()
```

### Example 5: Multiple Strategies

```python
class TechStrategy(Strategy):
    def run(self):
        self.place_trade("AAPL", Trade.BUY, 100, Trade.MARKET, price=150)
        self.place_trade("GOOGL", Trade.BUY, 50, Trade.MARKET, price=140)

class FinanceStrategy(Strategy):
    def run(self):
        self.place_trade("JPM", Trade.BUY, 200, Trade.MARKET, price=145)
        self.place_trade("BAC", Trade.BUY, 300, Trade.MARKET, price=32)

tech = TechStrategy("TECH001", "Tech", 100_000, portfolio)
finance = FinanceStrategy("FIN001", "Finance", 100_000, portfolio)

tech.run()
finance.run()

# View portfolio ledger (contains trades from both strategies)
portfolio.ledger.summary()
```

### Run Comprehensive Example

```bash
python3 example_comprehensive.py
```

This demonstrates:
- Complete hierarchy setup
- Multiple funds and portfolios
- Rule configuration
- Trade execution
- Ledger system
- Query capabilities
- Performance reporting

---

## Design Philosophy

### Why This Architecture?

1. **Separation of Concerns**: Each level has a clear responsibility
2. **Flexibility**: Strategies have no enforced rules for maximum flexibility
3. **Safety**: Portfolio and fund rules provide safety nets
4. **Transparency**: Ledger system creates complete audit trail
5. **Scalability**: Hierarchy supports complex organizational structures

### Why NO Rules at Strategy Level?

The framework **trusts programmers** to implement correct logic at the strategy level while providing **safety nets** through portfolio and fund rules. This gives:

- ✅ Maximum flexibility for strategy implementation
- ✅ Safety against catastrophic errors (fund/portfolio validation)
- ✅ Clear separation between business logic (strategy) and compliance (fund/portfolio)
- ✅ Ability to test strategies without rule interference

### Data Source Agnostic Design

The system doesn't depend on any specific data provider. The `data_provider` parameter is **purely a pass-through mechanism**:

- Set it at `TradeAccount` level → flows down to all children
- Framework NEVER calls it - you use it in YOUR custom strategies
- No required interface - use ANY data source you want
- You control when/how/if to fetch prices

**Compatible with:**
- **Yahoo Finance** (yfinance library)
- **Alpha Vantage** (alpha_vantage library)
- **Interactive Brokers API** (ib_insync or ibapi)
- **Alpaca** (alpaca-trade-api)
- **Polygon.io** (polygon library)
- **TD Ameritrade API**
- **CSV files, databases, or any custom source**

### Trade Execution

Currently simulated (instant fill) for development and testing:
```python
# In production, replace with real broker integration:
# - Submit order to broker API
# - Monitor order status
# - Update when filled
# - Handle partial fills, cancellations, rejections
```

---

## Future Enhancements

### Planned Features

- [ ] **Async Support**: Real-time trading with asyncio
- [ ] **Broker Integration**: Interactive Brokers, Alpaca, TD Ameritrade APIs
- [ ] **Backtesting Framework**: Historical data replay and strategy testing
- [ ] **Performance Metrics**: Sharpe ratio, alpha, beta, drawdown analysis
- [ ] **Database Persistence**: SQLite/PostgreSQL for trade history
- [ ] **Order Book Management**: Queue management for pending orders
- [ ] **Event-Driven Architecture**: Real-time market data processing
- [ ] **Risk Metrics**: VaR, exposure analysis, correlation matrices
- [ ] **Tax Lot Tracking**: FIFO, LIFO, specific identification
- [ ] **Commission Models**: Configurable commission structures
- [ ] **Slippage Simulation**: Realistic execution modeling
- [ ] **Web Dashboard**: Real-time monitoring and control
- [ ] **Alert System**: Notifications for trades, rule violations, errors
- [ ] **Strategy Templates**: Pre-built strategies (momentum, mean reversion, etc.)
- [ ] **Paper Trading**: Simulated trading with live data

### Contributing

Contributions welcome! Areas for improvement:
- Type hints throughout codebase
- Unit tests (pytest)
- Integration tests
- Performance optimization
- Documentation improvements
- Example strategies

---

## Notes

- **Trade Execution**: Currently simulated (instant fill)
- **Data Provider**: Optional, but required for live price fetching
- **Currency**: All monetary values in USD
- **Accounting**: Uses average cost basis method
- **Timestamps**: All in UTC
- **Python Version**: Requires Python 3.7+

---

## License

This project is provided as-is for educational and commercial use.

---

## Support

For questions, issues, or feature requests:
1. Check the comprehensive example: `example_comprehensive.py`
2. Review this README
3. Examine the module source code (well-documented)

---

**Built with ❤️ for algorithmic traders and quantitative analysts**

---

*Last Updated: October 2025*

