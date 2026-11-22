#!/usr/bin/env python3
"""Static file server for local testing of the built editor/player bundles.

Serves ./website (or the first CLI arg) with caching disabled so a rebuilt
beepbox_editor.min.js is always picked up on refresh.

Usage: python3 tools/serve.py [dir] [port]
"""
import http.server
import os
import socketserver
import sys

DIRECTORY = sys.argv[1] if len(sys.argv) > 1 else "website"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("PORT", "8090"))


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):  # quiet
        pass


class Server(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with Server(("", PORT), NoCacheHandler) as httpd:
        print(f"serving {os.getcwd()} on http://localhost:{PORT}")
        print("  editor:  http://localhost:%d/" % PORT)
        print("  debug:   http://localhost:%d/index_debug.html" % PORT)
        print("  player:  http://localhost:%d/player/" % PORT)
        print("ctrl-c to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
