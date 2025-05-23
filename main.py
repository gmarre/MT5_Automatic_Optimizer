"""
Main Module for MT5 Automatic Optimizer

This module provides the main entry point for the MT5 Automatic Optimizer.
"""

import os
import sys
import json
import logging
import argparse
import tkinter as tk
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mt5_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

def run_gui():
    """
    Run the GUI.
    """
    try:
        logger.info("Starting MT5 Automatic Optimizer GUI")
        
        # Import GUI module
        from gui import MT5OptimizerGUI
        
        # Create the root window
        root = tk.Tk()
        
        # Create the GUI
        gui = MT5OptimizerGUI(root)
        
        # Run the main loop
        root.mainloop()
        
        logger.info("MT5 Automatic Optimizer GUI closed")
    except Exception as e:
        logger.error(f"Error running GUI: {str(e)}")
        print(f"Error running GUI: {str(e)}")
        sys.exit(1)

def run_cli(args):
    """
    Run the CLI.
    
    Args:
        args (argparse.Namespace): Command line arguments
    """
    try:
        logger.info("Starting MT5 Automatic Optimizer CLI")
        
        # Import optimizer module
        from optim.optimizer import Optimizer
        
        # Create the optimizer
        optimizer = Optimizer(args.config)
        
        # Run optimizations
        if args.mode == "all":
            # Run all optimizations
            logger.info("Running all optimizations")
            results = optimizer.run_all_optimizations()
            
            if results["status"] == "success":
                logger.info("All optimizations completed successfully")
                print("All optimizations completed successfully")
            else:
                logger.error(f"Optimizations failed: {results.get('message', 'Unknown error')}")
                print(f"Optimizations failed: {results.get('message', 'Unknown error')}")
                sys.exit(1)
        
        elif args.mode == "robot":
            # Run robot optimization
            if not args.robot:
                logger.error("--robot is required for robot mode")
                print("--robot is required for robot mode")
                sys.exit(1)
            
            logger.info(f"Running optimization for robot {args.robot}")
            results = optimizer.run_robot_optimization(args.robot)
            
            if results["status"] == "success":
                logger.info(f"Optimization for robot {args.robot} completed successfully")
                print(f"Optimization for robot {args.robot} completed successfully")
            else:
                logger.error(f"Optimization failed: {results.get('message', 'Unknown error')}")
                print(f"Optimization failed: {results.get('message', 'Unknown error')}")
                sys.exit(1)
        
        elif args.mode == "symbol":
            # Run symbol optimization
            if not args.robot or not args.symbol or not args.timeframe:
                logger.error("--robot, --symbol, and --timeframe are required for symbol mode")
                print("--robot, --symbol, and --timeframe are required for symbol mode")
                sys.exit(1)
            
            logger.info(f"Running optimization for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe}")
            results = optimizer.run_symbol_optimization(args.robot, args.symbol, args.timeframe)
            
            if results["status"] == "success":
                logger.info(f"Optimization for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe} completed successfully")
                print(f"Optimization for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe} completed successfully")
            else:
                logger.error(f"Optimization failed: {results.get('message', 'Unknown error')}")
                print(f"Optimization failed: {results.get('message', 'Unknown error')}")
                sys.exit(1)
        
        logger.info("MT5 Automatic Optimizer CLI completed")
    except Exception as e:
        logger.error(f"Error running CLI: {str(e)}")
        print(f"Error running CLI: {str(e)}")
        sys.exit(1)

