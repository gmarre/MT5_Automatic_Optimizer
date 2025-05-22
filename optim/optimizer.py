"""
Optimizer Module

This module provides the Optimizer class which orchestrates the optimization process
for Expert Advisors in MetaTrader 5.
"""

import os
import json
import logging
from datetime import datetime
from .mt5_launcher import MT5Launcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mt5_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Optimizer")

class Optimizer:
    """
    Class to orchestrate the optimization process for Expert Advisors in MT5.
    """
    
    def __init__(self, config_path):
        """
        Initialize the Optimizer with a configuration file.
        
        Args:
            config_path (str): Path to the configuration JSON file
        """
        self.config_path = config_path
        self.config = None
        self.mt5_launcher = None
        
        # Load configuration
        self._load_config()
        
        # Initialize MT5 launcher
        if self.config:
            self.mt5_launcher = MT5Launcher(
                self.config["mt5_path"],
                self.config["output_directory"]
            )
        
        logger.info("Optimizer initialized")
    
    def _load_config(self):
        """
        Load the configuration from the JSON file.
        
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def run_all_optimizations(self):
        """
        Run all optimizations defined in the configuration.
        
        Returns:
            dict: Summary of optimization results
        """
        if not self.config or not self.mt5_launcher:
            logger.error("Configuration or MT5 launcher not initialized")
            return {"status": "error", "message": "Configuration or MT5 launcher not initialized"}
        
        results = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "robots": [],
            "status": "success"
        }
        
        try:
            # Iterate through each robot in the configuration
            for robot in self.config["robots"]:
                robot_results = {
                    "name": robot["name"],
                    "optimizations": []
                }
                
                # Launch MT5 once per robot to avoid repeated launches
                if not self.mt5_launcher.launch_mt5():
                    logger.error(f"Failed to launch MT5 for robot {robot['name']}")
                    robot_results["status"] = "error"
                    robot_results["message"] = "Failed to launch MT5"
                    results["robots"].append(robot_results)
                    continue
                
                # Process each optimization for this robot
                for optim in robot["optimizations"]:
                    optim_results = {
                        "symbol": optim["symbol"],
                        "timeframe": optim["timeframe"],
                        "periods": []
                    }
                    
                    # Process each period for this optimization
                    for period in optim["periods"]:
                        period_result = {
                            "name": period["name"],
                            "type": period["type"],
                            "from_date": period["from_date"],
                            "to_date": period["to_date"]
                        }
                        
                        # Run the optimization for this period
                        success = self.mt5_launcher.run_optimization(
                            robot_name=robot["name"],
                            set_file=robot["set_file"],
                            symbol=optim["symbol"],
                            timeframe=optim["timeframe"],
                            from_date=period["from_date"],
                            to_date=period["to_date"],
                            leverage=optim.get("leverage", 100),
                            model=optim.get("model", 1),
                            initial_deposit=optim.get("initial_deposit", 10000),
                            optimization_type=optim.get("optimization_type", "genetic"),
                            period_name=period["name"],
                            period_type=period["type"]
                        )
                        
                        period_result["status"] = "success" if success else "error"
                        optim_results["periods"].append(period_result)
                    
                    robot_results["optimizations"].append(optim_results)
                
                # Close MT5 after processing all optimizations for this robot
                self.mt5_launcher.close_mt5()
                
                results["robots"].append(robot_results)
            
            results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save summary to file
            summary_path = os.path.join(self.config["output_directory"], "optimization_summary.json")
            with open(summary_path, "w") as f:
                json.dump(results, f, indent=4)
            
            logger.info(f"All optimizations completed. Summary saved to {summary_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error running optimizations: {str(e)}")
            results["status"] = "error"
            results["message"] = str(e)
            return results
    
    def run_specific_optimization(self, robot_name, symbol=None, timeframe=None, period_name=None):
        """
        Run a specific optimization based on filters.
        
        Args:
            robot_name (str): Name of the robot to optimize
            symbol (str, optional): Symbol to filter by
            timeframe (str, optional): Timeframe to filter by
            period_name (str, optional): Period name to filter by
            
        Returns:
            dict: Summary of optimization results
        """
        if not self.config or not self.mt5_launcher:
            logger.error("Configuration or MT5 launcher not initialized")
            return {"status": "error", "message": "Configuration or MT5 launcher not initialized"}
        
        results = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "robot": robot_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period_name,
            "optimizations": [],
            "status": "success"
        }
        
        try:
            # Find the robot in the configuration
            robot = next((r for r in self.config["robots"] if r["name"] == robot_name), None)
            if not robot:
                logger.error(f"Robot {robot_name} not found in configuration")
                results["status"] = "error"
                results["message"] = f"Robot {robot_name} not found in configuration"
                return results
            
            # Launch MT5
            if not self.mt5_launcher.launch_mt5():
                logger.error(f"Failed to launch MT5 for robot {robot_name}")
                results["status"] = "error"
                results["message"] = "Failed to launch MT5"
                return results
            
            # Filter optimizations based on parameters
            for optim in robot["optimizations"]:
                if symbol and optim["symbol"] != symbol:
                    continue
                if timeframe and optim["timeframe"] != timeframe:
                    continue
                
                optim_result = {
                    "symbol": optim["symbol"],
                    "timeframe": optim["timeframe"],
                    "periods": []
                }
                
                # Filter periods based on parameters
                for period in optim["periods"]:
                    if period_name and period["name"] != period_name:
                        continue
                    
                    period_result = {
                        "name": period["name"],
                        "type": period["type"],
                        "from_date": period["from_date"],
                        "to_date": period["to_date"]
                    }
                    
                    # Run the optimization for this period
                    success = self.mt5_launcher.run_optimization(
                        robot_name=robot["name"],
                        set_file=robot["set_file"],
                        symbol=optim["symbol"],
                        timeframe=optim["timeframe"],
                        from_date=period["from_date"],
                        to_date=period["to_date"],
                        leverage=optim.get("leverage", 100),
                        model=optim.get("model", 1),
                        initial_deposit=optim.get("initial_deposit", 10000),
                        optimization_type=optim.get("optimization_type", "genetic"),
                        period_name=period["name"],
                        period_type=period["type"]
                    )
                    
                    period_result["status"] = "success" if success else "error"
                    optim_result["periods"].append(period_result)
                
                if optim_result["periods"]:
                    results["optimizations"].append(optim_result)
            
            # Close MT5
            self.mt5_launcher.close_mt5()
            
            results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if not results["optimizations"]:
                logger.warning(f"No matching optimizations found for the specified filters")
                results["status"] = "warning"
                results["message"] = "No matching optimizations found for the specified filters"
            else:
                logger.info(f"Specific optimizations completed")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running specific optimization: {str(e)}")
            results["status"] = "error"
            results["message"] = str(e)
            return results


# Example usage
if __name__ == "__main__":
    optimizer = Optimizer("../config/optimization_config.json")
    results = optimizer.run_all_optimizations()
    print(f"Optimization completed with status: {results['status']}")
