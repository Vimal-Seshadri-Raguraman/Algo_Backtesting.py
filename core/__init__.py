"""
###############################################################################
# Trade Engine - Core Trading System
###############################################################################
# A comprehensive hierarchical trading framework with multi-level compliance
# and data-source agnostic architecture.
#
# Hierarchy: TradeAccount → Fund → Portfolio → Strategy → Position → Trade
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

