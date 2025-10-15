"""
###############################################################################
# Trade Management System (TMS) - Trade execution and position management
###############################################################################
"""

from datetime import datetime
import uuid
from .trade import Trade
from .position import Position


###############################################################################
# TMS Event Log (Internal, Optional)
###############################################################################

class TMSEventLog:
    """
    Internal debugging/audit trail (NOT a user-facing ledger)
    Can be disabled in production for performance
    """
    
    def __init__(self, enabled=False):
        self.enabled = enabled
        self._events = []
    
    def log(self, event_type, details):
        """Log an event if logging is enabled"""
        if not self.enabled:
            return
        
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            **details
        }
        self._events.append(event)
    
    def get_events(self, event_type=None):
        """Get events (for internal debugging only)"""
        if event_type:
            return [e for e in self._events if e['type'] == event_type]
        return self._events
    
    def clear(self):
        """Clear event log"""
        self._events = []


###############################################################################
# Trade Management System (TMS)
###############################################################################

class TradeManagementSystem:
    """
    ###############################################################################
    # Trade Management System - Trade execution and position management
    ###############################################################################
    
    Handles:
    - Trade execution (simulated for now)
    - Position tracking and updates
    - P&L calculation
    - Balance updates
    - Recording trades in hierarchy ledgers (single source of truth)
    """
    
    def __init__(self, enable_event_log=False):
        """
        Initialize TMS
        
        Args:
            enable_event_log: If True, enables internal event logging for debugging
        """
        self.positions = {}  # {(strategy_id, symbol): Position}
        self._event_log = TMSEventLog(enabled=enable_event_log)
    
    def execute_trade(self, instruction):
        """
        Execute a trade instruction and record in hierarchy ledgers
        
        Args:
            instruction: TradeInstruction from OMS
        
        Returns:
            Trade object
        """
        # Create trade object
        trade = Trade(
            symbol=instruction.symbol,
            direction=instruction.direction,
            quantity=instruction.quantity,
            trade_type=instruction.order_type,
            strategy=instruction.strategy,
            price=instruction.price,
            stop_price=instruction.kwargs.get('stop_price'),
            trade_date=instruction.trade_date
        )
        
        # Simulate immediate fill (in production, this would be async via broker)
        trade.trade_id = str(uuid.uuid4())
        trade.status = Trade.SUBMITTED
        trade.submitted_at = instruction.trade_date if instruction.trade_date else datetime.now()
        
        trade.status = Trade.FILLED
        trade.filled_quantity = instruction.quantity
        trade.avg_fill_price = instruction.price
        trade.filled_at = instruction.trade_date if instruction.trade_date else datetime.now()
        
        # Log execution
        self._event_log.log('TRADE_EXECUTED', {
            'trade_id': trade.trade_id,
            'symbol': trade.symbol,
            'direction': trade.direction,
            'quantity': trade.quantity,
            'price': trade.avg_fill_price,
            'strategy': instruction.strategy.strategy_name
        })
        
        # Update position
        old_position = self.get_position(instruction.strategy, instruction.symbol)
        self._update_position(instruction.strategy, trade)
        new_position = self.get_position(instruction.strategy, instruction.symbol)
        
        # Log position update
        self._event_log.log('POSITION_UPDATED', {
            'trade_id': trade.trade_id,
            'symbol': instruction.symbol,
            'strategy': instruction.strategy.strategy_name,
            'old_quantity': old_position.quantity if old_position else 0,
            'new_quantity': new_position.quantity,
            'position_status': 'CLOSED' if new_position.is_closed else 
                             'LONG' if new_position.is_long else 'SHORT'
        })
        
        # Update balances (for display purposes)
        # Note: Actual capital is managed at portfolio level
        self._update_display_balance(instruction.strategy, trade)
        
        # ✅ RECORD IN HIERARCHY LEDGERS (Single source of truth)
        self._record_in_hierarchy_ledgers(instruction.strategy, trade)
        
        return trade
    
    def get_position(self, strategy, symbol):
        """
        Get position for a strategy and symbol
        
        Args:
            strategy: Strategy object
            symbol: Ticker symbol
        
        Returns:
            Position object or None
        """
        key = (strategy.strategy_id, symbol)
        return self.positions.get(key)
    
    def get_portfolio_value(self, strategy):
        """
        Get portfolio value for a strategy (for position size calculations)
        
        Args:
            strategy: Strategy object
        
        Returns:
            float: Portfolio value
        """
        if strategy.portfolio:
            return strategy.portfolio.portfolio_balance
        return strategy.strategy_balance
    
    def _update_position(self, strategy, trade):
        """
        Update or create position from filled trade
        
        Args:
            strategy: Strategy object
            trade: Trade object
        """
        key = (strategy.strategy_id, trade.symbol)
        
        # Create position if doesn't exist
        if key not in self.positions:
            self.positions[key] = Position(trade.symbol, strategy)
        
        # Update position with trade
        position = self.positions[key]
        position.update_from_trade(trade)
        
        self._event_log.log('POSITION_STATE', {
            'symbol': trade.symbol,
            'strategy': strategy.strategy_name,
            'quantity': position.quantity,
            'avg_price': position.avg_entry_price,
            'realized_pnl': position.realized_pnl
        })
    
    def _update_display_balance(self, strategy, trade):
        """
        Update strategy balance for display purposes
        This is a simplified calculation - real capital management happens at portfolio level
        
        Args:
            strategy: Strategy object
            trade: Trade object
        """
        # For BUY/BUY_TO_COVER: reduce cash
        if trade.direction in {Trade.BUY, Trade.BUY_TO_COVER}:
            cost = trade.filled_quantity * trade.avg_fill_price
            # Don't update actual balance here - this is managed by hierarchy
            
        # For SELL/SELL_SHORT: increase cash
        elif trade.direction in {Trade.SELL, Trade.SELL_SHORT}:
            proceeds = trade.filled_quantity * trade.avg_fill_price
            # Don't update actual balance here - this is managed by hierarchy
        
        self._event_log.log('BALANCE_IMPACT', {
            'trade_id': trade.trade_id,
            'direction': trade.direction,
            'value': trade.filled_quantity * trade.avg_fill_price,
            'strategy': strategy.strategy_name
        })
    
    def _record_in_hierarchy_ledgers(self, strategy, trade):
        """
        Record trade in hierarchy ledgers (cascade upward)
        This is the ONLY place trades are permanently recorded
        
        Args:
            strategy: Strategy object
            trade: Trade object
        """
        ledgers_updated = []
        
        # Strategy ledger (always)
        strategy.ledger.record_trade(trade)
        ledgers_updated.append('Strategy')
        
        # Portfolio ledger (if linked)
        if strategy.portfolio:
            strategy.portfolio.ledger.record_trade(trade)
            ledgers_updated.append('Portfolio')
            
            # Fund ledger (if linked)
            if strategy.portfolio.fund:
                strategy.portfolio.fund.ledger.record_trade(trade)
                ledgers_updated.append('Fund')
                
                # Account ledger (if linked)
                if strategy.portfolio.fund.trade_account:
                    strategy.portfolio.fund.trade_account.ledger.record_trade(trade)
                    ledgers_updated.append('Account')
        
        self._event_log.log('LEDGER_PROPAGATION', {
            'trade_id': trade.trade_id,
            'symbol': trade.symbol,
            'ledgers': ledgers_updated
        })
        
        # Also store trade in strategy's trades list (for backward compatibility)
        strategy.trades.append(trade)

