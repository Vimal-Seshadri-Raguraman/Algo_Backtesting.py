"""
###############################################################################
# Ledger - Records and tracks all trades at each hierarchy level
###############################################################################
"""

from datetime import datetime
from typing import List, Dict, Optional, Set
from collections import defaultdict


class Ledger:
    ###############################################################################
    # Ledger - Comprehensive trade recording and reporting system
    # Each level (Account, Fund, Portfolio, Strategy) maintains its own ledger
    ###############################################################################
    
    def __init__(self, owner_name: str, owner_type: str):
        """
        Initialize a Ledger
        
        Args:
            owner_name: Name of the entity that owns this ledger
            owner_type: Type of entity (Account, Fund, Portfolio, Strategy)
        """
        self.owner_name = owner_name
        self.owner_type = owner_type
        self.trades: List = []  # All trades in chronological order
        self.created_at = datetime.now()
        
        # Index for fast lookups
        self._trades_by_symbol: Dict[str, List] = defaultdict(list)
        self._trades_by_status: Dict[str, List] = defaultdict(list)
        self._trades_by_direction: Dict[str, List] = defaultdict(list)
    
    def record_trade(self, trade) -> None:
        """
        Record a trade in the ledger
        
        Args:
            trade: Trade object to record
        """
        self.trades.append(trade)
        
        # Update indices for fast lookups
        self._trades_by_symbol[trade.symbol].append(trade)
        self._trades_by_status[trade.status].append(trade)
        self._trades_by_direction[trade.direction].append(trade)
    
    def get_all_trades(self) -> List:
        """Get all trades in chronological order"""
        return self.trades.copy()
    
    def get_trades_by_symbol(self, symbol: str) -> List:
        """
        Get all trades for a specific symbol
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            List of trades for the symbol
        """
        return self._trades_by_symbol.get(symbol, []).copy()
    
    def get_trades_by_status(self, status: str) -> List:
        """
        Get all trades with a specific status
        
        Args:
            status: Trade status (FILLED, CANCELLED, etc.)
            
        Returns:
            List of trades with that status
        """
        return self._trades_by_status.get(status, []).copy()
    
    def get_trades_by_direction(self, direction: str) -> List:
        """
        Get all trades with a specific direction
        
        Args:
            direction: Trade direction (BUY, SELL, etc.)
            
        Returns:
            List of trades with that direction
        """
        return self._trades_by_direction.get(direction, []).copy()
    
    def get_trades_by_date_range(self, start_date: datetime, end_date: datetime) -> List:
        """
        Get trades within a date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of trades within the date range
        """
        return [
            trade for trade in self.trades
            if start_date <= trade.created_at <= end_date
        ]
    
    def get_filled_trades(self) -> List:
        """Get all filled trades"""
        return self.get_trades_by_status("FILLED")
    
    def get_pending_trades(self) -> List:
        """Get all pending/submitted trades"""
        pending = self.get_trades_by_status("PENDING")
        submitted = self.get_trades_by_status("SUBMITTED")
        return pending + submitted
    
    def get_symbols_traded(self) -> Set[str]:
        """Get set of all symbols that have been traded"""
        return set(self._trades_by_symbol.keys())
    
    ###########################################################################
    # Statistics and Metrics
    ###########################################################################
    
    def get_trade_count(self) -> int:
        """Get total number of trades"""
        return len(self.trades)
    
    def get_filled_trade_count(self) -> int:
        """Get number of filled trades"""
        return len(self.get_filled_trades())
    
    def get_total_volume(self, symbol: Optional[str] = None) -> float:
        """
        Calculate total trading volume
        
        Args:
            symbol: Optional symbol to filter by
            
        Returns:
            Total dollar volume traded
        """
        trades = self.get_trades_by_symbol(symbol) if symbol else self.get_filled_trades()
        return sum(
            trade.filled_quantity * trade.avg_fill_price
            for trade in trades
            if trade.status == "FILLED"
        )
    
    def get_total_commission(self) -> float:
        """Calculate total commission paid"""
        return sum(trade.commission for trade in self.get_filled_trades())
    
    def get_buy_vs_sell_ratio(self) -> Dict[str, int]:
        """
        Get counts of buy vs sell trades
        
        Returns:
            Dictionary with buy/sell counts
        """
        from .trade import Trade
        
        buys = len(self.get_trades_by_direction(Trade.BUY))
        sells = len(self.get_trades_by_direction(Trade.SELL))
        shorts = len(self.get_trades_by_direction(Trade.SELL_SHORT))
        covers = len(self.get_trades_by_direction(Trade.BUY_TO_COVER))
        
        return {
            'BUY': buys,
            'SELL': sells,
            'SELL_SHORT': shorts,
            'BUY_TO_COVER': covers,
            'TOTAL_LONG': buys + sells,
            'TOTAL_SHORT': shorts + covers
        }
    
    def get_activity_by_date(self) -> Dict[str, int]:
        """
        Get trading activity grouped by date
        
        Returns:
            Dictionary with date -> trade count
        """
        activity = defaultdict(int)
        for trade in self.trades:
            date_key = trade.created_at.strftime('%Y-%m-%d')
            activity[date_key] += 1
        return dict(activity)
    
    ###########################################################################
    # Reporting
    ###########################################################################
    
    def summary(self, show_recent: int = 0) -> None:
        """
        Display comprehensive ledger summary
        
        Args:
            show_recent: Number of recent trades to display (0 = none)
        """
        print("=" * 80)
        print(f"📒 LEDGER SUMMARY: {self.owner_name} ({self.owner_type})")
        print("=" * 80)
        print(f"Total Trades:      {self.get_trade_count():>15}")
        print(f"Filled Trades:     {self.get_filled_trade_count():>15}")
        print(f"Pending Trades:    {len(self.get_pending_trades()):>15}")
        print(f"Symbols Traded:    {len(self.get_symbols_traded()):>15}")
        print(f"Total Volume:      ${self.get_total_volume():>14,.2f}")
        print(f"Total Commission:  ${self.get_total_commission():>14,.2f}")
        print()
        
        # Buy vs Sell breakdown
        ratios = self.get_buy_vs_sell_ratio()
        print("Trade Direction Breakdown:")
        print("-" * 80)
        print(f"  BUY trades:        {ratios['BUY']:>15}")
        print(f"  SELL trades:       {ratios['SELL']:>15}")
        print(f"  SELL_SHORT trades: {ratios['SELL_SHORT']:>15}")
        print(f"  BUY_TO_COVER:      {ratios['BUY_TO_COVER']:>15}")
        print()
        
        # Symbols traded
        if self.get_symbols_traded():
            print("Symbols Traded:")
            print("-" * 80)
            for symbol in sorted(self.get_symbols_traded()):
                count = len(self.get_trades_by_symbol(symbol))
                volume = self.get_total_volume(symbol)
                print(f"  {symbol:<10} Trades: {count:>3}  Volume: ${volume:>12,.2f}")
        
        print("=" * 80)
        
        # Show recent trades if requested
        if show_recent > 0 and self.trades:
            print()
            print(f"Recent Trades (Last {min(show_recent, len(self.trades))}):")
            print("-" * 80)
            for trade in self.trades[-show_recent:]:
                timestamp = trade.created_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"  [{timestamp}] {trade}")
            print("=" * 80)
    
    def export_to_dict(self) -> Dict:
        """
        Export ledger data to dictionary format
        
        Returns:
            Dictionary with ledger data
        """
        return {
            'owner_name': self.owner_name,
            'owner_type': self.owner_type,
            'created_at': self.created_at.isoformat(),
            'total_trades': self.get_trade_count(),
            'filled_trades': self.get_filled_trade_count(),
            'symbols_traded': list(self.get_symbols_traded()),
            'total_volume': self.get_total_volume(),
            'total_commission': self.get_total_commission(),
            'trade_directions': self.get_buy_vs_sell_ratio(),
            'activity_by_date': self.get_activity_by_date()
        }
    
    def __repr__(self):
        return (f"Ledger({self.owner_type}: {self.owner_name}, "
                f"Trades: {self.get_trade_count()}, "
                f"Symbols: {len(self.get_symbols_traded())})")
    
    def __len__(self):
        """Support len() function"""
        return len(self.trades)

