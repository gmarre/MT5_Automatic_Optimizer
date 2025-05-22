"""
MT5 Automatic Optimizer

Main orchestrator script for automating MetaTrader 5 optimization processes.
This script coordinates the optimization and analysis of Expert Advisors in MT5.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

from optim.optimizer import Optimizer
from analysis.results_parser import ResultsParser
from analysis.analyzer import Analyzer

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

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="MT5 Automatic Optimizer")
    
    # Main operation mode
    parser.add_argument("--mode", choices=["optimize", "analyze", "both"], default="both",
                      help="Operation mode: optimize, analyze, or both (default)")
    
    # Configuration
    parser.add_argument("--config", default="config/optimization_config.json",
                      help="Path to configuration file (default: config/optimization_config.json)")
    
    # Filtering options
    parser.add_argument("--robot", help="Filter by robot name")
    parser.add_argument("--symbol", help="Filter by symbol")
    parser.add_argument("--timeframe", help="Filter by timeframe")
    parser.add_argument("--period", help="Filter by period name")
    
    # Output options
    parser.add_argument("--output-dir", default="results",
                      help="Directory to store results (default: results)")
    parser.add_argument("--report", action="store_true",
                      help="Generate HTML report after analysis")
    
    return parser.parse_args()

def run_optimization(config_path, robot_name=None, symbol=None, timeframe=None, period_name=None):
    """
    Run optimization process based on configuration.
    
    Args:
        config_path (str): Path to configuration file
        robot_name (str, optional): Filter by robot name
        symbol (str, optional): Filter by symbol
        timeframe (str, optional): Filter by timeframe
        period_name (str, optional): Filter by period name
        
    Returns:
        dict: Summary of optimization results
    """
    logger.info("Starting optimization process")
    
    try:
        # Initialize optimizer
        optimizer = Optimizer(config_path)
        
        # Run optimization
        if robot_name:
            logger.info(f"Running specific optimization for robot: {robot_name}")
            results = optimizer.run_specific_optimization(
                robot_name=robot_name,
                symbol=symbol,
                timeframe=timeframe,
                period_name=period_name
            )
        else:
            logger.info("Running all optimizations")
            results = optimizer.run_all_optimizations()
        
        logger.info(f"Optimization completed with status: {results['status']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in optimization process: {str(e)}")
        return {"status": "error", "message": str(e)}

def run_analysis(config_path, output_dir, robot_name=None, symbol=None, timeframe=None, period_name=None, generate_report=False):
    """
    Run analysis process on optimization results.
    
    Args:
        config_path (str): Path to configuration file
        output_dir (str): Directory to store analysis outputs
        robot_name (str, optional): Filter by robot name
        symbol (str, optional): Filter by symbol
        timeframe (str, optional): Filter by timeframe
        period_name (str, optional): Filter by period name
        generate_report (bool): Whether to generate HTML report
        
    Returns:
        dict: Analysis results
    """
    logger.info("Starting analysis process")
    
    try:
        # Load criteria from config
        with open(config_path, "r") as f:
            config = json.load(f)
        
        criteria = config.get("analysis_criteria", None)
        
        # Initialize analyzer
        analyzer = Analyzer(output_dir, os.path.join(output_dir, "analysis"))
        
        # Run analysis
        results = analyzer.analyze_results(
            robot_name=robot_name,
            symbol=symbol,
            timeframe=timeframe,
            period_name=period_name,
            criteria=criteria
        )
        
        # Generate report if requested
        if generate_report and results["status"] == "success":
            report_path = analyzer.generate_report(results)
            if report_path:
                logger.info(f"Analysis report generated: {report_path}")
                results["report_path"] = report_path
        
        logger.info(f"Analysis completed with status: {results['status']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in analysis process: {str(e)}")
        return {"status": "error", "message": str(e)}

def main():
    """
    Main function to orchestrate the optimization and analysis processes.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Record start time
    start_time = datetime.now()
    logger.info(f"MT5 Automatic Optimizer started at {start_time}")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run processes based on mode
    optimization_results = None
    analysis_results = None
    
    if args.mode in ["optimize", "both"]:
        optimization_results = run_optimization(
            config_path=args.config,
            robot_name=args.robot,
            symbol=args.symbol,
            timeframe=args.timeframe,
            period_name=args.period
        )
    
    if args.mode in ["analyze", "both"]:
        analysis_results = run_analysis(
            config_path=args.config,
            output_dir=args.output_dir,
            robot_name=args.robot,
            symbol=args.symbol,
            timeframe=args.timeframe,
            period_name=args.period,
            generate_report=args.report
        )
    
    # Record end time and calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Print summary
    logger.info(f"MT5 Automatic Optimizer completed at {end_time}")
    logger.info(f"Total duration: {duration}")
    
    if optimization_results:
        logger.info(f"Optimization status: {optimization_results['status']}")
    
    if analysis_results:
        logger.info(f"Analysis status: {analysis_results['status']}")
        
        if args.report and analysis_results.get("report_path"):
            logger.info(f"Analysis report: {analysis_results['report_path']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
