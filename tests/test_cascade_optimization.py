"""
Test Cascade Optimization

This script tests running multiple optimizations in cascade with MT5.
"""

import os
import sys
import logging
import time
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from optim.mt5_launcher import MT5Launcher
from optim.optimizer import Optimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_cascade_optimization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestCascadeOptimization")

def main():
    """
    Main function.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test running multiple optimizations in cascade with MT5.')
    parser.add_argument('--config', type=str, default="config/optimization_config.json",
                        help='Path to the configuration file')
    parser.add_argument('--robot', type=str, default=None,
                        help='Name of the robot to optimize (if not specified, all robots in the configuration will be optimized)')
    parser.add_argument('--symbol', type=str, default=None,
                        help='Symbol to optimize (if not specified, all symbols for the robot will be optimized)')
    parser.add_argument('--timeframe', type=str, default=None,
                        help='Timeframe to optimize (if not specified, all timeframes for the symbol will be optimized)')
    parser.add_argument('--period_name', type=str, default=None,
                        help='Name of the period to optimize (if not specified, all periods for the timeframe will be optimized)')
    parser.add_argument('--period_type', type=str, default=None,
                        help='Type of the period to optimize (if not specified, all period types for the period will be optimized)')
    parser.add_argument('--wait_time', type=int, default=60,
                        help='Time to wait for each optimization to complete (seconds)')
    
    args = parser.parse_args()
    
    # Check if configuration file exists
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        return
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return
    
    # Initialize optimizer
    optimizer = Optimizer(args.config)
    
    # Override the wait time in the run_optimization method
    original_sleep = time.sleep
    
    def custom_sleep(seconds):
        if seconds == 60:  # The default wait time in run_optimization
            logger.info(f"Waiting {args.wait_time} seconds for optimization to complete...")
            original_sleep(args.wait_time)
        else:
            original_sleep(seconds)
    
    # Replace the sleep function
    time.sleep = custom_sleep
    
    try:
        # Run optimizations
        if args.robot:
            # Run optimizations for a specific robot
            if args.symbol:
                # Run optimizations for a specific symbol
                if args.timeframe:
                    # Run optimizations for a specific timeframe
                    logger.info(f"Running optimizations for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe}")
                    results = optimizer.run_symbol_optimization(args.robot, args.symbol, args.timeframe)
                else:
                    # Run optimizations for all timeframes
                    logger.info(f"Running optimizations for robot {args.robot}, symbol {args.symbol}")
                    results = optimizer.run_robot_optimization(args.robot)
            else:
                # Run optimizations for all symbols
                logger.info(f"Running optimizations for robot {args.robot}")
                results = optimizer.run_robot_optimization(args.robot)
        else:
            # Run optimizations for all robots
            logger.info("Running all optimizations")
            results = optimizer.run_all_optimizations()
        
        # Restore the original sleep function
        time.sleep = original_sleep
        
        # Print results
        if results["status"] == "success":
            logger.info("Optimizations completed successfully")
            
            # Print results for each robot
            for robot_results in results.get("results", []):
                if robot_results["status"] == "success":
                    logger.info(f"Robot: {robot_results['robot_name']}")
                    
                    # Print results for each symbol
                    for symbol_results in robot_results.get("results", []):
                        if symbol_results["status"] == "success":
                            logger.info(f"  Symbol: {symbol_results['symbol']}, Timeframe: {symbol_results['timeframe']}")
                            
                            # Print results for each period
                            for period_results in symbol_results.get("results", []):
                                if period_results["status"] == "success":
                                    period = period_results["period"]
                                    logger.info(f"    Period: {period['name']} ({period['type']})")
                                    logger.info(f"    Output directory: {period_results['output_dir']}")
                                    
                                    if "results_files" in period_results and period_results["results_files"]:
                                        logger.info(f"    Results files: {period_results['results_files']}")
                                    else:
                                        logger.warning("    No results files found")
                                else:
                                    logger.error(f"    Period optimization failed: {period_results.get('message', 'Unknown error')}")
                        else:
                            logger.error(f"  Symbol optimization failed: {symbol_results.get('message', 'Unknown error')}")
                else:
                    logger.error(f"Robot optimization failed: {robot_results.get('message', 'Unknown error')}")
        else:
            logger.error(f"Optimizations failed: {results.get('message', 'Unknown error')}")
    except Exception as e:
        # Restore the original sleep function
        time.sleep = original_sleep
        logger.error(f"Error running optimizations: {str(e)}")

if __name__ == "__main__":
    main()
