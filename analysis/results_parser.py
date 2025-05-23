"""
Results Parser Module

This module provides functionality to parse optimization results.
"""

import os
import sys
import json
import logging
import xml.etree.ElementTree as ET
import csv
import re
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger("ResultsParser")

class ResultsParser:
    """
    Class to parse optimization results.
    """
    
    def __init__(self, results_dir):
        """
        Initialize the results parser.
        
        Args:
            results_dir (str): Directory containing the results
        """
        self.results_dir = results_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
        
        logger.info(f"Results Parser initialized with results directory: {results_dir}")
    
    def parse_results(self, robot_name, symbol, timeframe, period_name, period_type):
        """
        Parse results for a specific robot, symbol, timeframe, and period.
        
        Args:
            robot_name (str): Name of the robot
            symbol (str): Symbol
            timeframe (str): Timeframe
            period_name (str): Name of the period
            period_type (str): Type of the period (backtest or forwardtest)
        
        Returns:
            dict: Parsed results
        """
        try:
            # Get robot base name
            robot_base_name = os.path.basename(robot_name).replace(".ex5", "")
            
            # Get results directory
            results_dir = os.path.join(self.results_dir, f"{robot_base_name}_{symbol}_{timeframe}_{period_name}_{period_type}")
            
            if not os.path.exists(results_dir):
                logger.error(f"Results directory not found: {results_dir}")
                return {"status": "error", "message": f"Results directory not found: {results_dir}"}
            
            # Find results files
            results_files = {}
            
            # Find XML files
            xml_files = list(Path(results_dir).glob("*.xml"))
            for xml_file in xml_files:
                results_files[xml_file.name] = {"type": "xml", "path": str(xml_file)}
            
            # Find HTML files
            html_files = list(Path(results_dir).glob("*.html"))
            for html_file in html_files:
                results_files[html_file.name] = {"type": "html", "path": str(html_file)}
            
            # Find CSV files
            csv_files = list(Path(results_dir).glob("*.csv"))
            for csv_file in csv_files:
                results_files[csv_file.name] = {"type": "csv", "path": str(csv_file)}
            
            # Find TXT files
            txt_files = list(Path(results_dir).glob("*.txt"))
            for txt_file in txt_files:
                results_files[txt_file.name] = {"type": "txt", "path": str(txt_file)}
            
            if not results_files:
                logger.error(f"No results files found in {results_dir}")
                return {"status": "error", "message": f"No results files found in {results_dir}"}
            
            # Parse results files
            parsed_results = {}
            
            for file_name, file_info in results_files.items():
                file_type = file_info["type"]
                file_path = file_info["path"]
                
                if file_type == "xml":
                    parsed_results[file_name] = self.parse_xml_file(file_path)
                elif file_type == "html":
                    parsed_results[file_name] = self.parse_html_file(file_path)
                elif file_type == "csv":
                    parsed_results[file_name] = self.parse_csv_file(file_path)
                elif file_type == "txt":
                    parsed_results[file_name] = self.parse_txt_file(file_path)
            
            # Return results
            return {
                "status": "success",
                "robot_name": robot_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "period_name": period_name,
                "period_type": period_type,
                "results_dir": results_dir,
                "results": parsed_results
            }
        except Exception as e:
            logger.error(f"Error parsing results: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def parse_xml_file(self, file_path):
        """
        Parse an XML file.
        
        Args:
            file_path (str): Path to the XML file
        
        Returns:
            dict: Parsed results
        """
        try:
            # Parse XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract passes
            passes = []
            
            for pass_element in root.findall(".//Pass"):
                pass_data = {}
                
                for child in pass_element:
                    pass_data[child.tag] = child.text
                
                passes.append(pass_data)
            
            # Extract parameters
            parameters = {}
            
            for param_element in root.findall(".//Inputs/Parameter"):
                param_name = param_element.get("name")
                param_value = param_element.get("value")
                
                if param_name and param_value:
                    parameters[param_name] = param_value
            
            # Extract optimization settings
            settings = {}
            
            for setting_element in root.findall(".//Settings/Setting"):
                setting_name = setting_element.get("name")
                setting_value = setting_element.get("value")
                
                if setting_name and setting_value:
                    settings[setting_name] = setting_value
            
            # Return results
            return {
                "type": "xml",
                "passes": passes,
                "parameters": parameters,
                "settings": settings
            }
        except Exception as e:
            logger.error(f"Error parsing XML file {file_path}: {str(e)}")
            return {"type": "xml", "error": str(e)}
    
    def parse_html_file(self, file_path):
        """
        Parse an HTML file.
        
        Args:
            file_path (str): Path to the HTML file
        
        Returns:
            dict: Parsed results
        """
        try:
            # Read HTML file
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Extract passes using regular expressions
            passes = []
            
            # Find the table with the passes
            table_pattern = r"<table[^>]*>(.*?)</table>"
            table_match = re.search(table_pattern, html_content, re.DOTALL)
            
            if table_match:
                table_content = table_match.group(1)
                
                # Find the header row
                header_pattern = r"<tr[^>]*>(.*?)</tr>"
                header_match = re.search(header_pattern, table_content, re.DOTALL)
                
                if header_match:
                    header_content = header_match.group(1)
                    
                    # Extract header columns
                    header_columns = []
                    
                    for th_match in re.finditer(r"<th[^>]*>(.*?)</th>", header_content, re.DOTALL):
                        header_columns.append(th_match.group(1).strip())
                    
                    # Find the data rows
                    for tr_match in re.finditer(r"<tr[^>]*>(.*?)</tr>", table_content, re.DOTALL):
                        row_content = tr_match.group(1)
                        
                        # Extract row columns
                        row_columns = []
                        
                        for td_match in re.finditer(r"<td[^>]*>(.*?)</td>", row_content, re.DOTALL):
                            row_columns.append(td_match.group(1).strip())
                        
                        # Create pass data
                        if len(row_columns) == len(header_columns):
                            pass_data = {}
                            
                            for i in range(len(header_columns)):
                                pass_data[header_columns[i]] = row_columns[i]
                            
                            passes.append(pass_data)
            
            # Return results
            return {
                "type": "html",
                "passes": passes
            }
        except Exception as e:
            logger.error(f"Error parsing HTML file {file_path}: {str(e)}")
            return {"type": "html", "error": str(e)}
    
    def parse_csv_file(self, file_path):
        """
        Parse a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
        
        Returns:
            dict: Parsed results
        """
        try:
            # Read CSV file
            passes = []
            
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                csv_reader = csv.DictReader(f)
                
                for row in csv_reader:
                    passes.append(dict(row))
            
            # Return results
            return {
                "type": "csv",
                "passes": passes
            }
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
            return {"type": "csv", "error": str(e)}
    
    def parse_txt_file(self, file_path):
        """
        Parse a TXT file.
        
        Args:
            file_path (str): Path to the TXT file
        
        Returns:
            dict: Parsed results
        """
        try:
            # Read TXT file
            with open(file_path, "r", encoding="utf-8") as f:
                txt_content = f.read()
            
            # Return results
            return {
                "type": "txt",
                "content": txt_content
            }
        except Exception as e:
            logger.error(f"Error parsing TXT file {file_path}: {str(e)}")
            return {"type": "txt", "error": str(e)}
    
    def get_all_results(self):
        """
        Get all results.
        
        Returns:
            dict: All results
        """
        try:
            # Get all subdirectories in the results directory
            results = {}
            
            for subdir in os.listdir(self.results_dir):
                subdir_path = os.path.join(self.results_dir, subdir)
                
                if os.path.isdir(subdir_path):
                    # Parse the directory name to get robot, symbol, timeframe, period name, and period type
                    parts = subdir.split("_")
                    
                    if len(parts) >= 5:
                        robot_name = "_".join(parts[:-4])
                        symbol = parts[-4]
                        timeframe = parts[-3]
                        period_name = parts[-2]
                        period_type = parts[-1]
                        
                        # Parse results
                        results[subdir] = self.parse_results(robot_name, symbol, timeframe, period_name, period_type)
            
            # Return results
            return {
                "status": "success",
                "results": results
            }
        except Exception as e:
            logger.error(f"Error getting all results: {str(e)}")
            return {"status": "error", "message": str(e)}
