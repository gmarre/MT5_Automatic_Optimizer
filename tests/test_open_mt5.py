"""
Test Open MT5

This script tests opening and closing MT5.
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
        logging.FileHandler("test_open_mt5.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestOpenMT5")

def main():
    """
    Main function.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test opening and closing MT5.')
    parser.add_argument('--mt5_path', type=str, default="C:\\Program Files\\IC Trading (MU) MT5 Terminal\\terminal64.exe",
                        help='Path to the MT5 executable')
    parser.add_argument('--output_dir', type=str, default="results",
                        help='Directory to store output files')
    parser.add_argument('--action', type=str, choices=['open', 'close', 'both'], default='both',
                        help='Action to perform (open, close, or both)')
    parser.add_argument('--wait_time', type=int, default=10,
                        help='Time to wait between opening and closing MT5 (seconds)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize MT5 launcher
    mt5_launcher = MT5Launcher(args.mt5_path, args.output_dir)
    
    # Check if MT5 is running
    is_running = mt5_launcher.is_mt5_running()
    logger.info(f"MT5 is {'running' if is_running else 'not running'}")
    
    # Open MT5
    if args.action in ['open', 'both']:
        if is_running and args.action == 'open':
            logger.info("MT5 is already running, skipping open action")
        else:
            logger.info("Opening MT5")
            if mt5_launcher.launch_mt5():
                logger.info("MT5 opened successfully")
            else:
                logger.error("Failed to open MT5")
    
    # Wait
    if args.action == 'both':
        logger.info(f"Waiting {args.wait_time} seconds")
        time.sleep(args.wait_time)
    
    # Close MT5
    if args.action in ['close', 'both']:
        if not mt5_launcher.is_mt5_running() and args.action == 'close':
            logger.info("MT5 is not running, skipping close action")
        else:
            logger.info("Closing MT5")
            if mt5_launcher.close_mt5():
                logger.info("MT5 closed successfully")
            else:
                logger.error("Failed to close MT5")
    
    # Check if MT5 is running
    is_running = mt5_launcher.is_mt5_running()
    logger.info(f"MT5 is {'running' if is_running else 'not running'}")

if __name__ == "__main__":
    main()
