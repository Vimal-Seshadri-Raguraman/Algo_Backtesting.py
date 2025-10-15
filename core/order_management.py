"""
###############################################################################
# Order Management System (OMS) - Order processing and validation
###############################################################################
"""

from datetime import datetime
import uuid
from .trade import Trade
from .exceptions import TradeComplianceError, InsufficientFundsError


###############################################################################
# Supporting Classes
###############################################################################

class Order:
    """Represents a user's order intent (simple BUY or SELL)"""
    
    def __init__(self, strategy, symbol, action, quantity, order_type, price, **kwargs):
        self.order_id = str(uuid.uuid4())
        self.strategy = strategy
        self.symbol = symbol
        self.action = action  # "BUY" or "SELL"
        self.quantity = quantity
        self.order_type = order_type
        self.price = price
        self.status = "PENDING"
        self.trade_instructions = []  # Filled by OMS
        self.executed_trades = []  # Filled after execution
        self.created_at = datetime.now()
        self.kwargs = kwargs
    
    def __repr__(self):
        return (f"Order({self.symbol}, {self.action}, {self.quantity}, "
                f"Status: {self.status})")


class TradeInstruction:
    """Internal instruction from OMS to TMS"""
    
    def __init__(self, strategy, symbol, direction, quantity, order_type, 
                 price, reason, trade_date=None, **kwargs):
        self.strategy = strategy
        self.symbol = symbol
        self.direction = direction  # "BUY", "SELL", "SELL_SHORT", "BUY_TO_COVER"
        self.quantity = quantity
        self.order_type = order_type
        self.price = price
        self.reason = reason
        self.trade_date = trade_date
        self.kwargs = kwargs
    
    def __repr__(self):
        return (f"TradeInstruction({self.direction}, {self.quantity} {self.symbol}, "
                f"{self.reason})")


class AggregatedRules:
    """
    ###########################################################################
    # Aggregated rules from all hierarchy levels
    # More restrictive rules take precedence
    ###############################################################################
    """
    
    def __init__(self):
        # Start with most permissive defaults
        self.allow_short_selling = True
        self.allow_margin = True
        self.allow_options = False
        self.allow_futures = False
        self.max_position_size_pct = 100.0
        self.max_single_trade_pct = 100.0
        self.allowed_symbols = None  # None = all allowed
        self.restricted_symbols = set()
        self.allowed_trade_types = {Trade.MARKET, Trade.LIMIT, Trade.STOP_LOSS, 
                                     Trade.STOP_LIMIT, Trade.TRAILING_STOP}
        self.allowed_directions = {Trade.BUY, Trade.SELL, Trade.SELL_SHORT, Trade.BUY_TO_COVER}
    
    def apply(self, rules):
        """
        Apply rules from a level, taking more restrictive values
        
        Args:
            rules: TradeRules object from Fund or Portfolio
        """
        # Boolean rules: AND logic (both must be True)
        self.allow_short_selling = self.allow_short_selling and rules.allow_short_selling
        self.allow_margin = self.allow_margin and rules.allow_margin
        self.allow_options = self.allow_options and rules.allow_options
        self.allow_futures = self.allow_futures and rules.allow_futures
        
        # Percentage limits: Take minimum (more restrictive)
        self.max_position_size_pct = min(self.max_position_size_pct, rules.max_position_size_pct)
        self.max_single_trade_pct = min(self.max_single_trade_pct, rules.max_single_trade_pct)
        
        # Allowed sets: Intersection (more restrictive)
        self.allowed_trade_types = self.allowed_trade_types.intersection(rules.allowed_trade_types)
        self.allowed_directions = self.allowed_directions.intersection(rules.allowed_directions)
        
        # Symbol restrictions: Union (more restrictive)
        if rules.allowed_symbols is not None:
            if self.allowed_symbols is None:
                self.allowed_symbols = rules.allowed_symbols
            else:
                self.allowed_symbols = self.allowed_symbols.intersection(rules.allowed_symbols)
        
        self.restricted_symbols = self.restricted_symbols.union(rules.restricted_symbols)


class OrderRejected(Exception):
    """Exception raised when order is rejected"""
    pass


