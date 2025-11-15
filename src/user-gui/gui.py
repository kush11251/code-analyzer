import wx
from datetime import datetime
import sys
from pathlib import Path
from typing import List, Optional

# Ensure the project root (which contains the detectors package) is importable
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from detectors.vulnerability_scanner import scan_project, Vulnerability


class TimeFrame(wx.Frame):
    def __init__(self, server_time: Optional[str] = None):
        super().__init__(parent=None, title="Code Analyzer")
        self.server_time = server_time
        self.selected_path: Optional[Path] = None

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Time display (local and server) ---
        time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_font = wx.Font(
            12,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )

        self.local_label = wx.StaticText(panel, label="", style=wx.ALIGN_LEFT)
        self.local_label.SetFont(time_font)

        self.server_label = wx.StaticText(panel, label="", style=wx.ALIGN_RIGHT)
        self.server_label.SetFont(time_font)

        time_sizer.Add(self.local_label, 1, wx.ALL | wx.EXPAND, 5)
        time_sizer.Add(self.server_label, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(time_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # --- Folder selection + scan controls ---
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.path_label = wx.StaticText(panel, label="No folder selected")
        controls_sizer.Add(self.path_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.select_button = wx.Button(panel, label="Select Folder...")
        self.scan_button = wx.Button(panel, label="Scan")

        controls_sizer.Add(self.select_button, 0, wx.ALL, 5)
        controls_sizer.Add(self.scan_button, 0, wx.ALL, 5)

        main_sizer.Add(controls_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # --- Results area ---
        results_label = wx.StaticText(panel, label="Analysis results:")
        main_sizer.Add(results_label, 0, wx.LEFT | wx.TOP, 5)

        self.results = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
            size=(800, 400),
        )
        results_font = wx.Font(
            10,
            wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        self.results.SetFont(results_font)

        main_sizer.Add(self.results, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(main_sizer)

        # --- Timer for updating time labels ---
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_time)
        self.timer.Start(1000)
        self.update_time(None)

        # --- Wire up events ---
        self.select_button.Bind(wx.EVT_BUTTON, self.on_select_folder)
        self.scan_button.Bind(wx.EVT_BUTTON, self.on_scan_clicked)

        self.SetSize((900, 600))
        self.Centre()
        self.Show()

    def update_time(self, event):
        # Update local time
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.local_label.SetLabel(f"Local Time: {local_time}")

        # Update server time if available
        if self.server_time:
            self.server_label.SetLabel(f"Server Time: {self.server_time}")
        else:
            self.server_label.SetLabel("")

    def on_select_folder(self, event):
        dlg = wx.DirDialog(
            self,
            "Select folder to analyze",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        try:
            if dlg.ShowModal() == wx.ID_OK:
                path_str = dlg.GetPath()
                self.selected_path = Path(path_str)
                self.path_label.SetLabel(str(self.selected_path))
                self.run_analysis()
        finally:
            dlg.Destroy()

    def on_scan_clicked(self, event):
        if not self.selected_path:
            wx.MessageBox(
                "Please select a folder first.",
                "No folder selected",
                style=wx.OK | wx.ICON_WARNING,
            )
            return
        self.run_analysis()

    def run_analysis(self):
        root = self.selected_path
        if root is None:
            return

        self.results.SetValue("Scanning project...\n")
        wx.GetApp().Yield()  # allow UI to refresh while scanning

        findings = scan_project(root)
        self.display_results(findings)

    def display_results(self, findings: List[Vulnerability]):
        if not findings:
            self.results.SetValue("No potential vulnerabilities found.\n")
            return

        # Sort by severity (high > medium > low), then by file and line
        severity_order = {"high": 0, "medium": 1, "low": 2}

        def sort_key(v: Vulnerability):
            return (
                severity_order.get(v.severity.lower(), 3),
                v.file_path,
                v.line,
                v.rule_id,
            )

        findings_sorted = sorted(findings, key=sort_key)

        lines: List[str] = []
        lines.append(f"Found {len(findings_sorted)} potential issue(s):")
        lines.append("")

        header = f"{'SEVERITY':8} {'LANG':8} {'RULE':8} LOCATION"
        lines.append(header)
        lines.append("-" * len(header))

        for v in findings_sorted:
            location = f"{v.file_path}:{v.line}"
            lines.append(
                f"{v.severity.upper():8} {v.language:8} {v.rule_id:8} {location}"
            )
            lines.append(f"  {v.description}")
            if v.code:
                lines.append(f"  > {v.code.strip()}")
            lines.append("")

        self.results.SetValue("\n".join(lines))


if __name__ == "__main__":
    app = wx.App()
    server_time = sys.argv[1] if len(sys.argv) > 1 else None
    frame = TimeFrame(server_time)
    app.MainLoop()
