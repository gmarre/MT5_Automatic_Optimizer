"""
Analyzer Module

This module provides functionality to analyze MetaTrader 5 optimization results,
identify interesting parameter combinations, and generate visualizations.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from .results_parser import ResultsParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mt5_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Analyzer")

class Analyzer:
    """
    Class to analyze MetaTrader 5 optimization results and generate insights.
    """
    
    def __init__(self, results_dir="results", output_dir="results/analysis"):
        """
        Initialize the Analyzer with paths to results and output directories.
        
        Args:
            results_dir (str): Path to the directory containing optimization results
            output_dir (str): Path to the directory to save analysis outputs
        """
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.parser = ResultsParser(results_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Analyzer initialized with results directory: {results_dir}")
        logger.info(f"Analysis outputs will be saved to: {output_dir}")
    
    def analyze_results(self, robot_name=None, symbol=None, timeframe=None, period_name=None, 
                       criteria=None):
        """
        Analyze optimization results based on specified criteria.
        
        Args:
            robot_name (str, optional): Filter by robot name
            symbol (str, optional): Filter by symbol
            timeframe (str, optional): Filter by timeframe
            period_name (str, optional): Filter by period name
            criteria (dict, optional): Dictionary of criteria for filtering results
                e.g., {"max_drawdown_percent": 25, "min_profit_factor": 1.5}
            
        Returns:
            dict: Dictionary containing analysis results
        """
        # Default criteria if none provided
        if criteria is None:
            criteria = {
                "max_drawdown_percent": 25,
                "min_profit_factor": 1.5,
                "min_expected_payoff": 10,
                "min_recovery_factor": 1.0,
                "min_sharpe_ratio": 0.5
            }
        
        try:
            # Parse results
            parsed_results = self.parser.parse_results(
                robot_name=robot_name,
                symbol=symbol,
                timeframe=timeframe,
                period_name=period_name
            )
            
            # Convert to DataFrame for analysis
            df = self.parser.convert_to_dataframe(parsed_results)
            
            if df.empty:
                logger.warning("No results found for analysis")
                return {"status": "warning", "message": "No results found for analysis"}
            
            # Clean and convert numeric columns
            numeric_columns = ["Profit", "Expected Payoff", "Drawdown", "Recovery Factor", 
                              "Sharpe Ratio", "Profit Factor", "Trades"]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Apply criteria filters
            filtered_df = df.copy()
            
            if "max_drawdown_percent" in criteria and "Drawdown" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Drawdown"] <= criteria["max_drawdown_percent"]]
            
            if "min_profit_factor" in criteria and "Profit Factor" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Profit Factor"] >= criteria["min_profit_factor"]]
            
            if "min_expected_payoff" in criteria and "Expected Payoff" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Expected Payoff"] >= criteria["min_expected_payoff"]]
            
            if "min_recovery_factor" in criteria and "Recovery Factor" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Recovery Factor"] >= criteria["min_recovery_factor"]]
            
            if "min_sharpe_ratio" in criteria and "Sharpe Ratio" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Sharpe Ratio"] >= criteria["min_sharpe_ratio"]]
            
            # Generate analysis results
            analysis_results = {
                "total_passes": len(df),
                "filtered_passes": len(filtered_df),
                "filter_criteria": criteria,
                "top_performers": self._get_top_performers(filtered_df),
                "parameter_importance": self._analyze_parameter_importance(df),
                "statistics": self._calculate_statistics(df, filtered_df),
                "status": "success"
            }
            
            # Generate visualizations
            self._generate_visualizations(df, filtered_df, robot_name, symbol, timeframe, period_name)
            
            logger.info(f"Analysis completed with {len(filtered_df)} passes meeting criteria")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing results: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_top_performers(self, df, top_n=10):
        """
        Get the top performing parameter combinations.
        
        Args:
            df (pandas.DataFrame): DataFrame containing optimization results
            top_n (int): Number of top performers to return
            
        Returns:
            list: List of top performing parameter combinations
        """
        if df.empty:
            return []
        
        # Sort by profit (or other metric if available)
        if "Profit" in df.columns:
            sorted_df = df.sort_values(by="Profit", ascending=False)
        elif "Net Profit" in df.columns:
            sorted_df = df.sort_values(by="Net Profit", ascending=False)
        else:
            # Find a numeric column to sort by
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                sorted_df = df.sort_values(by=numeric_cols[0], ascending=False)
            else:
                return []
        
        # Get top N rows
        top_df = sorted_df.head(top_n)
        
        # Convert to list of dictionaries
        top_performers = top_df.to_dict(orient="records")
        
        return top_performers
    
    def _analyze_parameter_importance(self, df):
        """
        Analyze the importance of different parameters on the optimization results.
        
        Args:
            df (pandas.DataFrame): DataFrame containing optimization results
            
        Returns:
            dict: Dictionary containing parameter importance analysis
        """
        if df.empty:
            return {}
        
        try:
            # Identify parameter columns (those starting with "param_")
            param_cols = [col for col in df.columns if col.startswith("param_")]
            
            if not param_cols:
                logger.warning("No parameter columns found for importance analysis")
                return {}
            
            # Identify target column (profit or similar)
            target_col = None
            for col in ["Profit", "Net Profit", "Balance"]:
                if col in df.columns:
                    target_col = col
                    break
            
            if target_col is None:
                # Find a numeric column to use as target
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    target_col = numeric_cols[0]
                else:
                    logger.warning("No suitable target column found for importance analysis")
                    return {}
            
            # Prepare data for model
            X = df[param_cols].copy()
            y = df[target_col].copy()
            
            # Convert all parameter columns to numeric
            for col in X.columns:
                X[col] = pd.to_numeric(X[col], errors="coerce")
            
            # Drop rows with NaN values
            valid_data = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_data]
            y = y[valid_data]
            
            if len(X) < 10:
                logger.warning("Not enough valid data points for parameter importance analysis")
                return {}
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train a Random Forest model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)
            
            # Get feature importances
            importances = model.feature_importances_
            
            # Create dictionary of parameter importances
            param_importance = {}
            for i, col in enumerate(param_cols):
                param_name = col.replace("param_", "")
                param_importance[param_name] = float(importances[i])
            
            # Sort by importance
            param_importance = {k: v for k, v in sorted(
                param_importance.items(), key=lambda item: item[1], reverse=True
            )}
            
            return param_importance
            
        except Exception as e:
            logger.error(f"Error in parameter importance analysis: {str(e)}")
            return {}
    
    def _calculate_statistics(self, df, filtered_df):
        """
        Calculate statistics on the optimization results.
        
        Args:
            df (pandas.DataFrame): DataFrame containing all optimization results
            filtered_df (pandas.DataFrame): DataFrame containing filtered optimization results
            
        Returns:
            dict: Dictionary containing statistics
        """
        statistics = {}
        
        try:
            # Calculate statistics for numeric columns
            numeric_columns = ["Profit", "Expected Payoff", "Drawdown", "Recovery Factor", 
                              "Sharpe Ratio", "Profit Factor", "Trades"]
            
            for col in numeric_columns:
                if col in df.columns:
                    col_stats = {
                        "all": {
                            "mean": float(df[col].mean()),
                            "median": float(df[col].median()),
                            "min": float(df[col].min()),
                            "max": float(df[col].max()),
                            "std": float(df[col].std())
                        }
                    }
                    
                    if not filtered_df.empty and col in filtered_df.columns:
                        col_stats["filtered"] = {
                            "mean": float(filtered_df[col].mean()),
                            "median": float(filtered_df[col].median()),
                            "min": float(filtered_df[col].min()),
                            "max": float(filtered_df[col].max()),
                            "std": float(filtered_df[col].std())
                        }
                    
                    statistics[col] = col_stats
            
            # Calculate trade duration statistics if available
            if "Trade Duration" in df.columns:
                statistics["Trade Duration"] = {
                    "all": {
                        "mean": str(df["Trade Duration"].mean()),
                        "median": str(df["Trade Duration"].median()),
                        "min": str(df["Trade Duration"].min()),
                        "max": str(df["Trade Duration"].max())
                    }
                }
                
                if not filtered_df.empty and "Trade Duration" in filtered_df.columns:
                    statistics["Trade Duration"]["filtered"] = {
                        "mean": str(filtered_df["Trade Duration"].mean()),
                        "median": str(filtered_df["Trade Duration"].median()),
                        "min": str(filtered_df["Trade Duration"].min()),
                        "max": str(filtered_df["Trade Duration"].max())
                    }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return statistics
    
    def _generate_visualizations(self, df, filtered_df, robot_name=None, symbol=None, 
                               timeframe=None, period_name=None):
        """
        Generate visualizations for the optimization results.
        
        Args:
            df (pandas.DataFrame): DataFrame containing all optimization results
            filtered_df (pandas.DataFrame): DataFrame containing filtered optimization results
            robot_name (str, optional): Robot name for file naming
            symbol (str, optional): Symbol for file naming
            timeframe (str, optional): Timeframe for file naming
            period_name (str, optional): Period name for file naming
            
        Returns:
            bool: True if visualizations were generated successfully, False otherwise
        """
        try:
            if df.empty:
                logger.warning("No data available for visualizations")
                return False
            
            # Create file name prefix
            prefix_parts = []
            if robot_name:
                prefix_parts.append(robot_name)
            if symbol:
                prefix_parts.append(symbol)
            if timeframe:
                prefix_parts.append(timeframe)
            if period_name:
                prefix_parts.append(period_name)
            
            prefix = "_".join(prefix_parts) if prefix_parts else "optimization"
            
            # 1. Profit vs Drawdown scatter plot
            if "Profit" in df.columns and "Drawdown" in df.columns:
                plt.figure(figsize=(10, 6))
                plt.scatter(df["Drawdown"], df["Profit"], alpha=0.5, label="All Passes")
                
                if not filtered_df.empty:
                    plt.scatter(filtered_df["Drawdown"], filtered_df["Profit"], 
                               color="red", alpha=0.7, label="Filtered Passes")
                
                plt.xlabel("Drawdown (%)")
                plt.ylabel("Profit")
                plt.title("Profit vs Drawdown")
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                # Save figure
                fig_path = os.path.join(self.output_dir, f"{prefix}_profit_vs_drawdown.png")
                plt.savefig(fig_path)
                plt.close()
                logger.info(f"Generated Profit vs Drawdown plot: {fig_path}")
            
            # 2. Parameter importance plot
            param_importance = self._analyze_parameter_importance(df)
            if param_importance:
                plt.figure(figsize=(12, 8))
                
                # Sort parameters by importance
                params = list(param_importance.keys())
                importances = list(param_importance.values())
                
                # Plot horizontal bar chart
                y_pos = np.arange(len(params))
                plt.barh(y_pos, importances, align="center")
                plt.yticks(y_pos, params)
                plt.xlabel("Importance")
                plt.title("Parameter Importance")
                plt.tight_layout()
                
                # Save figure
                fig_path = os.path.join(self.output_dir, f"{prefix}_parameter_importance.png")
                plt.savefig(fig_path)
                plt.close()
                logger.info(f"Generated Parameter Importance plot: {fig_path}")
            
            # 3. Profit distribution histogram
            if "Profit" in df.columns:
                plt.figure(figsize=(10, 6))
                plt.hist(df["Profit"], bins=30, alpha=0.5, label="All Passes")
                
                if not filtered_df.empty:
                    plt.hist(filtered_df["Profit"], bins=30, alpha=0.5, color="red", 
                            label="Filtered Passes")
                
                plt.xlabel("Profit")
                plt.ylabel("Frequency")
                plt.title("Profit Distribution")
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                # Save figure
                fig_path = os.path.join(self.output_dir, f"{prefix}_profit_distribution.png")
                plt.savefig(fig_path)
                plt.close()
                logger.info(f"Generated Profit Distribution plot: {fig_path}")
            
            # 4. Correlation heatmap
            numeric_columns = ["Profit", "Expected Payoff", "Drawdown", "Recovery Factor", 
                              "Sharpe Ratio", "Profit Factor", "Trades"]
            
            available_cols = [col for col in numeric_columns if col in df.columns]
            
            if len(available_cols) > 1:
                plt.figure(figsize=(10, 8))
                corr_matrix = df[available_cols].corr()
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
                plt.title("Correlation Matrix")
                plt.tight_layout()
                
                # Save figure
                fig_path = os.path.join(self.output_dir, f"{prefix}_correlation_matrix.png")
                plt.savefig(fig_path)
                plt.close()
                logger.info(f"Generated Correlation Matrix plot: {fig_path}")
            
            # 5. Parameter distribution plots for top parameters
            param_cols = [col for col in df.columns if col.startswith("param_")]
            
            if param_importance and param_cols:
                # Get top 5 parameters
                top_params = list(param_importance.keys())[:5]
                
                for param in top_params:
                    param_col = f"param_{param}"
                    if param_col in df.columns:
                        plt.figure(figsize=(10, 6))
                        
                        # Convert to numeric if needed
                        df[param_col] = pd.to_numeric(df[param_col], errors="coerce")
                        
                        if not filtered_df.empty and param_col in filtered_df.columns:
                            filtered_df[param_col] = pd.to_numeric(filtered_df[param_col], errors="coerce")
                            
                            # Create KDE plot for both all and filtered data
                            sns.kdeplot(df[param_col].dropna(), label="All Passes", fill=True, alpha=0.3)
                            sns.kdeplot(filtered_df[param_col].dropna(), label="Filtered Passes", 
                                      fill=True, alpha=0.3, color="red")
                        else:
                            # Create histogram for all data
                            plt.hist(df[param_col].dropna(), bins=20, alpha=0.5)
                        
                        plt.xlabel(param)
                        plt.ylabel("Density")
                        plt.title(f"Distribution of {param}")
                        plt.legend()
                        plt.grid(True, alpha=0.3)
                        
                        # Save figure
                        fig_path = os.path.join(self.output_dir, f"{prefix}_param_{param}_distribution.png")
                        plt.savefig(fig_path)
                        plt.close()
                        logger.info(f"Generated Parameter Distribution plot for {param}: {fig_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            return False
    
    def generate_report(self, analysis_results, output_path=None):
        """
        Generate a comprehensive HTML report from analysis results.
        
        Args:
            analysis_results (dict): Results from analyze_results method
            output_path (str, optional): Path to save the HTML report
            
        Returns:
            str: Path to the generated report or None if failed
        """
        try:
            if not analysis_results or analysis_results.get("status") != "success":
                logger.warning("No valid analysis results to generate report")
                return None
            
            # Default output path if not provided
            if output_path is None:
                output_path = os.path.join(self.output_dir, "optimization_report.html")
            
            # Generate HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MT5 Optimization Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2, h3 {{ color: #333366; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .summary {{ background-color: #eef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .visualization {{ margin: 20px 0; text-align: center; }}
                    .visualization img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <h1>MT5 Optimization Analysis Report</h1>
                
                <div class="summary">
                    <h2>Summary</h2>
                    <p>Total optimization passes: {analysis_results.get('total_passes', 0)}</p>
                    <p>Passes meeting criteria: {analysis_results.get('filtered_passes', 0)}</p>
                </div>
                
                <h2>Filter Criteria</h2>
                <table>
                    <tr>
                        <th>Criterion</th>
                        <th>Value</th>
                    </tr>
            """
            
            # Add filter criteria
            criteria = analysis_results.get("filter_criteria", {})
            for criterion, value in criteria.items():
                html_content += f"""
                    <tr>
                        <td>{criterion.replace('_', ' ').title()}</td>
                        <td>{value}</td>
                    </tr>
                """
            
            html_content += """
                </table>
                
                <h2>Top Performing Parameter Combinations</h2>
                <table>
                    <tr>
            """
            
            # Add top performers table
            top_performers = analysis_results.get("top_performers", [])
            if top_performers:
                # Add table headers
                headers = top_performers[0].keys()
                for header in headers:
                    html_content += f"<th>{header}</th>"
                
                html_content += "</tr>"
                
                # Add table rows
                for performer in top_performers:
                    html_content += "<tr>"
                    for header in headers:
                        html_content += f"<td>{performer.get(header, '')}</td>"
                    html_content += "</tr>"
            else:
                html_content += "<th>No top performers found</th></tr>"
            
            html_content += """
                </table>
                
                <h2>Parameter Importance</h2>
                <table>
                    <tr>
                        <th>Parameter</th>
                        <th>Importance</th>
                    </tr>
            """
            
            # Add parameter importance
            param_importance = analysis_results.get("parameter_importance", {})
            for param, importance in param_importance.items():
                html_content += f"""
                    <tr>
                        <td>{param}</td>
                        <td>{importance:.4f}</td>
                    </tr>
                """
            
            html_content += """
                </table>
                
                <h2>Statistics</h2>
            """
            
            # Add statistics tables
            statistics = analysis_results.get("statistics", {})
            for metric, stats in statistics.items():
                html_content += f"""
                <h3>{metric}</h3>
                <table>
                    <tr>
                        <th>Statistic</th>
                        <th>All Passes</th>
                        <th>Filtered Passes</th>
                    </tr>
                """
                
                all_stats = stats.get("all", {})
                filtered_stats = stats.get("filtered", {})
                
                for stat in ["mean", "median", "min", "max", "std"]:
                    html_content += f"""
                    <tr>
                        <td>{stat.title()}</td>
                        <td>{all_stats.get(stat, 'N/A')}</td>
                        <td>{filtered_stats.get(stat, 'N/A')}</td>
                    </tr>
                    """
                
                html_content += "</table>"
            
            # Add visualizations
            html_content += """
                <h2>Visualizations</h2>
                
                <div class="visualization">
                    <h3>Profit vs Drawdown</h3>
                    <img src="profit_vs_drawdown.png" alt="Profit vs Drawdown">
                </div>
                
                <div class="visualization">
                    <h3>Parameter Importance</h3>
                    <img src="parameter_importance.png" alt="Parameter Importance">
                </div>
                
                <div class="visualization">
                    <h3>Profit Distribution</h3>
                    <img src="profit_distribution.png" alt="Profit Distribution">
                </div>
                
                <div class="visualization">
                    <h3>Correlation Matrix</h3>
                    <img src="correlation_matrix.png" alt="Correlation Matrix">
                </div>
            </body>
            </html>
            """
            
            # Write HTML content to file
            with open(output_path, "w") as f:
                f.write(html_content)
            
            logger.info(f"Generated HTML report: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    analyzer = Analyzer("../results", "../results/analysis")
    
    # Load criteria from config
    try:
        with open("../config/optimization_config.json", "r") as f:
            config = json.load(f)
        criteria = config.get("analysis_criteria", None)
    except:
        criteria = None
    
    # Run analysis
    results = analyzer.analyze_results(criteria=criteria)
    
    # Generate report
    if results["status"] == "success":
        analyzer.generate_report(results)
