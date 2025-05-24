"""
INI Generator Module

This module provides functionality to generate .ini files for MT5 optimizations.
"""

import os
import sys
import logging
import re
from pathlib import Path

# Configure logging
logger = logging.getLogger("INIGenerator")

class INIGenerator:
    """
    Class to generate .ini files for MT5 optimizations.
    """
    
    @staticmethod
    def generate_optimization_ini(output_path, robot_name, symbol, timeframe, from_date, to_date, 
                                 is_forward=False, optimization_type=2, optimization_criterion=3,model=2, deposit=5000, 
                                 leverage=500, set_file=None, report_file=None):
        """
        Generate an .ini file for MT5 optimization.
        
        Args:
            output_path (str): Path to save the .ini file
            robot_name (str): Name of the robot (EA)
            symbol (str): Symbol to optimize
            timeframe (str): Timeframe to optimize (e.g., "H1", "M15")
            from_date (str): Start date in format "YYYY.MM.DD"
            to_date (str): End date in format "YYYY.MM.DD"
            is_forward (bool, optional): Whether to use forward testing. Defaults to False.
            optimization_type (int, optional): Type of optimization. Defaults to 2.
                1 = Slow complete algorithm
                2 = Fast genetic based algorithm
                3 = All symbols selected in Market Watch
            model (int, optional): Model. Defaults to 2.
                0 = Every tick
                1 = Control points
                2 = Open prices only
            deposit (int, optional): Initial deposit. Defaults to 5000.
            leverage (int, optional): Leverage. Defaults to 500.
            set_file (str, optional): Path to the .set file. Defaults to None.
            report_file (str, optional): Path to save the report file. Defaults to None.
        
        Returns:
            str: Path to the generated .ini file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get robot base name for the report file
            robot_base_name = os.path.basename(robot_name).replace(".ex5", "")
            
            # Create the .ini file content following the MT5 template format
            ini_content = f"""[Tester]
Expert={robot_name}
Symbol={symbol}
Period={timeframe}
Optimization={optimization_type}
Model={model}
FromDate={from_date}
ToDate={to_date}
ForwardMode={(2 if is_forward else 0)}
Deposit={deposit}
Leverage=1:{leverage}
OptimizationCriterion={optimization_criterion}
"""      
            # Add report file if provided
            if report_file:
                report_name = os.path.basename(report_file).replace(".html", "")
                ini_content += f"Report={report_name}\n"
                ini_content += "ReplaceReport=1\n"
            
            # Add shutdown terminal option (1 = shutdown, 0 = keep running)
            ini_content += "ShutdownTerminal=1\n"
            
            import chardet
            # [TesterInputs]
            if set_file and os.path.isfile(set_file):
                ini_content += "[TesterInputs]\n"
                # Detect file encoding
                with open(set_file, "rb") as f:
                    raw_data = f.read()
                    detected_encoding = chardet.detect(raw_data)["encoding"]

                # Read file using detected encoding
                with open(set_file, "r", encoding=detected_encoding) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith(";"):
                            ini_content += line + "\n"
                            
                            # Write the .ini file
                            with open(output_path, 'w') as f:
                                f.write(ini_content)
            
            logger.info(f"Generated optimization .ini file at {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error generating optimization .ini file: {str(e)}")
            return None
    
    @staticmethod
    def clean_parameter(param):
        """
        Clean a parameter to ensure it is properly formatted.
        
        Args:
            param (str): Parameter to clean
        
        Returns:
            str: Cleaned parameter
        """
        if not param:
            return ""
        
        # Remove spaces between characters (common issue with binary encoding)
        if ' ' in param and len(param) > 3:
            # Check if it's a parameter with spaces between each character
            if all(c == ' ' for c in param[1::2]):
                param = param.replace(" ", "")
        
        # Remove any trailing/leading whitespace
        param = param.strip()
        
        return param
    
    @staticmethod
    def parse_set_file(set_file_path):
        """
        Parse a .set file and extract parameters.
        
        Args:
            set_file_path (str): Path to the .set file
        
        Returns:
            dict: Dictionary of parameters
        """
        try:
            if not os.path.exists(set_file_path):
                logger.error(f"Set file not found: {set_file_path}")
                return {}
            
            parameters = {}
            
            with open(set_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith(';'):
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            parameters[key] = value
            
            logger.info(f"Parsed {len(parameters)} parameters from {set_file_path}")
            
            return parameters
        except Exception as e:
            logger.error(f"Error parsing .set file: {str(e)}")
            return {}
