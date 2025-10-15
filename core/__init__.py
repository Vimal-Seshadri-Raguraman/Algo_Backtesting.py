"""
###############################################################################
# Trade Engine - Core Trading System
###############################################################################
# A comprehensive hierarchical trading framework with multi-level compliance
# and data-source agnostic architecture.
#
# Hierarchy: TradeAccount → Fund → Portfolio → Strategy → Position → Trade
#
# Core modules:
# - account: TradeAccount (top-level container)
# - fund: Fund (raised capital unit)
# - portfolio: Portfolio (capital allocation)
# - strategy: Strategy (trading logic base class)
# - position: Position (symbol aggregate)
# - trade: Trade (individual order)
# - rules: TradeRules (compliance enforcement)
# - ledger: Ledger (automatic record keeping)
# - exceptions: Custom exceptions
#
# Note: Analysis tools (PerformanceMetrics, etc.) are in the 'tools' package
###############################################################################
"""

from .exceptions import TradeComplianceError, InsufficientFundsError
from .trade import Trade
from .position import Position
from .rules import TradeRules
from .ledger import Ledger
from .strategy import Strategy
from .portfolio import Portfolio
from .fund import Fund
from .account import TradeAccount

# OMS/TMS are internal - not exported to users
from . import order_management
from . import trade_management
from . import oms_tms_mixin

__all__ = [
    'TradeComplianceError',
    'InsufficientFundsError',
    'Trade',
    'Position',
    'TradeRules',
    'Ledger',
    'Strategy',
    'Portfolio',
    'Fund',
    'TradeAccount',
]

__version__ = '1.0.0'

