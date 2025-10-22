"""
Main window for the code analyzer application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import List
import threading
import queue

from core.main import CodeAnalyzer
from ui.selector import FileSelector

class AnalyzerWindow(tk.Tk):
    """Main window for the code analyzer application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.title("Code Analyzer")
        self.geometry("800x600")
        
        self.analyzer = CodeAnalyzer()
        self.result_queue = queue.Queue()
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Create main notebook
        self.notebook = ttk.Notebook(self)
        
        # Create selector tab
        selector_frame = ttk.Frame(self.notebook)
        self.file_selector = FileSelector(
            selector_frame,
            self._handle_analysis
        )
        self.file_selector.pack(fill='both', expand=True)
        
        # Create results tab
        self.results_frame = ttk.Frame(self.notebook)
        self._create_results_widgets()
        
        # Add tabs to notebook
        self.notebook.add(selector_frame, text='Select Files')
        self.notebook.add(self.results_frame, text='Results')
    
    def _create_results_widgets(self):
        """Create widgets for the results tab."""
        # Create results tree
        self.results_tree = ttk.Treeview(
            self.results_frame,
            columns=('severity', 'type', 'message', 'file', 'line'),
            show='headings'
        )
        
        # Configure columns
        self.results_tree.heading('severity', text='Severity')
        self.results_tree.heading('type', text='Type')
        self.results_tree.heading('message', text='Message')
        self.results_tree.heading('file', text='File')
        self.results_tree.heading('line', text='Line')
        
        self.results_tree.column('severity', width=80)
        self.results_tree.column('type', width=100)
        self.results_tree.column('message', width=300)
        self.results_tree.column('file', width=200)
        self.results_tree.column('line', width=60)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.results_frame,
            orient='vertical',
            command=self.results_tree.yview
        )
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Create progress frame
        self.progress_frame = ttk.Frame(self.results_frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            variable=self.progress_var
        )
        self.status_label = ttk.Label(
            self.progress_frame,
            text="Ready"
        )
        
        # Create summary frame
        self.summary_frame = ttk.LabelFrame(
            self.results_frame,
            text="Analysis Summary"
        )
        self.summary_text = tk.Text(
            self.summary_frame,
            height=5,
            width=50,
            wrap='word',
            state='disabled'
        )
    
    def _setup_layout(self):
        """Set up widget layout."""
        # Main notebook
        self.notebook.pack(fill='both', expand=True)
        
        # Results layout
        self.progress_frame.pack(fill='x', padx=5, pady=5)
        self.status_label.pack(side='left', padx=5)
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=5)
        
        self.summary_frame.pack(fill='x', padx=5, pady=5)
        self.summary_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results tree and scrollbar
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def _handle_analysis(self, paths: List[Path]):
        """
        Handle analysis of selected paths.
        
        Args:
            paths: List of paths to analyze
        """
        # Clear previous results
        self.results_tree.delete(*self.results_tree.get_children())
        self.progress_var.set(0)
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=self._analyze_paths,
            args=(paths,)
        )
        thread.start()
        
        # Start checking for results
        self.after(100, self._check_results)
    
    def _analyze_paths(self, paths: List[Path]):
        """
        Analyze paths in background thread.
        
        Args:
            paths: List of paths to analyze
        """
        try:
            total_files = sum(1 for p in paths for _ in p.rglob('*.py'))
            processed = 0
            
            for path in paths:
                if path.is_file():
                    results = self.analyzer.analyze_file(path)
                    if results:
                        self.result_queue.put(('file', path, results))
                    processed += 1
                    progress = (processed / total_files) * 100
                    self.result_queue.put(('progress', progress))
                else:
                    results = self.analyzer.analyze_project(str(path))
                    self.result_queue.put(('project', path, results))
            
            self.result_queue.put(('done', None))
            
        except Exception as e:
            self.result_queue.put(('error', str(e)))
    
    def _check_results(self):
        """Check for and process analysis results."""
        try:
            while True:
                result_type, *data = self.result_queue.get_nowait()
                
                if result_type == 'file':
                    path, results = data
                    self._add_file_results(path, results)
                elif result_type == 'project':
                    path, results = data
                    self._add_project_results(results)
                elif result_type == 'progress':
                    progress = data[0]
                    self.progress_var.set(progress)
                    self.status_label['text'] = f"Analyzing... {progress:.1f}%"
                elif result_type == 'done':
                    self.status_label['text'] = "Analysis complete"
                    self._show_summary()
                    return
                elif result_type == 'error':
                    error_msg = data[0]
                    messagebox.showerror("Error", f"Analysis failed: {error_msg}")
                    return
                
        except queue.Empty:
            # Queue is empty, check again later
            self.after(100, self._check_results)
    
    def _add_file_results(self, path: Path, results: dict):
        """Add results for a single file."""
        for issue in results.get('issues', []):
            self.results_tree.insert(
                '',
                'end',
                values=(
                    issue['severity'],
                    issue['type'],
                    issue['message'],
                    str(path),
                    issue.get('line', 'N/A')
                )
            )
    
    def _add_project_results(self, results: dict):
        """Add results for an entire project."""
        for file_path, file_results in results['files'].items():
            self._add_file_results(Path(file_path), file_results)
    
    def _show_summary(self):
        """Show analysis summary."""
        total_issues = len(self.results_tree.get_children())
        severity_counts = {}
        
        for item in self.results_tree.get_children():
            severity = self.results_tree.item(item)['values'][0]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        summary = f"Analysis Complete\n\n"
        summary += f"Total Issues: {total_issues}\n\n"
        summary += "Issues by Severity:\n"
        for severity, count in severity_counts.items():
            summary += f"- {severity}: {count}\n"
        
        self.summary_text.configure(state='normal')
        self.summary_text.delete('1.0', 'end')
        self.summary_text.insert('1.0', summary)
        self.summary_text.configure(state='disabled')
        
        # Switch to results tab
        self.notebook.select(1)