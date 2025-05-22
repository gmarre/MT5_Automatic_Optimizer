"""
Results Parser Module

This module provides functionality to parse and extract data from MetaTrader 5
optimization result files in various formats (XML, HTML, CSV).
"""

import os
import csv
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mt5_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ResultsParser")

class ResultsParser:
    """
    Class to parse and extract data from MetaTrader 5 optimization result files.
    """
    
    def __init__(self, results_dir="results"):
        """
        Initialize the ResultsParser with the path to the results directory.
        
        Args:
            results_dir (str): Path to the directory containing optimization results
        """
        self.results_dir = results_dir
        logger.info(f"ResultsParser initialized with results directory: {results_dir}")
    
    def parse_results(self, robot_name=None, symbol=None, timeframe=None, period_name=None):
        """
        Parse all results matching the specified filters.
        
        Args:
            robot_name (str, optional): Filter by robot name
            symbol (str, optional): Filter by symbol
            timeframe (str, optional): Filter by timeframe
            period_name (str, optional): Filter by period name
            
        Returns:
            dict: Dictionary containing parsed results
        """
        results = {
            "robot_name": robot_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "period_name": period_name,
            "results": []
        }
        
        try:
            # Walk through the results directory
            for root, dirs, files in os.walk(self.results_dir):
                # Skip the root directory itself
                if root == self.results_dir:
                    continue
                
                # Extract information from directory path
                path_parts = os.path.relpath(root, self.results_dir).split(os.sep)
                if len(path_parts) < 1:
                    continue
                
                # Parse directory name to extract symbol, timeframe, and period
                dir_name = path_parts[0]
                dir_parts = dir_name.split("_")
                
                if len(dir_parts) < 3:
                    logger.warning(f"Directory name format not recognized: {dir_name}")
                    continue
                
                current_symbol = dir_parts[0]
                current_timeframe = dir_parts[1]
                current_period = "_".join(dir_parts[2:])
                
                # Apply filters
                if symbol and current_symbol != symbol:
                    continue
                if timeframe and current_timeframe != timeframe:
                    continue
                if period_name and current_period != period_name:
                    continue
                
                # Process files in this directory
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # Extract robot name from filename
                    current_robot = file.split("_")[0]
                    if robot_name and current_robot != robot_name:
                        continue
                    
                    # Parse file based on extension
                    parsed_data = None
                    if file_ext == ".xml":
                        parsed_data = self._parse_xml(file_path)
                    elif file_ext == ".html":
                        parsed_data = self._parse_html(file_path)
                    elif file_ext == ".csv":
                        parsed_data = self._parse_csv(file_path)
                    
                    if parsed_data:
                        parsed_data["file_path"] = file_path
                        parsed_data["robot_name"] = current_robot
                        parsed_data["symbol"] = current_symbol
                        parsed_data["timeframe"] = current_timeframe
                        parsed_data["period_name"] = current_period
                        results["results"].append(parsed_data)
            
            logger.info(f"Parsed {len(results['results'])} result files")
            return results
            
        except Exception as e:
            logger.error(f"Error parsing results: {str(e)}")
            return results
    
    def _parse_xml(self, file_path):
        """
        Parse an XML result file from MT5.
        
        Args:
            file_path (str): Path to the XML file
            
        Returns:
            dict: Parsed data or None if parsing failed
        """
        try:
            logger.info(f"Parsing XML file: {file_path}")
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract optimization passes
            passes = []
            for pass_elem in root.findall(".//Pass"):
                pass_data = {}
                
                # Extract pass attributes
                for attr in pass_elem.attrib:
                    pass_data[attr] = pass_elem.attrib[attr]
                
                # Extract parameters
                parameters = {}
                for param in pass_elem.findall(".//Param"):
                    param_name = param.attrib.get("name", "unknown")
                    param_value = param.attrib.get("value", "0")
                    parameters[param_name] = param_value
                
                pass_data["parameters"] = parameters
                passes.append(pass_data)
            
            # Extract summary information
            summary = {}
            summary_elem = root.find(".//Summary")
            if summary_elem is not None:
                for attr in summary_elem.attrib:
                    summary[attr] = summary_elem.attrib[attr]
            
            return {
                "format": "xml",
                "passes": passes,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error parsing XML file {file_path}: {str(e)}")
            return None
    
    def _parse_html(self, file_path):
        """
        Parse an HTML result file from MT5.
        
        Args:
            file_path (str): Path to the HTML file
            
        Returns:
            dict: Parsed data or None if parsing failed
        """
        try:
            logger.info(f"Parsing HTML file: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract table data
            passes = []
            table = soup.find("table")
            if table:
                headers = []
                header_row = table.find("tr")
                if header_row:
                    headers = [th.text.strip() for th in header_row.find_all("th")]
                
                for row in table.find_all("tr")[1:]:  # Skip header row
                    cells = row.find_all("td")
                    if cells:
                        pass_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                pass_data[headers[i]] = cell.text.strip()
                        passes.append(pass_data)
            
            # Extract summary information
            summary = {}
            summary_div = soup.find("div", class_="summary")
            if summary_div:
                for p in summary_div.find_all("p"):
                    key_value = p.text.split(":", 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        summary[key] = value
            
            return {
                "format": "html",
                "passes": passes,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error parsing HTML file {file_path}: {str(e)}")
            return None
    
    def _parse_csv(self, file_path):
        """
        Parse a CSV result file from MT5.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            dict: Parsed data or None if parsing failed
        """
        try:
            logger.info(f"Parsing CSV file: {file_path}")
            
            # Read CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to list of dictionaries
            passes = df.to_dict(orient="records")
            
            # Extract summary information from header rows if present
            summary = {}
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i >= 3:  # Assuming first 3 rows might contain summary info
                        break
                    if len(row) >= 2 and not row[0].isdigit():
                        key = row[0].strip()
                        if key and key[0].isalpha():  # Skip if not starting with letter
                            summary[key] = row[1].strip() if len(row) > 1 else ""
            
            return {
                "format": "csv",
                "passes": passes,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
            return None
    
    def convert_to_dataframe(self, parsed_results):
        """
        Convert parsed results to a pandas DataFrame for easier analysis.
        
        Args:
            parsed_results (dict): Results from parse_results method
            
        Returns:
            pandas.DataFrame: DataFrame containing all passes from all results
        """
        try:
            all_passes = []
            
            for result in parsed_results["results"]:
                for pass_data in result["passes"]:
                    # Create a copy of the pass data
                    pass_copy = pass_data.copy()
                    
                    # Add metadata
                    pass_copy["robot_name"] = result["robot_name"]
                    pass_copy["symbol"] = result["symbol"]
                    pass_copy["timeframe"] = result["timeframe"]
                    pass_copy["period_name"] = result["period_name"]
                    
                    # Handle parameters if they exist in a nested dictionary
                    if "parameters" in pass_copy and isinstance(pass_copy["parameters"], dict):
                        for param_name, param_value in pass_copy["parameters"].items():
                            pass_copy[f"param_{param_name}"] = param_value
                        del pass_copy["parameters"]
                    
                    all_passes.append(pass_copy)
            
            # Convert to DataFrame
            if all_passes:
                df = pd.DataFrame(all_passes)
                logger.info(f"Converted {len(all_passes)} passes to DataFrame")
                return df
            else:
                logger.warning("No passes found to convert to DataFrame")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error converting to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def export_to_csv(self, parsed_results, output_path):
        """
        Export parsed results to a CSV file.
        
        Args:
            parsed_results (dict): Results from parse_results method
            output_path (str): Path to save the CSV file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            df = self.convert_to_dataframe(parsed_results)
            if df.empty:
                logger.warning("No data to export")
                return False
            
            df.to_csv(output_path, index=False)
            logger.info(f"Results exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def export_to_json(self, parsed_results, output_path):
        """
        Export parsed results to a JSON file.
        
        Args:
            parsed_results (dict): Results from parse_results method
            output_path (str): Path to save the JSON file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            with open(output_path, "w") as f:
                json.dump(parsed_results, f, indent=4)
            
            logger.info(f"Results exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    parser = ResultsParser("../results")
    results = parser.parse_results()
    
    # Export to CSV
    parser.export_to_csv(results, "../results/combined_results.csv")
    
    # Export to JSON
    parser.export_to_json(results, "../results/combined_results.json")
