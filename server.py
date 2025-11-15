from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import subprocess
import sys
import os

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.wfile.write(f"<html><body><h1>Current Time: {now}</h1></body></html>".encode())
        
        # Launch GUI with current server time
        gui_path = os.path.join(os.path.dirname(__file__), 'src', 'user-gui', 'gui.py')
        try:
            subprocess.Popen([sys.executable, gui_path, now])
        except Exception as e:
            print(f"Error launching GUI: {e}")

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHandler)
    print("Server running at http://localhost:8000 ...")
    print("Access the server in your browser to launch the GUI")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
