"""
MT5 Launcher Module

This module provides functionality to launch and control MetaTrader 5.
"""

import os
import sys
import time
import logging
import subprocess
import psutil
from pathlib import Path

# Import INI Generator
from optim.ini_generator import INIGenerator

# Configure logging
logger = logging.getLogger("MT5Launcher")

class MT5Launcher:
    """
    Class to launch and control MetaTrader 5.
    """
    
    def __init__(self, mt5_path, output_dir):
        """
        Initialize the MT5 launcher.
        
        Args:
            mt5_path (str): Path to the MT5 executable
            output_dir (str): Directory to store output files
        """
        self.mt5_path = mt5_path
        self.output_dir = output_dir
        self.mt5_process = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"MT5 Launcher initialized with MT5 path: {mt5_path}")
    
    def launch_mt5(self):
        """
        Launch MT5.
        
        Returns:
            bool: True if MT5 was launched successfully, False otherwise
        """
        try:
            # Check if MT5 is already running
            if self.is_mt5_running():
                logger.info("MT5 is already running")
                return True
            
            # Launch MT5
            logger.info(f"Launching MT5 from {self.mt5_path}")
            self.mt5_process = subprocess.Popen([self.mt5_path])
            
            # Wait for MT5 to start
            time.sleep(5)
            
            # Check if MT5 is running
            if self.is_mt5_running():
                logger.info("MT5 launched successfully")
                return True
            else:
                logger.error("Failed to launch MT5")
                return False
        except Exception as e:
            logger.error(f"Error launching MT5: {str(e)}")
            return False
    
    def close_mt5(self):
        """
        Close MT5.
        
        Returns:
            bool: True if MT5 was closed successfully, False otherwise
        """
        try:
            # Check if MT5 is running
            if not self.is_mt5_running():
                logger.info("MT5 is not running")
                return True
            
            # Close MT5
            logger.info("Closing MT5")
            for proc in psutil.process_iter(['pid', 'name']):
                if 'terminal64.exe' in proc.info['name'].lower():
                    logger.info(f"Terminating MT5 process with PID {proc.info['pid']}")
                    proc.terminate()
            
            # Wait for MT5 to close
            time.sleep(5)
            
            # Check if MT5 is still running
            if not self.is_mt5_running():
                logger.info("MT5 closed successfully")
                return True
            else:
                logger.error("Failed to close MT5")
                return False
        except Exception as e:
            logger.error(f"Error closing MT5: {str(e)}")
            return False
    
    def is_mt5_running(self):
        """
        Check if MT5 is running.
        
        Returns:
            bool: True if MT5 is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if 'terminal64.exe' in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking if MT5 is running: {str(e)}")
            return False
    
    def run_optimization(self, robot_name, symbol, timeframe, period, optimization_type="genetic", leverage=500, model=1, initial_deposit=10000, set_file=None):
        """
        Run an optimization.
        
        Args:
            robot_name (str): Name of the robot
            symbol (str): Symbol to optimize
            timeframe (str): Timeframe to optimize
            period (dict): Period to optimize (name, type, from_date, to_date)
            optimization_type (str or int, optional): Type of optimization. Defaults to "genetic".
                1 = Slow complete algorithm
                2 = Fast genetic based algorithm
                3 = All symbols selected in Market Watch
            leverage (int, optional): Leverage. Defaults to 500.
            model (int, optional): Model. Defaults to 1.
                0 = Every tick
                1 = Control points
                2 = Open prices only
            initial_deposit (int, optional): Initial deposit. Defaults to 10000.
            set_file (str, optional): Path to the .set file. Defaults to None.
        
        Returns:
            dict: Results of the optimization
        """
        try:
            # Check if MT5 is running
            if not self.is_mt5_running():
                logger.info("MT5 is not running, launching it")
                if not self.launch_mt5():
                    return {"status": "error", "message": "Failed to launch MT5"}
            
            # Create output directory
            robot_base_name = os.path.basename(robot_name).replace(".ex5", "")
            output_dir = os.path.join(self.output_dir, f"{robot_base_name}_{symbol}_{timeframe}_{period['name']}_{period['type']}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert optimization_type to string if it's an integer
            opt_type_str = str(optimization_type)
            if optimization_type == 1 or optimization_type == "1":
                opt_type_str = "Slow complete algorithm"
            elif optimization_type == 2 or optimization_type == "2":
                opt_type_str = "Fast genetic based algorithm"
            elif optimization_type == 3 or optimization_type == "3":
                opt_type_str = "All symbols selected in Market Watch"
            
            # Convert model to string
            model_str = str(model)
            if model == 0 or model == "0":
                model_str = "Every tick"
            elif model == 1 or model == "1":
                model_str = "Control points"
            elif model == 2 or model == "2":
                model_str = "Open prices only"
            
            # Prepare the command to launch MT5 with optimization parameters
            # We'll use the /config parameter to pass optimization settings
            
            # Create a temporary .ini file for the optimization
            ini_file = os.path.join(output_dir, "optimization.ini")
            
            # Generate the .ini file using INIGenerator
            is_forward = period['type'] == 'forwardtest'
            report_file = os.path.join(output_dir, f"report_{robot_base_name}_{symbol}_{timeframe}_{period['name']}_{period['type']}")
            
            ini_file = INIGenerator.generate_optimization_ini(
                output_path=ini_file,
                robot_name=robot_name,
                symbol=symbol,
                timeframe=timeframe,
                from_date=period['from_date'],
                to_date=period['to_date'],
                is_forward=is_forward,
                optimization_type=optimization_type,
                model=model,
                deposit=initial_deposit,
                leverage=leverage,
                set_file=set_file,
                report_file=report_file
            )
            
            if not ini_file:
                return {"status": "error", "message": "Failed to generate .ini file"}
            
            # Close MT5 if it's running
            if self.is_mt5_running():
                logger.info("Closing MT5 before launching optimization")
                self.close_mt5()
                time.sleep(2)
            
            # Launch MT5 with the optimization configuration
            cmd = [self.mt5_path, "/config:" + ini_file]
            logger.info(f"Running optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period['name']} ({period['type']})")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Launch MT5 with optimization
            process = subprocess.Popen(cmd)
            
            # Wait for MT5 to start
            time.sleep(10)
            
            # Wait for optimization to complete
            # In a real implementation, you would need to monitor MT5 to determine when the optimization is complete
            # For now, we'll just wait for a fixed amount of time
            optimization_time = 300  # seconds (5 minutes)
            logger.info(f"Waiting {optimization_time} seconds for optimization to complete...")
            time.sleep(optimization_time)
            
            # Wait for MT5 to close automatically (ShutdownTerminal=1 in .ini file)
            # If it doesn't close automatically, close it manually
            close_wait_time = 60  # seconds
            logger.info(f"Waiting {close_wait_time} seconds for MT5 to close automatically...")
            time.sleep(close_wait_time)
            
            # Close MT5 after optimization if it's still running
            if self.is_mt5_running():
                logger.info("MT5 is still running, closing it manually")
                self.close_mt5()
            
            # Check for results files
            results_files = []
            for ext in ['.xml', '.html', '.csv', '.txt']:
                results_files.extend(list(Path(output_dir).glob(f"*{ext}")))
            
            if not results_files:
                logger.warning(f"No results files found in {output_dir}")
            else:
                logger.info(f"Found {len(results_files)} results files in {output_dir}")
            
            # Return results
            return {
                "status": "success",
                "robot_name": robot_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "output_dir": output_dir,
                "results_files": [str(f) for f in results_files]
            }
        except Exception as e:
            logger.error(f"Error running optimization: {str(e)}")
            return {"status": "error", "message": str(e)}
