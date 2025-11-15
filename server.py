from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote
import html

from detectors.vulnerability_scanner import scan_project, Vulnerability

# Base directory for browsing; restrict folder picker to this tree
BASE_ROOT = Path(__file__).resolve().parent


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Code Analyzer</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 20px; }
    h1 { margin-bottom: 0.2rem; }
    .subtitle { color: #666; margin-bottom: 1rem; }
    .time { font-size: 0.9rem; color: #555; margin-bottom: 1rem; }
    form { margin-bottom: 1rem; }
    input[type=text] { width: 420px; padding: 4px 6px; }
    button { padding: 4px 10px; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: 0.9rem; }
    th, td { border: 1px solid #ccc; padding: 4px 6px; text-align: left; vertical-align: top; }
    th { background-color: #f2f2f2; }
    .sev-HIGH { background-color: #ffe5e5; }
    .sev-MEDIUM { background-color: #fff5e0; }
    .sev-LOW { background-color: #e9f5ff; }
    .code { font-family: Menlo, Monaco, Consolas, "Courier New", monospace; white-space: pre; }
    .path { font-family: Menlo, Monaco, Consolas, "Courier New", monospace; }
    .no-results { margin-top: 1rem; font-style: italic; color: #555; }
  </style>
</head>
<body>
  <h1>Code Analyzer</h1>
  <div class="subtitle">Simple multi-language static analysis via a web UI.</div>
  <div class="time">Server time: {time}</div>

  <form method="get" action="/scan">
    <label for="path">Project path to scan:</label><br />
    <input type="text" id="path" name="path" value="{path}" />
    <button type="submit">Scan</button>
  </form>
  <p><a href="/browse">Browse folders on server…</a></p>

  {content}

  <p style="margin-top:2rem; font-size:0.8rem; color:#888;">Tip: for large projects, start with a smaller subfolder (e.g. src/app).</p>
</body>
</html>
"""


def _render_template(*, path: str, content: str, time_str: str) -> str:
    """Simple placeholder replacement without interpreting CSS braces.

    We avoid str.format(), which would try to treat CSS braces as
    formatting fields and raise KeyError. Instead we replace only the
    three placeholders we intentionally use.
    """

    body = HTML_TEMPLATE
    body = body.replace("{time}", html.escape(time_str))
    body = body.replace("{path}", html.escape(path))
    body = body.replace("{content}", content)
    return body


def render_index(path: str = "") -> str:
    """Render the index page with an optional path and no results."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return _render_template(path=path, content="", time_str=now)


def render_results(path: str, findings: list[Vulnerability]) -> str:
    """Render the page with a table of findings for a given path."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not findings:
        content = "<div class='no-results'>No potential vulnerabilities found.</div>"
        return _render_template(path=path, content=content, time_str=now)

    rows: list[str] = []
    rows.append("<table>")
    rows.append("<tr><th>Severity</th><th>Lang</th><th>Rule</th><th>Location</th><th>Description</th><th>Code</th></tr>")

    for v in findings:
        sev = html.escape(v.severity.upper())
        lang = html.escape(v.language)
        rule = html.escape(v.rule_id)
        location = f"{v.file_path}:{v.line}"
        location_html = f"<span class='path'>{html.escape(location)}</span>"
        desc = html.escape(v.description)
        code = html.escape(v.code or "")
        sev_class = f"sev-{sev}" if sev in {"HIGH", "MEDIUM", "LOW"} else ""

        rows.append(
            f"<tr class='{sev_class}'>"
            f"<td>{sev}</td>"
            f"<td>{lang}</td>"
            f"<td>{rule}</td>"
            f"<td>{location_html}</td>"
            f"<td>{desc}</td>"
            f"<td class='code'>{code}</td>"
            f"</tr>"
        )

    rows.append("</table>")
    content = "".join(rows)
    return _render_template(path=path, content=content, time_str=now)


def _safe_browse_path(raw_path: str) -> Path:
    """Resolve *raw_path* and keep it inside BASE_ROOT for safety."""

    if not raw_path:
        return BASE_ROOT

    try:
        p = Path(raw_path).expanduser().resolve()
    except Exception:
        return BASE_ROOT

    try:
        p.relative_to(BASE_ROOT)
    except ValueError:
        # Outside allowed tree; clamp back to base
        return BASE_ROOT

    return p


def render_browse(path: Path) -> str:
    """Render a simple server-side folder picker UI."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        entries = sorted(
            [p for p in path.iterdir() if p.is_dir()],
            key=lambda p: p.name.lower(),
        )
    except OSError:
        entries = []

    parts: list[str] = []
    parts.append("<h2>Select folder</h2>")
    parts.append(
        "<p>Current folder: <span class='path'>{}</span></p>".format(
            html.escape(str(path))
        )
    )
    parts.append("<ul>")

    # Parent directory link (do not go above BASE_ROOT)
    if path != BASE_ROOT:
        parent = path.parent
        parts.append(
            f"<li><a href=\"/browse?path={quote(str(parent))}\">.. (parent)</a></li>"
        )

    for entry in entries:
        name = entry.name or str(entry)
        parts.append(
            f"<li><a href=\"/browse?path={quote(str(entry))}\">{html.escape(name)}</a></li>"
        )

    parts.append("</ul>")

    # Button to scan the currently selected folder
    parts.append(
        "<form method=\"get\" action=\"/scan\">"
        f"<input type=\"hidden\" name=\"path\" value=\"{html.escape(str(path))}\" />"
        "<button type=\"submit\">Scan this folder</button>"
        "</form>"
    )

    content = "".join(parts)
    return _render_template(path=str(path), content=content, time_str=now)


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            html_body = render_index()
            self._send_html(html_body)
        elif parsed.path == "/scan":
            self.handle_scan(parsed)
        elif parsed.path == "/browse":
            self.handle_browse(parsed)
        else:
            self.send_error(404, "Not Found")

    def handle_scan(self, parsed):
        params = parse_qs(parsed.query)
        raw_path = params.get("path", [""])[0]
        path_str = raw_path or "."

        try:
            root = Path(path_str).expanduser().resolve()
        except Exception:
            root = Path(".").resolve()

        findings = scan_project(root)

        # Sort by severity then file/line for a stable display
        severity_order = {"high": 0, "medium": 1, "low": 2}

        def sort_key(v: Vulnerability):
            return (
                severity_order.get(v.severity.lower(), 3),
                v.file_path,
                v.line,
                v.rule_id,
            )

        findings_sorted = sorted(findings, key=sort_key)
        html_body = render_results(path_str, findings_sorted)
        self._send_html(html_body)

    def handle_browse(self, parsed):
        params = parse_qs(parsed.query)
        raw_path = params.get("path", [""])[0]
        path = _safe_browse_path(raw_path)
        html_body = render_browse(path)
        self._send_html(html_body)

    def _send_html(self, content: str):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))


def run_server():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, SimpleHandler)
    print("Web analyzer running at http://localhost:8080 ...")
    print("Open this URL in your browser, enter a project path, and click Scan.")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
