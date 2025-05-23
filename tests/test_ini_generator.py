"""
Test INI Generator

This script tests the INI Generator module.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from optim.ini_generator import INIGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_ini_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestINIGenerator")

def main():
    """
    Main function.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test the INI Generator module.')
    parser.add_argument('--robot', type=str, required=True,
                        help='Path to the robot (EA) file')
    parser.add_argument('--symbol', type=str, default="EURUSD",
                        help='Symbol to optimize')
    parser.add_argument('--timeframe', type=str, default="H1",
                        help='Timeframe to optimize (e.g., H1, M15, D1)')
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
    parser.add_argument('--output_file', type=str, default="test_optimization.ini",
                        help='Name of the output .ini file')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate .ini file
    output_path = os.path.join(args.output_dir, args.output_file)
    
    logger.info(f"Generating .ini file for robot {args.robot}, symbol {args.symbol}, timeframe {args.timeframe}")
    
    ini_file = INIGenerator.generate_optimization_ini(
        output_path=output_path,
        robot_name=args.robot,
        symbol=args.symbol,
        timeframe=args.timeframe,
        from_date=args.from_date,
        to_date=args.to_date,
        is_forward=args.forward,
        optimization_type=args.optimization_type,
        model=args.model,
        deposit=args.deposit,
        leverage=args.leverage,
        set_file=args.set_file,
        report_file=f"report_{os.path.basename(args.robot).replace('.ex5', '')}_{args.symbol}_{args.timeframe}"
    )
    
    if ini_file:
        logger.info(f"INI file generated successfully at {ini_file}")
        
        # Print the content of the .ini file
        try:
            with open(ini_file, 'r') as f:
                content = f.read()
            
            logger.info("INI file content:")
            logger.info(content)
        except Exception as e:
            logger.error(f"Error reading .ini file: {str(e)}")
    else:
        logger.error("Failed to generate .ini file")
    
    # If a .set file was provided, parse it and print the parameters
    if args.set_file and os.path.exists(args.set_file):
        logger.info(f"Parsing .set file: {args.set_file}")
        
        parameters = INIGenerator.parse_set_file(args.set_file)
        
        if parameters:
            logger.info(f"Parsed {len(parameters)} parameters from .set file")
            
            # Print the parameters
            for key, value in parameters.items():
                logger.info(f"{key} = {value}")
        else:
            logger.error("Failed to parse .set file or no parameters found")

if __name__ == "__main__":
    main()
