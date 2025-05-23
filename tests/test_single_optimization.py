"""
Test Single Optimization

This script tests running a single optimization with MT5.
"""

import os
import sys
import logging
import time
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from optim.mt5_launcher import MT5Launcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_single_optimization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestSingleOptimization")

def main():
    """
    Main function.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test running a single optimization with MT5.')
    parser.add_argument('--mt5_path', type=str, default="C:\\Program Files\\IC Trading (MU) MT5 Terminal\\terminal64.exe",
                        help='Path to the MT5 executable')
    parser.add_argument('--robot', type=str, required=True,
                        help='Path to the robot (EA) file')
    parser.add_argument('--symbol', type=str, default="EURUSD",
                        help='Symbol to optimize')
    parser.add_argument('--timeframe', type=str, default="H1",
                        help='Timeframe to optimize')
    parser.add_argument('--from_date', type=str, default="2023.01.01",
                        help='Start date in format YYYY.MM.DD')
    parser.add_argument('--to_date', type=str, default="2023.06.30",
                        help='End date in format YYYY.MM.DD')
    parser.add_argument('--forward', action='store_true',
                        help='Use forward testing')
    parser.add_argument('--optimization_type', type=int, default=2,
                        help='Type of optimization (1=Slow, 2=Fast genetic, 3=All symbols)')
    parser.add_argument('--model', type=int, default=2,
                        help='Model (0=Every tick, 1=Control points, 2=Open prices only)')
    parser.add_argument('--deposit', type=int, default=5000,
                        help='Initial deposit')
    parser.add_argument('--leverage', type=int, default=500,
                        help='Leverage')
    parser.add_argument('--set_file', type=str, default=None,
                        help='Path to the .set file')
    parser.add_argument('--output_dir', type=str, default="results",
                        help='Directory to store output files')
    parser.add_argument('--wait_time', type=int, default=300,
                        help='Time to wait for optimization to complete (seconds)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize MT5 launcher
    mt5_launcher = MT5Launcher(args.mt5_path, args.output_dir)
    
    # Create period information
    period = {
        "name": "test",
        "type": "forwardtest" if args.forward else "backtest",
        "from_date": args.from_date,
        "to_date": args.to_date
    }
    
    # Override the wait time in the run_optimization method
    original_sleep = time.sleep
    
    def custom_sleep(seconds):
        if seconds == 300:  # The default wait time in run_optimization
            logger.info(f"Waiting {args.wait_time} seconds for optimization to complete...")
            original_sleep(args.wait_time)
        else:
            original_sleep(seconds)
    
    # Replace the sleep function
    time.sleep = custom_sleep
    
    try:
        # Run optimization
        logger.info(f"Running optimization for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe}")
        
        results = mt5_launcher.run_optimization(
            robot_name=args.robot,
            symbol=args.symbol,
            timeframe=args.timeframe,
            period=period,
            optimization_type=args.optimization_type,
            leverage=args.leverage,
            model=args.model,
            initial_deposit=args.deposit,
            set_file=args.set_file
        )
        
        # Restore the original sleep function
        time.sleep = original_sleep
        
        # Print results
        if results["status"] == "success":
            logger.info("Optimization completed successfully")
            logger.info(f"Output directory: {results['output_dir']}")
            
            if "results_files" in results and results["results_files"]:
                logger.info(f"Results files: {results['results_files']}")
            else:
                logger.warning("No results files found")
        else:
            logger.error(f"Optimization failed: {results.get('message', 'Unknown error')}")
    except Exception as e:
        # Restore the original sleep function
        time.sleep = original_sleep
        logger.error(f"Error running optimization: {str(e)}")

if __name__ == "__main__":
    main()
