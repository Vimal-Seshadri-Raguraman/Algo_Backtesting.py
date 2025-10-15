"""
###############################################################################
# RiskAnalyzer - Portfolio Risk Analysis and Metrics
###############################################################################
"""

import pandas as pd
import numpy as np


class RiskAnalyzer:
    ###############################################################################
    # RiskAnalyzer - Comprehensive risk analysis for portfolios and strategies
    ###############################################################################
    
    def __init__(self, strategy=None, portfolio=None, price_history=None, benchmark=None):
        """
        Initialize RiskAnalyzer
        
        Args:
            strategy: Strategy object to analyze (optional)
            portfolio: Portfolio object to analyze (optional)
            price_history: pandas DataFrame with historical prices
            benchmark: pandas Series with benchmark returns (optional, e.g., S&P 500)
        
        Example:
            analyzer = RiskAnalyzer(
                strategy=my_strategy,
                price_history=price_df,
                benchmark=sp500_returns
            )
            
            var_95 = analyzer.calculate_var(confidence=0.95)
            beta = analyzer.calculate_beta()
        """
        self.strategy = strategy
        self.portfolio = portfolio
        self.price_history = price_history
        self.benchmark = benchmark
        
        # Calculate returns if price history provided
        if price_history is not None:
            self.returns = price_history.pct_change().dropna()
        else:
            self.returns = None
    
    ###########################################################################
    # Value at Risk (VaR)
    ###########################################################################
    
    def calculate_var(self, confidence=0.95, method='historical'):
        """
        Calculate Value at Risk
        
        Args:
            confidence: Confidence level (0.95 = 95%, 0.99 = 99%)
            method: 'historical', 'parametric', or 'monte_carlo'
        
        Returns:
            float: VaR as percentage (negative value represents potential loss)
        
        Example:
            var_95 = analyzer.calculate_var(confidence=0.95)
            # Result: -2.5% means 95% confident losses won't exceed 2.5%
        """
        if self.returns is None:
            raise ValueError("Price history required for VaR calculation")
        
        if method == 'historical':
            # Historical VaR: percentile of historical returns
            portfolio_returns = self.returns.mean(axis=1)  # Equal-weighted portfolio
            var_percentile = 1 - confidence
            var = np.percentile(portfolio_returns, var_percentile * 100)
            return var * 100  # Convert to percentage
        
        elif method == 'parametric':
            # Parametric VaR: assumes normal distribution
            portfolio_returns = self.returns.mean(axis=1)
            mean = portfolio_returns.mean()
            std = portfolio_returns.std()
            
            # Z-score for confidence level
            from scipy import stats
            z_score = stats.norm.ppf(1 - confidence)
            var = mean + z_score * std
            return var * 100
        
        else:
            raise ValueError(f"Method '{method}' not supported. Use 'historical' or 'parametric'")
    
    def calculate_cvar(self, confidence=0.95):
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall)
        Average of losses beyond VaR threshold
        
        Args:
            confidence: Confidence level
        
        Returns:
            float: CVaR as percentage
        """
        if self.returns is None:
            raise ValueError("Price history required for CVaR calculation")
        
        portfolio_returns = self.returns.mean(axis=1)
        var_threshold = np.percentile(portfolio_returns, (1 - confidence) * 100)
        cvar = portfolio_returns[portfolio_returns <= var_threshold].mean()
        return cvar * 100
    
    ###########################################################################
    # Correlation & Diversification
    ###########################################################################
    
    def get_correlation_matrix(self):
        """
        Calculate correlation matrix between symbols
        
        Returns:
            pandas DataFrame: Correlation matrix
        """
        if self.returns is None:
            raise ValueError("Price history required for correlation calculation")
        
        return self.returns.corr()
    
    def get_portfolio_volatility(self, weights=None):
        """
        Calculate portfolio volatility
        
        Args:
            weights: Dict of {symbol: weight} or None for equal-weight
        
        Returns:
            float: Annualized portfolio volatility as percentage
        """
        if self.returns is None:
            raise ValueError("Price history required for volatility calculation")
        
        if weights is None:
            # Equal weight
            portfolio_returns = self.returns.mean(axis=1)
        else:
            # Weighted portfolio
            portfolio_returns = sum(self.returns[symbol] * weights.get(symbol, 0) 
                                  for symbol in self.returns.columns)
        
        # Annualized volatility
        vol = portfolio_returns.std() * np.sqrt(252) * 100
        return vol
    
    ###########################################################################
    # Market Risk Metrics
    ###########################################################################
    
    def calculate_beta(self, symbol=None):
        """
        Calculate beta relative to benchmark
        
        Args:
            symbol: Specific symbol (None = portfolio beta)
        
        Returns:
            float: Beta coefficient
        """
        if self.returns is None or self.benchmark is None:
            raise ValueError("Price history and benchmark required for beta calculation")
        
        if symbol:
            asset_returns = self.returns[symbol]
        else:
            asset_returns = self.returns.mean(axis=1)  # Portfolio returns
        
        # Align dates
        aligned = pd.DataFrame({'asset': asset_returns, 'benchmark': self.benchmark}).dropna()
        
        # Calculate beta: Cov(asset, benchmark) / Var(benchmark)
        covariance = aligned['asset'].cov(aligned['benchmark'])
        benchmark_variance = aligned['benchmark'].var()
        
        if benchmark_variance == 0:
            return 0.0
        
        beta = covariance / benchmark_variance
        return beta
    
    def calculate_alpha(self, symbol=None, risk_free_rate=0.02):
        """
        Calculate alpha (excess return vs. benchmark)
        
        Args:
            symbol: Specific symbol (None = portfolio alpha)
            risk_free_rate: Annual risk-free rate
        
        Returns:
            float: Alpha as percentage
        """
        if self.returns is None or self.benchmark is None:
            raise ValueError("Price history and benchmark required for alpha calculation")
        
        beta = self.calculate_beta(symbol)
        
        if symbol:
            asset_returns = self.returns[symbol]
        else:
            asset_returns = self.returns.mean(axis=1)
        
        # Annualized returns
        asset_annual_return = (1 + asset_returns.mean()) ** 252 - 1
        benchmark_annual_return = (1 + self.benchmark.mean()) ** 252 - 1
        
        # Alpha = Asset Return - (Risk Free + Beta * (Benchmark Return - Risk Free))
        alpha = asset_annual_return - (risk_free_rate + beta * (benchmark_annual_return - risk_free_rate))
        return alpha * 100
    
    ###########################################################################
    # Exposure Analysis
    ###########################################################################
    
    def get_position_exposure(self):
        """
        Get current position exposure breakdown
        
        Returns:
            dict: {symbol: exposure_pct}
        """
        if self.strategy is None:
            raise ValueError("Strategy required for position exposure")
        
        total_value = self.strategy.strategy_balance
        exposures = {}
        
        if self.price_history is not None:
            current_prices = self.price_history.iloc[-1].to_dict()
        else:
            current_prices = {}
        
        for symbol, position in self.strategy.get_open_positions().items():
            price = current_prices.get(symbol, position.avg_entry_price)
            position_value = position.get_market_value(price)
            exposure_pct = (position_value / total_value) * 100
            exposures[symbol] = exposure_pct
        
        return exposures
    
    ###########################################################################
    # Summary & Reports
    ###########################################################################
    
    def summary(self):
        """Display comprehensive risk analysis"""
        print("=" * 80)
        print(f"⚠️  RISK ANALYSIS")
        print("=" * 80)
        
        if self.returns is not None:
            print(f"\n📊 Value at Risk:")
            print("-" * 80)
            var_95 = self.calculate_var(confidence=0.95)
            var_99 = self.calculate_var(confidence=0.99)
            cvar_95 = self.calculate_cvar(confidence=0.95)
            print(f"  VaR (95%):              {var_95:>15.2f}%")
            print(f"  VaR (99%):              {var_99:>15.2f}%")
            print(f"  CVaR (95%):             {cvar_95:>15.2f}%")
            
            print(f"\n📈 Portfolio Metrics:")
            print("-" * 80)
            vol = self.get_portfolio_volatility()
            print(f"  Portfolio Volatility:   {vol:>15.2f}%")
            
            if self.benchmark is not None:
                beta = self.calculate_beta()
                alpha = self.calculate_alpha()
                print(f"  Beta (vs Benchmark):    {beta:>15.2f}")
                print(f"  Alpha (vs Benchmark):   {alpha:>15.2f}%")
        
        if self.strategy is not None:
            exposures = self.get_position_exposure()
            if exposures:
                print(f"\n🎯 Position Exposure:")
                print("-" * 80)
                for symbol, exposure in sorted(exposures.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {symbol:<10} {exposure:>15.2f}%")
        
        if self.returns is not None:
            print(f"\n🔗 Correlation Matrix:")
            print("-" * 80)
            corr = self.get_correlation_matrix()
            print(corr.round(2))
        
        print("=" * 80)





