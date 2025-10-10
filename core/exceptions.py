"""
###############################################################################
# Custom Exceptions for Trade Engine
###############################################################################
"""


class TradeComplianceError(Exception):
    """Raised when a trade violates compliance rules"""
    pass


class InsufficientFundsError(Exception):
    """Raised when strategy doesn't have enough cash for trade"""
    pass

