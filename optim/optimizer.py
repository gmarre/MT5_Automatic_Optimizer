"""
Optimizer Module

This module provides functionality to manage optimizations.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path

# Configure logging
logger = logging.getLogger("Optimizer")

class Optimizer:
    """
    Class to manage optimizations.
    """
    
    def __init__(self, config_path):
        """
        Initialize the optimizer.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config_path = config_path
        self.config = None
        self.mt5_launcher = None
        
        # Load configuration
        self.load_config()
        
        logger.info(f"Optimizer initialized with configuration from {config_path}")
    
    def load_config(self):
        """
        Load configuration from file.
        
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
            
            # Initialize MT5 launcher
            from optim.mt5_launcher import MT5Launcher
            self.mt5_launcher = MT5Launcher(
                self.config.get("mt5_path", "C:\\Program Files\\IC Trading (MU) MT5 Terminal\\terminal64.exe"),
                self.config.get("output_directory", "results")
            )
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def run_all_optimizations(self):
        """
        Run all optimizations.
        
        Returns:
            dict: Results of the optimizations
        """
        try:
            # Check if configuration is loaded
            if not self.config:
                logger.error("Configuration not loaded")
                return {"status": "error", "message": "Configuration not loaded"}
            
            # Get robots
            robots = self.config.get("robots", [])
            if not robots:
                logger.error("No robots found in configuration")
                return {"status": "error", "message": "No robots found in configuration"}
            
            # Run optimizations for each robot
            results = []
            for robot in robots:
                robot_results = self.run_robot_optimization(robot["name"])
                if robot_results["status"] == "error":
                    return robot_results
                results.append(robot_results)
            
            # Return results
            return {
                "status": "success",
                "results": results
            }
        except Exception as e:
            logger.error(f"Error running all optimizations: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_robot_optimization(self, robot_name):
        """
        Run optimization for a specific robot.
        
        Args:
            robot_name (str): Name of the robot
        
        Returns:
            dict: Results of the optimization
        """
        try:
            # Check if configuration is loaded
            if not self.config:
                logger.error("Configuration not loaded")
                return {"status": "error", "message": "Configuration not loaded"}
            
            # Find the robot
            robot = None
            for r in self.config.get("robots", []):
                if r["name"] == robot_name:
                    robot = r
                    break
            
            if not robot:
                logger.error(f"Robot {robot_name} not found in configuration")
                return {"status": "error", "message": f"Robot {robot_name} not found in configuration"}
            
            # Get optimizations
            optimizations = robot.get("optimizations", [])
            if not optimizations:
                logger.error(f"No optimizations found for robot {robot_name}")
                return {"status": "error", "message": f"No optimizations found for robot {robot_name}"}
            
            # Run optimizations for each symbol and timeframe
            results = []
            for optimization in optimizations:
                symbol = optimization.get("symbol")
                timeframe = optimization.get("timeframe")
                
                if not symbol or not timeframe:
                    logger.error(f"Symbol or timeframe not specified for robot {robot_name}")
                    continue
                
                optimization_results = self.run_symbol_optimization(robot_name, symbol, timeframe)
                if optimization_results["status"] == "error":
                    return optimization_results
                results.append(optimization_results)
            
            # Return results
            return {
                "status": "success",
                "robot_name": robot_name,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error running optimization for robot {robot_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_symbol_optimization(self, robot_name, symbol, timeframe):
        """
        Run optimization for a specific robot, symbol, and timeframe.
        
        Args:
            robot_name (str): Name of the robot
            symbol (str): Symbol to optimize
            timeframe (str): Timeframe to optimize
        
        Returns:
            dict: Results of the optimization
        """
        try:
            # Check if configuration is loaded
            if not self.config:
                logger.error("Configuration not loaded")
                return {"status": "error", "message": "Configuration not loaded"}
            
            # Find the robot
            robot = None
            for r in self.config.get("robots", []):
                if r["name"] == robot_name:
                    robot = r
                    break
            
            if not robot:
                logger.error(f"Robot {robot_name} not found in configuration")
                return {"status": "error", "message": f"Robot {robot_name} not found in configuration"}
            
            # Find the optimization
            optimization = None
            for o in robot.get("optimizations", []):
                if o.get("symbol") == symbol and o.get("timeframe") == timeframe:
                    optimization = o
                    break
            
            if not optimization:
                logger.error(f"Optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe} not found in configuration")
                return {"status": "error", "message": f"Optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe} not found in configuration"}
            
            # Get periods
            periods = optimization.get("periods", [])
            if not periods:
                logger.error(f"No periods found for robot {robot_name}, symbol {symbol}, timeframe {timeframe}")
                return {"status": "error", "message": f"No periods found for robot {robot_name}, symbol {symbol}, timeframe {timeframe}"}
            
            # Run optimizations for each period
            results = []
            for period in periods:
                period_name = period.get("name")
                period_type = period.get("type")
                from_date = period.get("from_date")
                to_date = period.get("to_date")
                
                if not period_name or not period_type or not from_date or not to_date:
                    logger.error(f"Period not properly specified for robot {robot_name}, symbol {symbol}, timeframe {timeframe}")
                    continue
                
                # Run optimization
                period_results = self.mt5_launcher.run_optimization(
                    robot_name=robot_name,
                    symbol=symbol,
                    timeframe=timeframe,
                    period=period,
                    optimization_type=optimization.get("optimization_type", "genetic"),
                    leverage=optimization.get("leverage", 500),
                    model=optimization.get("model", 1),
                    initial_deposit=optimization.get("initial_deposit", 10000),
                    set_file=robot.get("set_file")
                )
                
                if period_results["status"] == "error":
                    return period_results
                
                results.append(period_results)
            
            # Return results
            return {
                "status": "success",
                "robot_name": robot_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error running optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe}: {str(e)}")
            return {"status": "error", "message": str(e)}
