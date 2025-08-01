#!/usr/bin/env python3
"""
SafeData Pipeline - GUI Application
Government of India - Ministry of Electronics and IT
Standalone desktop application for data privacy and anonymization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import json
import os
from datetime import datetime
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Import core modules
from core.data_handler import DataHandler
from core.risk_assessment import RiskAssessment
from core.privacy_enhancement import PrivacyEnhancement
from core.utility_measurement import UtilityMeasurement
from core.report_generator import ReportGenerator

class SafeDataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SafeData Pipeline - Government of India")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')
        
        # Initialize data storage
        self.current_data = None
        self.processed_data = None
        self.risk_results = None
        self.utility_results = None
        self.config = {}
        
        # Initialize core modules
        self.data_handler = DataHandler()
        self.risk_assessment = RiskAssessment()
        self.privacy_enhancement = PrivacyEnhancement()
        self.utility_measurement = UtilityMeasurement()
        self.report_generator = ReportGenerator()
        
        # Create GUI elements
        self.setup_gui()
        
        # Status queue for threading
        self.status_queue = queue.Queue()
        self.root.after(100, self.check_status_queue)
    
    def setup_styles(self):
        """Setup ttk styles for better appearance"""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure('TNotebook', background='#f8f9fa')
        style.configure('TNotebook.Tab', padding=[20, 8], font=('Arial', 10, 'bold'))
        
        # Configure frame styles
        style.configure('Card.TLabelFrame', relief='solid', borderwidth=1, background='white')
        style.configure('Card.TLabelFrame.Label', font=('Arial', 11, 'bold'), foreground='#2c3e50')
        
        # Create custom style if it doesn't exist
        try:
            style.element_create('Card.TLabelFrame.border', 'from', 'TLabelFrame.border')
            style.layout('Card.TLabelFrame', [('Card.TLabelFrame.border', {'children': [('Card.TLabelFrame.padding', {'children': [('Card.TLabelFrame.label', {'side': 'top'}), ('Card.TLabelFrame.text', {'expand': '1', 'sticky': 'nswe'})], 'sticky': 'nswe'})], 'sticky': 'nswe'})])
        except:
            # Fallback to default style if custom style creation fails
            pass
        
        # Configure button styles
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', '#3498db'), ('!active', '#2980b9')],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Configure entry and combobox styles
        style.configure('TEntry', fieldbackground='white', borderwidth=1)
        style.configure('TCombobox', fieldbackground='white', borderwidth=1)
        
        # Configure treeview style
        style.configure('Treeview', background='white', foreground='black', 
                       fieldbackground='white', borderwidth=1)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'),
                       background='#ecf0f1', foreground='#2c3e50')
    
    def setup_gui(self):
        """Setup the main GUI interface with scrollable content"""
        # Configure main window
        self.root.title("SafeData Pipeline - Government of India")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg='#f8f9fa')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Setup styles
        self.setup_styles()
        
        # Create main container with scrollbars
        self.main_canvas = tk.Canvas(self.root, bg='#f8f9fa')
        self.main_scrollbar_v = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollbar_h = ttk.Scrollbar(self.root, orient="horizontal", command=self.main_canvas.xview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar_v.set, xscrollcommand=self.main_scrollbar_h.set)
        
        # Pack canvas and scrollbars
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar_v.pack(side="right", fill="y")
        self.main_scrollbar_h.pack(side="bottom", fill="x")
        
        # Bind mouse wheel to canvas
        self.main_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.main_canvas.bind("<Button-4>", self._on_mousewheel)
        self.main_canvas.bind("<Button-5>", self._on_mousewheel)
        
        # Create header with Government of India branding
        self.create_header()
        
        # Create notebook for different modules
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Create tabs
        self.create_data_upload_tab()
        self.create_risk_assessment_tab()
        self.create_privacy_enhancement_tab()
        self.create_utility_measurement_tab()
        self.create_report_generation_tab()
        self.create_configuration_tab()
        self.create_help_tab()
        
        # Create status bar
        self.create_status_bar()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.delta:
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:
            self.main_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.main_canvas.yview_scroll(1, "units")
    
    def create_header(self):
        """Create header with government branding"""
        header_frame = tk.Frame(self.scrollable_frame, bg='#FF6B35', height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Left section with logo placeholder and title
        left_frame = tk.Frame(header_frame, bg='#FF6B35')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=15)
        
        # Government emblem placeholder (could be replaced with actual image)
        emblem_frame = tk.Frame(left_frame, bg='white', width=60, height=60)
        emblem_frame.pack(side=tk.LEFT, padx=(0, 15))
        emblem_frame.pack_propagate(False)
        
        emblem_label = tk.Label(emblem_frame, text="🇮🇳", font=('Arial', 24), bg='white')
        emblem_label.pack(expand=True)
        
        # Title section
        title_frame = tk.Frame(left_frame, bg='#FF6B35')
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(
            title_frame,
            text="SafeData Pipeline",
            font=('Arial', 22, 'bold'),
            bg='#FF6B35',
            fg='white'
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Data Privacy Protection & Anonymization System",
            font=('Arial', 11),
            bg='#FF6B35',
            fg='#FFE4D6'
        )
        subtitle_label.pack(anchor=tk.W)
        
        # Right section with ministry info
        right_frame = tk.Frame(header_frame, bg='#FF6B35')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=15)
        
        ministry_label = tk.Label(
            right_frame,
            text="Government of India",
            font=('Arial', 12, 'bold'),
            bg='#FF6B35',
            fg='white'
        )
        ministry_label.pack(anchor=tk.E)
        
        dept_label = tk.Label(
            right_frame,
            text="Ministry of Electronics and IT",
            font=('Arial', 10),
            bg='#FF6B35',
            fg='#FFE4D6'
        )
        dept_label.pack(anchor=tk.E)
    
    def create_data_upload_tab(self):
        """Create data upload and quality assessment tab"""
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="📁 Data Upload")
        
        # File selection frame with improved styling
        file_frame = ttk.LabelFrame(self.data_tab, text="📁 File Selection", padding=15)
        file_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(
            file_frame,
            text="📂 Select Data File",
            command=self.select_file,
            width=20,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # Data preview frame with improved styling
        preview_frame = ttk.LabelFrame(self.data_tab, text="📋 Data Preview", padding=15)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Create treeview for data display
        self.data_tree = ttk.Treeview(preview_frame, show='headings', height=15)
        self.data_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        
        # Quality assessment frame with improved styling
        quality_frame = ttk.LabelFrame(self.data_tab, text="🔍 Data Quality Assessment", padding=15)
        quality_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.quality_text = scrolledtext.ScrolledText(quality_frame, height=6, wrap=tk.WORD)
        self.quality_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(self.data_tab)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            action_frame,
            text="🔧 Apply Automatic Fixes",
            command=self.apply_fixes,
            width=22,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="🔄 Refresh Preview",
            command=self.refresh_preview,
            width=17
        ).pack(side=tk.LEFT, padx=5)
    
    def create_risk_assessment_tab(self):
        """Create risk assessment tab"""
        self.risk_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.risk_tab, text="⚠️ Risk Assessment")
        
        # Configuration frame
        config_frame = ttk.LabelFrame(self.risk_tab, text="⚙️ Assessment Configuration", padding=15)
        config_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Quasi-identifiers selection with scrollbar
        ttk.Label(config_frame, text="Quasi-Identifiers:").grid(row=0, column=0, sticky=tk.W, pady=2)
        qi_frame = ttk.Frame(config_frame)
        qi_frame.grid(row=0, column=1, padx=10, pady=2, sticky=tk.W+tk.E)
        self.qi_listbox = tk.Listbox(qi_frame, selectmode=tk.MULTIPLE, height=4)
        qi_scrollbar = ttk.Scrollbar(qi_frame, orient=tk.VERTICAL, command=self.qi_listbox.yview)
        self.qi_listbox.configure(yscrollcommand=qi_scrollbar.set)
        self.qi_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        qi_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sensitive attributes selection with scrollbar
        ttk.Label(config_frame, text="Sensitive Attributes:").grid(row=1, column=0, sticky=tk.W, pady=2)
        sa_frame = ttk.Frame(config_frame)
        sa_frame.grid(row=1, column=1, padx=10, pady=2, sticky=tk.W+tk.E)
        self.sa_listbox = tk.Listbox(sa_frame, selectmode=tk.MULTIPLE, height=4)
        sa_scrollbar = ttk.Scrollbar(sa_frame, orient=tk.VERTICAL, command=self.sa_listbox.yview)
        self.sa_listbox.configure(yscrollcommand=sa_scrollbar.set)
        self.sa_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sa_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # K-threshold
        ttk.Label(config_frame, text="K-Anonymity Threshold:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.k_threshold = tk.IntVar(value=3)
        k_scale = ttk.Scale(config_frame, from_=2, to=20, variable=self.k_threshold, orient=tk.HORIZONTAL)
        k_scale.grid(row=2, column=1, padx=10, pady=2, sticky=tk.W+tk.E)
        self.k_label = ttk.Label(config_frame, text="3")
        self.k_label.grid(row=2, column=2, padx=5, pady=2)
        k_scale.configure(command=lambda v: self.k_label.configure(text=str(int(float(v)))))
        
        # Sample size
        ttk.Label(config_frame, text="Sample Size (%):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sample_size = tk.DoubleVar(value=0.5)
        sample_scale = ttk.Scale(config_frame, from_=0.1, to=1.0, variable=self.sample_size, orient=tk.HORIZONTAL)
        sample_scale.grid(row=3, column=1, padx=10, pady=2, sticky=tk.W+tk.E)
        self.sample_label = ttk.Label(config_frame, text="50%")
        self.sample_label.grid(row=3, column=2, padx=5, pady=2)
        sample_scale.configure(command=lambda v: self.sample_label.configure(text=f"{int(float(v)*100)}%"))
        
        config_frame.columnconfigure(1, weight=1)
        
        # Run assessment button
        ttk.Button(
            config_frame,
            text="🔍 Run Risk Assessment",
            command=self.run_risk_assessment,
            width=22,
            style='Primary.TButton'
        ).grid(row=4, column=1, pady=15)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.risk_tab, text="📊 Risk Assessment Results", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.risk_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD)
        self.risk_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_privacy_enhancement_tab(self):
        """Create privacy enhancement tab"""
        self.privacy_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.privacy_tab, text="🔒 Privacy Enhancement")
        
        # Technique selection frame
        technique_frame = ttk.LabelFrame(self.privacy_tab, text="Privacy Technique Selection", padding=10)
        technique_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.privacy_technique = tk.StringVar(value="K-Anonymity")
        techniques = ["K-Anonymity", "L-Diversity", "T-Closeness", "Differential Privacy"]
        
        for i, technique in enumerate(techniques):
            ttk.Radiobutton(
                technique_frame,
                text=technique,
                variable=self.privacy_technique,
                value=technique,
                command=self.update_privacy_params
            ).grid(row=0, column=i, padx=10, pady=5)
        
        # Parameters frame
        self.params_frame = ttk.LabelFrame(self.privacy_tab, text="Technique Parameters", padding=10)
        self.params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.update_privacy_params()
        
        # Apply button
        ttk.Button(
            self.privacy_tab,
            text="Apply Privacy Enhancement",
            command=self.apply_privacy_enhancement,
            width=25
        ).pack(pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.privacy_tab, text="Enhancement Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.privacy_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD)
        self.privacy_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_utility_measurement_tab(self):
        """Create utility measurement tab"""
        self.utility_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.utility_tab, text="📊 Utility Measurement")
        
        # Metrics selection frame
        metrics_frame = ttk.LabelFrame(self.utility_tab, text="Utility Metrics Selection", padding=10)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.selected_metrics = {}
        metrics = [
            "Statistical Similarity",
            "Correlation Preservation", 
            "Distribution Similarity",
            "Information Loss",
            "Classification Utility"
        ]
        
        for i, metric in enumerate(metrics):
            var = tk.BooleanVar(value=True)
            self.selected_metrics[metric.lower().replace(' ', '_')] = var
            ttk.Checkbutton(
                metrics_frame,
                text=metric,
                variable=var
            ).grid(row=i//3, column=i%3, padx=10, pady=5, sticky=tk.W)
        
        # Run measurement button
        ttk.Button(
            metrics_frame,
            text="Measure Utility",
            command=self.measure_utility,
            width=20
        ).grid(row=2, column=1, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.utility_tab, text="Utility Measurement Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.utility_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD)
        self.utility_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_report_generation_tab(self):
        """Create report generation tab"""
        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text="📄 Reports")
        
        # Report configuration frame
        config_frame = ttk.LabelFrame(self.report_tab, text="Report Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Report type
        ttk.Label(config_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.report_type = tk.StringVar(value="Comprehensive")
        report_combo = ttk.Combobox(
            config_frame,
            textvariable=self.report_type,
            values=["Executive Summary", "Technical Report", "Comprehensive"],
            state="readonly",
            width=20
        )
        report_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Output format
        ttk.Label(config_frame, text="Output Format:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_format = tk.StringVar(value="PDF")
        format_combo = ttk.Combobox(
            config_frame,
            textvariable=self.output_format,
            values=["PDF", "HTML", "Both"],
            state="readonly",
            width=20
        )
        format_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Include options
        ttk.Label(config_frame, text="Include:").grid(row=2, column=0, sticky=tk.W, pady=5)
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.include_visualizations = tk.BooleanVar(value=True)
        self.include_recommendations = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Visualizations", variable=self.include_visualizations).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Recommendations", variable=self.include_recommendations).pack(side=tk.LEFT, padx=5)
        
        # Generate report button
        ttk.Button(
            config_frame,
            text="Generate Report",
            command=self.generate_report,
            width=20
        ).grid(row=3, column=1, pady=10)
        
        # Export data frame
        export_frame = ttk.LabelFrame(self.report_tab, text="Data Export", padding=10)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        export_buttons = [
            ("Export to CSV", self.export_csv),
            ("Export to Excel", self.export_excel),
            ("Export to JSON", self.export_json)
        ]
        
        for i, (text, command) in enumerate(export_buttons):
            ttk.Button(export_frame, text=text, command=command, width=15).grid(row=0, column=i, padx=5, pady=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.report_tab, text="Generation Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.report_status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD)
        self.report_status_text.pack(fill=tk.BOTH, expand=True)
    
    def create_configuration_tab(self):
        """Create configuration and settings tab"""
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="⚙️ Configuration")
        
        # Privacy profiles frame
        profiles_frame = ttk.LabelFrame(self.config_tab, text="Privacy Profiles", padding=10)
        profiles_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Profile selection
        ttk.Label(profiles_frame, text="Load Profile:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(profiles_frame, textvariable=self.profile_var, width=20)
        self.profile_combo.grid(row=0, column=1, padx=10, pady=5)
        self.load_profiles()
        
        ttk.Button(profiles_frame, text="Load", command=self.load_profile, width=10).grid(row=0, column=2, padx=5)
        
        # New profile creation
        ttk.Label(profiles_frame, text="New Profile:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_profile_name = tk.StringVar()
        ttk.Entry(profiles_frame, textvariable=self.new_profile_name, width=20).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(profiles_frame, text="Save", command=self.save_profile, width=10).grid(row=1, column=2, padx=5)
        
        # System settings frame
        system_frame = ttk.LabelFrame(self.config_tab, text="System Settings", padding=10)
        system_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Max file size
        ttk.Label(system_frame, text="Max File Size (MB):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_file_size = tk.IntVar(value=100)
        ttk.Spinbox(system_frame, from_=1, to=1000, textvariable=self.max_file_size, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        # Chunk size
        ttk.Label(system_frame, text="Chunk Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chunk_size = tk.IntVar(value=10000)
        ttk.Spinbox(system_frame, from_=1000, to=100000, textvariable=self.chunk_size, width=20, increment=1000).grid(row=1, column=1, padx=10, pady=5)
        
        # Security options
        self.enable_encryption = tk.BooleanVar(value=True)
        self.enable_logging = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(system_frame, text="Enable Data Encryption", variable=self.enable_encryption).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(system_frame, text="Enable Detailed Logging", variable=self.enable_logging).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Save settings button
        ttk.Button(system_frame, text="Save Settings", command=self.save_settings, width=20).grid(row=4, column=1, pady=10)
    
    def create_help_tab(self):
        """Create help and documentation tab"""
        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="❓ Help")
        
        # Help topic selection
        topic_frame = ttk.Frame(self.help_tab)
        topic_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(topic_frame, text="Help Topic:").pack(side=tk.LEFT, padx=5)
        
        self.help_topic = tk.StringVar(value="Quick Start Guide")
        help_combo = ttk.Combobox(
            topic_frame,
            textvariable=self.help_topic,
            values=[
                "Quick Start Guide",
                "Data Upload",
                "Risk Assessment", 
                "Privacy Enhancement",
                "Utility Measurement",
                "Report Generation",
                "Configuration",
                "Troubleshooting"
            ],
            state="readonly",
            width=25
        )
        help_combo.pack(side=tk.LEFT, padx=10)
        help_combo.bind('<<ComboboxSelected>>', self.show_help_content)
        
        # Help content
        self.help_text = scrolledtext.ScrolledText(self.help_tab, wrap=tk.WORD, font=('Arial', 10))
        self.help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Load initial help content
        self.show_help_content()
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ttk.Frame(self.scrollable_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=2, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.status_bar, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def select_file(self):
        """Handle file selection"""
        file_types = [
            ("All Supported", "*.csv;*.xlsx;*.xls;*.json;*.xml;*.parquet"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx;*.xls"),
            ("JSON files", "*.json"),
            ("XML files", "*.xml"),
            ("Parquet files", "*.parquet"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=file_types
        )
        
        if filename:
            self.file_label.configure(text=os.path.basename(filename))
            self.load_data_file(filename)
    
    def load_data_file(self, filename):
        """Load data file in background thread"""
        def load_in_thread():
            try:
                self.status_queue.put(("status", "Loading data file..."))
                self.status_queue.put(("progress", "start"))
                
                # Load data using DataHandler
                self.current_data = self.data_handler.load_file(filename)
                
                # Assess quality
                quality_results = self.data_handler.assess_data_quality(self.current_data)
                
                self.status_queue.put(("data_loaded", (self.current_data, quality_results)))
                self.status_queue.put(("progress", "stop"))
                self.status_queue.put(("status", "Data loaded successfully"))
                
            except Exception as e:
                self.status_queue.put(("error", f"Error loading file: {str(e)}"))
                self.status_queue.put(("progress", "stop"))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def check_status_queue(self):
        """Check for status updates from background threads"""
        try:
            while True:
                message_type, data = self.status_queue.get_nowait()
                
                if message_type == "status":
                    self.status_label.configure(text=data)
                elif message_type == "progress":
                    if data == "start":
                        self.progress.start()
                    else:
                        self.progress.stop()
                elif message_type == "data_loaded":
                    self.handle_data_loaded(data)
                elif message_type == "error":
                    messagebox.showerror("Error", data)
                    self.status_label.configure(text="Error occurred")
                elif message_type == "results":
                    self.handle_results(data)
                    
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_status_queue)
    
    def handle_data_loaded(self, data):
        """Handle data loading completion"""
        data_df, quality_results = data
        
        # Update data preview
        self.update_data_preview(data_df)
        
        # Update quality assessment
        self.update_quality_assessment(quality_results)
        
        # Update column lists for risk assessment
        self.update_column_lists(data_df.columns)
    
    def update_data_preview(self, data):
        """Update data preview treeview"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if data is not None and not data.empty:
            # Configure columns
            columns = list(data.columns)
            self.data_tree['columns'] = columns
            
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, minwidth=50)
            
            # Add data rows (first 100 for performance)
            for i, row in data.head(100).iterrows():
                self.data_tree.insert('', 'end', values=list(row))
    
    def update_quality_assessment(self, quality_results):
        """Update quality assessment display"""
        self.quality_text.delete(1.0, tk.END)
        
        if quality_results:
            quality_report = f"""Data Quality Assessment Results:

Quality Score: {quality_results.get('quality_score', 0):.1f}%
Total Rows: {quality_results.get('total_rows', 0):,}
Total Columns: {quality_results.get('total_columns', 0)}
Missing Values: {quality_results.get('missing_percentage', 0):.1f}%

Issues Detected:
"""
            
            issues = quality_results.get('issues', [])
            if issues:
                for issue in issues[:10]:  # Show first 10 issues
                    quality_report += f"• {issue}\n"
                if len(issues) > 10:
                    quality_report += f"... and {len(issues) - 10} more issues\n"
            else:
                quality_report += "No significant issues detected.\n"
            
            self.quality_text.insert(1.0, quality_report)
    
    def update_column_lists(self, columns):
        """Update column lists for risk assessment"""
        # Clear existing items
        self.qi_listbox.delete(0, tk.END)
        self.sa_listbox.delete(0, tk.END)
        
        # Add columns
        for col in columns:
            self.qi_listbox.insert(tk.END, col)
            self.sa_listbox.insert(tk.END, col)
    
    def apply_fixes(self):
        """Apply automatic data fixes"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        def fix_in_thread():
            try:
                self.status_queue.put(("status", "Applying automatic fixes..."))
                self.status_queue.put(("progress", "start"))
                
                # Apply fixes
                if self.current_data is not None:
                    fixed_data = self.data_handler.repair_data(self.current_data.copy())
                else:
                    raise ValueError("No data available to repair")
                
                # Re-assess quality
                quality_results = self.data_handler.assess_data_quality(fixed_data)
                
                self.current_data = fixed_data
                self.status_queue.put(("data_loaded", (fixed_data, quality_results)))
                self.status_queue.put(("progress", "stop"))
                self.status_queue.put(("status", "Fixes applied successfully"))
                
            except Exception as e:
                self.status_queue.put(("error", f"Error applying fixes: {str(e)}"))
        
        threading.Thread(target=fix_in_thread, daemon=True).start()
    
    def refresh_preview(self):
        """Refresh data preview"""
        if self.current_data is not None:
            self.update_data_preview(self.current_data)
        else:
            messagebox.showinfo("Info", "No data loaded to refresh")
    
    def run_risk_assessment(self):
        """Run risk assessment"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        # Get selected quasi-identifiers and sensitive attributes
        qi_indices = self.qi_listbox.curselection()
        sa_indices = self.sa_listbox.curselection()
        
        if not qi_indices:
            messagebox.showwarning("Warning", "Please select at least one quasi-identifier")
            return
        
        qi_cols = [self.qi_listbox.get(i) for i in qi_indices]
        sa_cols = [self.sa_listbox.get(i) for i in sa_indices] if sa_indices else []
        
        def assess_in_thread():
            try:
                self.status_queue.put(("status", "Running risk assessment..."))
                self.status_queue.put(("progress", "start"))
                
                # Run assessment
                if self.current_data is not None:
                    results = self.risk_assessment.assess_risk(
                        self.current_data,
                        quasi_identifiers=qi_cols,
                        sensitive_attributes=sa_cols,
                        k_threshold=self.k_threshold.get(),
                        sample_size=self.sample_size.get()
                    )
                else:
                    raise ValueError("No data available for risk assessment")
                
                self.risk_results = results
                self.status_queue.put(("results", ("risk", results)))
                self.status_queue.put(("progress", "stop"))
                self.status_queue.put(("status", "Risk assessment completed"))
                
            except Exception as e:
                self.status_queue.put(("error", f"Error in risk assessment: {str(e)}"))
        
        threading.Thread(target=assess_in_thread, daemon=True).start()
    
    def handle_results(self, data):
        """Handle analysis results"""
        result_type, results = data
        
        if result_type == "risk":
            self.display_risk_results(results)
        elif result_type == "privacy":
            self.display_privacy_results(results)
        elif result_type == "utility":
            self.display_utility_results(results)
    
    def display_risk_results(self, results):
        """Display risk assessment results"""
        self.risk_results_text.delete(1.0, tk.END)
        
        report = f"""Risk Assessment Results:

Overall Risk Score: {results.get('overall_risk', 0):.3f}
Risk Level: {results.get('risk_level', 'Unknown')}

K-Anonymity Analysis:
• K-Anonymity Violations: {results.get('k_anonymity_violations', 0)}
• Unique Records: {results.get('unique_records', 0)}
• Total Equivalence Classes: {results.get('total_classes', 0)}

Attack Scenario Results:
"""
        
        attack_results = results.get('attack_scenarios', {})
        for attack, score in attack_results.items():
            report += f"• {attack.title()} Attack Risk: {score:.3f}\n"
        
        recommendations = results.get('recommendations', [])
        if recommendations:
            report += "\nRecommendations:\n"
            for rec in recommendations:
                report += f"• {rec}\n"
        
        self.risk_results_text.insert(1.0, report)
    
    def display_privacy_results(self, processed_data):
        """Display privacy enhancement results"""
        self.privacy_results_text.delete(1.0, tk.END)
        
        if processed_data is not None:
            original_rows = len(self.current_data) if self.current_data is not None else 0
            processed_rows = len(processed_data)
            
            report = f"""Privacy Enhancement Results:
            
Technique Applied: {self.privacy_technique.get()}
Original Data Shape: {self.current_data.shape if self.current_data is not None else 'Unknown'}
Processed Data Shape: {processed_data.shape}

Records Summary:
• Original Records: {original_rows:,}
• Processed Records: {processed_rows:,}
• Information Loss: {((original_rows - processed_rows) / original_rows * 100) if original_rows > 0 else 0:.1f}%

Status: Privacy enhancement completed successfully.
You can now proceed to Utility Measurement to assess data quality preservation.
"""
        else:
            report = "Privacy enhancement failed. Please check your parameters and try again."
        
        self.privacy_results_text.insert(1.0, report)
    
    def update_privacy_params(self):
        """Update privacy technique parameters"""
        # Clear existing parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        technique = self.privacy_technique.get()
        
        if technique == "K-Anonymity":
            ttk.Label(self.params_frame, text="K Value:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.k_value = tk.IntVar(value=3)
            ttk.Spinbox(self.params_frame, from_=2, to=20, textvariable=self.k_value, width=10).grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(self.params_frame, text="Method:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
            self.k_method = tk.StringVar(value="Global Recoding")
            method_combo = ttk.Combobox(self.params_frame, textvariable=self.k_method, 
                                       values=["Global Recoding", "Local Recoding", "Clustering"], 
                                       state="readonly", width=15)
            method_combo.grid(row=0, column=3, padx=5, pady=5)
            
        elif technique == "L-Diversity":
            ttk.Label(self.params_frame, text="L Value:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.l_value = tk.IntVar(value=2)
            ttk.Spinbox(self.params_frame, from_=2, to=10, textvariable=self.l_value, width=10).grid(row=0, column=1, padx=5, pady=5)
            
        elif technique == "T-Closeness":
            ttk.Label(self.params_frame, text="T Value:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.t_value = tk.DoubleVar(value=0.3)
            ttk.Scale(self.params_frame, from_=0.1, to=1.0, variable=self.t_value, 
                     orient=tk.HORIZONTAL, length=150).grid(row=0, column=1, padx=5, pady=5)
            
        elif technique == "Differential Privacy":
            ttk.Label(self.params_frame, text="Epsilon:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.epsilon = tk.DoubleVar(value=1.0)
            ttk.Scale(self.params_frame, from_=0.1, to=10.0, variable=self.epsilon, 
                     orient=tk.HORIZONTAL, length=150).grid(row=0, column=1, padx=5, pady=5)
    
    def apply_privacy_enhancement(self):
        """Apply privacy enhancement technique"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        technique = self.privacy_technique.get()
        
        def enhance_in_thread():
            try:
                self.status_queue.put(("status", f"Applying {technique}..."))
                self.status_queue.put(("progress", "start"))
                
                # Get quasi-identifiers
                qi_indices = self.qi_listbox.curselection()
                if not qi_indices:
                    self.status_queue.put(("error", "Please select quasi-identifiers from Risk Assessment tab first"))
                    return
                
                qi_cols = [self.qi_listbox.get(i) for i in qi_indices]
                
                # Apply technique based on selection
                if self.current_data is None:
                    raise ValueError("No data available for privacy enhancement")
                
                if technique == "K-Anonymity":
                    self.processed_data = self.privacy_enhancement.apply_k_anonymity(
                        self.current_data,
                        k=self.k_value.get(),
                        quasi_identifiers=qi_cols,
                        method=self.k_method.get().lower().replace(' ', '_')
                    )
                
                elif technique == "L-Diversity":
                    sa_indices = self.sa_listbox.curselection()
                    if not sa_indices:
                        self.status_queue.put(("error", "Please select sensitive attributes for L-Diversity"))
                        return
                    
                    sa_col = self.sa_listbox.get(sa_indices[0])  # Use first selected
                    self.processed_data = self.privacy_enhancement.apply_l_diversity(
                        self.current_data,
                        l=self.l_value.get(),
                        quasi_identifiers=qi_cols,
                        sensitive_attribute=sa_col
                    )
                
                # Add other techniques as needed...
                
                self.status_queue.put(("results", ("privacy", self.processed_data)))
                self.status_queue.put(("progress", "stop"))
                self.status_queue.put(("status", f"{technique} applied successfully"))
                
            except Exception as e:
                self.status_queue.put(("error", f"Error applying {technique}: {str(e)}"))
        
        threading.Thread(target=enhance_in_thread, daemon=True).start()
    
    def measure_utility(self):
        """Measure utility of processed data"""
        if self.current_data is None or self.processed_data is None:
            messagebox.showwarning("Warning", "Please load data and apply privacy enhancement first")
            return
        
        def measure_in_thread():
            try:
                self.status_queue.put(("status", "Measuring utility..."))
                self.status_queue.put(("progress", "start"))
                
                # Get selected metrics
                selected = [metric for metric, var in self.selected_metrics.items() if var.get()]
                
                # Measure utility
                if self.current_data is not None and self.processed_data is not None:
                    results = self.utility_measurement.measure_utility(
                        self.current_data,
                        self.processed_data,
                        metrics=selected
                    )
                else:
                    raise ValueError("Both original and processed data are required for utility measurement")
                
                self.utility_results = results
                self.status_queue.put(("results", ("utility", results)))
                self.status_queue.put(("progress", "stop"))
                self.status_queue.put(("status", "Utility measurement completed"))
                
            except Exception as e:
                self.status_queue.put(("error", f"Error measuring utility: {str(e)}"))
        
        threading.Thread(target=measure_in_thread, daemon=True).start()
    
    def display_utility_results(self, results):
        """Display utility measurement results"""
        self.utility_results_text.delete(1.0, tk.END)
        
        report = f"""Utility Measurement Results:

Overall Utility Score: {results.get('overall_utility', 0):.3f}
Utility Level: {results.get('utility_level', 'Unknown')}

Detailed Metrics:
"""
        
        for metric, value in results.items():
            if metric not in ['overall_utility', 'utility_level', 'visualizations', 'recommendations']:
                if isinstance(value, dict) and 'overall' in value:
                    report += f"• {metric.replace('_', ' ').title()}: {value['overall']:.3f}\n"
                elif isinstance(value, (int, float)):
                    report += f"• {metric.replace('_', ' ').title()}: {value:.3f}\n"
        
        recommendations = results.get('recommendations', [])
        if recommendations:
            report += "\nRecommendations:\n"
            for rec in recommendations:
                report += f"• {rec}\n"
        
        self.utility_results_text.insert(1.0, report)
    
    def generate_report(self):
        """Generate analysis report"""
        if not any([self.risk_results, self.utility_results]):
            messagebox.showwarning("Warning", "Please run analysis first")
            return
        
        # Get save location
        file_types = []
        if self.output_format.get() in ["PDF", "Both"]:
            file_types.append(("PDF files", "*.pdf"))
        if self.output_format.get() in ["HTML", "Both"]:
            file_types.append(("HTML files", "*.html"))
        
        filename = filedialog.asksaveasfilename(
            title="Save Report",
            filetypes=file_types,
            defaultextension=".pdf" if "PDF" in self.output_format.get() else ".html"
        )
        
        if filename:
            def generate_in_thread():
                try:
                    self.status_queue.put(("status", "Generating report..."))
                    self.status_queue.put(("progress", "start"))
                    
                    # Prepare report data
                    report_data = {
                        'dataset_info': {
                            'name': os.path.basename(self.file_label.cget('text')),
                            'rows': len(self.current_data) if self.current_data is not None else 0,
                            'columns': len(self.current_data.columns) if self.current_data is not None else 0,
                            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        },
                        'risk_results': self.risk_results,
                        'utility_results': self.utility_results,
                        'configuration': {
                            'report_type': self.report_type.get(),
                            'include_visualizations': self.include_visualizations.get(),
                            'include_recommendations': self.include_recommendations.get()
                        }
                    }
                    
                    # Generate report
                    if filename.endswith('.pdf'):
                        report_content = self.report_generator.generate_pdf_report(
                            report_data, 
                            self.report_type.get()
                        )
                        with open(filename, 'wb') as f:
                            f.write(report_content)
                    else:
                        report_content = self.report_generator.generate_html_report(
                            report_data,
                            self.report_type.get()
                        )
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(report_content)
                    
                    self.status_queue.put(("progress", "stop"))
                    self.status_queue.put(("status", f"Report saved to {filename}"))
                    
                    # Show success message
                    messagebox.showinfo("Success", f"Report generated successfully!\nSaved to: {filename}")
                    
                except Exception as e:
                    self.status_queue.put(("error", f"Error generating report: {str(e)}"))
            
            threading.Thread(target=generate_in_thread, daemon=True).start()
    
    def export_csv(self):
        """Export processed data to CSV"""
        self.export_data("csv")
    
    def export_excel(self):
        """Export processed data to Excel"""
        self.export_data("excel")
    
    def export_json(self):
        """Export processed data to JSON"""
        self.export_data("json")
    
    def export_data(self, format_type):
        """Export data in specified format"""
        if self.processed_data is None:
            messagebox.showwarning("Warning", "No processed data to export")
            return
        
        file_types = {
            "csv": [("CSV files", "*.csv")],
            "excel": [("Excel files", "*.xlsx")],
            "json": [("JSON files", "*.json")]
        }
        
        filename = filedialog.asksaveasfilename(
            title=f"Export to {format_type.upper()}",
            filetypes=file_types[format_type],
            defaultextension=f".{format_type if format_type != 'excel' else 'xlsx'}"
        )
        
        if filename:
            try:
                if format_type == "csv":
                    self.processed_data.to_csv(filename, index=False)
                elif format_type == "excel":
                    self.processed_data.to_excel(filename, index=False)
                elif format_type == "json":
                    self.processed_data.to_json(filename, orient='records', indent=2)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                self.status_label.configure(text=f"Data exported to {format_type.upper()}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def load_profiles(self):
        """Load available privacy profiles"""
        try:
            if os.path.exists('config/privacy_profiles.json'):
                with open('config/privacy_profiles.json', 'r') as f:
                    profiles = json.load(f)
                self.profile_combo['values'] = list(profiles.keys())
        except Exception:
            pass
    
    def load_profile(self):
        """Load selected privacy profile"""
        profile_name = self.profile_var.get()
        if not profile_name:
            return
        
        try:
            with open('config/privacy_profiles.json', 'r') as f:
                profiles = json.load(f)
            
            if profile_name in profiles:
                profile = profiles[profile_name]
                # Apply profile settings
                self.k_threshold.set(profile.get('k_threshold', 3))
                messagebox.showinfo("Success", f"Profile '{profile_name}' loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile: {str(e)}")
    
    def save_profile(self):
        """Save current settings as new profile"""
        profile_name = self.new_profile_name.get()
        if not profile_name:
            messagebox.showwarning("Warning", "Please enter a profile name")
            return
        
        try:
            # Load existing profiles
            profiles = {}
            if os.path.exists('config/privacy_profiles.json'):
                with open('config/privacy_profiles.json', 'r') as f:
                    profiles = json.load(f)
            
            # Create new profile
            new_profile = {
                'k_threshold': self.k_threshold.get(),
                'privacy_technique': self.privacy_technique.get(),
                'created_date': datetime.now().isoformat()
            }
            
            profiles[profile_name] = new_profile
            
            # Save profiles
            os.makedirs('config', exist_ok=True)
            with open('config/privacy_profiles.json', 'w') as f:
                json.dump(profiles, f, indent=2)
            
            # Update combo box
            self.load_profiles()
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def save_settings(self):
        """Save system settings"""
        try:
            settings = {
                'max_file_size': self.max_file_size.get(),
                'chunk_size': self.chunk_size.get(),
                'enable_encryption': self.enable_encryption.get(),
                'enable_logging': self.enable_logging.get(),
                'updated_date': datetime.now().isoformat()
            }
            
            os.makedirs('config', exist_ok=True)
            with open('config/system_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def show_help_content(self, event=None):
        """Show help content based on selected topic"""
        topic = self.help_topic.get()
        
        help_content = {
            "Quick Start Guide": """
SafeData Pipeline - Quick Start Guide

1. LOAD DATA
   • Click 'Select Data File' to upload your dataset
   • Supported formats: CSV, Excel, JSON, XML, Parquet
   • Review the data quality assessment

2. ASSESS RISK
   • Go to Risk Assessment tab
   • Select quasi-identifiers (age, location, etc.)
   • Select sensitive attributes (salary, medical info, etc.)
   • Click 'Run Risk Assessment'

3. ENHANCE PRIVACY
   • Go to Privacy Enhancement tab
   • Choose a privacy technique
   • Configure parameters
   • Click 'Apply Privacy Enhancement'

4. MEASURE UTILITY
   • Go to Utility Measurement tab
   • Select metrics to evaluate
   • Click 'Measure Utility'

5. GENERATE REPORTS
   • Go to Reports tab
   • Choose report type and format
   • Click 'Generate Report'
            """,
            
            "Data Upload": """
Data Upload Module

SUPPORTED FORMATS:
• CSV files (.csv)
• Excel files (.xlsx, .xls)
• JSON files (.json)
• XML files (.xml)
• Parquet files (.parquet)

DATA QUALITY CHECKS:
• Missing value detection
• Data type validation
• Duplicate record identification
• Format consistency verification
• Statistical outlier detection

AUTOMATIC FIXES:
• Fill missing values
• Standardize data types
• Remove duplicates
• Correct formatting issues
            """,
            
            "Risk Assessment": """
Risk Assessment Module

PURPOSE:
Evaluate re-identification risks in your dataset

QUASI-IDENTIFIERS:
• Attributes that can identify individuals
• Examples: Age, Gender, ZIP code, Education
• Select multiple columns from the list

SENSITIVE ATTRIBUTES:
• Information you want to protect
• Examples: Salary, Medical conditions, Religion
• Optional but recommended for comprehensive assessment

PARAMETERS:
• K-Anonymity Threshold: Minimum group size (2-20)
• Sample Size: Percentage of data to analyze (10-100%)

RESULTS:
• Overall risk score and level
• K-anonymity violations
• Attack scenario simulations
• Recommendations for improvement
            """,
            
            "Privacy Enhancement": """
Privacy Enhancement Module

AVAILABLE TECHNIQUES:

K-ANONYMITY:
• Ensures each record appears in groups of at least k individuals
• Parameters: K value (2-20), Method (Global/Local/Clustering)
• Best for: General privacy protection

L-DIVERSITY:
• Ensures diversity in sensitive attributes within each group
• Parameters: L value (2-10)
• Best for: Protecting against homogeneity attacks

T-CLOSENESS:
• Maintains distribution similarity between groups and population
• Parameters: T value (0.1-1.0)
• Best for: Protecting against skewness attacks

DIFFERENTIAL PRIVACY:
• Adds statistical noise to protect individual privacy
• Parameters: Epsilon (0.1-10.0)
• Best for: Statistical analysis and research
            """,
            
            "Utility Measurement": """
Utility Measurement Module

PURPOSE:
Assess how much data quality is preserved after anonymization

AVAILABLE METRICS:

STATISTICAL SIMILARITY:
• Compares basic statistics (mean, std, etc.)
• Measures distribution preservation

CORRELATION PRESERVATION:
• Evaluates relationship maintenance between variables
• Important for analytical validity

DISTRIBUTION SIMILARITY:
• Compares data distributions using statistical tests
• Ensures representative samples

INFORMATION LOSS:
• Quantifies amount of information removed
• Lower is better for utility

CLASSIFICATION UTILITY:
• Tests machine learning model performance
• Practical utility assessment
            """,
            
            "Report Generation": """
Report Generation Module

REPORT TYPES:

EXECUTIVE SUMMARY:
• High-level overview for management
• 2-5 pages, non-technical language
• Focus on compliance and recommendations

TECHNICAL REPORT:
• Detailed analysis for technical teams
• 10-20 pages with methodology details
• Complete statistical analysis

COMPREHENSIVE:
• Complete documentation for all audiences
• 15-30 pages with appendices
• Suitable for compliance and archival

OUTPUT FORMATS:
• PDF: Professional, printable format
• HTML: Interactive, web-friendly format
• Both: Generate both formats

EXPORT OPTIONS:
• CSV: Processed data for analysis
• Excel: Formatted data with multiple sheets
• JSON: Structured data for applications
            """,
            
            "Configuration": """
Configuration Module

PRIVACY PROFILES:
• Save commonly used settings
• Quick setup for routine tasks
• Share configurations across team
• Version control for settings

SYSTEM SETTINGS:

Max File Size (1-1000 MB):
• Controls maximum upload size
• Adjust based on system resources

Chunk Size (1,000-100,000):
• Processing batch size
• Smaller for limited memory
• Larger for better performance

SECURITY OPTIONS:
• Enable Data Encryption: Protects data in memory
• Enable Detailed Logging: Comprehensive audit trail

BEST PRACTICES:
• Start with default profiles
• Test with small datasets first
• Document configuration rationale
• Enable all security features
            """,
            
            "Troubleshooting": """
Troubleshooting Guide

COMMON ISSUES:

FILE LOADING ERRORS:
• Check file format and encoding
• Ensure file is not corrupted
• Try smaller sample first
• Verify column headers

MEMORY ERRORS:
• Reduce file size or chunk size
• Close other applications
• Use sampling for large datasets
• Consider system upgrade

PRIVACY TECHNIQUE FAILURES:
• Check quasi-identifier selection
• Verify data types are compatible
• Try different parameter values
• Ensure sufficient data volume

POOR UTILITY SCORES:
• Adjust privacy parameters
• Try different techniques
• Consider hybrid approaches
• Balance privacy vs utility

EXPORT ISSUES:
• Check disk space availability
• Verify write permissions
• Try different file locations
• Contact system administrator

PERFORMANCE TIPS:
• Use appropriate chunk sizes
• Enable system optimizations
• Process during low-usage hours
• Monitor system resources
            """
        }
        
        content = help_content.get(topic, "Help content not available for this topic.")
        
        self.help_text.delete(1.0, tk.END)
        self.help_text.insert(1.0, content)


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = SafeDataGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.quit()


if __name__ == "__main__":
    main()
