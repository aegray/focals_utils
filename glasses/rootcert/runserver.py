import ssl

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        value = ''
        self.send_response(200)
        self.send_header('Content type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body>ITWORKS</body></html>\n')
#            self.send_error(404, "File not Found")


httpd = HTTPServer(('0.0.0.0', 4443), MyHandler)

httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile="bysouth.com.key",
        certfile='bysouth.com.crt', server_side=True)

httpd.serve_forever()

