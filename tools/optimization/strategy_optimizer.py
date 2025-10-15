"""
###############################################################################
# StrategyOptimizer - Strategy Parameter Optimization
###############################################################################
"""

import pandas as pd
import numpy as np
from itertools import product
from tools.backtesting import Backtester


class StrategyOptimizer:
    ###############################################################################
    # StrategyOptimizer - Find optimal strategy parameters via backtesting
    ###############################################################################
    
    def __init__(self, strategy_class, historical_data, optimize_params,
                 initial_capital=100_000, objective='sharpe_ratio',
                 commission_pct=0.001, slippage_pct=0.0005):
        """
        Initialize StrategyOptimizer
        
        Args:
            strategy_class: Strategy class to optimize
            historical_data: pandas DataFrame with historical prices
            optimize_params: Dict of {param_name: [list of values to test]}
            initial_capital: Starting capital for each backtest
            objective: Metric to optimize ('sharpe_ratio', 'return', 'sortino', 'calmar')
            commission_pct: Commission percentage
            slippage_pct: Slippage percentage
        
        Example:
            optimizer = StrategyOptimizer(
                strategy_class=MovingAverageCrossover,
                historical_data=price_df,
                optimize_params={
                    'short_window': [5, 10, 15, 20],
                    'long_window': [30, 50, 70, 100]
                },
                objective='sharpe_ratio'
            )
            
            results = optimizer.optimize(method='grid_search')
            best_params = results.get_best_parameters()
        """
        self.strategy_class = strategy_class
        self.historical_data = historical_data
        self.optimize_params = optimize_params
        self.initial_capital = initial_capital
        self.objective = objective
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
        # Validate objective
        valid_objectives = ['sharpe_ratio', 'return', 'sortino', 'calmar', 'win_rate', 'profit_factor']
        if objective not in valid_objectives:
            raise ValueError(f"Objective must be one of: {valid_objectives}")
    
    def optimize(self, method='grid_search', max_iterations=None):
        """
        Run optimization
        
        Args:
            method: 'grid_search' or 'random_search'
            max_iterations: Maximum iterations (None = all combinations)
        
        Returns:
            OptimizationResults object
        """
        print("=" * 80)
        print(f"OPTIMIZATION: {self.strategy_class.__name__}")
        print("=" * 80)
        print(f"Method: {method}")
        print(f"Objective: {self.objective}")
        print(f"Parameters: {self.optimize_params}")
        
        if method == 'grid_search':
            return self._grid_search()
        elif method == 'random_search':
            return self._random_search(max_iterations or 100)
        else:
            raise ValueError(f"Method '{method}' not supported")
    
    def _grid_search(self):
        """Exhaustive grid search over all parameter combinations"""
        # Generate all combinations
        param_names = list(self.optimize_params.keys())
        param_values = list(self.optimize_params.values())
        combinations = list(product(*param_values))
        
        total_combinations = len(combinations)
        print(f"\n🔍 Testing {total_combinations} parameter combinations...")
        print("=" * 80)
        
        results = []
        
        for i, combo in enumerate(combinations, 1):
            # Create parameter dict
            params = dict(zip(param_names, combo))
            
            # Run backtest
            try:
                backtester = Backtester(
                    strategy_class=self.strategy_class,
                    historical_data=self.historical_data,
                    initial_capital=self.initial_capital,
                    commission_pct=self.commission_pct,
                    slippage_pct=self.slippage_pct
                )
                
                backtest_results = backtester.run(strategy_params=params)
                
                # Get objective value
                objective_value = self._get_objective_value(backtest_results)
                
                results.append({
                    'params': params,
                    'objective_value': objective_value,
                    'backtest_results': backtest_results
                })
                
                # Progress
                if i % 10 == 0 or i == total_combinations:
                    print(f"Progress: {i}/{total_combinations} ({i/total_combinations*100:.0f}%) - "
                          f"Current {self.objective}: {objective_value:.2f}")
                
            except Exception as e:
                print(f"  ⚠️  Failed for params {params}: {str(e)[:50]}")
                continue
        
        print(f"\n✅ Optimization complete: {len(results)} successful runs")
        
        # Find best
        best_result = max(results, key=lambda x: x['objective_value'])
        print(f"\n🏆 Best Parameters:")
        for param, value in best_result['params'].items():
            print(f"   {param}: {value}")
        print(f"   {self.objective}: {best_result['objective_value']:.2f}")
        
        return OptimizationResults(
            results=results,
            objective=self.objective,
            param_names=param_names
        )
    
    def _random_search(self, n_iterations):
        """Random search over parameter space"""
        print(f"\n🎲 Random search: {n_iterations} iterations...")
        print("=" * 80)
        
        results = []
        param_names = list(self.optimize_params.keys())
        
        for i in range(n_iterations):
            # Random sample from each parameter
            params = {}
            for param_name, param_values in self.optimize_params.items():
                params[param_name] = np.random.choice(param_values)
            
            # Run backtest
            try:
                backtester = Backtester(
                    strategy_class=self.strategy_class,
                    historical_data=self.historical_data,
                    initial_capital=self.initial_capital,
                    commission_pct=self.commission_pct,
                    slippage_pct=self.slippage_pct
                )
                
                backtest_results = backtester.run(strategy_params=params)
                objective_value = self._get_objective_value(backtest_results)
                
                results.append({
                    'params': params,
                    'objective_value': objective_value,
                    'backtest_results': backtest_results
                })
                
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i+1}/{n_iterations} ({(i+1)/n_iterations*100:.0f}%)")
                
            except Exception as e:
                continue
        
        best_result = max(results, key=lambda x: x['objective_value'])
        print(f"\n🏆 Best Parameters:")
        for param, value in best_result['params'].items():
            print(f"   {param}: {value}")
        print(f"   {self.objective}: {best_result['objective_value']:.2f}")
        
        return OptimizationResults(
            results=results,
            objective=self.objective,
            param_names=param_names
        )
    
    def _get_objective_value(self, backtest_results):
        """Extract objective value from backtest results"""
        if self.objective == 'sharpe_ratio':
            return backtest_results.sharpe_ratio()
        elif self.objective == 'return':
            return backtest_results.total_return_pct()
        elif self.objective == 'sortino':
            return backtest_results.sortino_ratio()
        elif self.objective == 'calmar':
            return backtest_results.metrics.calmar_ratio()
        elif self.objective == 'win_rate':
            return backtest_results.win_rate()
        elif self.objective == 'profit_factor':
            return backtest_results.profit_factor()
        else:
            return 0.0


