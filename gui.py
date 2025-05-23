"""
GUI Module for MT5 Automatic Optimizer

This module provides a graphical user interface for the MT5 Automatic Optimizer.
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from threading import Thread

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optim.mt5_launcher import MT5Launcher
from optim.optimizer import Optimizer
from analysis.analyzer import Analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mt5_optimizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GUI")

class MT5OptimizerGUI:
    """
    Graphical User Interface for the MT5 Automatic Optimizer.
    """
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root (tk.Tk): The root window
        """
        self.root = root
        self.root.title("MT5 Automatic Optimizer")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.mt5_path_var = tk.StringVar()
        self.mt5_path_var.set("C:\\Program Files\\IC Trading (MU) MT5 Terminal\\terminal64.exe")
        self.config_path_var = tk.StringVar()
        self.config_path_var.set("config/optimization_config.json")
        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set("results")
        self.mt5_status_var = tk.StringVar()
        self.mt5_status_var.set("Not running")
        self.robot_var = tk.StringVar()
        self.symbol_var = tk.StringVar()
        self.timeframe_var = tk.StringVar()
        self.optimization_status_var = tk.StringVar()
        self.optimization_status_var.set("Ready")
        self.progress_var = tk.DoubleVar()
        self.analysis_robot_var = tk.StringVar()
        self.analysis_symbol_var = tk.StringVar()
        self.analysis_timeframe_var = tk.StringVar()
        self.analysis_period_var = tk.StringVar()
        self.analysis_status_var = tk.StringVar()
        self.analysis_status_var.set("Ready")
        self.max_drawdown_var = tk.DoubleVar()
        self.max_drawdown_var.set(25.0)
        self.min_profit_factor_var = tk.DoubleVar()
        self.min_profit_factor_var.set(1.5)
        self.min_expected_payoff_var = tk.DoubleVar()
        self.min_expected_payoff_var.set(10.0)
        self.min_recovery_factor_var = tk.DoubleVar()
        self.min_recovery_factor_var.set(1.0)
        self.min_trades_var = tk.IntVar()
        self.min_trades_var.set(30)
        self.max_consecutive_losses_var = tk.IntVar()
        self.max_consecutive_losses_var.set(5)
        self.min_win_rate_var = tk.DoubleVar()
        self.min_win_rate_var.set(50.0)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Initialize components
        self.mt5_launcher = None
        self.optimizer = None
        self.analyzer = None
        self.robot_combo = None
        self.symbol_combo = None
        self.timeframe_combo = None
        self.analysis_robot_combo = None
        self.analysis_symbol_combo = None
        self.analysis_timeframe_combo = None
        self.analysis_period_combo = None
        self.progress_bar = None
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create the tabs
        self.create_mt5_tab()
        self.create_optimization_tab()
        self.create_analysis_tab()
        self.create_settings_tab()
        
        # Create the status bar
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load settings
        self.load_settings()
        
        # Initialize components
        self.initialize_components()
        
        logger.info("GUI initialized")
    
    def initialize_components(self):
        """
        Initialize the components.
        """
        try:
            # Initialize MT5 launcher
            self.mt5_launcher = MT5Launcher(self.mt5_path_var.get(), "results")
            
            # Initialize optimizer
            self.optimizer = Optimizer(self.config_path_var.get())
            
            # Initialize analyzer
            self.analyzer = Analyzer("results")
            
            logger.info("Components initialized")
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            messagebox.showerror("Error", f"Error initializing components: {str(e)}")
    
    def create_mt5_tab(self):
        """
        Create the MT5 tab.
        """
        self.mt5_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mt5_tab, text="MT5")
        
        # Create the MT5 frame
        mt5_frame = ttk.LabelFrame(self.mt5_tab, text="MetaTrader 5", padding=10)
        mt5_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # MT5 path
        ttk.Label(mt5_frame, text="MT5 Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mt5_path_var = tk.StringVar()
        self.mt5_path_var.set("C:\\Program Files\\IC Trading (MU) MT5 Terminal\\terminal64.exe")
        ttk.Entry(mt5_frame, textvariable=self.mt5_path_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(mt5_frame, text="Browse...", command=self.browse_mt5_path).grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # MT5 buttons
        button_frame = ttk.Frame(mt5_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Button(button_frame, text="Launch MT5", command=self.launch_mt5).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close MT5", command=self.close_mt5).pack(side=tk.LEFT, padx=5)
        
        # MT5 status
        ttk.Label(mt5_frame, text="Status:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.mt5_status_var = tk.StringVar()
        self.mt5_status_var.set("Not running")
        ttk.Label(mt5_frame, textvariable=self.mt5_status_var).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Update MT5 status
        self.update_mt5_status()
    
    def create_optimization_tab(self):
        """
        Create the optimization tab.
        """
        self.optimization_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.optimization_tab, text="Optimization")
        
        # Create the optimization frame
        optimization_frame = ttk.LabelFrame(self.optimization_tab, text="Optimization", padding=10)
        optimization_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuration file
        ttk.Label(optimization_frame, text="Configuration File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_path_var = tk.StringVar()
        self.config_path_var.set("config/optimization_config.json")
        ttk.Entry(optimization_frame, textvariable=self.config_path_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(optimization_frame, text="Browse...", command=self.browse_config_path).grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Robot selection
        ttk.Label(optimization_frame, text="Robot:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.robot_var = tk.StringVar()
        self.robot_combo = ttk.Combobox(optimization_frame, textvariable=self.robot_var, width=30)
        self.robot_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.robot_combo.bind("<<ComboboxSelected>>", self.on_robot_selected)
        
        # Symbol selection
        ttk.Label(optimization_frame, text="Symbol:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.symbol_var = tk.StringVar()
        self.symbol_combo = ttk.Combobox(optimization_frame, textvariable=self.symbol_var, width=30)
        self.symbol_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.on_symbol_selected)
        
        # Timeframe selection
        ttk.Label(optimization_frame, text="Timeframe:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.timeframe_var = tk.StringVar()
        self.timeframe_combo = ttk.Combobox(optimization_frame, textvariable=self.timeframe_var, width=30)
        self.timeframe_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Optimization buttons
        button_frame = ttk.Frame(optimization_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Button(button_frame, text="Run All Optimizations", command=self.run_all_optimizations).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Robot Optimization", command=self.run_robot_optimization).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Symbol Optimization", command=self.run_symbol_optimization).pack(side=tk.LEFT, padx=5)
        
        # Optimization status
        ttk.Label(optimization_frame, text="Status:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.optimization_status_var = tk.StringVar()
        self.optimization_status_var.set("Ready")
        ttk.Label(optimization_frame, textvariable=self.optimization_status_var).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Progress bar
        ttk.Label(optimization_frame, text="Progress:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(optimization_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Load robots from configuration
        self.load_robots_from_config()
    
    def create_analysis_tab(self):
        """
        Create the analysis tab.
        """
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="Analysis")
        
        # Create the analysis frame
        analysis_frame = ttk.LabelFrame(self.analysis_tab, text="Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Robot selection
        ttk.Label(analysis_frame, text="Robot:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.analysis_robot_var = tk.StringVar()
        self.analysis_robot_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_robot_var, width=30)
        self.analysis_robot_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.analysis_robot_combo.bind("<<ComboboxSelected>>", self.on_analysis_robot_selected)
        
        # Symbol selection
        ttk.Label(analysis_frame, text="Symbol:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.analysis_symbol_var = tk.StringVar()
        self.analysis_symbol_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_symbol_var, width=30)
        self.analysis_symbol_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.analysis_symbol_combo.bind("<<ComboboxSelected>>", self.on_analysis_symbol_selected)
        
        # Timeframe selection
        ttk.Label(analysis_frame, text="Timeframe:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.analysis_timeframe_var = tk.StringVar()
        self.analysis_timeframe_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_timeframe_var, width=30)
        self.analysis_timeframe_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Period selection
        ttk.Label(analysis_frame, text="Period:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.analysis_period_var = tk.StringVar()
        self.analysis_period_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_period_var, width=30)
        self.analysis_period_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Analysis criteria
        criteria_frame = ttk.LabelFrame(analysis_frame, text="Analysis Criteria", padding=10)
        criteria_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)
        
        # Max drawdown
        ttk.Label(criteria_frame, text="Max Drawdown (%):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_drawdown_var = tk.DoubleVar()
        self.max_drawdown_var.set(25.0)
        ttk.Entry(criteria_frame, textvariable=self.max_drawdown_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Min profit factor
        ttk.Label(criteria_frame, text="Min Profit Factor:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.min_profit_factor_var = tk.DoubleVar()
        self.min_profit_factor_var.set(1.5)
        ttk.Entry(criteria_frame, textvariable=self.min_profit_factor_var, width=10).grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # Min expected payoff
        ttk.Label(criteria_frame, text="Min Expected Payoff:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.min_expected_payoff_var = tk.DoubleVar()
        self.min_expected_payoff_var.set(10.0)
        ttk.Entry(criteria_frame, textvariable=self.min_expected_payoff_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Min recovery factor
        ttk.Label(criteria_frame, text="Min Recovery Factor:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.min_recovery_factor_var = tk.DoubleVar()
        self.min_recovery_factor_var.set(1.0)
        ttk.Entry(criteria_frame, textvariable=self.min_recovery_factor_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Min trades
        ttk.Label(criteria_frame, text="Min Trades:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.min_trades_var = tk.IntVar()
        self.min_trades_var.set(30)
        ttk.Entry(criteria_frame, textvariable=self.min_trades_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Max consecutive losses
        ttk.Label(criteria_frame, text="Max Consecutive Losses:").grid(row=2, column=2, sticky=tk.W, pady=5)
        self.max_consecutive_losses_var = tk.IntVar()
        self.max_consecutive_losses_var.set(5)
        ttk.Entry(criteria_frame, textvariable=self.max_consecutive_losses_var, width=10).grid(row=2, column=3, sticky=tk.W, pady=5)
        
        # Min win rate
        ttk.Label(criteria_frame, text="Min Win Rate (%):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.min_win_rate_var = tk.DoubleVar()
        self.min_win_rate_var.set(50.0)
        ttk.Entry(criteria_frame, textvariable=self.min_win_rate_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Analysis buttons
        button_frame = ttk.Frame(analysis_frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Button(button_frame, text="Analyze Results", command=self.analyze_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Report", command=self.open_report).pack(side=tk.LEFT, padx=5)
        
        # Analysis status
        ttk.Label(analysis_frame, text="Status:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.analysis_status_var = tk.StringVar()
        self.analysis_status_var.set("Ready")
        ttk.Label(analysis_frame, textvariable=self.analysis_status_var).grid(row=6, column=1, sticky=tk.W, pady=5)
    
    def create_settings_tab(self):
        """
        Create the settings tab.
        """
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Create the settings frame
        settings_frame = ttk.LabelFrame(self.settings_tab, text="Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Output directory
        ttk.Label(settings_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set("results")
        ttk.Entry(settings_frame, textvariable=self.output_dir_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(settings_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Settings buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Settings", command=self.load_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Settings", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
    
    def browse_mt5_path(self):
        """
        Browse for the MT5 executable.
        """
        path = filedialog.askopenfilename(
            title="Select MT5 Executable",
            filetypes=[("Executable Files", "*.exe")]
        )
        if path:
            self.mt5_path_var.set(path)
            
            # Re-initialize MT5 launcher
            if self.mt5_launcher:
                self.mt5_launcher = MT5Launcher(self.mt5_path_var.get(), self.output_dir_var.get())
                
                # Update MT5 status
                self.update_mt5_status()
    
    def browse_config_path(self):
        """
        Browse for the configuration file.
        """
        path = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=[("JSON Files", "*.json")]
        )
        if path:
            self.config_path_var.set(path)
            
            # Re-initialize optimizer
            if self.optimizer:
                self.optimizer = Optimizer(self.config_path_var.get())
                
                # Load robots from configuration
                self.load_robots_from_config()
    
    def browse_output_dir(self):
        """
        Browse for the output directory.
        """
        path = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if path:
            self.output_dir_var.set(path)
            
            # Re-initialize components
            if self.mt5_launcher:
                self.mt5_launcher = MT5Launcher(self.mt5_path_var.get(), self.output_dir_var.get())
            
            if self.analyzer:
                self.analyzer = Analyzer(self.output_dir_var.get())
    
    def load_settings(self):
        """
        Load settings from a file.
        """
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                
                # Set values
                if "mt5_path" in settings:
                    self.mt5_path_var.set(settings["mt5_path"])
                
                if "config_path" in settings:
                    self.config_path_var.set(settings["config_path"])
                
                if "output_dir" in settings:
                    self.output_dir_var.set(settings["output_dir"])
                
                logger.info("Settings loaded")
                self.status_var.set("Settings loaded")
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            self.status_var.set(f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """
        Save settings to a file.
        """
        try:
            settings = {
                "mt5_path": self.mt5_path_var.get(),
                "config_path": self.config_path_var.get(),
                "output_dir": self.output_dir_var.get()
            }
            
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            
            logger.info("Settings saved")
            self.status_var.set("Settings saved")
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            self.status_var.set(f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """
        Reset settings to default values.
        """
        self.mt5_path_var.set("C:\\Program Files\\IC Trading (MU) MT5 Terminal\\terminal64.exe")
        self.config_path_var.set("config/optimization_config.json")
        self.output_dir_var.set("results")
        
        logger.info("Settings reset")
        self.status_var.set("Settings reset")
    
    def update_mt5_status(self):
        """
        Update the MT5 status.
        """
        if self.mt5_launcher and self.mt5_launcher.is_mt5_running():
            self.mt5_status_var.set("Running")
        else:
            self.mt5_status_var.set("Not running")
        
        # Schedule the next update
        self.root.after(1000, self.update_mt5_status)
    
    def launch_mt5(self):
        """
        Launch MT5.
        """
        try:
            if self.mt5_launcher:
                if self.mt5_launcher.launch_mt5():
                    logger.info("MT5 launched successfully")
                    self.status_var.set("MT5 launched successfully")
                else:
                    logger.error("Failed to launch MT5")
                    self.status_var.set("Failed to launch MT5")
                    messagebox.showerror("Error", "Failed to launch MT5")
        except Exception as e:
            logger.error(f"Error launching MT5: {str(e)}")
            self.status_var.set(f"Error launching MT5: {str(e)}")
            messagebox.showerror("Error", f"Error launching MT5: {str(e)}")
    
    def close_mt5(self):
        """
        Close MT5.
        """
        try:
            if self.mt5_launcher:
                if self.mt5_launcher.close_mt5():
                    logger.info("MT5 closed successfully")
                    self.status_var.set("MT5 closed successfully")
                else:
                    logger.error("Failed to close MT5")
                    self.status_var.set("Failed to close MT5")
                    messagebox.showerror("Error", "Failed to close MT5")
        except Exception as e:
            logger.error(f"Error closing MT5: {str(e)}")
            self.status_var.set(f"Error closing MT5: {str(e)}")
            messagebox.showerror("Error", f"Error closing MT5: {str(e)}")
    
    def load_robots_from_config(self):
        """
        Load robots from the configuration file.
        """
        try:
            if os.path.exists(self.config_path_var.get()):
                with open(self.config_path_var.get(), "r") as f:
                    config = json.load(f)
                
                # Get robots
                robots = [robot["name"] for robot in config.get("robots", [])]
                
                # Update robot comboboxes
                self.robot_combo["values"] = robots
                self.analysis_robot_combo["values"] = robots
                
                logger.info(f"Loaded {len(robots)} robots from configuration")
        except Exception as e:
            logger.error(f"Error loading robots from configuration: {str(e)}")
            self.status_var.set(f"Error loading robots from configuration: {str(e)}")
    
    def on_robot_selected(self, event=None):
        """
        Handle robot selection.
        """
        try:
            if os.path.exists(self.config_path_var.get()):
                with open(self.config_path_var.get(), "r") as f:
                    config = json.load(f)
                
                # Find the selected robot
                robot_name = self.robot_var.get()
                robot = None
                for r in config.get("robots", []):
                    if r["name"] == robot_name:
                        robot = r
                        break
                
                if robot:
                    # Get symbols and timeframes
                    symbols = []
                    for optimization in robot.get("optimizations", []):
                        symbol = optimization.get("symbol")
                        if symbol and symbol not in symbols:
                            symbols.append(symbol)
                    
                    # Update symbol combobox
                    self.symbol_combo["values"] = symbols
                    
                    logger.info(f"Loaded {len(symbols)} symbols for robot {robot_name}")
        except Exception as e:
            logger.error(f"Error loading symbols for robot: {str(e)}")
            self.status_var.set(f"Error loading symbols for robot: {str(e)}")
    
    def on_symbol_selected(self, event=None):
        """
        Handle symbol selection.
        """
        try:
            if os.path.exists(self.config_path_var.get()):
                with open(self.config_path_var.get(), "r") as f:
                    config = json.load(f)
                
                # Find the selected robot
                robot_name = self.robot_var.get()
                robot = None
                for r in config.get("robots", []):
                    if r["name"] == robot_name:
                        robot = r
                        break
                
                if robot:
                    # Get timeframes for the selected symbol
                    symbol = self.symbol_var.get()
                    timeframes = []
                    for optimization in robot.get("optimizations", []):
                        if optimization.get("symbol") == symbol:
                            timeframe = optimization.get("timeframe")
                            if timeframe and timeframe not in timeframes:
                                timeframes.append(timeframe)
                    
                    # Update timeframe combobox
                    self.timeframe_combo["values"] = timeframes
                    
                    logger.info(f"Loaded {len(timeframes)} timeframes for symbol {symbol}")
        except Exception as e:
            logger.error(f"Error loading timeframes for symbol: {str(e)}")
            self.status_var.set(f"Error loading timeframes for symbol: {str(e)}")
    
    def on_analysis_robot_selected(self, event=None):
        """
        Handle robot selection in the analysis tab.
        """
        try:
            if os.path.exists(self.config_path_var.get()):
                with open(self.config_path_var.get(), "r") as f:
                    config = json.load(f)
                
                # Find the selected robot
                robot_name = self.analysis_robot_var.get()
                robot = None
                for r in config.get("robots", []):
                    if r["name"] == robot_name:
                        robot = r
                        break
                
                if robot:
                    # Get symbols and timeframes
                    symbols = []
                    for optimization in robot.get("optimizations", []):
                        symbol = optimization.get("symbol")
                        if symbol and symbol not in symbols:
                            symbols.append(symbol)
                    
                    # Update symbol combobox
                    self.analysis_symbol_combo["values"] = symbols
                    
                    logger.info(f"Loaded {len(symbols)} symbols for robot {robot_name}")
        except Exception as e:
            logger.error(f"Error loading symbols for robot: {str(e)}")
            self.status_var.set(f"Error loading symbols for robot: {str(e)}")
    
    def on_analysis_symbol_selected(self, event=None):
        """
        Handle symbol selection in the analysis tab.
        """
        try:
            if os.path.exists(self.config_path_var.get()):
                with open(self.config_path_var.get(), "r") as f:
                    config = json.load(f)
                
                # Find the selected robot
                robot_name = self.analysis_robot_var.get()
                robot = None
                for r in config.get("robots", []):
                    if r["name"] == robot_name:
                        robot = r
                        break
                
                if robot:
                    # Get timeframes for the selected symbol
                    symbol = self.analysis_symbol_var.get()
                    timeframes = []
                    periods = []
                    for optimization in robot.get("optimizations", []):
                        if optimization.get("symbol") == symbol:
                            timeframe = optimization.get("timeframe")
                            if timeframe and timeframe not in timeframes:
                                timeframes.append(timeframe)
                            
                            # Get periods
                            for period in optimization.get("periods", []):
                                period_name = period.get("name")
                                if period_name and period_name not in periods:
                                    periods.append(period_name)
                    
                    # Update timeframe combobox
                    self.analysis_timeframe_combo["values"] = timeframes
                    
                    # Update period combobox
                    self.analysis_period_combo["values"] = periods
                    
                    logger.info(f"Loaded {len(timeframes)} timeframes and {len(periods)} periods for symbol {symbol}")
        except Exception as e:
            logger.error(f"Error loading timeframes and periods for symbol: {str(e)}")
            self.status_var.set(f"Error loading timeframes and periods for symbol: {str(e)}")
    
    def run_all_optimizations(self):
        """
        Run all optimizations.
        """
        try:
            # Check if optimizer is initialized
            if not self.optimizer:
                logger.error("Optimizer not initialized")
                self.status_var.set("Optimizer not initialized")
                messagebox.showerror("Error", "Optimizer not initialized")
                return
            
            # Confirm with the user
            if not messagebox.askyesno("Confirm", "Are you sure you want to run all optimizations? This may take a long time."):
                return
            
            # Update status
            self.optimization_status_var.set("Running all optimizations...")
            self.status_var.set("Running all optimizations...")
            self.progress_var.set(0)
            
            # Run optimizations in a separate thread
            thread = Thread(target=self._run_all_optimizations_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Error running all optimizations: {str(e)}")
            self.status_var.set(f"Error running all optimizations: {str(e)}")
            self.optimization_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error running all optimizations: {str(e)}")
    
    def _run_all_optimizations_thread(self):
        """
        Run all optimizations in a separate thread.
        """
        try:
            # Run all optimizations
            results = self.optimizer.run_all_optimizations()
            
            # Update status
            if results["status"] == "success":
                self.root.after(0, lambda: self.optimization_status_var.set("All optimizations completed successfully"))
                self.root.after(0, lambda: self.status_var.set("All optimizations completed successfully"))
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: messagebox.showinfo("Success", "All optimizations completed successfully"))
            else:
                self.root.after(0, lambda: self.optimization_status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error running all optimizations: {results.get('message', 'Unknown error')}"))
        except Exception as e:
            logger.error(f"Error running all optimizations: {str(e)}")
            self.root.after(0, lambda: self.status_var.set(f"Error running all optimizations: {str(e)}"))
            self.root.after(0, lambda: self.optimization_status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error running all optimizations: {str(e)}"))
    
    def run_robot_optimization(self):
        """
        Run optimization for a specific robot.
        """
        try:
            # Check if optimizer is initialized
            if not self.optimizer:
                logger.error("Optimizer not initialized")
                self.status_var.set("Optimizer not initialized")
                messagebox.showerror("Error", "Optimizer not initialized")
                return
            
            # Check if a robot is selected
            robot_name = self.robot_var.get()
            if not robot_name:
                logger.error("No robot selected")
                self.status_var.set("No robot selected")
                messagebox.showerror("Error", "No robot selected")
                return
            
            # Confirm with the user
            if not messagebox.askyesno("Confirm", f"Are you sure you want to run optimization for robot {robot_name}? This may take a long time."):
                return
            
            # Update status
            self.optimization_status_var.set(f"Running optimization for robot {robot_name}...")
            self.status_var.set(f"Running optimization for robot {robot_name}...")
            self.progress_var.set(0)
            
            # Run optimization in a separate thread
            thread = Thread(target=self._run_robot_optimization_thread, args=(robot_name,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Error running robot optimization: {str(e)}")
            self.status_var.set(f"Error running robot optimization: {str(e)}")
            self.optimization_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error running robot optimization: {str(e)}")
    
    def _run_robot_optimization_thread(self, robot_name):
        """
        Run optimization for a specific robot in a separate thread.
        """
        try:
            # Run robot optimization
            results = self.optimizer.run_robot_optimization(robot_name)
            
            # Update status
            if results["status"] == "success":
                self.root.after(0, lambda: self.optimization_status_var.set(f"Optimization for robot {robot_name} completed successfully"))
                self.root.after(0, lambda: self.status_var.set(f"Optimization for robot {robot_name} completed successfully"))
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Optimization for robot {robot_name} completed successfully"))
            else:
                self.root.after(0, lambda: self.optimization_status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error running robot optimization: {results.get('message', 'Unknown error')}"))
        except Exception as e:
            logger.error(f"Error running robot optimization: {str(e)}")
            self.root.after(0, lambda: self.status_var.set(f"Error running robot optimization: {str(e)}"))
            self.root.after(0, lambda: self.optimization_status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error running robot optimization: {str(e)}"))
    
    def run_symbol_optimization(self):
        """
        Run optimization for a specific robot, symbol, and timeframe.
        """
        try:
            # Check if optimizer is initialized
            if not self.optimizer:
                logger.error("Optimizer not initialized")
                self.status_var.set("Optimizer not initialized")
                messagebox.showerror("Error", "Optimizer not initialized")
                return
            
            # Check if a robot, symbol, and timeframe are selected
            robot_name = self.robot_var.get()
            symbol = self.symbol_var.get()
            timeframe = self.timeframe_var.get()
            
            if not robot_name:
                logger.error("No robot selected")
                self.status_var.set("No robot selected")
                messagebox.showerror("Error", "No robot selected")
                return
            
            if not symbol:
                logger.error("No symbol selected")
                self.status_var.set("No symbol selected")
                messagebox.showerror("Error", "No symbol selected")
                return
            
            if not timeframe:
                logger.error("No timeframe selected")
                self.status_var.set("No timeframe selected")
                messagebox.showerror("Error", "No timeframe selected")
                return
            
            # Confirm with the user
            if not messagebox.askyesno("Confirm", f"Are you sure you want to run optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe}? This may take a long time."):
                return
            
            # Update status
            self.optimization_status_var.set(f"Running optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe}...")
            self.status_var.set(f"Running optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe}...")
            self.progress_var.set(0)
            
            # Run optimization in a separate thread
            thread = Thread(target=self._run_symbol_optimization_thread, args=(robot_name, symbol, timeframe))
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Error running symbol optimization: {str(e)}")
            self.status_var.set(f"Error running symbol optimization: {str(e)}")
            self.optimization_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error running symbol optimization: {str(e)}")
    
    def _run_symbol_optimization_thread(self, robot_name, symbol, timeframe):
        """
        Run optimization for a specific robot, symbol, and timeframe in a separate thread.
        """
        try:
            # Run symbol optimization
            results = self.optimizer.run_symbol_optimization(robot_name, symbol, timeframe)
            
            # Update status
            if results["status"] == "success":
                self.root.after(0, lambda: self.optimization_status_var.set(f"Optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe} completed successfully"))
                self.root.after(0, lambda: self.status_var.set(f"Optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe} completed successfully"))
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Optimization for robot {robot_name}, symbol {symbol}, timeframe {timeframe} completed successfully"))
            else:
                self.root.after(0, lambda: self.optimization_status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error running symbol optimization: {results.get('message', 'Unknown error')}"))
        except Exception as e:
            logger.error(f"Error running symbol optimization: {str(e)}")
            self.root.after(0, lambda: self.status_var.set(f"Error running symbol optimization: {str(e)}"))
            self.root.after(0, lambda: self.optimization_status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error running symbol optimization: {str(e)}"))
    
    def analyze_results(self):
        """
        Analyze results.
        """
        try:
            # Check if analyzer is initialized
            if not self.analyzer:
                logger.error("Analyzer not initialized")
                self.status_var.set("Analyzer not initialized")
                messagebox.showerror("Error", "Analyzer not initialized")
                return
            
            # Check if a robot, symbol, timeframe, and period are selected
            robot_name = self.analysis_robot_var.get()
            symbol = self.analysis_symbol_var.get()
            timeframe = self.analysis_timeframe_var.get()
            period = self.analysis_period_var.get()
            
            if not robot_name:
                logger.error("No robot selected")
                self.status_var.set("No robot selected")
                messagebox.showerror("Error", "No robot selected")
                return
            
            if not symbol:
                logger.error("No symbol selected")
                self.status_var.set("No symbol selected")
                messagebox.showerror("Error", "No symbol selected")
                return
            
            if not timeframe:
                logger.error("No timeframe selected")
                self.status_var.set("No timeframe selected")
                messagebox.showerror("Error", "No timeframe selected")
                return
            
            if not period:
                logger.error("No period selected")
                self.status_var.set("No period selected")
                messagebox.showerror("Error", "No period selected")
                return
            
            # Get analysis criteria
            criteria = {
                "max_drawdown": self.max_drawdown_var.get(),
                "min_profit_factor": self.min_profit_factor_var.get(),
                "min_expected_payoff": self.min_expected_payoff_var.get(),
                "min_recovery_factor": self.min_recovery_factor_var.get(),
                "min_trades": self.min_trades_var.get(),
                "max_consecutive_losses": self.max_consecutive_losses_var.get(),
                "min_win_rate": self.min_win_rate_var.get()
            }
            
            # Update status
            self.analysis_status_var.set(f"Analyzing results for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period}...")
            self.status_var.set(f"Analyzing results for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period}...")
            
            # Run analysis in a separate thread
            thread = Thread(target=self._analyze_results_thread, args=(robot_name, symbol, timeframe, period, criteria))
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Error analyzing results: {str(e)}")
            self.status_var.set(f"Error analyzing results: {str(e)}")
            self.analysis_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error analyzing results: {str(e)}")
    
    def _analyze_results_thread(self, robot_name, symbol, timeframe, period, criteria):
        """
        Analyze results in a separate thread.
        """
        try:
            # Analyze results
            results = self.analyzer.analyze_results(robot_name, symbol, timeframe, period, "backtest", criteria)
            
            # Update status
            if results["status"] == "success":
                self.root.after(0, lambda: self.analysis_status_var.set(f"Analysis for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period} completed successfully"))
                self.root.after(0, lambda: self.status_var.set(f"Analysis for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period} completed successfully"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Analysis for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period} completed successfully"))
            else:
                self.root.after(0, lambda: self.analysis_status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error analyzing results: {results.get('message', 'Unknown error')}"))
        except Exception as e:
            logger.error(f"Error analyzing results: {str(e)}")
            self.root.after(0, lambda: self.status_var.set(f"Error analyzing results: {str(e)}"))
            self.root.after(0, lambda: self.analysis_status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error analyzing results: {str(e)}"))
    
    def generate_report(self):
        """
        Generate a report.
        """
        try:
            # Check if analyzer is initialized
            if not self.analyzer:
                logger.error("Analyzer not initialized")
                self.status_var.set("Analyzer not initialized")
                messagebox.showerror("Error", "Analyzer not initialized")
                return
            
            # Check if a robot, symbol, timeframe, and period are selected
            robot_name = self.analysis_robot_var.get()
            symbol = self.analysis_symbol_var.get()
            timeframe = self.analysis_timeframe_var.get()
            period = self.analysis_period_var.get()
            
            if not robot_name:
                logger.error("No robot selected")
                self.status_var.set("No robot selected")
                messagebox.showerror("Error", "No robot selected")
                return
            
            if not symbol:
                logger.error("No symbol selected")
                self.status_var.set("No symbol selected")
                messagebox.showerror("Error", "No symbol selected")
                return
            
            if not timeframe:
                logger.error("No timeframe selected")
                self.status_var.set("No timeframe selected")
                messagebox.showerror("Error", "No timeframe selected")
                return
            
            if not period:
                logger.error("No period selected")
                self.status_var.set("No period selected")
                messagebox.showerror("Error", "No period selected")
                return
            
            # Get analysis criteria
            criteria = {
                "max_drawdown": self.max_drawdown_var.get(),
                "min_profit_factor": self.min_profit_factor_var.get(),
                "min_expected_payoff": self.min_expected_payoff_var.get(),
                "min_recovery_factor": self.min_recovery_factor_var.get(),
                "min_trades": self.min_trades_var.get(),
                "max_consecutive_losses": self.max_consecutive_losses_var.get(),
                "min_win_rate": self.min_win_rate_var.get()
            }
            
            # Update status
            self.analysis_status_var.set(f"Generating report for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period}...")
            self.status_var.set(f"Generating report for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period}...")
            
            # Generate report in a separate thread
            thread = Thread(target=self._generate_report_thread, args=(robot_name, symbol, timeframe, period, criteria))
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            self.status_var.set(f"Error generating report: {str(e)}")
            self.analysis_status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
    
    def _generate_report_thread(self, robot_name, symbol, timeframe, period, criteria):
        """
        Generate a report in a separate thread.
        """
        try:
            # Generate report
            results = self.analyzer.generate_report(robot_name, symbol, timeframe, period, "backtest", criteria)
            
            # Update status
            if results["status"] == "success":
                self.root.after(0, lambda: self.analysis_status_var.set(f"Report for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period} generated successfully"))
                self.root.after(0, lambda: self.status_var.set(f"Report for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period} generated successfully"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Report for robot {robot_name}, symbol {symbol}, timeframe {timeframe}, period {period} generated successfully"))
                
                # Store report file
                self.report_file = results["report_file"]
            else:
                self.root.after(0, lambda: self.analysis_status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: self.status_var.set(f"Error: {results.get('message', 'Unknown error')}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error generating report: {results.get('message', 'Unknown error')}"))
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            self.root.after(0, lambda: self.status_var.set(f"Error generating report: {str(e)}"))
            self.root.after(0, lambda: self.analysis_status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error generating report: {str(e)}"))
    
    def open_report(self):
        """
        Open a report.
        """
        try:
            # Check if a report file exists
            if hasattr(self, 'report_file') and os.path.exists(self.report_file):
                # Open the report file
                import webbrowser
                webbrowser.open(self.report_file)
                
                logger.info(f"Opened report file: {self.report_file}")
                self.status_var.set(f"Opened report file: {self.report_file}")
            else:
                logger.error("No report file available")
                self.status_var.set("No report file available")
                messagebox.showerror("Error", "No report file available. Please generate a report first.")
        except Exception as e:
            logger.error(f"Error opening report: {str(e)}")
            self.status_var.set(f"Error opening report: {str(e)}")
            messagebox.showerror("Error", f"Error opening report: {str(e)}")
