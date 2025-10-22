#!/usr/bin/env python3
"""
GUI entry point for the code analyzer.
"""
from ui.analyzer_window import AnalyzerWindow

def main():
    """Start the GUI application."""
    app = AnalyzerWindow()
    app.mainloop()

if __name__ == '__main__':
    main()