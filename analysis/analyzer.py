"""
Analyzer Module

This module provides functionality to analyze optimization results.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Import results parser
from analysis.results_parser import ResultsParser

# Configure logging
logger = logging.getLogger("Analyzer")

class Analyzer:
    """
    Class to analyze optimization results.
    """
    
    def __init__(self, results_dir):
        """
        Initialize the analyzer.
        
        Args:
            results_dir (str): Directory containing the results
        """
        self.results_dir = results_dir
        self.results_parser = ResultsParser(results_dir)
        
        # Create output directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
        
        logger.info(f"Analyzer initialized with results directory: {results_dir}")
    
    def analyze_results(self, robot_name, symbol, timeframe, period_name, period_type, criteria=None):
        """
        Analyze results for a specific robot, symbol, timeframe, and period.
        
        Args:
            robot_name (str): Name of the robot
            symbol (str): Symbol
            timeframe (str): Timeframe
            period_name (str): Name of the period
            period_type (str): Type of the period (backtest or forwardtest)
            criteria (dict, optional): Criteria for filtering results. Defaults to None.
        
        Returns:
            dict: Analysis results
        """
        try:
            # Parse results
            results = self.results_parser.parse_results(robot_name, symbol, timeframe, period_name, period_type)
            
            if results["status"] == "error":
                return results
            
            # Convert results to DataFrame
            passes = []
            for file_name, file_results in results["results"].items():
                passes.extend(file_results.get("passes", []))
            
            if not passes:
                logger.error(f"No passes found for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period_name} ({period_type})")
                return {"status": "error", "message": f"No passes found for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period_name} ({period_type})"}
            
            df = pd.DataFrame(passes)
            
            # Convert columns to numeric
            numeric_columns = [
                "Pass", "Profit", "Expected Payoff", "Drawdown", "Drawdown %",
                "Total trades", "Profit trades", "Loss trades", "Profit factor",
                "Recovery factor", "Sharpe ratio", "Custom criterion", "Equity DD %",
                "Balance DD %", "Balance DD absolute", "Equity DD absolute"
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Filter results based on criteria
            if criteria:
                filtered_df = df.copy()
                
                if "max_drawdown" in criteria and criteria["max_drawdown"] > 0:
                    if "Drawdown %" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Drawdown %"] <= criteria["max_drawdown"]]
                    elif "Equity DD %" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Equity DD %"] <= criteria["max_drawdown"]]
                
                if "min_profit_factor" in criteria and criteria["min_profit_factor"] > 0:
                    if "Profit factor" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Profit factor"] >= criteria["min_profit_factor"]]
                
                if "min_expected_payoff" in criteria and criteria["min_expected_payoff"] > 0:
                    if "Expected Payoff" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Expected Payoff"] >= criteria["min_expected_payoff"]]
                
                if "min_recovery_factor" in criteria and criteria["min_recovery_factor"] > 0:
                    if "Recovery factor" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Recovery factor"] >= criteria["min_recovery_factor"]]
                
                if "min_trades" in criteria and criteria["min_trades"] > 0:
                    if "Total trades" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Total trades"] >= criteria["min_trades"]]
                
                if "max_consecutive_losses" in criteria and criteria["max_consecutive_losses"] > 0:
                    if "Consecutive losses" in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df["Consecutive losses"] <= criteria["max_consecutive_losses"]]
                
                if "min_win_rate" in criteria and criteria["min_win_rate"] > 0:
                    if "Profit trades" in filtered_df.columns and "Total trades" in filtered_df.columns:
                        filtered_df["Win Rate"] = filtered_df["Profit trades"] / filtered_df["Total trades"] * 100
                        filtered_df = filtered_df[filtered_df["Win Rate"] >= criteria["min_win_rate"]]
            else:
                filtered_df = df
            
            # Generate charts
            charts_dir = os.path.join(self.results_dir, f"{robot_name}_{symbol}_{timeframe}_{period_name}_{period_type}_charts")
            os.makedirs(charts_dir, exist_ok=True)
            
            # Generate charts only if there are results
            if not filtered_df.empty:
                self.generate_charts(filtered_df, charts_dir)
            
            # Return results
            return {
                "status": "success",
                "robot_name": robot_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "period_name": period_name,
                "period_type": period_type,
                "total_passes": len(df),
                "filtered_passes": len(filtered_df),
                "charts_dir": charts_dir,
                "best_passes": filtered_df.sort_values(by="Profit", ascending=False).head(10).to_dict(orient="records") if "Profit" in filtered_df.columns else []
            }
        except Exception as e:
            logger.error(f"Error analyzing results: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_charts(self, df, charts_dir):
        """
        Generate charts for the analysis.
        
        Args:
            df (pd.DataFrame): DataFrame containing the results
            charts_dir (str): Directory to save the charts
        """
        try:
            # Set the style
            sns.set(style="whitegrid")
            
            # Generate profit distribution chart
            if "Profit" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Profit"], kde=True)
                plt.title("Profit Distribution")
                plt.xlabel("Profit")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "profit_distribution.png"))
                plt.close()
            
            # Generate drawdown distribution chart
            if "Drawdown %" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Drawdown %"], kde=True)
                plt.title("Drawdown Distribution")
                plt.xlabel("Drawdown %")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "drawdown_distribution.png"))
                plt.close()
            
            # Generate profit factor distribution chart
            if "Profit factor" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Profit factor"], kde=True)
                plt.title("Profit Factor Distribution")
                plt.xlabel("Profit Factor")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "profit_factor_distribution.png"))
                plt.close()
            
            # Generate expected payoff distribution chart
            if "Expected Payoff" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Expected Payoff"], kde=True)
                plt.title("Expected Payoff Distribution")
                plt.xlabel("Expected Payoff")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "expected_payoff_distribution.png"))
                plt.close()
            
            # Generate recovery factor distribution chart
            if "Recovery factor" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Recovery factor"], kde=True)
                plt.title("Recovery Factor Distribution")
                plt.xlabel("Recovery Factor")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "recovery_factor_distribution.png"))
                plt.close()
            
            # Generate total trades distribution chart
            if "Total trades" in df.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Total trades"], kde=True)
                plt.title("Total Trades Distribution")
                plt.xlabel("Total Trades")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "total_trades_distribution.png"))
                plt.close()
            
            # Generate win rate distribution chart
            if "Profit trades" in df.columns and "Total trades" in df.columns:
                df["Win Rate"] = df["Profit trades"] / df["Total trades"] * 100
                plt.figure(figsize=(10, 6))
                sns.histplot(df["Win Rate"], kde=True)
                plt.title("Win Rate Distribution")
                plt.xlabel("Win Rate (%)")
                plt.ylabel("Frequency")
                plt.savefig(os.path.join(charts_dir, "win_rate_distribution.png"))
                plt.close()
            
            # Generate correlation matrix
            numeric_columns = [
                "Profit", "Expected Payoff", "Drawdown %", "Total trades",
                "Profit trades", "Loss trades", "Profit factor", "Recovery factor"
            ]
            
            numeric_columns = [col for col in numeric_columns if col in df.columns]
            
            if numeric_columns:
                plt.figure(figsize=(12, 10))
                sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm", fmt=".2f")
                plt.title("Correlation Matrix")
                plt.savefig(os.path.join(charts_dir, "correlation_matrix.png"))
                plt.close()
            
            logger.info(f"Charts generated in {charts_dir}")
        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")
    
    def generate_report(self, robot_name, symbol, timeframe, period_name, period_type, criteria=None):
        """
        Generate a report for the analysis.
        
        Args:
            robot_name (str): Name of the robot
            symbol (str): Symbol
            timeframe (str): Timeframe
            period_name (str): Name of the period
            period_type (str): Type of the period (backtest or forwardtest)
            criteria (dict, optional): Criteria for filtering results. Defaults to None.
        
        Returns:
            dict: Report generation results
        """
        try:
            # Analyze results
            analysis_results = self.analyze_results(robot_name, symbol, timeframe, period_name, period_type, criteria)
            
            if analysis_results["status"] == "error":
                return analysis_results
            
            # Generate report
            report_dir = os.path.join(self.results_dir, f"{robot_name}_{symbol}_{timeframe}_{period_name}_{period_type}_report")
            os.makedirs(report_dir, exist_ok=True)
            
            # Generate HTML report
            report_file = os.path.join(report_dir, "report.html")
            
            with open(report_file, "w") as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Optimization Report</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                        }}
                        h1, h2, h3 {{
                            color: #333;
                        }}
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin-bottom: 20px;
                        }}
                        th, td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        th {{
                            background-color: #f2f2f2;
                        }}
                        tr:nth-child(even) {{
                            background-color: #f9f9f9;
                        }}
                        .chart {{
                            margin: 20px 0;
                            text-align: center;
                        }}
                        .chart img {{
                            max-width: 100%;
                            height: auto;
                        }}
                    </style>
                </head>
                <body>
                    <h1>Optimization Report</h1>
                    
                    <h2>Overview</h2>
                    <table>
                        <tr>
                            <th>Robot</th>
                            <td>{robot_name}</td>
                        </tr>
                        <tr>
                            <th>Symbol</th>
                            <td>{symbol}</td>
                        </tr>
                        <tr>
                            <th>Timeframe</th>
                            <td>{timeframe}</td>
                        </tr>
                        <tr>
                            <th>Period</th>
                            <td>{period_name} ({period_type})</td>
                        </tr>
                        <tr>
                            <th>Total Passes</th>
                            <td>{analysis_results["total_passes"]}</td>
                        </tr>
                        <tr>
                            <th>Filtered Passes</th>
                            <td>{analysis_results["filtered_passes"]}</td>
                        </tr>
                        <tr>
                            <th>Generated</th>
                            <td>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
                        </tr>
                    </table>
                    
                    <h2>Criteria</h2>
                    <table>
                """)
                
                if criteria:
                    for key, value in criteria.items():
                        f.write(f"""
                        <tr>
                            <th>{key.replace("_", " ").title()}</th>
                            <td>{value}</td>
                        </tr>
                        """)
                else:
                    f.write(f"""
                    <tr>
                        <td colspan="2">No criteria specified</td>
                    </tr>
                    """)
                
                f.write(f"""
                    </table>
                    
                    <h2>Best Passes</h2>
                """)
                
                if analysis_results["best_passes"]:
                    f.write(f"""
                    <table>
                        <tr>
                    """)
                    
                    # Write headers
                    for key in analysis_results["best_passes"][0].keys():
                        f.write(f"""
                        <th>{key}</th>
                        """)
                    
                    f.write(f"""
                        </tr>
                    """)
                    
                    # Write rows
                    for pass_data in analysis_results["best_passes"]:
                        f.write(f"""
                        <tr>
                        """)
                        
                        for key, value in pass_data.items():
                            f.write(f"""
                            <td>{value}</td>
                            """)
                        
                        f.write(f"""
                        </tr>
                        """)
                    
                    f.write(f"""
                    </table>
                    """)
                else:
                    f.write(f"""
                    <p>No passes found</p>
                    """)
                
                f.write(f"""
                    <h2>Charts</h2>
                """)
                
                # Add charts
                charts = [
                    "profit_distribution.png",
                    "drawdown_distribution.png",
                    "profit_factor_distribution.png",
                    "expected_payoff_distribution.png",
                    "recovery_factor_distribution.png",
                    "total_trades_distribution.png",
                    "win_rate_distribution.png",
                    "correlation_matrix.png"
                ]
                
                for chart in charts:
                    chart_path = os.path.join(analysis_results["charts_dir"], chart)
                    if os.path.exists(chart_path):
                        chart_name = chart.replace("_", " ").replace(".png", "").title()
                        f.write(f"""
                        <div class="chart">
                            <h3>{chart_name}</h3>
                            <img src="../{os.path.relpath(chart_path, self.results_dir)}" alt="{chart_name}">
                        </div>
                        """)
                
                f.write(f"""
                </body>
                </html>
                """)
            
            logger.info(f"Report generated at {report_file}")
            
            # Return results
            return {
                "status": "success",
                "robot_name": robot_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "period_name": period_name,
                "period_type": period_type,
                "report_file": report_file
            }
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {"status": "error", "message": str(e)}
