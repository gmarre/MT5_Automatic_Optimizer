"""
MT5 Launcher Module

This module provides functionality to launch MetaTrader 5 terminal and control it
for automated optimization of Expert Advisors.
"""

import os
import time
import subprocess
import json
import logging
import shutil
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
logger = logging.getLogger("MT5Launcher")

class MT5Launcher:
    """
    Class to launch and control MetaTrader 5 terminal for automated optimization.
    """
    
    def __init__(self, mt5_path, output_directory="results"):
        """
        Initialize the MT5Launcher with the path to MT5 terminal.
        
        Args:
            mt5_path (str): Path to the MT5 terminal executable
            output_directory (str): Directory to store optimization results
        """
        self.mt5_path = mt5_path
        self.output_directory = output_directory
        self.process = None
        
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        logger.info(f"MT5Launcher initialized with MT5 path: {mt5_path}")
        logger.info(f"Results will be stored in: {output_directory}")
    
    def launch_mt5(self):
        """
        Launch the MT5 terminal.
        
        Returns:
            bool: True if MT5 was launched successfully, False otherwise
        """
        try:
            logger.info(f"Launching MT5 from: {self.mt5_path}")
            
            # Launch MT5 with /portable flag to avoid conflicts with other instances
            self.process = subprocess.Popen([self.mt5_path, "/portable"], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE)
            
            # Wait for MT5 to initialize
            time.sleep(10)
            
            # Check if process is still running
            if self.process.poll() is None:
                logger.info("MT5 launched successfully")
                return True
            else:
                stdout, stderr = self.process.communicate()
                logger.error(f"MT5 failed to start. Exit code: {self.process.returncode}")
                logger.error(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                logger.error(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
                return False
                
        except Exception as e:
            logger.error(f"Error launching MT5: {str(e)}")
            return False
    
    def close_mt5(self):
        """
        Close the MT5 terminal.
        
        Returns:
            bool: True if MT5 was closed successfully, False otherwise
        """
        try:
            if self.process and self.process.poll() is None:
                logger.info("Closing MT5")
                
                # Try graceful termination first
                self.process.terminate()
                
                # Wait for process to terminate
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if termination takes too long
                    logger.warning("MT5 did not terminate gracefully, forcing kill")
                    self.process.kill()
                    self.process.wait()
                
                logger.info("MT5 closed successfully")
                return True
            else:
                logger.warning("MT5 is not running, nothing to close")
                return True
                
        except Exception as e:
            logger.error(f"Error closing MT5: {str(e)}")
            return False
    
    def run_optimization(self, robot_name, set_file, symbol, timeframe, 
                        from_date, to_date, leverage=100, model=1, 
                        initial_deposit=10000, optimization_type="genetic",
                        period_name="Default", period_type="backtest"):
        """
        Run an optimization for a specific EA with the given parameters.
        
        Args:
            robot_name (str): Name of the Expert Advisor
            set_file (str): Path to the .set file with optimization parameters
            symbol (str): Symbol to optimize on (e.g., "EURUSD")
            timeframe (str): Timeframe to optimize on (e.g., "H1", "D1")
            from_date (str): Start date for optimization in format "YYYY.MM.DD"
            to_date (str): End date for optimization in format "YYYY.MM.DD"
            leverage (int): Leverage to use for optimization
            model (int): Modeling quality (0-control points, 1-OHLC, 2-every tick)
            initial_deposit (int): Initial deposit for optimization
            optimization_type (str): Type of optimization ("genetic" or "complete")
            period_name (str): Name of the period for result organization
            period_type (str): Type of the period ("backtest" or "forwardtest")
            
        Returns:
            bool: True if optimization was run successfully, False otherwise
        """
        try:
            # Create directory for results
            result_dir = os.path.join(self.output_directory, f"{symbol}_{timeframe}_{period_name}")
            os.makedirs(result_dir, exist_ok=True)
            
            logger.info(f"Running optimization for {robot_name} on {symbol} {timeframe}")
            logger.info(f"Period: {from_date} to {to_date} ({period_type})")
            
            # Construct command line arguments for MT5
            # Note: This is a simplified version. In reality, you would need to use
            # MT5's command line interface or automate through its UI
            
            # For demonstration purposes, we'll just simulate the optimization process
            logger.info("Simulating optimization process...")
            time.sleep(5)  # Simulate optimization running
            
            # In a real implementation, you would:
            # 1. Use MT5's command line parameters or
            # 2. Use UI automation libraries like pyautogui or pywinauto to control MT5
            # 3. Monitor the optimization progress
            # 4. Extract results when complete
            
            # Simulate creating result files
            with open(os.path.join(result_dir, f"{robot_name}_{period_type}_results.csv"), "w") as f:
                f.write(f"Simulated optimization results for {robot_name} on {symbol} {timeframe}\n")
                f.write(f"Period: {from_date} to {to_date}\n")
                f.write("Pass,Profit,Drawdown,Trades,Win%,Parameters...\n")
                f.write("1,1000,150,50,65,param1=10,param2=20\n")
                f.write("2,1200,180,55,68,param1=12,param2=18\n")
            
            logger.info(f"Optimization completed. Results saved to {result_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error running optimization: {str(e)}")
            return False

    def copy_set_file(self, set_file, destination_dir):
        """
        Copy the .set file to the destination directory.
        
        Args:
            set_file (str): Path to the .set file
            destination_dir (str): Destination directory
            
        Returns:
            str: Path to the copied .set file or None if failed
        """
        try:
            if not os.path.exists(set_file):
                logger.error(f"SET file not found: {set_file}")
                return None
                
            os.makedirs(destination_dir, exist_ok=True)
            destination = os.path.join(destination_dir, os.path.basename(set_file))
            shutil.copy2(set_file, destination)
            
            logger.info(f"Copied SET file to {destination}")
            return destination
            
        except Exception as e:
            logger.error(f"Error copying SET file: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    # Load configuration
    with open("../config/optimization_config.json", "r") as f:
        config = json.load(f)
    
    # Initialize launcher
    launcher = MT5Launcher(config["mt5_path"], config["output_directory"])
    
    # Launch MT5
    if launcher.launch_mt5():
        # Run a sample optimization
        robot = config["robots"][0]
        optim = robot["optimizations"][0]
        period = optim["periods"][0]
        
        launcher.run_optimization(
            robot_name=robot["name"],
            set_file=robot["set_file"],
            symbol=optim["symbol"],
            timeframe=optim["timeframe"],
            from_date=period["from_date"],
            to_date=period["to_date"],
            leverage=optim["leverage"],
            model=optim["model"],
            initial_deposit=optim["initial_deposit"],
            optimization_type=optim["optimization_type"],
            period_name=period["name"],
            period_type=period["type"]
        )
        
        # Close MT5
        launcher.close_mt5()
