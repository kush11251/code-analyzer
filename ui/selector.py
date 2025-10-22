"""
File selector module for the code analyzer.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Optional, Tuple, Callable
from pathlib import Path

class FileSelector(ttk.Frame):
    """A UI component for selecting files and folders for analysis."""
    
    def __init__(self, parent: tk.Widget, callback: Callable[[List[Path]], None]):
        """
        Initialize the file selector.
        
        Args:
            parent: Parent widget
            callback: Function to call with selected paths
        """
        super().__init__(parent)
        self.callback = callback
        self.selected_paths: List[Path] = []
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Create style
        style = ttk.Style()
        style.configure('FileList.Treeview', rowheight=25)
        
        # Create buttons
        btn_frame = ttk.Frame(self)
        self.add_file_btn = ttk.Button(
            btn_frame,
            text="Add File",
            command=self._add_file
        )
        self.add_folder_btn = ttk.Button(
            btn_frame,
            text="Add Folder",
            command=self._add_folder
        )
        self.remove_btn = ttk.Button(
            btn_frame,
            text="Remove Selected",
            command=self._remove_selected
        )
        
        # Create file list
        self.file_list = ttk.Treeview(
            self,
            columns=('type', 'path'),
            show='headings',
            style='FileList.Treeview'
        )
        self.file_list.heading('type', text='Type')
        self.file_list.heading('path', text='Path')
        self.file_list.column('type', width=100)
        self.file_list.column('path', width=400)
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.file_list.yview
        )
        self.file_list.configure(yscrollcommand=self.scrollbar.set)
        
        # Create analyze button
        self.analyze_btn = ttk.Button(
            self,
            text="Analyze Selected",
            command=self._analyze_selected
        )
    
    def _setup_layout(self):
        """Set up widget layout."""
        # Button layout
        btn_frame = ttk.Frame(self)
        self.add_file_btn.pack(side='left', padx=5)
        self.add_folder_btn.pack(side='left', padx=5)
        self.remove_btn.pack(side='left', padx=5)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        # File list and scrollbar layout
        list_frame = ttk.Frame(self)
        self.file_list.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        list_frame.pack(fill='both', expand=True, padx=5)
        
        # Analyze button layout
        self.analyze_btn.pack(fill='x', padx=5, pady=5)
    
    def _add_file(self):
        """Add a file to the list."""
        filetypes = (
            ('Python files', '*.py'),
            ('JavaScript files', '*.js *.jsx *.ts *.tsx'),
            ('Java files', '*.java'),
            ('All files', '*.*')
        )
        
        paths = filedialog.askopenfilenames(
            title='Select Files to Analyze',
            filetypes=filetypes
        )
        
        for path in paths:
            path = Path(path)
            if path not in self.selected_paths:
                self.selected_paths.append(path)
                self.file_list.insert(
                    '',
                    'end',
                    values=('File', str(path))
                )
    
    def _add_folder(self):
        """Add a folder to the list."""
        path = filedialog.askdirectory(
            title='Select Folder to Analyze'
        )
        
        if path:
            path = Path(path)
            if path not in self.selected_paths:
                self.selected_paths.append(path)
                self.file_list.insert(
                    '',
                    'end',
                    values=('Folder', str(path))
                )
    
    def _remove_selected(self):
        """Remove selected items from the list."""
        selected = self.file_list.selection()
        
        for item_id in selected:
            path = Path(self.file_list.item(item_id)['values'][1])
            self.selected_paths.remove(path)
            self.file_list.delete(item_id)
    
    def _analyze_selected(self):
        """Trigger analysis of selected paths."""
        if self.selected_paths:
            self.callback(self.selected_paths)