class OptimizationResults:
    """Stores and analyzes optimization results"""
    
    def __init__(self, results, objective, param_names):
        self.results = results
        self.objective = objective
        self.param_names = param_names
        
        # Sort by objective value
        self.results_sorted = sorted(results, key=lambda x: x['objective_value'], reverse=True)
    
    def get_best_parameters(self):
        """Get best parameter combination"""
        if self.results_sorted:
            return self.results_sorted[0]['params']
        return None
    
    def get_best_objective_value(self):
        """Get best objective value achieved"""
        if self.results_sorted:
            return self.results_sorted[0]['objective_value']
        return None
    
    def get_top_n(self, n=10):
        """Get top N parameter combinations"""
        return self.results_sorted[:n]
    
    def to_dataframe(self):
        """Convert results to pandas DataFrame"""
        data = []
        for result in self.results:
            row = result['params'].copy()
            row[self.objective] = result['objective_value']
            data.append(row)
        
        return pd.DataFrame(data)
    
    def summary(self, top_n=5):
        """Display optimization summary"""
        print("=" * 80)
        print(f"🎯 OPTIMIZATION RESULTS")
        print("=" * 80)
        
        print(f"\nObjective: {self.objective}")
        print(f"Total Runs: {len(self.results)}")
        
        print(f"\n🏆 Top {top_n} Parameter Combinations:")
        print("-" * 80)
        
        for i, result in enumerate(self.get_top_n(top_n), 1):
            print(f"\n{i}. {self.objective}: {result['objective_value']:.2f}")
            for param, value in result['params'].items():
                print(f"   {param}: {value}")
        
        print("=" * 80)





