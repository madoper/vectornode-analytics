"""Tiny proxy: moves form_data from query string to JSON body for Superset chart/data."""
import json, urllib.request, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

SUPERSET = "http://127.0.0.1:8088"

class Proxy(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b""

        # If form_data in query string and body is empty/non-JSON
        if "form_data=" in self.path and (not body or not body.strip()):
            try:
                from urllib.parse import urlparse, parse_qs
                qs = urlparse(self.path).query
                params = parse_qs(qs)
                fd = params.get("form_data", [None])[0]
                if fd:
                    j = json.loads(fd)
                    body = json.dumps(j).encode()
                    if "Content-Type" not in dict(self.headers):
                        self.headers["Content-Type"] = "application/json"
            except:
                pass

        # Forward to Superset
        url = SUPERSET + self.path
        req = urllib.request.Request(url, data=body, method="POST")
        for k, v in self.headers.items():
            if k.lower() not in ("host", "content-length"):
                req.add_header(k, v)

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() != "transfer-encoding":
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    do_GET = do_POST

    def log_message(self, format, *args):
        pass  # silent

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    HTTPServer(("127.0.0.1", port), Proxy).serve_forever()
