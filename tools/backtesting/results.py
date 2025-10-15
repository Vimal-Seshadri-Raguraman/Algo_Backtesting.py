"""
###############################################################################
# BacktestResults - Stores and analyzes backtest results
###############################################################################
"""

import pandas as pd
from tools import PerformanceMetrics


class BacktestResults:
    ###############################################################################
    # BacktestResults - Comprehensive backtest results with performance metrics
    ###############################################################################
    
    def __init__(self, strategy, equity_curve, dates, daily_returns, 
                 initial_capital, final_capital, historical_data,
                 commission_pct=0.0, slippage_pct=0.0):
        """
        Initialize BacktestResults
        
        Args:
            strategy: Strategy instance used in backtest
            equity_curve: List of equity values over time
            dates: List of dates corresponding to equity curve
            daily_returns: List of daily returns
            initial_capital: Starting capital
            final_capital: Ending capital
            historical_data: Original price DataFrame
            commission_pct: Commission percentage used
            slippage_pct: Slippage percentage used
        """
        self.strategy = strategy
        self.equity_curve = equity_curve
        self.dates = dates
        self.daily_returns = daily_returns
        self.initial_capital = initial_capital
        self.final_capital = final_capital
        self.historical_data = historical_data
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
        # Create equity DataFrame
        self.equity_df = pd.DataFrame({
            'equity': equity_curve,
            'date': dates
        }).set_index('date')
        
        # Calculate returns DataFrame
        self.equity_df['returns'] = self.equity_df['equity'].pct_change()
        self.equity_df['cumulative_returns'] = (1 + self.equity_df['returns']).cumprod() - 1
        
        # Create performance metrics
        current_prices = self.historical_data.iloc[-1].to_dict()
        self.metrics = PerformanceMetrics(
            owner_name=strategy.strategy_name,
            owner_type="Backtest",
            ledger=strategy.ledger,
            initial_balance=initial_capital,
            current_balance=final_capital,
            current_prices=current_prices
        )
    
    ###########################################################################
    # Performance Metrics
    ###########################################################################
    
    def total_return(self):
        """Total return in dollars"""
        return self.final_capital - self.initial_capital
    
    def total_return_pct(self):
        """Total return as percentage"""
        return (self.total_return() / self.initial_capital) * 100
    
    def annualized_return(self):
        """Annualized return (CAGR)"""
        return self.metrics.annualized_return()
    
    def sharpe_ratio(self, risk_free_rate=0.02):
        """Sharpe ratio"""
        return self.metrics.sharpe_ratio(risk_free_rate)
    
    def sortino_ratio(self, risk_free_rate=0.02):
        """Sortino ratio"""
        return self.metrics.sortino_ratio(risk_free_rate)
    
    def max_drawdown(self):
        """Maximum drawdown percentage"""
        return self.metrics.max_drawdown()
    
    def volatility(self):
        """Annualized volatility"""
        return self.metrics.volatility()
    
    def win_rate(self):
        """Win rate percentage"""
        return self.metrics.win_rate()
    
    def profit_factor(self):
        """Profit factor (gross profit / gross loss)"""
        return self.metrics.profit_factor()
    
    def total_trades(self):
        """Total number of trades"""
        return len(self.strategy.trades)
    
    ###########################################################################
    # Backtest-Specific Metrics
    ###########################################################################
    
    def trading_days(self):
        """Number of trading days in backtest"""
        return len(self.historical_data)
    
    def first_trade_date(self):
        """Date of first trade"""
        if self.strategy.trades:
            return self.strategy.trades[0].created_at
        return None
    
    def last_trade_date(self):
        """Date of last trade"""
        if self.strategy.trades:
            return self.strategy.trades[-1].filled_at or self.strategy.trades[-1].created_at
        return None
    
    def average_trades_per_day(self):
        """Average trades per trading day"""
        if self.trading_days() == 0:
            return 0.0
        return self.total_trades() / self.trading_days()
    
    def total_commission_paid(self):
        """Total commission paid during backtest"""
        return sum(trade.commission for trade in self.strategy.trades)
    
    ###########################################################################
    # Display & Export Methods
    ###########################################################################
    
    def summary(self):
        """Display comprehensive backtest summary"""
        print("=" * 80)
        print(f"📊 BACKTEST RESULTS: {self.strategy.strategy_name}")
        print("=" * 80)
        
        print(f"\n📅 Backtest Period:")
        print("-" * 80)
        print(f"  Start Date:             {self.dates[0].date()}")
        print(f"  End Date:               {self.dates[-1].date()}")
        print(f"  Trading Days:           {self.trading_days():>15}")
        
        print(f"\n💰 Capital:")
        print("-" * 80)
        print(f"  Initial Capital:        ${self.initial_capital:>15,.2f}")
        print(f"  Final Capital:          ${self.final_capital:>15,.2f}")
        print(f"  Total Return:           ${self.total_return():>15,.2f}")
        print(f"  Total Return %:         {self.total_return_pct():>15.2f}%")
        print(f"  Annualized Return:      {self.annualized_return():>15.2f}%")
        
        print(f"\n📈 Trade Statistics:")
        print("-" * 80)
        print(f"  Total Trades:           {self.total_trades():>15}")
        winners, _ = self.metrics.winning_trades()
        losers, _ = self.metrics.losing_trades()
        print(f"  Winning Trades:         {winners:>15}")
        print(f"  Losing Trades:          {losers:>15}")
        print(f"  Win Rate:               {self.win_rate():>15.2f}%")
        print(f"  Profit Factor:          {self.profit_factor():>15.2f}")
        print(f"  Avg Trades/Day:         {self.average_trades_per_day():>15.2f}")
        
        print(f"\n💸 Costs:")
        print("-" * 80)
        print(f"  Commission Rate:        {self.commission_pct*100:>15.3f}%")
        print(f"  Slippage Rate:          {self.slippage_pct*100:>15.3f}%")
        print(f"  Total Commission:       ${self.total_commission_paid():>15,.2f}")
        
        print(f"\n⚠️  Risk Metrics:")
        print("-" * 80)
        print(f"  Max Drawdown:           {self.max_drawdown():>15.2f}%")
        print(f"  Volatility (Ann.):      {self.volatility():>15.2f}%")
        
        print(f"\n🎯 Risk-Adjusted Returns:")
        print("-" * 80)
        print(f"  Sharpe Ratio:           {self.sharpe_ratio():>15.2f}")
        print(f"  Sortino Ratio:          {self.sortino_ratio():>15.2f}")
        print(f"  Calmar Ratio:           {self.metrics.calmar_ratio():>15.2f}")
        
        print("=" * 80)
    
    def get_equity_curve(self):
        """
        Get equity curve as pandas DataFrame
        
        Returns:
            DataFrame with columns: equity, returns, cumulative_returns
        """
        return self.equity_df
    
    def get_trades_dataframe(self):
        """
        Get all trades as pandas DataFrame
        
        Returns:
            DataFrame with trade details
        """
        trades_data = []
        for trade in self.strategy.trades:
            trades_data.append({
                'date': trade.filled_at or trade.created_at,
                'symbol': trade.symbol,
                'direction': trade.direction,
                'quantity': trade.filled_quantity,
                'price': trade.avg_fill_price,
                'value': trade.filled_quantity * trade.avg_fill_price,
                'commission': trade.commission,
                'realized_pnl': trade.realized_pnl if hasattr(trade, 'realized_pnl') else 0.0,
                'trade_type': trade.trade_type,
                'status': trade.status
            })
        
        return pd.DataFrame(trades_data)
    
    def to_dict(self):
        """
        Export results as dictionary
        
        Returns:
            dict: Comprehensive results dictionary
        """
        return {
            'strategy_name': self.strategy.strategy_name,
            'start_date': str(self.dates[0].date()),
            'end_date': str(self.dates[-1].date()),
            'trading_days': self.trading_days(),
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return(),
            'total_return_pct': self.total_return_pct(),
            'annualized_return': self.annualized_return(),
            'total_trades': self.total_trades(),
            'win_rate': self.win_rate(),
            'profit_factor': self.profit_factor(),
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'max_drawdown': self.max_drawdown(),
            'volatility': self.volatility(),
            'commission_pct': self.commission_pct,
            'slippage_pct': self.slippage_pct,
            'total_commission': self.total_commission_paid()
        }
    
    def plot_equity_curve(self):
        """
        Plot equity curve (requires matplotlib)
        """
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(12, 6))
            plt.plot(self.equity_df.index, self.equity_df['equity'], linewidth=2)
            plt.title(f'Equity Curve - {self.strategy.strategy_name}', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Equity ($)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("⚠️  matplotlib not installed - cannot plot")
            print("   Install with: pip install matplotlib")
    
    def __repr__(self):
        return (f"BacktestResults({self.strategy.strategy_name}, "
                f"Return: {self.total_return_pct():.2f}%, "
                f"Sharpe: {self.sharpe_ratio():.2f}, "
                f"Trades: {self.total_trades()})")


