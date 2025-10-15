"""
###############################################################################
# Performance Metrics Calculator - Calculates trading performance metrics
###############################################################################
"""

from datetime import datetime, timedelta
import math
from core.trade import Trade


class PerformanceMetrics:
    ###############################################################################
    # Performance Metrics - Calculates comprehensive trading performance metrics
    # Works at any level: Strategy, Portfolio, Fund, or Account
    ###############################################################################
    
    def __init__(self, owner_name, owner_type, ledger, initial_balance, current_balance=None, current_prices=None):
        """
        Initialize Performance Metrics Calculator
        
        Args:
            owner_name: Name of the owner (strategy, portfolio, etc.)
            owner_type: Type of owner ("Strategy", "Portfolio", "Fund", "TradeAccount")
            ledger: Ledger object containing all trades
            initial_balance: Starting capital
            current_balance: Current capital (if None, uses initial_balance)
            current_prices: Dict of {symbol: price} for unrealized P&L calculations
        """
        self.owner_name = owner_name
        self.owner_type = owner_type
        self.ledger = ledger
        self.initial_balance = initial_balance
        self.current_balance = current_balance if current_balance is not None else initial_balance
        self.current_prices = current_prices if current_prices is not None else {}
        
        # Get all filled trades
        self.trades = ledger.get_filled_trades()
        
    ###########################################################################
    # Return Metrics
    ###########################################################################
    
    def total_return(self):
        """
        Calculate total return (dollar amount)
        
        Returns:
            float: Total profit/loss in dollars
        """
        return self.current_balance - self.initial_balance
    
    def total_return_pct(self):
        """
        Calculate total return percentage
        
        Returns:
            float: Return as percentage
        """
        if self.initial_balance == 0:
            return 0.0
        return (self.total_return() / self.initial_balance) * 100
    
    def annualized_return(self):
        """
        Calculate annualized return percentage (CAGR)
        
        Returns:
            float: Annualized return percentage
        """
        if not self.trades:
            return 0.0
        
        # Calculate time period in years
        first_trade = min(self.trades, key=lambda t: t.created_at)
        last_trade = max(self.trades, key=lambda t: t.filled_at if t.filled_at else t.created_at)
        
        time_delta = last_trade.filled_at - first_trade.created_at
        years = time_delta.days / 365.25
        
        if years < 0.01:  # Less than ~4 days, use simple return
            return self.total_return_pct()
        
        # CAGR formula: (Ending Value / Beginning Value)^(1/years) - 1
        if self.initial_balance > 0 and self.current_balance > 0:
            cagr = (math.pow(self.current_balance / self.initial_balance, 1/years) - 1) * 100
            return cagr
        
        return 0.0
    
    ###########################################################################
    # Trade Statistics
    ###########################################################################
    
    def total_trades(self):
        """Total number of filled trades"""
        return len(self.trades)
    
    def winning_trades(self):
        """
        Calculate number and list of winning trades (closing trades with profit)
        
        Returns:
            tuple: (count, list of winning trades)
        """
        winners = []
        for trade in self.trades:
            # Only count closing trades (those that realize P&L)
            if hasattr(trade, 'is_opening') and not trade.is_opening:
                if hasattr(trade, 'realized_pnl') and trade.realized_pnl > 0:
                    winners.append(trade)
        
        return len(winners), winners
    
    def losing_trades(self):
        """
        Calculate number and list of losing trades (closing trades with loss)
        
        Returns:
            tuple: (count, list of losing trades)
        """
        losers = []
        for trade in self.trades:
            # Only count closing trades (those that realize P&L)
            if hasattr(trade, 'is_opening') and not trade.is_opening:
                if hasattr(trade, 'realized_pnl') and trade.realized_pnl < 0:
                    losers.append(trade)
        
        return len(losers), losers
    
    def win_rate(self):
        """
        Calculate win rate percentage (based on closing trades only)
        
        Returns:
            float: Win rate as percentage
        """
        winners_count, _ = self.winning_trades()
        losers_count, _ = self.losing_trades()
        total_closing_trades = winners_count + losers_count
        
        if total_closing_trades == 0:
            return 0.0
        
        return (winners_count / total_closing_trades) * 100
    
    def average_trade_pnl(self):
        """
        Calculate average P&L per trade
        
        Returns:
            float: Average profit/loss per trade
        """
        total = self.total_trades()
        if total == 0:
            return 0.0
        
        return self.total_return() / total
    
    def largest_win(self):
        """
        Calculate largest winning trade
        
        Returns:
            float: Largest win amount
        """
        winners_count, winners = self.winning_trades()
        if winners_count == 0:
            return 0.0
        
        max_win = max(trade.realized_pnl for trade in winners)
        return max_win
    
    def largest_loss(self):
        """
        Calculate largest losing trade
        
        Returns:
            float: Largest loss amount (negative)
        """
        losers_count, losers = self.losing_trades()
        if losers_count == 0:
            return 0.0
        
        max_loss = min(trade.realized_pnl for trade in losers)
        return max_loss
    
    def profit_factor(self):
        """
        Calculate profit factor (gross profits / gross losses)
        
        Returns:
            float: Profit factor ratio (>1 is profitable, <1 is losing)
        """
        winners_count, winners = self.winning_trades()
        losers_count, losers = self.losing_trades()
        
        if winners_count == 0:
            return 0.0
        
        gross_profit = sum(trade.realized_pnl for trade in winners)
        gross_loss = abs(sum(trade.realized_pnl for trade in losers)) if losers_count > 0 else 0.0
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    ###########################################################################
    # Risk Metrics
    ###########################################################################
    
    def max_drawdown(self):
        """
        Calculate maximum drawdown percentage
        
        Returns:
            float: Maximum drawdown as percentage (negative value)
        """
        if not self.trades:
            return 0.0
        
        # Build equity curve
        equity_curve = self._build_equity_curve()
        if not equity_curve:
            return 0.0
        
        # Find maximum drawdown
        peak = equity_curve[0]
        max_dd = 0.0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            
            drawdown = ((equity - peak) / peak) * 100
            if drawdown < max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def max_drawdown_duration(self):
        """
        Calculate maximum drawdown duration in days
        
        Returns:
            int: Maximum number of days in drawdown
        """
        # Simplified implementation
        return 0
    
    def volatility(self):
        """
        Calculate return volatility (standard deviation of returns)
        
        Returns:
            float: Annualized volatility percentage
        """
        if not self.trades or len(self.trades) < 2:
            return 0.0
        
        # Build daily returns
        equity_curve = self._build_equity_curve()
        if len(equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        # Calculate standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)
        
        # Annualize (assuming daily returns)
        annualized_vol = std_dev * math.sqrt(252) * 100
        return annualized_vol
    
    def downside_deviation(self):
        """
        Calculate downside deviation (volatility of negative returns)
        
        Returns:
            float: Annualized downside deviation percentage
        """
        if not self.trades or len(self.trades) < 2:
            return 0.0
        
        equity_curve = self._build_equity_curve()
        if len(equity_curve) < 2:
            return 0.0
        
        # Calculate negative returns only
        negative_returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            if ret < 0:
                negative_returns.append(ret)
        
        if not negative_returns:
            return 0.0
        
        # Calculate standard deviation of negative returns
        mean_return = sum(negative_returns) / len(negative_returns)
        variance = sum((r - mean_return) ** 2 for r in negative_returns) / len(negative_returns)
        std_dev = math.sqrt(variance)
        
        # Annualize
        annualized_dd = std_dev * math.sqrt(252) * 100
        return annualized_dd
    
    ###########################################################################
    # Risk-Adjusted Return Metrics
    ###########################################################################
    
    def sharpe_ratio(self, risk_free_rate=0.02):
        """
        Calculate Sharpe Ratio (risk-adjusted return)
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        
        Returns:
            float: Sharpe ratio
        """
        annual_return = self.annualized_return() / 100  # Convert to decimal
        vol = self.volatility() / 100  # Convert to decimal
        
        if vol == 0:
            return 0.0
        
        sharpe = (annual_return - risk_free_rate) / vol
        return sharpe
    
    def sortino_ratio(self, risk_free_rate=0.02):
        """
        Calculate Sortino Ratio (return vs downside risk)
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
        
        Returns:
            float: Sortino ratio
        """
        annual_return = self.annualized_return() / 100
        downside_dev = self.downside_deviation() / 100
        
        if downside_dev == 0:
            return 0.0
        
        sortino = (annual_return - risk_free_rate) / downside_dev
        return sortino
    
    def calmar_ratio(self):
        """
        Calculate Calmar Ratio (return vs max drawdown)
        
        Returns:
            float: Calmar ratio
        """
        annual_return = self.annualized_return()
        max_dd = abs(self.max_drawdown())
        
        if max_dd == 0:
            return 0.0
        
        calmar = annual_return / max_dd
        return calmar
    
    ###########################################################################
    # Trading Activity Metrics
    ###########################################################################
    
    def total_volume(self):
        """
        Calculate total trading volume
        
        Returns:
            float: Total dollar volume traded
        """
        return self.ledger.get_total_volume()
    
    def average_holding_period(self):
        """
        Calculate average holding period in days
        
        Returns:
            float: Average days per position
        """
        # Simplified - would need position tracking
        return 0.0
    
    def trade_frequency(self):
        """
        Calculate trade frequency (trades per day)
        
        Returns:
            float: Average trades per day
        """
        if not self.trades or len(self.trades) < 2:
            return 0.0
        
        first_trade = min(self.trades, key=lambda t: t.created_at)
        last_trade = max(self.trades, key=lambda t: t.filled_at if t.filled_at else t.created_at)
        
        time_delta = last_trade.filled_at - first_trade.created_at
        days = max(time_delta.days, 1)
        
        return len(self.trades) / days
    
    ###########################################################################
    # Helper Methods
    ###########################################################################
    
    def _build_equity_curve(self):
        """
        Build equity curve from trades
        Tracks portfolio value after each trade execution
        
        Returns:
            list: List of equity values over time
        """
        if not self.trades:
            return [self.initial_balance]
        
        # Sort trades by filled time
        sorted_trades = sorted(self.trades, key=lambda t: t.filled_at if t.filled_at else t.created_at)
        
        # Start with initial balance
        equity_curve = [self.initial_balance]
        
        # Track running P&L and positions value
        cumulative_realized_pnl = 0.0
        
        # Track position states at each point
        position_states = {}  # symbol -> (quantity, avg_price)
        
        for trade in sorted_trades:
            symbol = trade.symbol
            
            # Initialize position state if new symbol
            if symbol not in position_states:
                position_states[symbol] = {'quantity': 0, 'avg_price': 0.0}
            
            pos = position_states[symbol]
            
            # Calculate realized P&L from this trade
            if hasattr(trade, 'realized_pnl'):
                cumulative_realized_pnl += trade.realized_pnl
            
            # Update position state
            if trade.direction in {Trade.BUY, Trade.BUY_TO_COVER}:
                if trade.direction == Trade.BUY_TO_COVER:
                    # Covering short
                    pos['quantity'] += trade.filled_quantity
                else:
                    # Opening/adding long
                    old_value = pos['quantity'] * pos['avg_price']
                    new_value = trade.filled_quantity * trade.avg_fill_price
                    pos['quantity'] += trade.filled_quantity
                    if pos['quantity'] != 0:
                        pos['avg_price'] = (old_value + new_value) / pos['quantity']
            
            elif trade.direction in {Trade.SELL, Trade.SELL_SHORT}:
                if trade.direction == Trade.SELL:
                    # Closing long
                    pos['quantity'] -= trade.filled_quantity
                elif trade.direction == Trade.SELL_SHORT:
                    # Opening short
                    old_value = pos['quantity'] * pos['avg_price']
                    new_value = -trade.filled_quantity * trade.avg_fill_price
                    pos['quantity'] -= trade.filled_quantity
                    if pos['quantity'] != 0:
                        pos['avg_price'] = (old_value + new_value) / pos['quantity']
            
            # Calculate current equity: initial balance + realized P&L + unrealized P&L
            unrealized_pnl = 0.0
            for sym, pos_state in position_states.items():
                if pos_state['quantity'] != 0:
                    # Use current prices if available, otherwise use avg_price (break-even)
                    current_price = self.current_prices.get(sym, pos_state['avg_price'])
                    unrealized_pnl += (current_price - pos_state['avg_price']) * pos_state['quantity']
            
            # Calculate cash used in positions
            cash_in_positions = 0.0
            for sym, pos_state in position_states.items():
                if pos_state['quantity'] != 0:
                    current_price = self.current_prices.get(sym, pos_state['avg_price'])
                    cash_in_positions += abs(pos_state['quantity']) * current_price
            
            # Equity = initial balance + realized P&L + unrealized P&L
            # Or equivalently: cash remaining + value of positions
            current_equity = self.initial_balance + cumulative_realized_pnl + unrealized_pnl
            equity_curve.append(current_equity)
        
        return equity_curve
    
    ###########################################################################
    # Summary and Display Methods
    ###########################################################################
    
    def summary(self):
        """
        Display comprehensive performance summary
        """
        print("=" * 80)
        print(f"📊 PERFORMANCE METRICS: {self.owner_name} ({self.owner_type})")
        print("=" * 80)
        
        print("\n💰 Return Metrics:")
        print("-" * 80)
        print(f"  Initial Balance:        ${self.initial_balance:>15,.2f}")
        print(f"  Current Balance:        ${self.current_balance:>15,.2f}")
        print(f"  Total Return:           ${self.total_return():>15,.2f}")
        print(f"  Total Return %:         {self.total_return_pct():>15.2f}%")
        print(f"  Annualized Return:      {self.annualized_return():>15.2f}%")
        
        print("\n📈 Trade Statistics:")
        print("-" * 80)
        print(f"  Total Trades:           {self.total_trades():>15}")
        winners_count, _ = self.winning_trades()
        losers_count, _ = self.losing_trades()
        print(f"  Winning Trades:         {winners_count:>15}")
        print(f"  Losing Trades:          {losers_count:>15}")
        print(f"  Win Rate:               {self.win_rate():>15.2f}%")
        print(f"  Profit Factor:          {self.profit_factor():>15.2f}")
        print(f"  Avg Trade P&L:          ${self.average_trade_pnl():>15,.2f}")
        print(f"  Largest Win:            ${self.largest_win():>15,.2f}")
        print(f"  Largest Loss:           ${self.largest_loss():>15,.2f}")
        print(f"  Total Volume:           ${self.total_volume():>15,.2f}")
        print(f"  Trade Frequency:        {self.trade_frequency():>15.2f} trades/day")
        
        print("\n⚠️  Risk Metrics:")
        print("-" * 80)
        print(f"  Max Drawdown:           {self.max_drawdown():>15.2f}%")
        print(f"  Volatility (Ann.):      {self.volatility():>15.2f}%")
        print(f"  Downside Deviation:     {self.downside_deviation():>15.2f}%")
        
        print("\n🎯 Risk-Adjusted Returns:")
        print("-" * 80)
        print(f"  Sharpe Ratio:           {self.sharpe_ratio():>15.2f}")
        print(f"  Sortino Ratio:          {self.sortino_ratio():>15.2f}")
        print(f"  Calmar Ratio:           {self.calmar_ratio():>15.2f}")
        
        print("=" * 80)
    
    def to_dict(self):
        """
        Export metrics as dictionary
        
        Returns:
            dict: Dictionary of all metrics
        """
        winners_count, _ = self.winning_trades()
        losers_count, _ = self.losing_trades()
        
        return {
            'owner_name': self.owner_name,
            'owner_type': self.owner_type,
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'total_return': self.total_return(),
            'total_return_pct': self.total_return_pct(),
            'annualized_return': self.annualized_return(),
            'total_trades': self.total_trades(),
            'winning_trades': winners_count,
            'losing_trades': losers_count,
            'win_rate': self.win_rate(),
            'profit_factor': self.profit_factor(),
            'average_trade_pnl': self.average_trade_pnl(),
            'largest_win': self.largest_win(),
            'largest_loss': self.largest_loss(),
            'total_volume': self.total_volume(),
            'max_drawdown': self.max_drawdown(),
            'volatility': self.volatility(),
            'downside_deviation': self.downside_deviation(),
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'calmar_ratio': self.calmar_ratio(),
            'trade_frequency': self.trade_frequency()
        }