###############################################################################
# OMS Event Log (Internal, Optional)
###############################################################################

class OMSEventLog:
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
# Order Management System (OMS)
###############################################################################

class OrderManagementSystem:
    """
    ###############################################################################
    # Order Management System - Centralized order processing and validation
    ###############################################################################
    
    Handles:
    - Order creation and validation
    - Rule aggregation from hierarchy
    - Smart direction determination (BUY/SELL → actual directions)
    - Order splitting when needed
    - Compliance checking
    - Recording rejections in hierarchy ledgers
    """
    
    def __init__(self, tms, enable_event_log=False):
        """
        Initialize OMS
        
        Args:
            tms: TradeManagementSystem instance
            enable_event_log: If True, enables internal event logging for debugging
        """
        self.tms = tms
        self._event_log = OMSEventLog(enabled=enable_event_log)
    
    def create_order(self, strategy, symbol, action, quantity, order_type, price, **kwargs):
        """
        Create and validate an order
        
        Args:
            strategy: Strategy placing the order
            symbol: Ticker symbol
            action: "BUY" or "SELL" (simple intent)
            quantity: Desired quantity
            order_type: Trade.MARKET, Trade.LIMIT, etc.
            price: Execution price
            **kwargs: Additional parameters (trade_date, stop_price, etc.)
        
        Returns:
            Order object or raises exception
        
        Raises:
            OrderRejected: If order violates rules
            ValueError: If invalid parameters
        """
        # Validate action
        if action not in {"BUY", "SELL"}:
            raise ValueError(f"Action must be 'BUY' or 'SELL', got '{action}'")
        
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got {quantity}")
        
        # Create order object
        order = Order(strategy, symbol, action, quantity, order_type, price, **kwargs)
        
        # Log event
        self._event_log.log('ORDER_CREATED', {
            'order_id': order.order_id,
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'strategy': strategy.strategy_name
        })
        
        try:
            # 1. Aggregate rules from all levels
            aggregated_rules = self._aggregate_rules(strategy)
            
            # 2. Get current position from TMS
            current_position = self.tms.get_position(strategy, symbol)
            
            # 3. Determine actual trade direction(s) - SMART LOGIC
            trade_instructions = self._determine_trade_directions(
                order, current_position, aggregated_rules, **kwargs
            )
            
            # Log instructions
            self._event_log.log('INSTRUCTIONS_GENERATED', {
                'order_id': order.order_id,
                'num_instructions': len(trade_instructions),
                'instructions': [str(i) for i in trade_instructions]
            })
            
            # 4. Validate each instruction against rules
            for instruction in trade_instructions:
                is_valid, reason = self._validate_instruction(
                    instruction, aggregated_rules, current_position, strategy
                )
                if not is_valid:
                    # Log rejection
                    self._event_log.log('ORDER_REJECTED', {
                        'order_id': order.order_id,
                        'reason': reason
                    })
                    
                    # Record rejection in hierarchy ledgers
                    strategy.ledger.record_rejection(order, reason)
                    
                    raise OrderRejected(f"Order rejected: {reason}")
            
            # 5. Check sufficient funds
            self._check_sufficient_funds(strategy, trade_instructions)
            
            # 6. Store instructions in order
            order.trade_instructions = trade_instructions
            order.status = "VALIDATED"
            
            return order
            
        except Exception as e:
            # Log error
            self._event_log.log('ORDER_ERROR', {
                'order_id': order.order_id,
                'error': str(e),
                'error_type': type(e).__name__
            })
            raise
    
    def submit_order(self, order):
        """
        Submit validated order to TMS for execution
        
        Args:
            order: Validated Order object
        
        Returns:
            List of executed Trade objects
        """
        order.status = "SUBMITTED"
        
        self._event_log.log('ORDER_SUBMITTED', {
            'order_id': order.order_id,
            'num_instructions': len(order.trade_instructions)
        })
        
        executed_trades = []
        
        # Execute each trade instruction via TMS
        for instruction in order.trade_instructions:
            trade = self.tms.execute_trade(instruction)
            executed_trades.append(trade)
        
        order.status = "FILLED"
        order.executed_trades = executed_trades
        
        self._event_log.log('ORDER_FILLED', {
            'order_id': order.order_id,
            'num_trades': len(executed_trades),
            'trade_ids': [t.trade_id for t in executed_trades]
        })
        
        return executed_trades
    
    def _aggregate_rules(self, strategy):
        """
        Aggregate rules from all hierarchy levels
        Fund → Portfolio → Strategy (more restrictive takes precedence)
        
        Args:
            strategy: Strategy object
        
        Returns:
            AggregatedRules object
        """
        rules = AggregatedRules()
        
        # Apply Portfolio rules (if exists)
        if strategy.portfolio:
            rules.apply(strategy.portfolio.trade_rules)
            
            # Apply Fund rules (if exists)
            if strategy.portfolio.fund:
                rules.apply(strategy.portfolio.fund.trade_rules)
        
        return rules
    
    def _determine_trade_directions(self, order, current_position, rules, **kwargs):
        """
        SMART LOGIC: Determine actual trade direction(s) based on position and rules
        
        Args:
            order: Order object
            current_position: Current Position or None
            rules: AggregatedRules object
            **kwargs: Additional parameters (trade_date, etc.)
        
        Returns:
            List of TradeInstruction objects
        """
        instructions = []
        action = order.action
        quantity = order.quantity
        current_qty = current_position.quantity if current_position else 0
        
        trade_date = kwargs.get('trade_date', None)
        
        if action == "BUY":
            if current_qty >= 0:
                # Long or flat → simple BUY
                instructions.append(TradeInstruction(
                    strategy=order.strategy,
                    symbol=order.symbol,
                    direction=Trade.BUY,
                    quantity=quantity,
                    order_type=order.order_type,
                    price=order.price,
                    reason="Opening/adding to long position",
                    trade_date=trade_date
                ))
            elif current_qty < 0:
                # Short position exists
                short_qty = abs(current_qty)
                
                if quantity <= short_qty:
                    # Covering partial/full short
                    instructions.append(TradeInstruction(
                        strategy=order.strategy,
                        symbol=order.symbol,
                        direction=Trade.BUY_TO_COVER,
                        quantity=quantity,
                        order_type=order.order_type,
                        price=order.price,
                        reason=f"Covering {quantity} of {short_qty} short",
                        trade_date=trade_date
                    ))
                else:
                    # Cover short + go long
                    instructions.append(TradeInstruction(
                        strategy=order.strategy,
                        symbol=order.symbol,
                        direction=Trade.BUY_TO_COVER,
                        quantity=short_qty,
                        order_type=order.order_type,
                        price=order.price,
                        reason="Closing short position",
                        trade_date=trade_date
                    ))
                    instructions.append(TradeInstruction(
                        strategy=order.strategy,
                        symbol=order.symbol,
                        direction=Trade.BUY,
                        quantity=quantity - short_qty,
                        order_type=order.order_type,
                        price=order.price,
                        reason="Opening long position",
                        trade_date=trade_date
                    ))
        
        elif action == "SELL":
            if current_qty > 0:
                # Long position exists
                if quantity <= current_qty:
                    # Selling partial/full long
                    instructions.append(TradeInstruction(
                        strategy=order.strategy,
                        symbol=order.symbol,
                        direction=Trade.SELL,
                        quantity=quantity,
                        order_type=order.order_type,
                        price=order.price,
                        reason=f"Closing {quantity} of {current_qty} long",
                        trade_date=trade_date
                    ))
                else:
                    # Sell entire long + go short
                    instructions.append(TradeInstruction(
                        strategy=order.strategy,
                        symbol=order.symbol,
                        direction=Trade.SELL,
                        quantity=current_qty,
                        order_type=order.order_type,
                        price=order.price,
                        reason="Closing long position",
                        trade_date=trade_date
                    ))
                    
                    # Check if short selling allowed
                    if not rules.allow_short_selling:
                        raise OrderRejected(
                            f"Cannot sell {quantity - current_qty} more: "
                            f"Would require short selling (disabled in rules)"
                        )
                    
                    instructions.append(TradeInstruction(
                        strategy=order.strategy,
                        symbol=order.symbol,
                        direction=Trade.SELL_SHORT,
                        quantity=quantity - current_qty,
                        order_type=order.order_type,
                        price=order.price,
                        reason="Opening short position",
                        trade_date=trade_date
                    ))
            
            elif current_qty < 0:
                # Already short → add to short
                instructions.append(TradeInstruction(
                    strategy=order.strategy,
                    symbol=order.symbol,
                    direction=Trade.SELL_SHORT,
                    quantity=quantity,
                    order_type=order.order_type,
                    price=order.price,
                    reason="Adding to short position",
                    trade_date=trade_date
                ))
            
            else:
                # No position → open short
                if not rules.allow_short_selling:
                    raise OrderRejected(
                        f"Cannot sell {quantity}: No position exists and "
                        f"short selling disabled in rules"
                    )
                
                instructions.append(TradeInstruction(
                    strategy=order.strategy,
                    symbol=order.symbol,
                    direction=Trade.SELL_SHORT,
                    quantity=quantity,
                    order_type=order.order_type,
                    price=order.price,
                    reason="Opening short position",
                    trade_date=trade_date
                ))
        
        return instructions
    
    def _validate_instruction(self, instruction, rules, current_position, strategy):
        """
        Validate a trade instruction against aggregated rules
        
        Args:
            instruction: TradeInstruction object
            rules: AggregatedRules object
            current_position: Current Position or None
            strategy: Strategy object
        
        Returns:
            tuple: (is_valid, reason_if_not_valid)
        """
        # Check if direction is allowed
        if instruction.direction not in rules.allowed_directions:
            return False, f"Direction '{instruction.direction}' not allowed by rules"
        
        # Check if trade type is allowed
        if instruction.order_type not in rules.allowed_trade_types:
            return False, f"Trade type '{instruction.order_type}' not allowed by rules"
        
        # Check symbol restrictions
        if rules.allowed_symbols is not None and instruction.symbol not in rules.allowed_symbols:
            return False, f"Symbol '{instruction.symbol}' not in allowed list"
        
        if instruction.symbol in rules.restricted_symbols:
            return False, f"Symbol '{instruction.symbol}' is restricted"
        
        # Check position size limits (if strategy has portfolio for value calculation)
        if strategy.portfolio:
            portfolio_value = strategy.portfolio.portfolio_balance
            if portfolio_value > 0:
                trade_value = instruction.quantity * instruction.price
                
                # Check single trade size
                trade_pct = (trade_value / portfolio_value) * 100
                if trade_pct > rules.max_single_trade_pct:
                    return False, (f"Trade size {trade_pct:.1f}% exceeds "
                                 f"max single trade limit {rules.max_single_trade_pct}%")
                
                # Check resulting position size
                if current_position:
                    new_qty = current_position.quantity
                    if instruction.direction in {Trade.BUY, Trade.BUY_TO_COVER}:
                        new_qty += instruction.quantity
                    else:
                        new_qty -= instruction.quantity
                    
                    new_position_value = abs(new_qty) * instruction.price
                    position_pct = (new_position_value / portfolio_value) * 100
                    
                    if position_pct > rules.max_position_size_pct:
                        return False, (f"Resulting position size {position_pct:.1f}% exceeds "
                                     f"max position limit {rules.max_position_size_pct}%")
        
        return True, "OK"
    
    def _check_sufficient_funds(self, strategy, instructions):
        """
        Check if strategy has sufficient funds for all instructions
        
        Args:
            strategy: Strategy object
            instructions: List of TradeInstruction objects
        
        Raises:
            InsufficientFundsError: If not enough funds
        """
        total_cost = 0
        for instruction in instructions:
            if instruction.direction in {Trade.BUY, Trade.BUY_TO_COVER}:
                total_cost += instruction.quantity * instruction.price
        
        if total_cost > 0:
            available_cash = strategy.get_cash_balance()
            if total_cost > available_cash:
                raise InsufficientFundsError(
                    f"Insufficient funds: Need ${total_cost:,.2f}, "
                    f"have ${available_cash:,.2f}"
                )

