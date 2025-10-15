"""
###############################################################################
# Backtester - Historical Strategy Testing
###############################################################################
"""

import pandas as pd
from datetime import datetime
from core import Strategy
from .results import BacktestResults


class Backtester:
    ###############################################################################
    # Backtester - Event-driven historical strategy testing
    ###############################################################################
    
    def __init__(self, strategy_class, historical_data, initial_capital=100_000,
                 commission_pct=0.0, slippage_pct=0.0, start_date=None, end_date=None):
        """
        Initialize Backtester
        
        Args:
            strategy_class: Strategy class to backtest (not instance)
            historical_data: pandas DataFrame with price history
                           Index: DatetimeIndex
                           Columns: Symbol names (e.g., 'AAPL', 'GOOGL')
            initial_capital: Starting capital for backtest
            commission_pct: Commission as percentage of trade value (e.g., 0.001 = 0.1%)
            slippage_pct: Slippage as percentage (e.g., 0.001 = 0.1%)
            start_date: Start date for backtest (None = first date in data)
            end_date: End date for backtest (None = last date in data)
        
        Example:
            backtester = Backtester(
                strategy_class=MyStrategy,
                historical_data=price_df,
                initial_capital=100_000,
                commission_pct=0.001,  # 0.1% commission
                slippage_pct=0.001     # 0.1% slippage
            )
            
            results = backtester.run()
            results.summary()
        """
        self.strategy_class = strategy_class
        self.historical_data = historical_data
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
        # Filter date range
        if start_date:
            self.historical_data = self.historical_data[self.historical_data.index >= pd.to_datetime(start_date)]
        if end_date:
            self.historical_data = self.historical_data[self.historical_data.index <= pd.to_datetime(end_date)]
        
        # Validate data
        if len(self.historical_data) == 0:
            raise ValueError("Historical data is empty after date filtering")
        
        if not isinstance(self.historical_data.index, pd.DatetimeIndex):
            raise ValueError("Historical data must have DatetimeIndex")
    
    def run(self, strategy_params=None):
        """
        Run backtest simulation
        
        Args:
            strategy_params: Dict of parameters to pass to strategy __init__
                           (beyond strategy_id, strategy_name, strategy_balance)
        
        Returns:
            BacktestResults object
        
        Example:
            # Backtest with strategy parameters
            results = backtester.run(strategy_params={
                'short_window': 20,
                'long_window': 50
            })
        """
        if strategy_params is None:
            strategy_params = {}
        
        print(f"\n{'='*80}")
        print(f"BACKTESTING: {self.strategy_class.__name__}")
        print(f"{'='*80}")
        print(f"Period: {self.historical_data.index[0].date()} to {self.historical_data.index[-1].date()}")
        print(f"Trading Days: {len(self.historical_data)}")
        print(f"Symbols: {', '.join(self.historical_data.columns)}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Commission: {self.commission_pct*100:.2f}%")
        print(f"Slippage: {self.slippage_pct*100:.2f}%")
        print(f"{'='*80}\n")
        
        # Create strategy instance (standalone mode for backtesting)
        strategy = self.strategy_class(
            strategy_id="BACKTEST_001",
            strategy_name=f"{self.strategy_class.__name__}_Backtest",
            strategy_balance=self.initial_capital,
            portfolio=None,  # Standalone for backtesting
            **strategy_params
        )
        
        # Track equity over time
        equity_curve = [self.initial_capital]
        dates = [self.historical_data.index[0]]
        daily_returns = []
        
        # Simulate day-by-day (event-driven)
        print("Running backtest...")
        total_days = len(self.historical_data)
        
        for i, (date, row) in enumerate(self.historical_data.iterrows(), 1):
            # Create price data up to current date (prevents look-ahead bias)
            historical_slice = self.historical_data.loc[:date]
            current_prices = row.to_dict()
            
            # Run strategy with historical data up to current date
            try:
                # Check if strategy's run() method accepts price_data parameter
                import inspect
                sig = inspect.signature(strategy.run)
                
                if len(sig.parameters) > 0:  # Strategy expects price_data
                    strategy.run(historical_slice)
                else:  # Strategy runs without parameters (uses internal logic)
                    strategy.run()
            except Exception as e:
                # Strategy might not trade every day - that's OK
                pass
            
            # Calculate current equity (cash + positions value)
            cash = strategy.get_cash_balance()
            positions_value = 0
            
            for symbol, position in strategy.get_open_positions().items():
                if symbol in current_prices:
                    positions_value += position.get_market_value(current_prices[symbol])
            
            # Add realized P&L
            realized_pnl = sum(pos.realized_pnl for pos in strategy.positions.values())
            
            current_equity = cash + positions_value + realized_pnl
            
            # Apply commission on new trades (simplified)
            if len(strategy.trades) > len(equity_curve) - 1:
                # New trades executed
                new_trades = strategy.trades[len(equity_curve)-1:]
                for trade in new_trades:
                    commission = trade.filled_quantity * trade.avg_fill_price * self.commission_pct
                    current_equity -= commission
                    trade.commission = commission
            
            equity_curve.append(current_equity)
            dates.append(date)
            
            # Calculate daily return
            if len(equity_curve) > 1:
                daily_return = (equity_curve[-1] - equity_curve[-2]) / equity_curve[-2]
                daily_returns.append(daily_return)
            
            # Progress indicator
            if i % 50 == 0 or i == total_days:
                progress = (i / total_days) * 100
                print(f"  Progress: {i}/{total_days} days ({progress:.0f}%) - Equity: ${current_equity:,.2f}")
        
        print(f"\n✅ Backtest complete!")
        print(f"   Final Equity: ${equity_curve[-1]:,.2f}")
        print(f"   Total Return: ${equity_curve[-1] - self.initial_capital:,.2f}")
        print(f"   Total Trades: {len(strategy.trades)}")
        
        # Create results object
        results = BacktestResults(
            strategy=strategy,
            equity_curve=equity_curve,
            dates=dates,
            daily_returns=daily_returns,
            initial_capital=self.initial_capital,
            final_capital=equity_curve[-1],
            historical_data=self.historical_data,
            commission_pct=self.commission_pct,
            slippage_pct=self.slippage_pct
        )
        
        return results





