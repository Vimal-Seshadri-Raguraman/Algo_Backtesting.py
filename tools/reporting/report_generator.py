"""
###############################################################################
# ReportGenerator - Generate Trading Reports
###############################################################################
"""

import json
import pandas as pd
from datetime import datetime


class ReportGenerator:
    ###############################################################################
    # ReportGenerator - Generate comprehensive trading reports
    ###############################################################################
    
    def __init__(self, strategy=None, portfolio=None, fund=None, account=None):
        """
        Initialize ReportGenerator
        
        Args:
            strategy: Strategy object to report on
            portfolio: Portfolio object to report on
            fund: Fund object to report on
            account: TradeAccount object to report on
        
        Example:
            report = ReportGenerator(strategy=my_strategy)
            report.to_csv('strategy_report.csv')
            report.to_json('strategy_report.json')
        """
        self.strategy = strategy
        self.portfolio = portfolio
        self.fund = fund
        self.account = account
        
        # Determine report subject
        if strategy:
            self.subject = strategy
            self.subject_type = "Strategy"
            self.subject_name = strategy.strategy_name
        elif portfolio:
            self.subject = portfolio
            self.subject_type = "Portfolio"
            self.subject_name = portfolio.portfolio_name
        elif fund:
            self.subject = fund
            self.subject_type = "Fund"
            self.subject_name = fund.fund_name
        elif account:
            self.subject = account
            self.subject_type = "Account"
            self.subject_name = account.account_name
        else:
            raise ValueError("Must provide at least one of: strategy, portfolio, fund, account")
    
    ###########################################################################
    # CSV Export
    ###########################################################################
    
    def trades_to_csv(self, filepath):
        """
        Export trades to CSV
        
        Args:
            filepath: Path to save CSV file
        """
        trades_data = []
        
        for trade in self.subject.ledger.get_all_trades():
            trades_data.append({
                'date': trade.filled_at or trade.created_at,
                'symbol': trade.symbol,
                'direction': trade.direction,
                'quantity': trade.filled_quantity,
                'price': trade.avg_fill_price,
                'value': trade.filled_quantity * trade.avg_fill_price,
                'commission': trade.commission,
                'realized_pnl': trade.realized_pnl if hasattr(trade, 'realized_pnl') else 0.0,
                'trade_type': trade.trade_type,
                'status': trade.status,
                'trade_id': trade.trade_id
            })
        
        df = pd.DataFrame(trades_data)
        df.to_csv(filepath, index=False)
        print(f"✅ Trades exported to {filepath}")
        return df
    
    def ledger_summary_to_csv(self, filepath):
        """
        Export ledger summary to CSV
        
        Args:
            filepath: Path to save CSV file
        """
        summary_data = self.subject.ledger.export_to_dict()
        
        # Convert to DataFrame (single row summary)
        df = pd.DataFrame([summary_data])
        df.to_csv(filepath, index=False)
        print(f"✅ Ledger summary exported to {filepath}")
        return df
    
    ###########################################################################
    # JSON Export
    ###########################################################################
    
    def to_json(self, filepath):
        """
        Export complete report to JSON
        
        Args:
            filepath: Path to save JSON file
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'subject_type': self.subject_type,
            'subject_name': self.subject_name,
            'ledger': self.subject.ledger.export_to_dict(),
            'trades': []
        }
        
        # Add all trades
        for trade in self.subject.ledger.get_all_trades():
            report['trades'].append({
                'date': (trade.filled_at or trade.created_at).isoformat(),
                'symbol': trade.symbol,
                'direction': trade.direction,
                'quantity': trade.filled_quantity,
                'price': trade.avg_fill_price,
                'commission': trade.commission,
                'realized_pnl': trade.realized_pnl if hasattr(trade, 'realized_pnl') else 0.0,
                'trade_type': trade.trade_type
            })
        
        # Add performance metrics if available
        try:
            from tools import PerformanceMetrics
            metrics = self.subject.performance_metrics(show_summary=False)
            report['performance'] = metrics.to_dict()
        except:
            pass
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Complete report exported to {filepath}")
        return report
    
    ###########################################################################
    # Text Report
    ###########################################################################
    
    def generate_text_report(self, filepath=None):
        """
        Generate formatted text report
        
        Args:
            filepath: Path to save report (None = print to console)
        
        Returns:
            str: Report content
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"TRADING REPORT: {self.subject_name} ({self.subject_type})")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Ledger summary
        lines.append("📊 Trade Summary:")
        lines.append("-" * 80)
        lines.append(f"Total Trades: {self.subject.ledger.get_trade_count()}")
        lines.append(f"Filled Trades: {self.subject.ledger.get_filled_trade_count()}")
        lines.append(f"Symbols Traded: {', '.join(self.subject.ledger.get_symbols_traded())}")
        lines.append(f"Total Volume: ${self.subject.ledger.get_total_volume():,.2f}")
        lines.append("")
        
        # Trade breakdown
        ratios = self.subject.ledger.get_buy_vs_sell_ratio()
        lines.append("📈 Trade Directions:")
        lines.append("-" * 80)
        lines.append(f"BUY trades: {ratios['BUY']}")
        lines.append(f"SELL trades: {ratios['SELL']}")
        lines.append(f"SELL_SHORT trades: {ratios['SELL_SHORT']}")
        lines.append(f"BUY_TO_COVER trades: {ratios['BUY_TO_COVER']}")
        lines.append("")
        
        # Performance metrics (if available)
        try:
            from tools import PerformanceMetrics
            metrics = self.subject.performance_metrics(show_summary=False)
            
            lines.append("💰 Performance Metrics:")
            lines.append("-" * 80)
            lines.append(f"Total Return: {metrics.total_return_pct():.2f}%")
            lines.append(f"Sharpe Ratio: {metrics.sharpe_ratio():.2f}")
            lines.append(f"Max Drawdown: {metrics.max_drawdown():.2f}%")
            lines.append(f"Win Rate: {metrics.win_rate():.2f}%")
            lines.append("")
        except:
            pass
        
        lines.append("=" * 80)
        
        report_text = "\n".join(lines)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(report_text)
            print(f"✅ Text report saved to {filepath}")
        else:
            print(report_text)
        
        return report_text





