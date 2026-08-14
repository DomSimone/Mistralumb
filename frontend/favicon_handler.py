"""
Simple favicon handler for Python HTTP server.
Place this in the frontend directory and use it with a custom HTTP server.
"""

from http.server import SimpleHTTPRequestHandler
import os

class FaviconHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            # Return 204 No Content to suppress 404
            self.send_response(204)
            self.end_headers()
        else:
            super().do_GET()
