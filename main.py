from http.server import HTTPServer, BaseHTTPRequestHandler
from time import sleep
from datetime import datetime
import urllib.parse
import mimetypes
import pathlib
import socket
import json
import threading


HOST = '127.0.0.1'
HTTP_PORT = 3000
UDP_IP = '127.0.0.1'
UDP_PORT = 5000
data = ''


def run_http_server():
    class HttpHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            pr_url = urllib.parse.urlparse(self.path)
            if pr_url.path == '/':
                self.send_html_file('index.html')
            elif pr_url.path == '/contact':
                self.send_html_file('contact.html')
            else:
                if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                    self.send_static()
                else:
                    self.send_html_file('error.html', 404)

        def send_html_file(self, filename, status=200):
            self.send_response(status)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(filename, 'rb') as fd:
                self.wfile.write(fd.read())

        def send_static(self):
            self.send_response(200)
            mt = mimetypes.guess_type(self.path)
            if mt:
                self.send_header("Content-type", mt[0])
            else:
                self.send_header("Content-type", 'text/plain')
            self.end_headers()
            with open(f'.{self.path}', 'rb') as file:
                self.wfile.write(file.read())

        def do_POST(self):
            data = self.rfile.read(int(self.headers['Content-Length']))
            print(data)
            data_parse = urllib.parse.unquote_plus(data.decode())
            print(data_parse)
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            print(data_dict)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return data_dict

    server_address = ('', HTTP_PORT)
    http_server = HTTPServer(server_address, HttpHandler)
    print(f"HTTP server started on port {HTTP_PORT}")
    http_server.serve_forever()


def run_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = UDP_IP, UDP_PORT
    sock.bind(server)
    print(f"UDP server started on {UDP_IP}:{UDP_PORT}")
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')
            
            # Отримання поточного часу та створення запису для JSON
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            message = data.decode()
            record = {timestamp: {"message": message}}
            
            # Зберігання запису у файлі data.json
            with open('storage/data.json', 'a') as file:
                json.dump(record, file, indent=2)
                file.write('\n')
            
            sock.sendto(data, address)
            print(f'Send data: {data.decode()} to: {address}')

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    http_server_thread = threading.Thread(target=run_http_server)
    udp_server_thread = threading.Thread(target=run_udp_server)
    
    http_server_thread.start()
    udp_server_thread.start()
    
    http_server_thread.join()
    udp_server_thread.join()
    print('Done!')
