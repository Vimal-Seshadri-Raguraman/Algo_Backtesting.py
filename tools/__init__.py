"""
###############################################################################
# Tools - Analysis, Metrics, and Utilities
###############################################################################
# Analysis and utility tools for the Trade Engine
# 
# Modules:
# - performance: Performance metrics and analytics (NO dependencies)
# - backtesting: Historical testing framework (requires pandas, numpy)
# - optimization: Strategy parameter optimization (requires pandas, numpy)
# - risk: Risk analytics and metrics (requires pandas, numpy)
# - reporting: Report generation (requires pandas)
###############################################################################
"""

# Performance Metrics - NO dependencies (always available)
from .performance import PerformanceMetrics

__all__ = ['PerformanceMetrics']

# Optional tools (require pandas/numpy)
try:
    from .backtesting import Backtester, BacktestResults
    __all__.extend(['Backtester', 'BacktestResults'])
except ImportError:
    pass

try:
    from .optimization import StrategyOptimizer, OptimizationResults
    __all__.extend(['StrategyOptimizer', 'OptimizationResults'])
except ImportError:
    pass

try:
    from .risk import RiskAnalyzer
    __all__.append('RiskAnalyzer')
except ImportError:
    pass

try:
    from .reporting import ReportGenerator
    __all__.append('ReportGenerator')
except ImportError:
    pass

__version__ = '2.0.0'