def run_analysis(args):
    """
    Run the analysis.
    
    Args:
        args (argparse.Namespace): Command line arguments
    """
    try:
        logger.info("Starting MT5 Automatic Optimizer Analysis")
        
        # Import analyzer module
        from analysis.analyzer import Analyzer
        
        # Create the analyzer
        analyzer = Analyzer(args.results_dir)
        
        # Create criteria
        criteria = {
            "max_drawdown": args.max_drawdown,
            "min_profit_factor": args.min_profit_factor,
            "min_expected_payoff": args.min_expected_payoff,
            "min_recovery_factor": args.min_recovery_factor,
            "min_trades": args.min_trades,
            "max_consecutive_losses": args.max_consecutive_losses,
            "min_win_rate": args.min_win_rate
        }
        
        # Run analysis
        if args.action == "analyze":
            # Analyze results
            logger.info(f"Analyzing results for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe}, period {args.period_name} ({args.period_type})")
            results = analyzer.analyze_results(args.robot, args.symbol, args.timeframe, args.period_name, args.period_type, criteria)
            
            if results["status"] == "success":
                logger.info(f"Analysis completed successfully")
                print(f"Analysis completed successfully")
                print(f"Total passes: {results['total_passes']}")
                print(f"Filtered passes: {results['filtered_passes']}")
                print(f"Charts generated in: {results['charts_dir']}")
            else:
                logger.error(f"Analysis failed: {results.get('message', 'Unknown error')}")
                print(f"Analysis failed: {results.get('message', 'Unknown error')}")
                sys.exit(1)
        
        elif args.action == "report":
            # Generate report
            logger.info(f"Generating report for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe}, period {args.period_name} ({args.period_type})")
            results = analyzer.generate_report(args.robot, args.symbol, args.timeframe, args.period_name, args.period_type, criteria)
            
            if results["status"] == "success":
                logger.info(f"Report generated successfully at {results['report_file']}")
                print(f"Report generated successfully at {results['report_file']}")
            else:
                logger.error(f"Report generation failed: {results.get('message', 'Unknown error')}")
                print(f"Report generation failed: {results.get('message', 'Unknown error')}")
                sys.exit(1)
        
        logger.info("MT5 Automatic Optimizer Analysis completed")
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}")
        print(f"Error running analysis: {str(e)}")
        sys.exit(1)

def main():
    """
    Main entry point.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MT5 Automatic Optimizer")
    
    # Add arguments
    parser.add_argument("--gui", action="store_true", help="Run the GUI")
    parser.add_argument("--config", default="config/optimization_config.json", help="Path to configuration file")
    parser.add_argument("--mode", choices=["all", "robot", "symbol"], default="all", help="Optimization mode")
    parser.add_argument("--robot", help="Name of the robot to optimize (for robot and symbol modes)")
    parser.add_argument("--symbol", help="Symbol to optimize (for symbol mode)")
    parser.add_argument("--timeframe", help="Timeframe to optimize (for symbol mode)")
    
    # Analysis arguments
    parser.add_argument("--analysis", action="store_true", help="Run analysis")
    parser.add_argument("--results_dir", default="results", help="Path to results directory")
    parser.add_argument("--period_name", help="Name of the period")
    parser.add_argument("--period_type", choices=["backtest", "forwardtest"], default="backtest", help="Type of the period")
    parser.add_argument("--action", choices=["analyze", "report"], default="analyze", help="Analysis action")
    parser.add_argument("--max_drawdown", type=float, default=25.0, help="Maximum drawdown")
    parser.add_argument("--min_profit_factor", type=float, default=1.5, help="Minimum profit factor")
    parser.add_argument("--min_expected_payoff", type=float, default=10.0, help="Minimum expected payoff")
    parser.add_argument("--min_recovery_factor", type=float, default=1.0, help="Minimum recovery factor")
    parser.add_argument("--min_trades", type=int, default=30, help="Minimum number of trades")
    parser.add_argument("--max_consecutive_losses", type=int, default=5, help="Maximum consecutive losses")
    parser.add_argument("--min_win_rate", type=float, default=50.0, help="Minimum win rate")
    
    args = parser.parse_args()
    
    # Run the appropriate mode
    if args.gui:
        # Run the GUI
        run_gui()
    elif args.analysis:
        # Run analysis
        run_analysis(args)
    else:
        # Run the CLI
        run_cli(args)

if __name__ == "__main__":
    main()
